# NoRBERT reproduction and improvement experiments

This repository contains a local reproduction project for **NoRBERT: Transfer Learning for Requirements Classification** (IEEE RE 2020), together with LR/TF-IDF improvement experiments and recorded results.

## Repository layout

- `NFR_classification_project/src/`: experiment scripts, analysis utilities, and report-generation scripts.
- `NFR_classification_project/data/Code/`: original task notebooks and datasets.
- `NFR_classification_project/data/Dataset/`: functional-concern annotations.
- `NFR_classification_project/data/*results*.json`: saved local experiment results.
- `NFR_classification_project/data/README.md`: original supplementary-material documentation and attribution.
- `NoRBERT_pretrained_models/`: configuration files and license for downloaded author models; large weights are excluded.

## Current experiment entry points

- `src/task1_binary_classification.py`: LR and BERT Task 1 experiments.
- `src/advanced_improvement_v2.py`: Task 1 feature fusion and ten-class NFR experiments (the latter is named Task 2/3 in the script).
- `src/task4_task5_improvement.py`: Task 4/5 cost-sensitive and classifier-chain experiments.

These paths are relative to `NFR_classification_project/`. This upload preserves the existing experiments; it does not include a new DeBERTa experiment or a tested Colab setup. Scripts currently contain absolute Windows data paths, which must be adapted before running on Colab or another machine. Existing reports use different evaluation settings; inspect the script and result metadata before comparing scores.

## Large files

Model weights, archives, generated office documents, and temporary presentation assets remain local and are excluded from Git. Download author weights separately from the original supplementary materials when needed. Full-dataset predictions using author-trained models are pipeline checks, not held-out generalization results.

## Attribution

Original NoRBERT supplementary materials: <https://doi.org/10.5281/zenodo.3833660>. See the retained README and LICENSE files in the data and model directories for source attribution and licensing. No new blanket license is assigned to this mixed-source repository.
