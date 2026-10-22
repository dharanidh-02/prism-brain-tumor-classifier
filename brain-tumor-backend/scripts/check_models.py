"""Model verification script.

Inspects configured model paths, calculates SHA-256 fingerprints,
loads models using Keras, and performs a test forward pass.
Usage:
    python scripts/check_models.py
"""

import sys
import time
from pathlib import Path
import numpy as np

# Ensure backend root is on sys.path
backend_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_root))

from app.config import settings

try:
    import keras
    KERAS_INSTALLED = True
except ImportError:
    KERAS_INSTALLED = False


def main():
    print("=" * 70)
    print("PRISM: Precision Radiology Imaging for Solid Masses")
    print("A Hybrid EfficientNet-MobileNet Attention Classifier for Brain Tumors")
    print("Model Integrity and Compatibility Checker")
    print("=" * 70)
    print(f"Keras Library Available: {KERAS_INSTALLED}")

    definitions = settings.get_model_definitions()
    results_summary = []

    for model_id, cfg in definitions.items():
        print(f"\n[{model_id}] {cfg['display_name']}")
        path = Path(cfg["path"])
        print(f"  Configured Path: {path}")

        if not path.is_file():
            print("  [ERROR] File does NOT exist at configured path.")
            results_summary.append((model_id, "NOT_FOUND", "N/A", "N/A"))
            continue

        size_mb = path.stat().st_size / (1024 * 1024)
        print(f"  File Size: {size_mb:.2f} MB")

        # SHA-256 Checksum
        import hashlib
        sha = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                sha.update(chunk)
        digest = sha.hexdigest()
        print(f"  SHA-256: {digest}")

        if not KERAS_INSTALLED:
            print("  [SKIP] Keras not installed; skipping model load test.")
            results_summary.append((model_id, "EXISTS", f"{size_mb:.2f} MB", "Keras missing"))
            continue

        # Test model loading
        t0 = time.perf_counter()
        try:
            model = keras.models.load_model(str(path), compile=False)
            load_ms = (time.perf_counter() - t0) * 1000
            print(f"  Loaded successfully in {load_ms:.2f} ms")

            # Inspect shapes
            in_shape = getattr(model, "input_shape", "Unknown")
            out_shape = getattr(model, "output_shape", "Unknown")
            total_params = getattr(model, "count_params", lambda: "Unknown")()
            print(f"  Input Shape: {in_shape}")
            print(f"  Output Shape: {out_shape}")
            print(f"  Total Parameters: {total_params:,}" if isinstance(total_params, int) else f"  Total Parameters: {total_params}")

            # Test inference with dummy batch (1, 224, 224, 3)
            dummy_input = np.zeros((1, 224, 224, 3), dtype=np.float32)
            t_inf0 = time.perf_counter()
            pred = model(dummy_input, training=False)
            inf_ms = (time.perf_counter() - t_inf0) * 1000
            pred_arr = pred.numpy()[0] if hasattr(pred, "numpy") else np.array(pred)[0]
            print(f"  Test forward pass latency: {inf_ms:.2f} ms")
            print(f"  Output vector: {np.round(pred_arr, 4)} (sum={np.sum(pred_arr):.4f})")

            results_summary.append((model_id, "LOADED_OK", f"{size_mb:.2f} MB", f"{load_ms:.0f}ms load"))

        except Exception as e:
            print(f"  [ERROR] Loading failed: {e}")
            results_summary.append((model_id, "LOAD_FAILED", f"{size_mb:.2f} MB", str(e)[:30]))

    print("\n" + "=" * 70)
    print("Model Verification Summary:")
    print(f"{'Model ID':<22} | {'Status':<12} | {'Size':<10} | {'Details'}")
    print("-" * 70)
    for mid, stat, sz, det in results_summary:
        print(f"{mid:<22} | {stat:<12} | {sz:<10} | {det}")
    print("=" * 70)


if __name__ == "__main__":
    main()
