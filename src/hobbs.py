"""
Adapted from https://github.com/cmward/hobbs/blob/master/hobbs.py
"""

from typing import Dict, Tuple, Optional, List, Any
import queue
import nltk
from nltk import Tree
from mlmorph import Analyser

NOMINAL_LABELS = {"PRP", "NNPS", "NNP", "NNS", "NN"}
LOCATIVE_PRONOUNS = {"ഇവിടെ", "അവിടെ"}
REFLEXIVE_SUFFIX = "തന്നെ"   # crude reflexive cue
PERSONAL_PRONOUNS = {"അവൻ", "അവൾ", "അവർ", "അവള്", "അവന്‍"}  # extend as needed
DEMONSTRATIVES   = {"ഇത്", "അത്", "ഇവ", "അവ"}


def _first_analysis(analyser: Analyser, token: str) -> tuple[str, int] | dict[Any, Any]:
    """Return first mlmorph analysis dict (or {} if none)."""
    try:
        analyses = analyser.analyse(token)
        if analyses:
            return analyses[0]
    except Exception:
        pass
    return {}

def get_feat(analyser: Analyser, token: str) -> Dict[str, str]:
    """
    Extract a compact feature bundle from mlmorph for agreement checks.
    Returns keys among: gend, num, pers, case, pos (if available).
    """
    analys = _first_analysis(analyser, token)
    feat = analys.get("feat", {}) if isinstance(analys, dict) else {}
    out = {}
    for k in ("gend", "num", "pers", "case"):
        if k in feat:
            out[k] = feat[k]
    if "pos" in analys:
        out["pos"] = analys["pos"]
    return out


def morph_compatible(analyser: Analyser, pronoun_tok: str, np_head_tok: str) -> bool:
    """
    Malayalam agreement heuristics using mlmorph.
    - person, number, gender must match if both present
    - antecedent case should be nominative or unspecified
    """
    p = get_feat(analyser, pronoun_tok)
    a = get_feat(analyser, np_head_tok)

    # If we couldn't analyze either token, be permissive
    if not p or not a:
        return True

    # person
    if p.get("pers") and a.get("pers") and p["pers"] != a["pers"]:
        return False

    # number
    if p.get("num") and a.get("num") and p["num"] != a["num"]:
        return False

    # gender (Only aims to block explicit conflict)
    if p.get("gend") and a.get("gend") and p["gend"] != a["gend"]:
        return False

    # case: prefer nominative/unspecified for antecedent head
    if a.get("case") and a["case"] not in ("nom",):
        return False

    return True

def classify_pronoun(tok: str) -> str:
    if tok in LOCATIVE_PRONOUNS:
        return "locative"
    if tok.endswith(REFLEXIVE_SUFFIX):
        return "reflexive"
    if tok in PERSONAL_PRONOUNS:
        return "personal"
    if tok in DEMONSTRATIVES:
        return "demonstrative"
    return "other"

def get_pos(tree: Tree, node) -> Optional[Tuple[int, ...]]:
    for pos in tree.treepositions():
        if tree[pos] == node:
            return pos
    return None

def bft(tree: Tree):
    nodes = []
    q = queue.Queue()
    q.put(tree)
    while not q.empty():
        node = q.get()
        nodes.append(node)
        for child in node:
            if isinstance(child, nltk.Tree):
                q.put(child)
    return nodes

def get_dom_np(sents: List[Tree], pos: Tuple[int, ...]):
    tree = sents[-1]
    return tree, pos[:-1]

def walk_to_np_or_s(tree: Tree, pos: Tuple[int, ...], label_to_check: str):
    path = [pos]
    while True:
        pos = pos[:-1]
        path.append(pos)
        if label_to_check in tree[pos].label() or tree[pos].label() == "S":
            return path, pos

def check_for_intervening_np(tree: Tree, pos, proposal, pro, label_to_check: str):
    bf_nodes = bft(tree[pos])
    bf_pos = [get_pos(tree, node) for node in bf_nodes]
    # Count at least three NP-like nodes in subtree
    def _count_np(t):
        if not isinstance(t, nltk.Tree): return 0
        if label_to_check in t.label() and t.label() not in NOMINAL_LABELS:
            return 1 + sum(_count_np(c) for c in t)
        return sum(_count_np(c) for c in t)
    if _count_np(tree[pos]) >= 3:
        for node_pos in bf_pos:
            if node_pos is None: continue
            if label_to_check in tree[node_pos].label() and tree[node_pos].label() not in NOMINAL_LABELS:
                if node_pos != proposal and node_pos != get_pos(tree, pro):
                    if node_pos < proposal:
                        return True
    return False

def traverse_left(tree: Tree, pos, path, pro, label_to_check: str, check=1):
    bf_nodes = bft(tree[pos])
    bf_pos = [get_pos(tree, node) for node in bf_nodes]
    for p in bf_pos:
        if p is None:
            continue
        if p < path[0] and p not in path:
            if label_to_check in tree[p].label():
                if check == 1:
                    if check_for_intervening_np(tree, pos, p, pro, label_to_check):
                        return tree, p
                else:
                    return tree, p
    return None, None

def traverse_right(tree: Tree, pos, path, pro, label_to_check: str):
    bf_nodes = bft(tree[pos])
    bf_pos = [get_pos(tree, node) for node in bf_nodes]
    for p in bf_pos:
        if p is None:
            continue
        if p > path[0] and p not in path:
            if label_to_check in tree[p].label() or tree[p].label() == "S":
                if label_to_check in tree[p].label() and tree[p].label() not in NOMINAL_LABELS:
                    return tree, p
                return None, None
        return None, None

def traverse_tree(tree: Tree, pro, label_to_check: str):
    q = queue.Queue()
    q.put(tree)
    while not q.empty():
        node = q.get()
        if label_to_check in node.label():
            return tree, get_pos(tree, node)
        for child in node:
            if isinstance(child, nltk.Tree):
                q.put(child)
    return None, None

def hobbs(sents: List[Tree], pos: Tuple[int, ...], label_to_check: str):
    sentence_id = len(sents) - 1
    tree, pos = get_dom_np(sents, pos)
    pro = tree[pos].leaves()[0].lower()
    path, pos = walk_to_np_or_s(tree, pos, label_to_check)
    proposal = traverse_left(tree, pos, path, pro, label_to_check)
    while proposal == (None, None):
        if pos == ():
            sentence_id -= 1
            if sentence_id < 0:
                return None, None
            proposal = traverse_tree(sents[sentence_id], pro, label_to_check)
            if proposal != (None, None):
                return proposal
        path, pos = walk_to_np_or_s(tree, pos, label_to_check)
        if label_to_check in tree[pos].label() and tree[pos].label() not in NOMINAL_LABELS:
            for c in tree[pos]:
                if isinstance(c, nltk.Tree) and c.label() in NOMINAL_LABELS:
                    if get_pos(tree, c) not in path:
                        return tree, pos
        proposal = traverse_left(tree, pos, path, pro, label_to_check, check=0)
        if proposal != (None, None):
            return proposal
        if tree[pos].label() == "S":
            proposal = traverse_right(tree, pos, path, pro, label_to_check)
            if proposal != (None, None):
                return proposal
    return proposal

def _apply_hobbs(temp_trees: List[Tree], pronoun_token: str, label_to_check: str):
    pos = get_pos(temp_trees[-1], pronoun_token)
    if pos is None:
        return None, None
    pos = pos[:-1]  # drop leaf index
    return hobbs(temp_trees, pos, label_to_check)

def resolve_pronouns(
    words_list: List[List[str]],
    parsable_strings: List[str],
    pronouns: dict,
    analyser: Analyser,
    return_all_candidates: bool = False,
):
    trees = [Tree.fromstring(s) for s in parsable_strings]
    results = {}

    for sent_no, pron_indices in pronouns.items():
        temp_trees = trees[:sent_no + 1]
        out_for_sent = {}

        for pidx in pron_indices:
            pro_tok = words_list[sent_no][pidx]
            pclass = classify_pronoun(pro_tok)
            candidates = []

            # LOCATIVE special-case
            if pclass == "locative":
                tree, pos = _apply_hobbs(temp_trees, pro_tok, "LOCATIVE")
                if tree and pos:
                    cand = str(tree[pos].leaves()[0])
                    if morph_compatible(analyser, pro_tok, cand):
                        candidates.append(cand)
                if candidates:
                    out_for_sent[pidx] = candidates
                continue

            # Regular Hobbs with NP/NN passes
            for label in ("NP", "NN"):
                tree, pos = _apply_hobbs(temp_trees, pro_tok, label)
                if not (tree and pos):
                    continue
                cand = str(tree[pos].leaves()[0])

                # morphology check
                if morph_compatible(analyser, pro_tok, cand):
                    candidates.append(cand)
                    if not return_all_candidates:
                        break

            if candidates:
                out_for_sent[pidx] = list(dict.fromkeys(candidates))

        if out_for_sent:
            results[sent_no] = out_for_sent

    return results
