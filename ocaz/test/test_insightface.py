from insightface.app import FaceAnalysis


def test_load_insightface():
    assert FaceAnalysis(providers=["CPUExecutionProvider"])
    assert FaceAnalysis(providers=["CUDAExecutionProvider"])
