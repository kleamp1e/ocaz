import insightface
from insightface.app import FaceAnalysis
app = FaceAnalysis(providers=["CUDAExecutionProvider"])
