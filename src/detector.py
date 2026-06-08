from pathlib import Path
import os

from ultralytics import YOLO


ROOT = Path(__file__).resolve().parent.parent

DEFAULT_MODEL_PATH = os.getenv(
    "MODEL_PATH",
    str(ROOT / "weights/best.pt")
)

DEFAULT_CLASS_NAMES = {
    0: "normal",
    1: "abnormal"
}


class Detector:
    def __init__(self, model_path=DEFAULT_MODEL_PATH, prediction_threshold=0.5):
        self.model_path = str(model_path)
        self.prediction_threshold = prediction_threshold

        if not Path(self.model_path).exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")

        self.model = YOLO(self.model_path)
        self.class_names = self._load_class_names()

    def _load_class_names(self):
        try:
            names = self.model.names

            if isinstance(names, dict):
                return {
                    int(class_id): str(class_name)
                    for class_id, class_name in names.items()
                }

            if isinstance(names, list):
                return {
                    class_id: str(class_name)
                    for class_id, class_name in enumerate(names)
                }

        except Exception:
            pass

        return DEFAULT_CLASS_NAMES

    def _get_label(self, class_id):
        return self.class_names.get(
            class_id,
            DEFAULT_CLASS_NAMES.get(class_id, str(class_id))
        )

    def predict(self, image_path):
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        results = self.model(str(image_path), verbose=False)[0]

        detections = []

        for box in results.boxes:
            class_id = int(box.cls.item())
            confidence = float(box.conf.item())
            bbox = [float(v) for v in box.xyxy[0].tolist()]
            label = self._get_label(class_id)

            detections.append({
                "class_id": class_id,
                "label": label,
                "confidence": confidence,
                "bbox": bbox
            })

        normal_confidence = 0.0
        abnormal_confidence = 0.0

        for det in detections:
            label = det.get("label")
            confidence = float(det.get("confidence", 0.0))

            if label == "normal":
                normal_confidence = max(normal_confidence, confidence)
            elif label == "abnormal":
                abnormal_confidence = max(abnormal_confidence, confidence)

        if abnormal_confidence >= self.prediction_threshold:
            prediction = "abnormal"
            confidence = abnormal_confidence
        elif normal_confidence >= self.prediction_threshold:
            prediction = "normal"
            confidence = normal_confidence
        else:
            prediction = "none"
            confidence = max(normal_confidence, abnormal_confidence, 0.0)

        risk_score = round(abnormal_confidence * 100, 1)
        annotated_image = results.plot()

        return {
            "image_path": str(image_path),
            "prediction": prediction,
            "confidence": confidence,
            "normal_confidence": normal_confidence,
            "abnormal_confidence": abnormal_confidence,
            "risk_score": risk_score,
            "violation_score": risk_score,
            "detections": detections,
            "annotated_image": annotated_image
        }