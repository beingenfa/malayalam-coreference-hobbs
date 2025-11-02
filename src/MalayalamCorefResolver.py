from indicnlp.tokenize import sentence_tokenize
from mlmorph import Analyser

from external.devdath.wrapper import MalayalamShallowParser
from hobbs import resolve_pronouns


class MalayalamCorefResolver:
    """
    Malayalam Coreference Resolver using Shallow Parsing + Hobbs' Algorithm.
    """
    def __init__(self):
        self.morph_analyzer = Analyser()
        self.shallow_parser = MalayalamShallowParser()

    def find_coref(self, text):
        """
        Run full Malayalam Hobbs pipeline and return structured output.
        """
        processed_doc = []
        tokenised_sentences = [s.strip() for s in sentence_tokenize.sentence_split(text, lang='ml') if s.strip()]
        for sent in tokenised_sentences:
            pos_tags = self.shallow_parser.tag_parts_of_speech(sent)
            chunks = self.shallow_parser.chunking(pos_tags)
            processed_doc.append(chunks)

        tokens = [[tok for tok, _, _ in sent] for sent in processed_doc]
        parsable_string = self.list_to_parsable_string(processed_doc)
        pronoun_map = self.build_pronoun_map(processed_doc)

        coref_groups = resolve_pronouns(tokens, parsable_string, pronoun_map, self.morph_analyzer,
            return_all_candidates=False)

        return {"sentences": tokenised_sentences, "tokens": tokens, "coref": coref_groups}

    @staticmethod
    def build_pronoun_map(processed_doc):
        """Return dict mapping sentence_id → list of pronoun token indices."""
        pronoun_map = {}
        for sent_id, sent in enumerate(processed_doc):
            indices = [i for i, (tok, pos, _) in enumerate(sent) if pos.startswith("PR__PRP")]
            if indices:
                pronoun_map[sent_id] = indices
        return pronoun_map

    @staticmethod
    def list_to_parsable_string(chunks_list):
        """Convert shallow parser chunks to Penn Treebank-style bracketed strings."""
        treesentences = []
        for sentence in chunks_list:
            treetext = "( S "
            layerstoclose = 1
            for token in sentence:
                word, pos, chunk = token
                postags = pos.split('__')
                # New chunk begins
                if "B-" in chunk:
                    if layerstoclose > 1:
                        treetext += " ) " * (layerstoclose - 1)
                        layerstoclose = 1
                    treetext += " ( CHUNK "
                    layerstoclose += 1
                # Add POS tags and token
                for postag in postags:
                    treetext += f" ( {postag}"
                    layerstoclose += 1
                treetext += f" {word} ) " * 2
                layerstoclose -= 2
            treetext += " ) " * layerstoclose
            treesentences.append(treetext)
        return treesentences