from pathlib import Path
import os
from ultralytics import YOLO

ROOT = Path("/data1/workspaces/tp2026/scooter-anomaly-detection")

DEFAULT_MODEL_PATH = os.getenv(
    "MODEL_PATH",
    str(ROOT / "results/yolov8n_binary_v1_train/weights/best.pt")
)

CLASS_NAMES = {
    0: "normal",
    1: "abnormal"
}


class Detector:
    def __init__(self, model_path=DEFAULT_MODEL_PATH):
        self.model_path = str(model_path)
        self.model = YOLO(self.model_path)

    def predict(self, image_path):
        results = self.model(str(image_path))[0]

        detections = []

        for box in results.boxes:
            class_id = int(box.cls.item())
            confidence = float(box.conf.item())
            bbox = box.xyxy[0].tolist()

            detections.append({
                "class_id": class_id,
                "label": CLASS_NAMES.get(class_id, str(class_id)),
                "confidence": confidence,
                "bbox": bbox
            })

        normal_confidence = 0.0
        abnormal_confidence = 0.0

        for det in detections:
            if det["label"] == "normal":
                normal_confidence = max(normal_confidence, det["confidence"])
            elif det["label"] == "abnormal":
                abnormal_confidence = max(abnormal_confidence, det["confidence"])

        if abnormal_confidence > 0:
            prediction = "abnormal"
            confidence = abnormal_confidence
        elif normal_confidence > 0:
            prediction = "normal"
            confidence = normal_confidence
        else:
            prediction = "none"
            confidence = 0.0

        violation_score = round(abnormal_confidence * 100, 1)

        annotated_image = results.plot()

        return {
            "prediction": prediction,
            "confidence": confidence,
            "abnormal_confidence": abnormal_confidence,
            "violation_score": violation_score,
            "detections": detections,
            "annotated_image": annotated_image
        }
