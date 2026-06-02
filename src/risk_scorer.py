VIOLATION_LEVELS = [
    (80, "매우 높음 🔴", "우선 단속/수거"),
    (50, "높음 🟡", "현장 확인 필요"),
    (30, "낮음 🟢", "모니터링"),
    (0, "정상 ⚪", "정상 주차 가능성 높음"),
]


class RiskScorer:
    def score(self, abnormal_confidence=0.0, detections=None, **kwargs):
        if detections:
            for det in detections:
                if det.get("label") == "abnormal":
                    abnormal_confidence = max(
                        abnormal_confidence,
                        det.get("confidence", 0.0)
                    )

        violation_score = round(abnormal_confidence * 100, 1)

        for threshold, level, action in VIOLATION_LEVELS:
            if violation_score >= threshold:
                return {
                    "violation_score": violation_score,
                    "level": level,
                    "action": action,
                    "abnormal_confidence": abnormal_confidence
                }
