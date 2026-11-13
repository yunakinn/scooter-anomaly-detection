import math


VIOLATION_LEVELS = [
    (80, "매우 높음 🔴", "즉시 확인 및 수거 필요"),
    (50, "높음 🟡", "현장 확인 필요"),
    (30, "낮음 🟢", "모니터링 필요"),
    (0, "정상 ⚪", "정상 주차 가능성 높음"),
]


class RiskScorer:
    def _validated_confidence(self, value):
        try:
            value = float(value)
        except (TypeError, ValueError, OverflowError):
            return None
        return value if math.isfinite(value) and 0 <= value <= 1 else None

    def _indeterminate(self, abnormal_confidence=0.0):
        return {"risk_score": 0.0, "violation_score": 0.0, "level": "판단 불가",
                "action": "사진과 탐지 결과 재확인 필요", "abnormal_confidence": abnormal_confidence}

    def score(self, abnormal_confidence=0.0, detections=None, prediction=None, **kwargs):
        abnormal_confidence = self._validated_confidence(abnormal_confidence)
        if abnormal_confidence is None:
            return self._indeterminate()

        if detections:
            for det in detections:
                if not isinstance(det, dict):
                    continue

                label = det.get("label", det.get("class_name", ""))
                if label == "abnormal":
                    confidence = self._validated_confidence(det.get("confidence"))
                    if confidence is None:
                        return self._indeterminate()
                    abnormal_confidence = max(abnormal_confidence, confidence)

        if prediction == "none" or (prediction is None and not detections and abnormal_confidence == 0):
            return self._indeterminate(abnormal_confidence)

        risk_score = round(abnormal_confidence * 100, 1)

        for threshold, level, action in VIOLATION_LEVELS:
            if risk_score >= threshold:
                return {
                    "risk_score": risk_score,
                    "violation_score": risk_score,
                    "level": level,
                    "action": action,
                    "abnormal_confidence": abnormal_confidence,
                }

        return {
            "risk_score": 0.0,
            "violation_score": 0.0,
            "level": "정상 ⚪",
            "action": "정상 주차 가능성 높음",
            "abnormal_confidence": 0.0,
        }
