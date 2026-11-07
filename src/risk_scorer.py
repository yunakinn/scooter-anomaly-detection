VIOLATION_LEVELS = [
    (80, "매우 높음 🔴", "즉시 확인 및 수거 필요"),
    (50, "높음 🟡", "현장 확인 필요"),
    (30, "낮음 🟢", "모니터링 필요"),
    (0, "정상 ⚪", "정상 주차 가능성 높음"),
]


class RiskScorer:
    def _to_float(self, value, default=0.0):
        try:
            if value is None:
                return default
            return float(value)
        except (TypeError, ValueError):
            return default

    def _clamp_confidence(self, value):
        value = self._to_float(value, 0.0)
        return max(0.0, min(value, 1.0))

    def score(self, abnormal_confidence=0.0, detections=None, prediction=None, **kwargs):
        abnormal_confidence = self._clamp_confidence(abnormal_confidence)

        if detections:
            for det in detections:
                if not isinstance(det, dict):
                    continue

                label = det.get("label", det.get("class_name", ""))
                confidence = self._clamp_confidence(det.get("confidence", 0.0))

                if label == "abnormal":
                    abnormal_confidence = max(abnormal_confidence, confidence)

        if prediction == "none" or (prediction is None and not detections and abnormal_confidence == 0):
            return {"risk_score": 0.0, "violation_score": 0.0, "level": "판단 불가",
                    "action": "사진과 탐지 결과 재확인 필요", "abnormal_confidence": abnormal_confidence}

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