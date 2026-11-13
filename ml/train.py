"""Fine-tune YOLOv8n on the prepared dataset, evaluate on the held-out test split and install the weights.

    pip install -r backend/requirements-ml.txt
    python ml/train.py --data data/yolo/data.yaml --epochs 80
Run on a GPU (Google Colab free tier is enough for YOLOv8n). Needs an internet connection for the base weights.
Ultralytics YOLOv8 is AGPL-3.0: fine for this academic project; read the licence before offering it as a public service.
"""
import argparse
import json
import shutil
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--model", default="yolov8n.pt")
    ap.add_argument("--epochs", type=int, default=80)
    ap.add_argument("--imgsz", type=int, default=640)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--install-to", default="backend/models/defect.pt")
    a = ap.parse_args()
    from ultralytics import YOLO

    model = YOLO(a.model)
    model.train(data=a.data, epochs=a.epochs, imgsz=a.imgsz, batch=a.batch, patience=20, project="runs", name="defects",
                fliplr=0.5, flipud=0.5, degrees=10, hsv_h=0.015, hsv_s=0.5, hsv_v=0.4, mosaic=1.0)
    best = Path(model.trainer.best)
    metrics = YOLO(str(best)).val(data=a.data, split="test", imgsz=a.imgsz)
    report = {"map50": float(metrics.box.map50), "map50_95": float(metrics.box.map),
              "precision": float(metrics.box.mp), "recall": float(metrics.box.mr),
              "per_class_map50": {metrics.names[i]: float(v) for i, v in zip(metrics.box.ap_class_index, metrics.box.ap50)}}
    Path("runs/defects/test_metrics.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    dst = Path(a.install_to)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(best, dst)
    print("installed", dst, "- restart the backend; /api/health will show defect_model_loaded=true")


if __name__ == "__main__":
    main()
