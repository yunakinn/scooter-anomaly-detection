import torch
from src.posture_analyzer import PostureAnalyzer
from src.bbox_tensor import BBoxTensor

class AnomalyScorer:
    def __init__(self):
        pass

    def score(self, bbox_tensor: BBoxTensor):
        w, h = bbox_tensor.get_wh()
        
        # requires_grad 설정 (autograd 사용)
        w = w.float().requires_grad_(True)
        h = h.float().requires_grad_(True)
        
        # 이상 점수 함수: w/h 비율을 기반으로 계산
        ratio = w / h
        score = torch.mean(ratio)
        
        # gradient 계산
        score.backward()
        
        return {
            'score': score.item(),
            'w_grad': w.grad,  # w가 점수에 기여한 정도
            'h_grad': h.grad   # h가 점수에 기여한 정도
        }