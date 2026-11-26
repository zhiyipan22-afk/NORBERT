"""GPU experiment runner. Smoke runs never evaluate the outer test fold."""
import argparse
import gc
import hashlib
import json
import math
import os
from pathlib import Path
import random
import time

import numpy as np
from sklearn.metrics import accuracy_score, classification_report, f1_score

from task_data import load_task, make_splits


def write_json(path, value):
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2), encoding="utf-8")
    os.replace(temp, path)


def metrics(y, pred, names):
    if y.ndim == 1:
        ids = list(range(len(names)))
        return {"accuracy": accuracy_score(y, pred),
                "weighted_f1": f1_score(y, pred, labels=ids, average="weighted", zero_division=0),
                "macro_f1": f1_score(y, pred, labels=ids, average="macro", zero_division=0),
                "per_class": classification_report(y, pred, labels=ids, target_names=names,
                                                    output_dict=True, zero_division=0)}
    per_label = {}
    for i, name in enumerate(names):
        per_label[name] = {
            "accuracy": accuracy_score(y[:, i], pred[:, i]),
            "weighted_f1": f1_score(y[:, i], pred[:, i], labels=[0, 1], average="weighted", zero_division=0),
            "positive_f1": f1_score(y[:, i], pred[:, i], zero_division=0),
            "positive_support": int(y[:, i].sum()),
        }
    return {"mean_label_weighted_f1": float(np.mean([v["weighted_f1"] for v in per_label.values()])),
            "macro_positive_f1": f1_score(y, pred, average="macro", zero_division=0),
            "subset_accuracy": accuracy_score(y, pred), "per_label": per_label}


def selection_score(result):
    return result.get("weighted_f1", result.get("mean_label_weighted_f1"))


def summarize(run_dir, data, splits):
    import pandas as pd
    records, fold_scores = [], []
    for split in splits:
        path = run_dir / f"fold_{split['fold']}.json"
        if not path.exists():
            continue
        result = json.loads(path.read_text(encoding="utf-8"))
        fold_scores.append(result["metrics"])
        for i, sample in enumerate(result["indices"]):
            records.append({"sample": sample, "fold": split["fold"],
                            "source_row": int(data["source_rows"][sample]),
                            "project": data["projects"][sample],
                            "true": data["labels"][sample].tolist(),
                            "pred": result["predictions"][i],
                            "probabilities": result["probabilities"][i]})
    if not records:
        return
    records.sort(key=lambda r: r["sample"])
    if len({r["sample"] for r in records}) != len(records):
        raise ValueError("Duplicate outer-test predictions")
    y = np.array([r["true"] for r in records])
    pred = np.array([r["pred"] for r in records])
    summary = {"status": "complete_cv" if len(fold_scores) == len(splits) else "partial_cv",
               "completed_folds": len(fold_scores), "total_folds": len(splits),
               "pooled_oof": metrics(y, pred, data["names"]),
               "mean_fold_selection_metric": float(np.mean([selection_score(m) for m in fold_scores])),
               "fold_selection_metric_std": float(np.std([selection_score(m) for m in fold_scores], ddof=1))
               if len(fold_scores) > 1 else None,
               "note": "Exploratory fixed-configuration evaluation; not nested hyperparameter search."}
    write_json(run_dir / "summary.json", summary)
    pd.DataFrame([{**r, "true": json.dumps(r["true"]), "pred": json.dumps(r["pred"]),
                   "probabilities": json.dumps(r["probabilities"])} for r in records]).to_csv(
        run_dir / "oof_predictions.csv", index=False)
    print(json.dumps(summary, indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=int, choices=range(1, 6), default=1)
    parser.add_argument("--model", default="bert-base-uncased")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--folds", default="0", help="0 or 0,1 or all; zero-based")
    parser.add_argument("--seed", type=int, default=42, help="Model/training seed")
    parser.add_argument("--split-seed", type=int, default=42)
    parser.add_argument("--n-splits", type=int, default=10)
    parser.add_argument("--epochs", type=int, default=4)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--accumulation", type=int, default=4)
    parser.add_argument("--max-length", type=int, default=128)
    parser.add_argument("--lr", type=float, default=2e-5)
    parser.add_argument("--weight-decay", type=float, default=0.01)
    parser.add_argument("--precision", choices=["fp32", "fp16"], default="fp32")
    parser.add_argument("--smoke", action="store_true", help="Two optimizer steps, inner validation only")
    parser.add_argument("--validation-only", action="store_true",
                        help="Train and select epochs on inner validation; never evaluate outer test")
    parser.add_argument("--audit-only", action="store_true")
    args = parser.parse_args()
    for name in ("epochs", "batch_size", "accumulation", "max_length"):
        if getattr(args, name) < 1:
            parser.error(f"{name} must be positive")
    data = load_task(args.task)
    splits = make_splits(data, args.n_splits, args.split_seed)
    selected = list(range(args.n_splits)) if args.folds == "all" else [int(f) for f in args.folds.split(",")]
    if not selected or any(f < 0 or f >= args.n_splits for f in selected):
        parser.error("Fold indices out of range")
    config = {k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()
              if k not in ("output_dir", "folds", "audit_only")}
    config["dataset_sha256"] = data["sha256"]
    config["label_names"] = data["names"]
    config["protocol"] = "outer_cv_inner_20pct_epoch_selection_v1"
    config["runner_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    config["data_loader_sha256"] = hashlib.sha256(Path(__file__).with_name("task_data.py").read_bytes()).hexdigest()
    run_id = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[:12]
    run_dir = args.output_dir / f"task{args.task}_{args.model.replace('/', '_')}_{run_id}"
    run_dir.mkdir(parents=True, exist_ok=True)
    write_json(run_dir / "config.json", config)
    write_json(run_dir / "splits.json", splits)
    print(f"Task {args.task}: {len(data['texts'])} samples; labels={data['names']}", flush=True)
    print(f"OUTPUT: {run_dir}", flush=True)
    if args.audit_only:
        return

    # Import GPU libraries only after offline data validation.
    import torch
    from torch.utils.data import Dataset, DataLoader
    from transformers import AutoModelForSequenceClassification, AutoTokenizer, DataCollatorWithPadding
    from transformers import get_linear_schedule_with_warmup
    import transformers
    import sklearn
    import pandas

    if not torch.cuda.is_available():
        raise RuntimeError("No CUDA GPU detected. Select T4 GPU in Colab before training.")
    environment = {"torch": torch.__version__, "transformers": transformers.__version__,
                   "numpy": np.__version__, "pandas": pandas.__version__,
                   "sklearn": sklearn.__version__, "gpu": torch.cuda.get_device_name(0)}
    write_json(run_dir / "environment.json", environment)
    print(f"GPU: {torch.cuda.get_device_name(0)}; precision={args.precision}", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(args.model, use_fast=True)
    encoded = tokenizer(data["texts"], truncation=True, max_length=args.max_length)
    is_multi = args.task >= 4
    collator = DataCollatorWithPadding(tokenizer, pad_to_multiple_of=8)

    class TextDataset(Dataset):
        def __init__(self, indices):
            self.indices = list(indices)
        def __len__(self):
            return len(self.indices)
        def __getitem__(self, index):
            sample = self.indices[index]
            item = {key: value[sample] for key, value in encoded.items()}
            item["labels"] = (data["labels"][sample].astype(float).tolist() if is_multi
                              else int(data["labels"][sample]))
            return item

    def loader(indices, shuffle=False):
        return DataLoader(TextDataset(indices), batch_size=args.batch_size,
                          shuffle=shuffle, collate_fn=collator, num_workers=0)

    def evaluate(model, indices):
        model.eval()
        probabilities = []
        with torch.no_grad():
            for batch in loader(indices):
                batch.pop("labels")
                logits = model(**{k: v.cuda() for k, v in batch.items()}).logits.float()
                probabilities.extend((logits.sigmoid() if is_multi else logits.softmax(-1)).cpu().numpy())
        probs = np.asarray(probabilities)
        pred = (probs >= 0.5).astype(int) if is_multi else probs.argmax(axis=1)
        return metrics(data["labels"][indices], pred, data["names"]), pred, probs

    checkpoint_path = run_dir / "resume.pt"  # One rolling checkpoint for all folds.
    for fold in selected:
        split = splits[fold]
        result_name = (f"smoke_fold_{fold}.json" if args.smoke else
                       f"validation_fold_{fold}.json" if args.validation_only else f"fold_{fold}.json")
        result_path = run_dir / result_name
        if result_path.exists():
            print(f"Fold {fold}: already complete, skipping", flush=True)
            continue
        seed = args.seed + fold
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        model = AutoModelForSequenceClassification.from_pretrained(
            args.model, num_labels=len(data["names"]),
            id2label=dict(enumerate(data["names"])),
            label2id={name: i for i, name in enumerate(data["names"])},
            problem_type="multi_label_classification" if is_multi else "single_label_classification",
        ).cuda()
        environment["model_commit"] = getattr(model.config, "_commit_hash", None)
        write_json(run_dir / "environment.json", environment)
        train_loader = loader(split["train"], shuffle=True)
        epochs = 1 if args.smoke else args.epochs
        steps_per_epoch = math.ceil(len(train_loader) / args.accumulation)
        total_steps = 2 if args.smoke else steps_per_epoch * epochs
        optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
        scheduler = get_linear_schedule_with_warmup(optimizer, int(total_steps * 0.1), total_steps)
        scaler = torch.amp.GradScaler("cuda", enabled=args.precision == "fp16")
        start_epoch, best_score, best_state, history = 0, -1., None, []
        elapsed_before = 0.
        if checkpoint_path.exists() and not args.smoke:
            state = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
            if state["run_id"] == run_id and state["fold"] == fold:
                model.load_state_dict(state["model"])
                optimizer.load_state_dict(state["optimizer"])
                scheduler.load_state_dict(state["scheduler"])
                scaler.load_state_dict(state["scaler"])
                start_epoch, best_score, best_state = state["next_epoch"], state["best_score"], state["best_state"]
                history, elapsed_before = state["history"], state["elapsed_seconds"]
                random.setstate(state["python_rng"])
                np.random.set_state(state["numpy_rng"])
                torch.set_rng_state(state["torch_rng"])
                torch.cuda.set_rng_state_all(state["cuda_rng"])
                print(f"Fold {fold}: resuming after epoch {start_epoch}", flush=True)
            del state
        started = time.time()
        torch.cuda.reset_peak_memory_stats()
        for epoch in range(start_epoch, epochs):
            model.train()
            optimizer.zero_grad(set_to_none=True)
            train_loss, updates = 0., 0
            for step, batch in enumerate(train_loader):
                batch = {k: v.cuda() for k, v in batch.items()}
                if is_multi:
                    batch["labels"] = batch["labels"].float()
                group_start = (step // args.accumulation) * args.accumulation
                group_size = min(args.accumulation, len(train_loader) - group_start)
                with torch.autocast("cuda", dtype=torch.float16, enabled=args.precision == "fp16"):
                    loss = model(**batch).loss
                if not torch.isfinite(loss):
                    raise RuntimeError("Non-finite loss. Retry with --precision fp32.")
                train_loss += loss.item()
                scaler.scale(loss / group_size).backward()
                if (step + 1) % args.accumulation == 0 or step + 1 == len(train_loader):
                    scaler.unscale_(optimizer)
                    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                    old_scale = scaler.get_scale()
                    scaler.step(optimizer)
                    scaler.update()
                    if scaler.get_scale() >= old_scale:
                        scheduler.step()
                    optimizer.zero_grad(set_to_none=True)
                    updates += 1
                    if args.smoke and updates >= 2:
                        break
            val_metrics, _, _ = evaluate(model, split["validation"])
            score = selection_score(val_metrics)
            entry = {"epoch": epoch + 1, "train_loss": train_loss / (step + 1),
                     "optimizer_updates": updates,
                     "inner_validation": val_metrics}
            history.append(entry)
            print(f"Fold {fold}, epoch {epoch+1}: loss={entry['train_loss']:.4f}; inner F1={score:.4f}", flush=True)
            if score > best_score:
                best_score = score
                best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            if not args.smoke:
                temp = checkpoint_path.with_suffix(".tmp")
                torch.save({"run_id": run_id, "fold": fold, "next_epoch": epoch + 1,
                            "model": model.state_dict(), "optimizer": optimizer.state_dict(),
                            "scheduler": scheduler.state_dict(), "scaler": scaler.state_dict(),
                            "best_score": best_score, "best_state": best_state, "history": history,
                            "elapsed_seconds": elapsed_before + time.time() - started,
                            "python_rng": random.getstate(), "numpy_rng": np.random.get_state(),
                            "torch_rng": torch.get_rng_state(), "cuda_rng": torch.cuda.get_rng_state_all()}, temp)
                os.replace(temp, checkpoint_path)
        if args.smoke:
            write_json(result_path, {"status": "smoke_only_not_a_test_score", "history": history,
                       "elapsed_seconds": time.time() - started,
                       "peak_gpu_gb": torch.cuda.max_memory_allocated() / 1024**3})
            print("SMOKE PASS: GPU training and inner validation worked. Outer test fold was not evaluated.", flush=True)
        elif args.validation_only:
            diagnostic = {"status": "inner_validation_only_not_a_test_score", "fold": fold,
                          "best_inner_f1": best_score,
                          "best_epoch": max(history, key=lambda h: selection_score(h["inner_validation"]))["epoch"],
                          "train_samples": len(split["train"]),
                          "validation_samples": len(split["validation"]),
                          "history": history,
                          "elapsed_seconds": elapsed_before + time.time() - started,
                          "peak_gpu_gb": torch.cuda.max_memory_allocated() / 1024**3}
            write_json(result_path, diagnostic)
            print(json.dumps({k: v for k, v in diagnostic.items() if k != "history"}, indent=2), flush=True)
            print("VALIDATION ONLY COMPLETE: outer test fold was not evaluated.", flush=True)
        else:
            model.load_state_dict(best_state)
            test_metrics, pred, probs = evaluate(model, split["test"])
            write_json(result_path, {"fold": fold, "metrics": test_metrics, "history": history,
                       "indices": split["test"], "predictions": pred.tolist(),
                       "probabilities": probs.tolist(), "threshold": 0.5 if is_multi else None,
                       "elapsed_seconds": elapsed_before + time.time() - started,
                       "peak_gpu_gb": torch.cuda.max_memory_allocated() / 1024**3})
            summarize(run_dir, data, splits)
        del model, optimizer, scheduler, scaler, best_state, train_loader
        gc.collect()
        torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
