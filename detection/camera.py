# detection/camera.py
import json
import cv2
from django.utils.timezone import now
from .models import Detection
from .yolo_service import run_detection  # ensure you have yolo_service.run_detection(frame) -> (boxes_data, annotated_frame)

# Default GPS location (replace with real GPS if you have it)
DEFAULT_LOCATION = {
    "lat": 12.9716,
    "lng": 77.5946,
}


def gen_frames(camera_index: int = 0):
    """
    Capture frames from the camera, run YOLO detection, save detections to the local Django DB,
    and yield MJPEG frames (multipart/x-mixed-replace) suitable for StreamingHttpResponse.

    - camera_index: OpenCV camera index or RTSP/URL (if you pass a string replace above usage)
    """
    # allow camera_index to be a device index (int) or a string source (rtsp/http)
    cap = cv2.VideoCapture(camera_index)

    try:
        while True:
            success, frame = cap.read()
            if not success:
                # no frame, stop streaming
                break

            # Run your YOLOv8 detection on the current frame.
            # run_detection should return:
            #   boxes_data: list[ { "class": "animal", "confidence": 0.88, "bbox": [x1,y1,x2,y2], ... }, ... ]
            #   annotated_frame: an image (numpy array) with boxes drawn (BGR color)
            try:
                boxes_data, annotated_frame = run_detection(frame)
            except Exception as e:
                # If detection fails, fallback to sending the raw frame
                annotated_frame = frame
                boxes_data = []
                # (optional) log exception to server logs
                # import logging; logging.exception("YOLO detection error")

            # Persist detections to Django DB (Detection model)
            # Only save when there are detections to avoid spam
            if boxes_data:
                for det in boxes_data:
                    try:
                        # Normalize fields from detection output to match your model:
                        class_name = det.get("class") or det.get("label") or "unknown"
                        confidence = det.get("confidence", det.get("conf", None))
                        bbox = det.get("bbox") or det.get("xyxy") or None

                        # Save as Python types — Django JSONField will store them correctly
                        Detection.objects.create(
                            class_name=str(class_name),
                            confidence=float(confidence) if confidence is not None else 0.0,
                            bbox=bbox,
                            location=DEFAULT_LOCATION,
                            raw=det,
                            timestamp=now(),
                        )
                    except Exception:
                        # Ignore individual save errors to keep stream running
                        # import logging; logging.exception("Failed to save detection")
                        pass

            # Convert annotated_frame (numpy BGR) to JPEG bytes
            try:
                ret, buffer = cv2.imencode('.jpg', annotated_frame)
                if not ret:
                    continue
                frame_bytes = buffer.tobytes()
            except Exception:
                # fallback to encoding the original frame if annotated_frame fails
                try:
                    ret, buffer = cv2.imencode('.jpg', frame)
                    if not ret:
                        continue
                    frame_bytes = buffer.tobytes()
                except Exception:
                    continue

            # Yield multipart JPEG frame
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        try:
            cap.release()
        except Exception:
            pass
