---
license: apache-2.0
language:
- multilingual
library_name: gliner
datasets:
- urchade/pile-mistral-v0.1
pipeline_tag: token-classification
---

# GLiNER multi-v2.1 — offline mirror

This repository is a self-contained, offline-ready mirror of `urchade/gliner_multi-v2.1` plus the DeBERTa v3 Large tokenizer/config files it needs at runtime. It is intended for environments that cannot reach `huggingface.co` (model-file fetch is blocked), but can install Python packages from PyPI or an internal mirror.

## What's in this repo

| File | Source | Purpose |
|---|---|---|
| `pytorch_model.bin` | upstream gliner | Fine-tuned GLiNER weights (encoder + head), 1.7 GB, Git LFS |
| `gliner_config.json` | upstream gliner, modified | GLiNER head config + **inline `encoder_config`** for the DeBERTa encoder (added so offline load skips the `AutoConfig.from_pretrained("microsoft/deberta-v3-large")` HF call) |
| `tokenizer_config.json` | upstream microsoft/deberta-v3-large | Picked up by GLiNER's `_load_tokenizer` (looks in `model_dir` first) |
| `spm.model` | upstream microsoft/deberta-v3-large | SentencePiece vocab, 2.5 MB, Git LFS |
| `config.json` | upstream microsoft/deberta-v3-large | DeBERTa base-model config (kept as reference; the encoder load uses the inline `encoder_config` in `gliner_config.json`) |
| `generator_config.json` | upstream microsoft/deberta-v3-large | Pretraining generator config (unused at inference, kept for fidelity) |
| `.gitattributes` | upstream gliner | LFS filter rules |

DeBERTa base-model weights (`microsoft/deberta-v3-large/pytorch_model.bin`, ~870 MB) are NOT included — the GLiNER `pytorch_model.bin` already contains the fine-tuned encoder.

The following upstream files do not exist in `microsoft/deberta-v3-large` (HF returns 404) and are not needed: `special_tokens_map.json`, `tokenizer.json` (fast), `added_tokens.json`.

## Clone

The 1.7 GB `pytorch_model.bin` is stored in Git LFS — you need `git-lfs` installed for the clone to materialize the file (otherwise you'll get a small pointer text file).

```bash
# One-time, per machine
git lfs install

git clone https://github.com/Jashjeet/address-parser.git
cd address-parser

# Confirm the bin landed (should be ~1.7 GB, not a few hundred bytes)
ls -lh pytorch_model.bin
```

If `pytorch_model.bin` is small (a text pointer), run `git lfs pull` to fetch the actual object.

## Install Python deps

```bash
pip install gliner torch transformers sentencepiece protobuf
```

Versions confirmed working: `gliner==0.2.26`, `torch==2.12.0`, `transformers==5.1.0`, `sentencepiece==0.2.1`, `protobuf==7.35.0`.

## Offline load (verified)

```python
import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

from gliner import GLiNER

# Pass the path to this checkout — works from any cwd
model = GLiNER.from_pretrained("/path/to/address-parser", local_files_only=True)

text = "Mary Smith works at Acme Corp at 500 Market St, San Francisco, CA 94105."
labels = ["person", "organization", "street", "city", "state", "postal code"]
for e in model.predict_entities(text, labels):
    print(e["text"], "=>", e["label"])
```

Expected output:
```
Mary Smith     => person
Acme Corp      => organization
500 Market St  => street
San Francisco  => city
CA             => state
94105          => postal code
```

## How offline loading works (under the hood)

GLiNER's `from_pretrained` reads `gliner_config.json` from `model_dir`, then:

1. **Tokenizer**: `gliner/model.py:_load_tokenizer` checks for `tokenizer_config.json` in `model_dir` first; if found, calls `AutoTokenizer.from_pretrained(model_dir)` — bypassing the HF lookup. This is why `tokenizer_config.json`, `spm.model`, and `config.json` must live at the repo root, not in a subfolder.
2. **Encoder config**: `gliner/modeling/encoder.py` checks `config.encoder_config` first; if populated, skips the `AutoConfig.from_pretrained("microsoft/deberta-v3-large")` call. This is why the deberta config is inlined into `gliner_config.json` as `encoder_config`.
3. **Encoder weights**: `model.py` passes `backbone_from_pretrained=False`, so the encoder is built from `encoder_config` and weights are loaded from the saved `pytorch_model.bin` — no HF fetch.

The `model_name` field in `gliner_config.json` still reads `"microsoft/deberta-v3-large"` but is **not used at load time** with the layout above. It only serves as a metadata pointer to the upstream base model.

---

# Upstream model card

GLiNER is a Named Entity Recognition (NER) model capable of identifying any entity type using a bidirectional transformer encoder (BERT-like). It provides a practical alternative to traditional NER models, which are limited to predefined entities, and Large Language Models (LLMs) that, despite their flexibility, are costly and large for resource-constrained scenarios.


## Links

* Paper: https://arxiv.org/abs/2311.08526
* Repository: https://github.com/urchade/GLiNER

## Available models

| Release | Model Name | # of Parameters | Language | License |
| - | - | - | - | - |
| v0 | [urchade/gliner_base](https://huggingface.co/urchade/gliner_base)<br>[urchade/gliner_multi](https://huggingface.co/urchade/gliner_multi) | 209M<br>209M | English<br>Multilingual | cc-by-nc-4.0 |
| v1 | [urchade/gliner_small-v1](https://huggingface.co/urchade/gliner_small-v1)<br>[urchade/gliner_medium-v1](https://huggingface.co/urchade/gliner_medium-v1)<br>[urchade/gliner_large-v1](https://huggingface.co/urchade/gliner_large-v1) | 166M<br>209M<br>459M | English <br> English <br> English | cc-by-nc-4.0 |
| v2 | [urchade/gliner_small-v2](https://huggingface.co/urchade/gliner_small-v2)<br>[urchade/gliner_medium-v2](https://huggingface.co/urchade/gliner_medium-v2)<br>[urchade/gliner_large-v2](https://huggingface.co/urchade/gliner_large-v2) | 166M<br>209M<br>459M |  English <br> English <br> English | apache-2.0 |
| v2.1 | [urchade/gliner_small-v2.1](https://huggingface.co/urchade/gliner_small-v2.1)<br>[urchade/gliner_medium-v2.1](https://huggingface.co/urchade/gliner_medium-v2.1)<br>[urchade/gliner_large-v2.1](https://huggingface.co/urchade/gliner_large-v2.1) <br>[urchade/gliner_multi-v2.1](https://huggingface.co/urchade/gliner_multi-v2.1) | 166M<br>209M<br>459M<br>209M | English <br> English <br> English <br> Multilingual | apache-2.0 |

## Installation
To use this model, you must install the GLiNER Python library:
```
!pip install gliner
```

## Usage
Once you've downloaded the GLiNER library, you can import the GLiNER class. You can then load this model using `GLiNER.from_pretrained` and predict entities with `predict_entities`.

```python
from gliner import GLiNER

model = GLiNER.from_pretrained("urchade/gliner_large-v2.1")

text = """
Cristiano Ronaldo dos Santos Aveiro (Portuguese pronunciation: [kɾiʃˈtjɐnu ʁɔˈnaldu]; born 5 February 1985) is a Portuguese professional footballer who plays as a forward for and captains both Saudi Pro League club Al Nassr and the Portugal national team. Widely regarded as one of the greatest players of all time, Ronaldo has won five Ballon d'Or awards,[note 3] a record three UEFA Men's Player of the Year Awards, and four European Golden Shoes, the most by a European player. He has won 33 trophies in his career, including seven league titles, five UEFA Champions Leagues, the UEFA European Championship and the UEFA Nations League. Ronaldo holds the records for most appearances (183), goals (140) and assists (42) in the Champions League, goals in the European Championship (14), international goals (128) and international appearances (205). He is one of the few players to have made over 1,200 professional career appearances, the most by an outfield player, and has scored over 850 official senior career goals for club and country, making him the top goalscorer of all time.
"""

labels = ["person", "award", "date", "competitions", "teams"]

entities = model.predict_entities(text, labels)

for entity in entities:
    print(entity["text"], "=>", entity["label"])
```

```
Cristiano Ronaldo dos Santos Aveiro => person
5 February 1985 => date
Al Nassr => teams
Portugal national team => teams
Ballon d'Or => award
UEFA Men's Player of the Year Awards => award
European Golden Shoes => award
UEFA Champions Leagues => competitions
UEFA European Championship => competitions
UEFA Nations League => competitions
Champions League => competitions
European Championship => competitions
```

## Named Entity Recognition benchmark result

![image/png](https://cdn-uploads.huggingface.co/production/uploads/6317233cc92fd6fee317e030/Y5f7tK8lonGqeeO6L6bVI.png)

## Model Authors
The model authors are:
* [Urchade Zaratiana](https://huggingface.co/urchade)
* Nadi Tomeh
* Pierre Holat
* Thierry Charnois

## Citation
```bibtex
@misc{zaratiana2023gliner,
      title={GLiNER: Generalist Model for Named Entity Recognition using Bidirectional Transformer}, 
      author={Urchade Zaratiana and Nadi Tomeh and Pierre Holat and Thierry Charnois},
      year={2023},
      eprint={2311.08526},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```