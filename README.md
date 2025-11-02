# Malayalam Pronominal Anaphoric Coreference Resolution

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17508334.svg)](https://zenodo.org/records/17508334)

An exploratory implementation applying Hobbs' algorithm for resolving pronominal anaphoric coreferences in Malayalam text. 

🏆 **Best Paper Award @ [ABACon'20 (Abacus Conference)](docs/conference/PET3-107_Ms.Enfa%20Rose%20George_Best%20Paper%20Award.pdf)**

### About

This project explores whether rule-based coreference resolution methods designed for English can be adapted to Malayalam. While the system demonstrates proof-of-concept feasibility, the error rate remains too high for production use, a finding that supports the need for Malayalam-specific approaches rather than direct adaptation of English methods.

This system was developed as part of my undergraduate thesis project at Rajagiri School of Engineering and Technology (2020) under the advisement of Prof.Mathews Abraham. The work was presented at the Abacus Conference in 2020, organized by Sahrdaya College of Engineering and Technology, Kodakara, where it won the best paper award.

### Installation
```bash
# Clone the repository
git clone https://github.com/beingenfa/malayalam-hobbs-coreference.git
cd malayalam-hobbs-coreference

# Install dependencies
pip install -r requirements.txt
```
### Usage
```python
from MalayalamCorefResolver import MalayalamCorefResolver

resolver = MalayalamCorefResolver()
text = "പൂച്ച മേശയ്‌ക്ക് മുകളിൽ ഇരിക്കുന്നു. അത് ഉറങ്ങുന്നു."
result = resolver.find_coref(text)
```

See `src/example_usage.py` for details.

### Citation

If you use this work, please cite:
```bibtex
@software{enfa_fane_2025_17508334,
  author       = {Enfa Fane and
                  Abraham, Mathews},
  title        = {beingenfa/malayalam-coreference-hobbs: public
                   archive
                  },
  month        = nov,
  year         = 2025,
  publisher    = {Zenodo},
  version      = {1.0},
  doi          = {10.5281/zenodo.17508334},
  url          = {https://doi.org/10.5281/zenodo.17508334},
}
```
### External Tools

This work would not have been possible without the following Malayalam NLP tools:

- **[anoopkunchukuttan/indic_nlp_library](https://github.com/anoopkunchukuttan/indic_nlp_library)** - Morphological analysis for Indic languages

- **[ltrc/indic-tokenizer](https://github.com/ltrc/indic-tokenizer)** - Tokenization with Indic language support

- **[Devadath/Malayalam-Shallow-Parser](https://github.com/Devadath/Malayalam-Shallow-Parser)** - POS tagging and chunking models
    
    V V & Sharma (2016). [Significance of an Accurate Sandhi-Splitter in Shallow Parsing of Dravidian Languages](https://aclanthology.org/P16-3006/). *ACL 2016*.

Please cite the original authors of these tools when using this system.

- [ccmward/hobbs](cmward/hobbs) implementation of Hobb's algorithm was adapted for use.
- Hobbs, J. R. (1978). [Resolving pronoun references. Lingua, 44(4)](https://www.sciencedirect.com/science/article/pii/0024384178900062), 311-338.

### License

This project is licensed under the MIT License

-----

Last Updated: Nov 2, 2025

Contact: enfafane at gmail
