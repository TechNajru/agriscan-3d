# Training the defect model (YOLOv8n)

The app runs without a model (experimental colour-anomaly fallback, always labelled "experimental").
A trained model replaces it automatically when `backend/models/defect.pt` exists.

## 1. Collect data (do this first, it is the slow part)
Target classes: `bruise, cut, fungal spot, rot, crack, insect damage` (merge or drop classes with fewer than ~100 training boxes).
Sources worth checking (each needs its **licence recorded** in a `LICENSE.txt` inside its folder):
- Public apple/fruit defect sets on Roboflow Universe and Kaggle (need a free account, so they must be downloaded on your machine or Colab; export in *YOLOv8* format).
- Fruits-360 (fruit classification, single fruit on white background) is useful for fruit-type work, not defect boxes.
- Your own photos: plain light background, even light, ~1000+ px, several fruits per class; label with Label Studio or Roboflow.
Aim for 1,500-2,500 annotated images with at least a few hundred boxes for each class you keep.

## 2. Map classes and merge
```
cp ml/class_map.example.json ml/class_map.json      # edit: one entry per source folder name
python ml/prepare_dataset.py --sources data/raw/* --class-map ml/class_map.json --out data/yolo
```
It splits **per fruit group** (use `--group-regex` if your file names contain a fruit id) so the same fruit never appears in train and test.

## 3. Train and install
```
pip install -r backend/requirements-ml.txt
python ml/train.py --data data/yolo/data.yaml --epochs 80       # use a GPU (Colab T4 is fine)
```
This prints precision / recall / mAP50 per class on the **held-out test split** and copies the weights to `backend/models/defect.pt`.
Report those numbers honestly in your project report; do not claim classes with poor results.
