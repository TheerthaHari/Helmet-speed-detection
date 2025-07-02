import cv2
import re
import base64
from database import init_db,log_violation
from tracker import track_update
from model import detect_helmets, detect_plates
from speed_text import annotate_frame
from datetime import datetime
from collections.abc import Iterable
from paddleocr import PaddleOCR
from email_alert import send_email
from datetime import datetime
from speed2 import speed_track
from speed2 import frame_to_time

prev_pos = {}
prev_time = {}
prev_frame_idx = {}


init_db()
cap= cv2.VideoCapture("/home/theertha/Desktop/helmet/2025-03-25_12-42-09.mkv")
fps=cap.get(cv2.CAP_PROP_FPS)
ocr = PaddleOCR(use_angle_cls=True, lang='en')
speed_limit=60
violation_dict={}
prev_pos={}

helmet_status = {}  
violation_reported = set()

conf_threshold = 0.95
frame_no = 0

while cap.isOpened():
    ret, frame=cap.read()
    if not ret:
        print("End of Frame")
        break
    frame_no += 1
    frame_copy=frame.copy()

    current_time= datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    track=track_update(frame)
    helmet_detection= detect_helmets(frame)
    plate_detection= detect_plates(frame)

    if not isinstance(helmet_detection, Iterable):
            helmet_detection= []
    for track_id,cls_id,(x1,y1,x2,y2) in track:
         #speed
        cy = (y1 + y2) // 2

        if track_id in prev_pos and track_id in prev_frame_idx:
            cy_prev = prev_pos[track_id]
            prev_idx = prev_frame_idx[track_id]

            time_prev = frame_to_time(prev_idx, fps)
            time_curr = frame_to_time(frame_no, fps)

            speed = speed_track(track_id, cy_prev, cy, time_prev, time_curr, fps)
        else:
            speed = 0.0

        prev_pos[track_id] = cy
        prev_frame_idx[track_id] = frame_no

        cv2.putText(
            frame, 
            f"Speed: {int(speed)} km/h", 
            (x1, y1 - 10), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.6, 
            (0, 0, 255) if speed > speed_limit else (0, 255, 0), 
            2
        )


        
        #helmet
        if cls_id in [0]:
            if track_id not in helmet_status:
                helmet_status[track_id] = True
            for det in helmet_detection:
                hx1,hy1,hx2,hy2,conf,helmet_label= det
                hx1, hy1, hx2, hy2 = map(int, [hx1, hy1, hx2, hy2])
                overlap_x = max(0, min(x2, hx2) - max(x1, hx1))
                overlap_y = max(0, min(y2, hy2) - max(y1, hy1))
                if overlap_x > 0 and overlap_y > 0:
                    if helmet_label == 0:
                       helmet_status[track_id] = False
                    break

        #License plate
        if plate_detection is None:
            plate_detection = []
        DB_plate=[]
        plate_text=''
        for p in plate_detection:
            px1,py1,px2,py2=map(int, p[:4])
            if x1 < px1 < x2 and y1 < py1 < y2:
                plate_crop = frame[int(py1):int(py2), int(px1):int(px2)]
                gray = cv2.cvtColor(plate_crop, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                thresh_3ch = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

                result = ocr.ocr(thresh_3ch)
                print(f"[Frame {frame_no}] OCR raw result:", result)

                filtered_text= []

                if result and isinstance(result[0], list):
                    for line in result[0]:
                        if len(line) >= 2 and isinstance(line[1], tuple):
                            text, conf = line[1]
                            if conf > conf_threshold:
                                filtered_text.append(text)
                else:
                    print(f"[Frame {frame_no}] No valid OCR result.")

                if filtered_text:
                    plate_text = ' '.join(filtered_text).upper()
                    plate_text = re.sub(r'\W+', '', plate_text) 
                    DB_plate.append(plate_text)
                    break
                else:
                    plate_text = ''
                    print(f"[Frame {frame_no}] No text above confidence threshold.")

        helmet_violation = not helmet_status.get(track_id, True)
        violation = None
 
        if speed>speed_limit and helmet_violation:
             violation="speed & helmet" 
        elif speed>speed_limit:
             violation="speed"
        elif helmet_violation:
             violation="helmet"
        
        annotate_frame(frame, violation,plate_text, (x1, y1 - 10))

        if violation:
             key = f"{track_id}_{violation}"
             print(f"Logging violation: ID {track_id}, {violation}, Speed: {speed}")
             if key not in violation_dict:
                img_path = f"violations/violation_{current_time.replace(' ', '_').replace(':', '-')}_id{track_id}.jpg"
                cv2.imwrite(img_path,frame_copy)
                _, buffer = cv2.imencode('.jpg', frame_copy)
                img_base64 = base64.b64encode(buffer).decode('utf-8')
                violation_dict[key]={
                "track_id": track_id,
                "time":current_time,
                "violation":violation,
                "plate": plate_text,
                "speed":speed, 
                "img_base64": img_base64,                            
                }
                print(f"[DB] Track ID: {track_id}, Plate: {plate_text}, Violation: {violation}, Speed: {speed}")
                log_violation(track_id, current_time, violation, plate_text, speed,img_base64)
                send_email(track_id,violation,plate_text,speed,img_base64)

                violation_reported.add(key)
             #annotate_frame(frame, f" {violation.upper()} Speed:{int(speed)} km/h Plate License:{plate_text}", (x1, y1 - 10))

        print("***************************************************************************************SPEED:",speed)

        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        cv2.putText(frame, f'ID:{track_id}',(x1, y1 - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        #cv2.line(frame, (0, 400), (frame.shape[1],400), (0, 255, 0), 2)
        #cv2.line(frame, (0, 500), (frame.shape[1],500), (0, 0, 255), 2)

    cv2.imshow("Helmet & Speed & Plate Detection with Tracking", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()