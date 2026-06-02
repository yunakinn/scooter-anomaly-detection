CLASS_NAMES = {0: "normal", 1: "abnormal"}

RISK_LEVELS = [
    (80, "위험 🔴", "즉시 수거 필요"),
    (50, "주의 🟡", "재배치 필요"),
    (30, "낮음 🟢", "현장 확인 필요"),
    (0,  "정상 ⚪", "정상 반납"),
]

# IMU 기준값
TILT_THRESHOLD = 30   # 30도 이상 이상
TILT_MAX = 90


class RiskScorer:
    def score(self, detections, tilt_angle, shock_detected):
        # abnormal confidence 추출
        abnormal_conf = 0.0
        for det in detections:
            if det["label"] == "abnormal":
                abnormal_conf = max(abnormal_conf, det["confidence"])

        # IMU 점수 정규화 (0~1)
        tilt_score = min(tilt_angle / TILT_MAX, 1.0)
        shock_score = 1.0 if shock_detected else 0.0

        # 위험도 계산
        risk_score = (
            abnormal_conf * 70
            + tilt_score * 20
            + shock_score * 10
        )

        # 위험 등급 판단
        for threshold, level, action in RISK_LEVELS:
            if risk_score >= threshold:
                return {
                    "risk_score": round(risk_score, 1),
                    "level": level,
                    "action": action,
                    "abnormal_conf": abnormal_conf,
                    "tilt_score": tilt_score,
                    "shock_score": shock_score
                }