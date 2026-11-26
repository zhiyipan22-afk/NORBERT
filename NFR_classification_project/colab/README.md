# Colab GPU experiments

Open `NORBERT_Colab.ipynb` in Colab, select T4 GPU, and run its cells in order. Alternatively use the commands below from an existing notebook after cloning the repository and mounting Drive.

```python
%cd /content/NORBERT
!git pull --ff-only origin main
%pip install -q -r NFR_classification_project/colab/requirements.txt
!python NFR_classification_project/colab/task_data.py
```

Run the first GPU check:

```python
!python -u NFR_classification_project/colab/train_transformer.py --task 1 --model bert-base-uncased --output-dir /content/drive/MyDrive/NORBERT_experiments --folds 0 --smoke
```

Expected final output: `SMOKE PASS`. This is two optimizer updates and an inner-validation pass; it is not a performance experiment and does not evaluate the outer test fold. A randomly initialized classification-head warning is normal when fine-tuning a general pretrained encoder.

## Subsequent experiments

Only after smoke validation, remove `--smoke` to train one complete fold. Use `--folds all` for ten-fold evaluation. Use `--model microsoft/deberta-v3-base` for the second encoder. Do not assume a partial-fold score establishes 90% performance. Defaults: 4 epochs, learning rate 2e-5, batch size 4, gradient accumulation 4, maximum length 128, FP32. These are initial settings, not optimized hyperparameters. Optional FP16 can reduce compute costs, but use FP32 if training becomes non-finite.

Tasks 1/2/3 use softmax classification. Task 2 contains US/SE/O/PE (249 rows); Task 3 contains ten NFR subclasses excluding PO (369 rows), consistent with the existing task definition. Tasks 4/5 start with a shared encoder and independent sigmoid outputs, using binary cross entropy at threshold 0.5. They do not yet include the previous LR chain, label-specific thresholds, or cost-sensitive loss.

Outer folds match the legacy protocol: stratified folds for Tasks 1–3, ordinary shuffled folds for Tasks 4–5, seed 42. Within each outer training fold, 20% is held out for epoch selection. The outer test fold is evaluated once after selecting an epoch. The selected model is trained on approximately 72% of the complete dataset, not the full 90% outer training pool; future refit protocols must be labeled separately. Comparing with the legacy LR result is exploratory because its training protocol differs. Cross-model comparisons in this runner share splits. Repeatedly selecting configurations based on outer scores can bias estimates: use a nested selection protocol before making final claims about optimized methods.

Data audit reports exact-text duplicates (2 additional rows in Task 1, 3 in Task 4). All original rows are retained. Legacy random splits may place identical text across folds; do not describe this protocol as duplicate-group-isolated. A grouped robustness evaluation should be added before strong generalization claims. Cross-project generalization is also a separate evaluation.

## Saved outputs and restart behavior

Each configuration and source-code hash receives its own Drive directory. It contains data hashes, exact split indices, environment/model version metadata, per-fold probabilities and metrics, `oof_predictions.csv`, and `summary.json`. Summaries distinguish partial CV from complete CV and report pooled OOF metrics and fold-average metrics separately. Task 4/5 report each label's weighted and positive-class F1; the mean-label score is only for epoch selection and does not establish that all labels reached 90%.

One rolling `resume.pt` stores the current model, optimizer, best epoch state, and random states after every completed epoch. Rerunning the identical command skips completed folds and resumes an interrupted fold after its last saved epoch. Partial epochs are rerun. This checkpoint can occupy several GB; ensure sufficient Drive storage. Smoke runs save only a small JSON result. Checkpoint files should only be loaded from your own experiment directory.

Dependencies preserve Colab's existing GPU PyTorch installation. Local data, metrics, split-integrity and syntax checks are available through `python -m unittest discover -s NFR_classification_project/colab -p "test_*.py"`; actual GPU training must be verified in Colab.
