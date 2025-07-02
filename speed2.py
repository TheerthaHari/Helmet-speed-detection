from datetime import datetime


crossing_time = {}
speed_record = {}

def frame_to_time(frame_idx, fps):
    """Convert frame index to timestamp based on FPS."""
    return datetime.fromtimestamp(frame_idx / fps)

def interpolate_time(line_y, y1, y2, t1, t2):
    if y2 == y1:
        return t2.timestamp()
    ratio = (line_y - y1) / (y2 - y1)
    time_diff = (t2 - t1).total_seconds()
    return t1.timestamp() + ratio * time_diff

def speed_track(track_id, cy_prev, cy_curr, time_prev, time_curr, fps):

    ENTRY_LINE_Y = 400
    EXIT_LINE_Y = 500
    REAL_DISTANCE_METERS = 10 
    MIN_TIME_DIFF = 0.05

    if track_id not in crossing_time:
        crossing_time[track_id] = {}

    track_data = crossing_time[track_id]

    if 'entry' not in track_data and cy_prev < ENTRY_LINE_Y <= cy_curr:
        t_entry = interpolate_time(ENTRY_LINE_Y, cy_prev, cy_curr, time_prev, time_curr)
        track_data['entry'] = datetime.fromtimestamp(t_entry)

    if 'entry' in track_data and 'exit' not in track_data and cy_prev < EXIT_LINE_Y <= cy_curr:
        t_exit = interpolate_time(EXIT_LINE_Y, cy_prev, cy_curr, time_prev, time_curr)
        track_data['exit'] = datetime.fromtimestamp(t_exit)

        time_diff = (track_data['exit'] - track_data['entry']).total_seconds()
        if time_diff > MIN_TIME_DIFF:
            speed_mps = REAL_DISTANCE_METERS / time_diff
            speed_kmph = round(speed_mps * 3.6, 2)
            speed_record[track_id] = speed_kmph
            return speed_kmph
        
    return speed_record.get(track_id, 0.0)
