from ultralytics import YOLO

helmet_model=YOLO("/home/theertha/Desktop/Helmet_overspeed_detection/models/helmet_best.pt")
plate_model=YOLO("/home/theertha/Desktop/Helmet_overspeed_detection/models/license_plate_detector.pt")


def detect_helmets(frame):
    results= helmet_model(frame)
    boxes= results[0].boxes.xyxy.numpy()
    scores= results[0].boxes.conf.numpy()
    cls_id= results[0].boxes.cls.numpy()
    detections=[]
    for box,score, cls in zip(boxes,scores,cls_id):
        detections.append(tuple([*box, float(score), int(cls)]))
        return detections
    
def detect_plates(frame):
    results= plate_model(frame)
    boxes= results[0].boxes.xyxy.numpy()
    scores= results[0].boxes.conf.numpy()
    cls_id= results[0].boxes.cls.numpy()
    detections=[]
    for box,score, cls in zip(boxes,scores,cls_id):
        detections.append(tuple([*box, float(score), int(cls)]))
        return detections

    
    
