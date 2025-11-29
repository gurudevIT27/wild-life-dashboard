# detection/yolo_service.py
from ultralytics import YOLO
import numpy as np

# path to your trained/pretrained model file (you said you have this)
MODEL_PATH = "yolov8_model/yolov8n.pt"

# Load model once
model = YOLO(MODEL_PATH)

# model.names is usually a dict mapping id->label (works for COCO or custom)
CLASS_MAP = getattr(model, "names", None) or {}

def run_detection(frame):
    """
    Run YOLOv8 inference on a single BGR frame (numpy array).
    Returns:
      - boxes_data: list of dicts {class, confidence, bbox}
      - annotated_frame: numpy BGR image (with drawn boxes) or original frame on failure
    """
    try:
        # ultralytics accepts numpy arrays directly as `source=frame`
        # imgsz optional; remove or adjust if you have memory/latency concerns
        results = model.predict(source=frame, imgsz=640, verbose=False)
    except Exception as e:
        # inference failed
        print("YOLO predict() raised:", e)
        return [], frame

    # results can be empty list or contain a result object
    if not results or len(results) == 0:
        return [], frame

    r = results[0]

    # The `.boxes` attribute can be None if nothing detected
    if not hasattr(r, "boxes") or r.boxes is None:
        # still try to return annotated frame if available
        try:
            annotated = r.plot() if hasattr(r, "plot") else frame
        except Exception:
            annotated = frame
        return [], annotated

    # Try to create an annotated frame (may throw on some versions)
    try:
        annotated = r.plot()
    except Exception:
        annotated = frame

    boxes = []
    # r.boxes is an iterable of box objects; iterate safely
    for box in r.boxes:
        try:
            # Box fields differ by ultralytics version; handle common cases:
            # box.cls -> tensor with class index
            # box.conf -> tensor with confidence
            # box.xyxy -> tensor with coordinates [x1,y1,x2,y2]
            cls_id = None
            conf = None
            xyxy = None

            # Try common access patterns (robust)
            if hasattr(box, "cls"):
                # box.cls may be tensor like [idx]
                cls_val = box.cls[0] if hasattr(box.cls, "__len__") else box.cls
                cls_id = int(cls_val.item()) if hasattr(cls_val, "item") else int(cls_val)
            if hasattr(box, "conf"):
                conf_val = box.conf[0] if hasattr(box.conf, "__len__") else box.conf
                conf = float(conf_val.item()) if hasattr(conf_val, "item") else float(conf_val)
            if hasattr(box, "xyxy"):
                coords = box.xyxy[0] if hasattr(box.xyxy, "__len__") else box.xyxy
                # convert to python floats
                xyxy = [float(x) for x in coords.tolist()] if hasattr(coords, "tolist") else [float(x) for x in coords]

            # fallback if attributes not present
            if cls_id is None:
                # some versions use box.cls_id or box.class_id
                for alt in ("cls_id", "class_id"):
                    if hasattr(box, alt):
                        v = getattr(box, alt)
                        cls_id = int(v.item()) if hasattr(v, "item") else int(v)
                        break

            if conf is None:
                for alt in ("confidence",):
                    if hasattr(box, alt):
                        v = getattr(box, alt)
                        conf = float(v.item()) if hasattr(v, "item") else float(v)
                        break

            if xyxy is None:
                # try box.xyxy or box.xyxy[0]
                pass

            # if we still couldn't parse bbox, skip this box
            if cls_id is None:
                continue

            label = CLASS_MAP.get(cls_id, f"class_{cls_id}")
            boxes.append({
                "class": label,
                "confidence": conf if conf is not None else 0.0,
                "bbox": xyxy if xyxy is not None else None,
            })
        except Exception as e:
            # skip malformed box but keep inference running
            print("Warning: skipped box due to parse error:", e)
            continue

    return boxes, annotated
