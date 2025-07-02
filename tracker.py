import cv2
from ultralytics import YOLO

model= YOLO("yolov8n.pt")
VEHICLE_CLASS_IDS= {0,2,3,5,7}

def track_update(frame):
    results = model.track(frame, persist=True, verbose=False) 
    all_detections = []

    if results and results[0].boxes is not None:
        boxes = results[0].boxes
        for box in boxes:
            cls_id = int(box.cls.item()) if box.cls is not None else -1
            track_id = int(box.id.item()) if box.id is not None else -1

            if cls_id in VEHICLE_CLASS_IDS and track_id != -1:
                xyxy = box.xyxy.cpu().numpy().astype(int)[0]
                all_detections.append((track_id, cls_id, tuple(xyxy)))

    return all_detections