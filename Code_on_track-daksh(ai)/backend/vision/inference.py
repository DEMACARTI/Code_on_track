import random
import base64
import numpy as np
import cv2

def run_inference(image_bytes):
    """
    Mock inference engine for defect detection.
    In a real system, this would load a PyTorch/TensorFlow model.
    """
    # Decoding image to check validity (and for resizing if we were doing real CV)
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise ValueError("Invalid image data")

    # Mock logic: Randomly detect defects
    defects = [
        {"issue": "Rust", "severity": "HIGH", "action": "Replace soon"},
        {"issue": "Crack", "severity": "CRITICAL", "action": "Urgent replacement"},
        {"issue": "Broken Clip", "severity": "CRITICAL", "action": "Urgent replacement"},
        {"issue": "Chipped Pad", "severity": "MEDIUM", "action": "Schedule inspection"},
        {"issue": None, "severity": "LOW", "action": "Monitor"}
    ]
    
    # Weighted choice to favor "Rust" or "Safe" for demo purposes
    weights = [0.3, 0.1, 0.1, 0.2, 0.3]
    result = random.choices(defects, weights=weights, k=1)[0]
    
    score = random.uniform(0.7, 0.99) if result["issue"] else random.uniform(0.9, 1.0)
    
    bbox = []
    if result["issue"]:
        # Mock bounding box [x, y, w, h]
        h, w, _ = img.shape
        bx = random.randint(0, int(w * 0.5))
        by = random.randint(0, int(h * 0.5))
        bw = random.randint(50, int(w * 0.4))
        bh = random.randint(50, int(h * 0.4))
        bbox = [bx, by, bw, bh]

    return {
        "issue": result["issue"] or "No Issues Detected",
        "confidence": round(score, 2),
        "severity": result["severity"],
        "recommended_action": result["action"],
        "bbox": bbox
    }
