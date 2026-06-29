from config import DIST_THRESHOLD
from utils import iou


def match_person(
    detections,
    people,
    next_id,
    now,
    getcenter,
    iou
):
    matched = set()

    for x1, y1, x2, y2 in detections.xyxy:

        cx, cy = getcenter((x1, y1, x2, y2))

        

        for pid, p in people.items():

            px, py = p["center"]

            vx, vy = p.get("velocity", (0, 0))

            predx = px + vx
            predy = py + vy

            iou_score = iou((x1, y1, x2, y2), p["box"])

            dist = abs(predx - cx) + abs(predy - cy)

            dist_score = max(0, 1 - dist / DIST_THRESHOLD)

            score = 0.6 * iou_score + 0.4 * dist_score

        if best is None or best_score < 0.35:

            pid = next_id
            next_id += 1

            people[pid] = {
                "center": (cx, cy),
                "last": now,
                "inside": False,
                "enter_time": None,
                "total_time": 0,
                "box": (x1, y1, x2, y2),
                "outside_time": None,
                "velocity": (0, 0),
                "matched_frames": 1
            }

        else:
            pid = best

        people[pid]["box"] = (x1, y1, x2, y2)
        
        people[pid]["center"] = (cx, cy)


        people[pid]["last"] = now
        people[pid]["matched_frames"] += 1

        matched.add(pid)

    return people, matched, next_id