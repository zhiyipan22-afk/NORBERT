"""Offline checks for real task definitions, split isolation, and metric summaries."""
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from task_data import load_task, make_splits, training_class_weights
from train_transformer import metrics, summarize


class ProtocolTests(unittest.TestCase):
    def test_class_weights_help_rare_classes_without_changing_sample_scale(self):
        labels = np.array([0] * 9 + [1])
        mild = training_class_weights(labels, 2, "sqrt")
        strong = training_class_weights(labels, 2, "balanced")
        self.assertAlmostEqual(float(mild[1] / mild[0]), 3., places=5)
        self.assertAlmostEqual(float(strong[1] / strong[0]), 9., places=5)
        self.assertAlmostEqual(float(mild[labels].mean()), 1., places=5)
        self.assertAlmostEqual(float(strong[labels].mean()), 1., places=5)
        np.testing.assert_array_equal(training_class_weights(labels, 2), [1., 1.])
        with self.assertRaises(ValueError):
            training_class_weights(np.zeros(10, dtype=int), 2, "sqrt")

    def test_task_definitions_and_split_isolation(self):
        for task, size in enumerate([625, 249, 369, 612, 309], start=1):
            with self.subTest(task=task):
                data = load_task(task)
                self.assertEqual(len(data["texts"]), size)
                splits = make_splits(data)
                all_test = []
                for split in splits:
                    train, val, test = (set(split[key]) for key in ("train", "validation", "test"))
                    self.assertFalse(train & val or train & test or val & test)
                    self.assertEqual(train | val | test, set(range(size)))
                    all_test.extend(split["test"])
                self.assertEqual(sorted(all_test), list(range(size)))
                self.assertEqual(splits, make_splits(data))
        self.assertEqual(load_task(2)["names"], ["US", "SE", "O", "PE"])
        self.assertEqual(len(load_task(3)["names"]), 10)

    def test_multilabel_does_not_hide_failed_positive_class(self):
        y = np.array([[0, 1], [0, 0], [0, 1], [1, 0]])
        result = metrics(y, np.zeros_like(y), ["Data", "Function"])
        self.assertEqual(result["per_label"]["Data"]["positive_f1"], 0.)
        self.assertGreater(result["per_label"]["Data"]["weighted_f1"], 0.)

    def test_summary_marks_partial_and_complete(self):
        data = load_task(1)
        splits = make_splits(data)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for split in splits:
                ids = split["test"]
                truth = data["labels"][ids]
                result = {"indices": ids, "predictions": truth.tolist(),
                          "probabilities": np.eye(2)[truth].tolist(),
                          "metrics": metrics(truth, truth, data["names"])}
                (root / f"fold_{split['fold']}.json").write_text(json.dumps(result), encoding="utf-8")
                if split["fold"] == 0:
                    summarize(root, data, splits)
                    summary = json.loads((root / "summary.json").read_text())
                    self.assertEqual(summary["status"], "partial_cv")
            summarize(root, data, splits)
            summary = json.loads((root / "summary.json").read_text())
            self.assertEqual(summary["status"], "complete_cv")
            self.assertEqual(summary["pooled_oof"]["weighted_f1"], 1.)


if __name__ == "__main__":
    unittest.main()
