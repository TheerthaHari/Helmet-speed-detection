import cv2
import numpy as np

def estimate_speed(prev_pos,curr_pos,fps,scale=0.05):
    dx= curr_pos[0]-prev_pos[0]
    dy= curr_pos[1]-prev_pos[1]
    dist_pixels= np. hypot(dx,dy)
    return dist_pixels*fps*scale

#def annotate_frame(frame, text,plate_text,pos=(10, 30), color=(0,0,255)):
    #cv2.putText(frame, text,plate_text, pos, cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
def annotate_frame(frame, violation, plate_text, pos):
    color = (0, 0, 255)  # Red for violations
    if violation: #else f"Plate: {plate_text}
        text = f"{violation.upper()} - Plate: {plate_text}" 
        cv2.putText(frame, text, pos, cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)