import logging
import re
from pathlib import Path

import morfessor
from indicnlp import langinfo
from indicnlp.morph.unsupervised_morph import UnsupervisedMorphAnalyzer

logger = logging.getLogger(__name__)


class CustomUnsupervisedMorphAnalyzer(UnsupervisedMorphAnalyzer):
    def __init__(self, model_path: str, lang: str = 'ml', add_marker=False):
        self.lang = lang
        self.add_marker = add_marker

        io = morfessor.MorfessorIO()
        self._morfessor_model = io.read_any_model(model_path)

        # retain Indic NLP’s script checks
        self._script_range_pat = r'^[{}-{}]+$'.format(chr(langinfo.SCRIPT_RANGES[lang][0]),
            chr(langinfo.SCRIPT_RANGES[lang][1]))
        self._script_check_re = re.compile(self._script_range_pat)


def load_unsupervised_morph_analyzer():
    base_dir = Path(__file__).resolve().parent
    model_path = base_dir / "models" / "morph_ml.model"
    return CustomUnsupervisedMorphAnalyzer(model_path.as_posix())
