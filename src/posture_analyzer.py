import torch
from src.bbox_tensor import BBoxTensor

class PostureAnalyzer:
    def __init__(self, threshold=1.0):
        # threshold: w/h 비율이 이 값을 초과하면 쓰러진 것으로 판정
        self.threshold = threshold

    def analyze(self, bbox_tensor: BBoxTensor):
        w, h = bbox_tensor.get_wh()
        
        # w/h 비율 계산 (broadcasting 활용)
        ratio = w / h
        
        # 판정: ratio > threshold면 abnormal (쓰러짐)
        is_fallen = ratio > self.threshold
        
        return {
            'ratio': ratio,
            'is_fallen': is_fallen
        }