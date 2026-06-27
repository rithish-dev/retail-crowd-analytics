from config import DIST_THRESHOLD


def match_person(
    detections,
    people,
    next_id,
    now,
    getcenter,
    iou
):
    matched = set()

    for (x1, y1, x2, y2) in detections:

        cx, cy = getcenter((x1, y1, x2, y2))

        best = None
        best_score = 0

        for pid, p in people.items():

            if "box" not in p:
                continue

            iou_score = iou((x1, y1, x2, y2), p["box"])

            px, py = p["center"]

            dist = abs(px - cx) + abs(py - cy)
            dist_score = max(0, 1 - dist / DIST_THRESHOLD)

            score = 0.6 * iou_score + 0.4 * dist_score

            if score > best_score:
                best_score = score
                best = pid

        if best is None or best_score < 0.15:

            pid = next_id
            next_id += 1

            people[pid] = {
                "center": (cx, cy),
                "last": now,
                "inside": False,
                "enter_time": None,
                "total_time": 0,
                "box": (x1, y1, x2, y2),
                "outside_time": None
            }

        else:
            pid = best

        people[pid]["box"] = (x1, y1, x2, y2)
        people[pid]["center"] = (cx, cy)
        people[pid]["last"] = now

        matched.add(pid)

    return people, matched, next_id