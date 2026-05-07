import torch
from src.bbox_tensor import BBoxTensor
from src.posture_analyzer import PostureAnalyzer
from src.anomaly_scorer import AnomalyScorer

class AbandonmentClassifier:
    def __init__(self, score_threshold=1.0, posture_threshold=1.0):
        self.score_threshold = score_threshold
        self.posture_analyzer = PostureAnalyzer(threshold=posture_threshold)
        self.anomaly_scorer = AnomalyScorer()

    def classify(self, bbox_tensor: BBoxTensor):
        # 1. 자세 판정
        posture = self.posture_analyzer.analyze(bbox_tensor)
        
        # 2. 이상 점수 계산
        anomaly = self.anomaly_scorer.score(bbox_tensor)
        
        # 3. 최종 판정
        # 자세가 쓰러짐 + 이상 점수가 threshold 초과 시 방치로 판정
        is_abandoned = posture['is_fallen'] & (anomaly['score'] > self.score_threshold)
        
        result = {
            'is_abandoned': is_abandoned,
            'posture': posture,
            'anomaly': anomaly,
            'label': ['normal' if not x else 'abnormal' for x in is_abandoned]
        }
        
        return result