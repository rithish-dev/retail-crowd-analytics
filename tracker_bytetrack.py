import supervision as sv

tracker = sv.ByteTrack()

def update_tracker(detections):
    return tracker.update_with_detections(detections)
