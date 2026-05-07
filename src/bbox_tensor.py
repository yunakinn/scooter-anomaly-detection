import torch
import os

class BBoxTensor:
    def __init__(self, label_path):
        self.label_path = label_path
        self.data = self._load()

    def _load(self):
        boxes = []
        with open(self.label_path, 'r') as f:
            for line in f:
                values = list(map(float, line.strip().split()))
                boxes.append(values)
        # shape: (N, 5) — [class, cx, cy, w, h]
        return torch.tensor(boxes)

    def get_classes(self):
        return self.data[:, 0].long()

    def get_boxes(self):
        # [cx, cy, w, h]
        return self.data[:, 1:]

    def get_wh(self):
        # w, h만 추출
        return self.data[:, 3], self.data[:, 4]