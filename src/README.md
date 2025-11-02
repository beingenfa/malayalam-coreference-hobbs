# External Models & Tools

This folder contains external resources and wrappers.

## Structure
```
external/
├── devdath/          # Malayalam Shallow Parser models and wrapper
├── indicNLP/         # IndicNLP morphological analyzer
└── irtokz/           # Indic tokenizer
```

## External Tools

This work would not have been possible without the following Malayalam NLP tools:

- **[anoopkunchukuttan/indic_nlp_library](https://github.com/anoopkunchukuttan/indic_nlp_library)** - Morphological analysis for Indic languages

- **[ltrc/indic-tokenizer](https://github.com/ltrc/indic-tokenizer)** - Tokenization with Indic language support

- **[Devadath/Malayalam-Shallow-Parser](https://github.com/Devadath/Malayalam-Shallow-Parser)** - POS tagging and chunking models
  
  [Significance of an Accurate Sandhi-Splitter in Shallow Parsing of Dravidian Languages](https://aclanthology.org/P16-3006/) (V V & Sharma, ACL 2016)

Please cite the original authors of these tools when using this system.

## File Details

### IndicNLP
- `indicNLP/models/morph_ml.model` - The Malayalam morphological model is a copy of [ml.model](https://github.com/anoopkunchukuttan/indic_nlp_resources/blob/master/morph/morfessor/ml.model) from [Indic NLP Resources](https://github.com/anoopkunchukuttan/indic_nlp_resources). Released under the MIT License.
- `indicNLP/wrapper.py` - Wrapper module for integrating IndicNLP morphological analysis

### Devadath Malayalam Shallow Parser
- `devdath/models/` - Contains POS tagging and chunking models
- `devdath/sandhi_splitter/` - Sandhi splitting implementation (compiled Java classes and rules)
- `devdath/wrapper.py` - Wrapper module adapted from the original Malayalam Shallow Parser for integration into this project

### IRTokenizer
- `irtokz/data/NONBREAKING_PREFIXES` - Malayalam-specific non-breaking prefix rules
- `irtokz/tokenise.py` - Tokenization implementation

## Licenses

Each tool retains its original license. Please refer to the respective repositories for license details.