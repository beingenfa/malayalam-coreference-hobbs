import subprocess
import tempfile
from pathlib import Path
from typing import List, Tuple

from external.irtokz.tokenise import tokenize_ind


class MalayalamShallowParser:
    """
    Performs shallow parsing for Malayalam text.

    This class is a rough wrapper of Shallow Parser here -
    https://github.com/Devadath/Malayalam-Shallow-Parser
    """

    def __init__(self):
        base_dir = Path(__file__).resolve().parent.resolve().parent / "devdath"
        models_dir = base_dir / "models"
        self.pos_model_path = models_dir / "devdath_pos.model"
        self.chunk_model_path = models_dir / "devdath_chunk.model"
        self.sandhi_dir = base_dir / "sandhi_splitter"
        self.sandhi_config = self.sandhi_dir / "config"

    def sandhi_split(self, text: str) -> str:
        """Used mostly as found in original repo. Did not refactor"""
        input_file = self.sandhi_dir / "input.txt"
        output_file = self.sandhi_dir / "san.out"

        # Write text to temporary input
        input_file.write_text(text, encoding="utf-8")

        # Load original config and replace paths
        config_template = self.sandhi_config.read_text(encoding="utf-8")
        config_dynamic = (
            config_template.replace("input_file", str(input_file)).replace("output_file", str(output_file)))

        config_path = self.sandhi_dir / "config_dynamic.xml"
        config_path.write_text(config_dynamic, encoding="utf-8")

        # Run Java splitter
        result = subprocess.run(["java", "-cp", str(self.sandhi_dir), "StatisticalSandhiSplitter9", str(config_path)],
                                cwd=self.sandhi_dir, text=True, capture_output=True, )

        if result.returncode != 0:
            raise RuntimeError(result.stderr)

        return output_file.read_text(encoding="utf-8")

    @staticmethod
    def tokenize_sandhi_text(sandhi_text: str) -> List[str]:
        """
        Tokenize Sandhi-split text using IIT-B tokenizer directly (no file IO).
        """
        tok = tokenize_ind(lang="'mal'", split_sen=False)
        tokenized = tok.tokenize(sandhi_text)
        return [t for t in tokenized.split() if t.strip()]

    @staticmethod
    def featurize_tokens(tokens: List[str]) -> str:
        """
        Generate character-level morphological features for each token.

        This is adapted from featurise_test.py. It produces the same feature
        format that the CRF POS tagger expects.

        Args:
            tokens: List of token strings (already tokenized and Sandhi-split)

        Returns:
            List of feature strings (one per token)
        """

        features = []

        for token in tokens:
            token = token.strip()
            if not token:
                continue

            chars = list(token)
            length = len(chars)
            if length == 0:
                continue

            # Forward and backward substring lists
            fo1 = ["".join(chars[:i + 1]) for i in range(length)]
            ba1 = ["".join(chars[-(i + 1):]) for i in range(length)]
            ba1.reverse()

            # Helper to pad or truncate sequences
            def pad(seq, size, pad_value="NONE"):
                if len(seq) >= size:
                    return seq[:size]
                return seq + [pad_value] * (size - len(seq))

            # Fixed-length prefix/suffix window
            prefixes = pad(fo1, 3)
            suffixes = pad(ba1, 7)

            feature_line = "\t".join([token] + prefixes + suffixes + [str(length)])
            features.append(feature_line)

        return "\n".join(features)

    def tag_parts_of_speech(self, text: str) -> List[tuple[str, str]]:
        """
        Full pipeline:
        Malayalam sentence → tokens → CRF features → POS tags
        """

        sandhi_text = self.sandhi_split(text)
        tokens = self.tokenize_sandhi_text(sandhi_text)
        crf_input = self.featurize_tokens(tokens)

        # Step 3: Run CRF++
        with tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8", delete=False) as tmp_in:
            tmp_in.write(crf_input)
            tmp_in.flush()
            tmp_in_path = Path(tmp_in.name)

        result = subprocess.run(["crf_test", "-m", str(self.pos_model_path), str(tmp_in_path)], text=True,
                                capture_output=True)

        if result.returncode != 0:
            raise RuntimeError(f"CRF++ failed with exit code {result.returncode}:\n{result.stderr}")

        tagged = []
        for line in result.stdout.splitlines():
            if not line.strip():
                continue
            cols = line.split("\t")
            token = cols[0]
            pos_tag = cols[-1]
            tagged.append((token, pos_tag))

        return tagged

    def chunking(self, pos_tagged: List[Tuple[str, str]]) -> List[Tuple[str, str, str]]:
        """
        Run CRF++ chunking using pre-trained Chunk.model.

        Args:
            pos_tagged: List of (token, POS_tag) pairs.

        Returns:
            List of (token, POS_tag, CHUNK_tag) tuples.
        """
        # Build CRF++ input: all POS-tagged tokens with features + POS as last column
        feature_lines = []
        for token, pos in pos_tagged:
            # reuse same featurization for each token, but append POS at the end
            chars = list(token)
            length = len(chars)
            fo1 = ["".join(chars[:i + 1]) for i in range(length)]
            ba1 = ["".join(chars[-(i + 1):]) for i in range(length)]
            ba1.reverse()

            def pad(seq, size, pad_value="NONE"):
                if len(seq) >= size:
                    return seq[:size]
                return seq + [pad_value] * (size - len(seq))

            prefixes = pad(fo1, 3)
            suffixes = pad(ba1, 7)

            feature_line = "\t".join([token] + prefixes + suffixes + [str(length), pos])
            feature_lines.append(feature_line)

        crf_input = "\n".join(feature_lines) + "\n"

        # Run CRF++ chunking
        with tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8", delete=False) as tmp_in:
            tmp_in.write(crf_input)
            tmp_in.flush()
            tmp_in_path = Path(tmp_in.name)

        result = subprocess.run(["crf_test", "-m", str(self.chunk_model_path), str(tmp_in_path)], text=True,
                                capture_output=True, )

        tmp_in_path.unlink(missing_ok=True)

        if result.returncode != 0:
            raise RuntimeError(f"CRF++ Chunking failed:\n{result.stderr}")

        chunked = []
        for line in result.stdout.splitlines():
            if not line.strip():
                continue
            cols = line.split("\t")
            token = cols[0]
            pos_tag = cols[-2]  # The second last col is POS
            chunk_tag = cols[-1]  # Last col is the chunk prediction
            chunked.append((token, pos_tag, chunk_tag))

        return chunked
