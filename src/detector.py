from pathlib import Path
from ultralytics import YOLO
import cv2

ROOT = Path("/data1/workspaces/tp2026/scooter-anomaly-detection")
BEST_MODEL = ROOT / "results/yolov8n_binary_v1_train/weights/best.pt"

CLASS_NAMES = {0: "normal", 1: "abnormal"}


class Detector:
    def __init__(self, model_path=BEST_MODEL):
        self.model = YOLO(str(model_path))

    def predict(self, image_path):
        results = self.model(str(image_path))[0]

        detections = []
        for box in results.boxes:
            class_id = int(box.cls.item())
            confidence = float(box.conf.item())
            bbox = box.xyxy[0].tolist()  # [x1, y1, x2, y2]

            detections.append({
                "class_id": class_id,
                "label": CLASS_NAMES[class_id],
                "confidence": confidence,
                "bbox": bbox
            })

        # bbox 그려진 이미지 반환
        annotated_image = results.plot()

        return {
            "detections": detections,
            "annotated_image": annotated_image
        }