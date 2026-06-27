def detect_people(frame, model):
    results = model(frame, stream=True)

    detections = []

    for r in results:
        for b in r.boxes:
            cls = int(b.cls)

            if cls == 0:
                x1, y1, x2, y2 = map(int, b.xyxy[0])
                detections.append((x1, y1, x2, y2))

    return detections
