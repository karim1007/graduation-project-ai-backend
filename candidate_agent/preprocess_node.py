import numpy as np
from langchain.nodes import BaseNode

def min_max_normalization(data):
    """Perform Min-Max Normalization"""
    min_val = np.min(data)
    max_val = np.max(data)
    return (data - min_val) / (max_val - min_val)

def z_score_normalization(data):
    """Perform Z-Score Normalization"""
    mean_val = np.mean(data)
    std_dev = np.std(data)
    return (data - mean_val) / std_dev

class PreprocessNode(BaseNode):
    def __init__(self, normalization_type="min_max"):
        self.normalization_type = normalization_type

    def process(self, features):
        """Process the incoming features by applying normalization"""
        if self.normalization_type == "min_max":
            return min_max_normalization(features)
        elif self.normalization_type == "z_score":
            return z_score_normalization(features)
        else:
            raise ValueError("Unsupported normalization type")
