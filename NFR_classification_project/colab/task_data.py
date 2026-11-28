"""Task definitions and fixed outer/inner splits; no model downloads required."""
from pathlib import Path
import hashlib
import json
import warnings

import numpy as np
import pandas as pd
from sklearn.model_selection import KFold, StratifiedKFold, train_test_split

DATA = Path(__file__).resolve().parents[1] / "data" / "Code"


def load_task(task):
    if task in (1, 2, 3):
        path = DATA / "Task1_to_3_original_Promise_NFR_dataset" / "promise_nfr.csv"
        frame = pd.read_csv(path)
        if task == 1:
            names = ["NFR", "FR"]
            labels = frame["F"].astype(int).to_numpy()
        else:
            names = (["US", "SE", "O", "PE"] if task == 2 else
                     ["A", "FT", "L", "LF", "MN", "O", "PE", "SC", "SE", "US"])
            selected = (frame["NFR"] == 1) & (frame[names].sum(axis=1) == 1)
            frame = frame.loc[selected].copy()
            labels = frame[names].to_numpy().argmax(axis=1)
    elif task == 4:
        path = DATA / "Task4_relabeled_Promise_NFR_dataset" / "promise-reclass.csv"
        frame = pd.read_csv(path)
        frame = frame.loc[frame["NotR"] == 0].copy()
        names = ["IsFunctional", "IsQuality", "IsOnlyFunctional", "IsOnlyQuality"]
        labels = frame[names].astype(int).to_numpy()
    elif task == 5:
        path = DATA / "Task5_func_concerns_dataset" / "func_concerns.csv"
        frame = pd.read_csv(path, sep=None, engine="python")
        names = ["Function", "Data", "Behavior"]
        labels = frame[names].astype(int).to_numpy()
    else:
        raise ValueError("task must be 1..5")
    if frame["RequirementText"].isna().any():
        raise ValueError("Missing requirement text")
    if task >= 4 and not np.isin(labels, [0, 1]).all():
        raise ValueError("Non-binary labels")
    return {
        "task": task, "names": names, "labels": labels,
        "texts": frame["RequirementText"].astype(str).tolist(),
        "source_rows": frame.index.to_numpy(),
        "projects": frame["ProjectID"].astype(str).tolist(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def training_class_weights(labels, num_classes, mode="none"):
    """Return sample-normalized inverse-frequency weights from training labels only."""
    if mode not in ("none", "sqrt", "balanced"):
        raise ValueError("Unknown class-weight mode")
    labels = np.asarray(labels, dtype=int)
    if labels.ndim != 1 or not len(labels) or (labels < 0).any() or (labels >= num_classes).any():
        raise ValueError("Expected nonempty one-dimensional class indices")
    counts = np.bincount(labels, minlength=num_classes)
    if mode == "none":
        return np.ones(num_classes, dtype=np.float32)
    if (counts == 0).any():
        raise ValueError("Cannot weight a class with no training examples")
    power = 0.5 if mode == "sqrt" else 1.0
    weights = (len(labels) / (num_classes * counts)) ** power
    weights /= np.dot(counts, weights) / len(labels)
    return weights.astype(np.float32)


def make_splits(data, n_splits=10, seed=42):
    """Match legacy outer folds; select epochs only on an inner holdout."""
    y = data["labels"]
    if data["task"] <= 3:
        counts = np.bincount(y, minlength=len(data["names"]))
        if counts.min() < 2:
            raise ValueError("A class has fewer than two examples; cannot split safely")
        if counts.min() < n_splits:
            warnings.warn("Some outer folds lack rare classes; report pooled OOF and support.")
        outer = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
        pairs = outer.split(np.zeros(len(y)), y)
    else:
        outer = KFold(n_splits=n_splits, shuffle=True, random_state=seed)
        pairs = outer.split(np.zeros(len(y)))
    result = []
    for fold, (outer_train, test) in enumerate(pairs):
        if data["task"] <= 3:
            counts = np.bincount(y[outer_train], minlength=len(data["names"]))
            if counts.min() < 2:
                raise ValueError("Inner stratification impossible for a rare class")
            stratify = y[outer_train]
        else:
            # Preserve joint label patterns where every observed pattern can be split.
            patterns = np.array(["".join(map(str, row)) for row in y[outer_train]])
            _, counts = np.unique(patterns, return_counts=True)
            stratify = patterns if counts.min() >= 2 else None
        train, validation = train_test_split(
            outer_train, test_size=0.2, random_state=seed + fold, stratify=stratify)
        result.append({"fold": fold, "train": train.tolist(),
                       "validation": validation.tolist(), "test": test.tolist()})
    return result


def audit():
    rows = []
    for task in range(1, 6):
        d = load_task(task)
        y = d["labels"]
        counts = (np.bincount(y, minlength=len(d["names"])) if task <= 3 else y.sum(axis=0))
        row = {"task": task, "samples": len(y), "class_or_positive_counts":
               dict(zip(d["names"], counts.tolist())), "sha256": d["sha256"],
               "duplicate_texts": len(d["texts"]) - len(set(d["texts"])),
               "outer_folds": len(make_splits(d))}
        if task == 4:
            row["only_f_identity"] = bool(np.array_equal(y[:, 2], y[:, 0] * (1-y[:, 1])))
            row["only_q_identity"] = bool(np.array_equal(y[:, 3], y[:, 1] * (1-y[:, 0])))
        rows.append(row)
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    audit()
