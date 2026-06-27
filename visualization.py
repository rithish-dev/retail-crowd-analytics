import cv2
import time


def draw_ui(
    frame,
    people,
    enter_count,
    exit_count,
    zone,
):
    x1, y1, x2, y2 = zone

    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 2)

    y = 30

    for pid, p in people.items():

        path = p["path"]
        print(path)
        for i in range(1, len(path)):
            cv2.line(
                frame,
                path[i - 1],
                path[i],
                (0, 255, 0),
                2
            )

        t = p["total_time"]

        if p["inside"] and p["enter_time"]:
            t += time.time() - p["enter_time"]

        cv2.putText(
            frame,
            f"ID{pid}: {t:.1f}s",
            (10, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 255),
            2
        )

        y += 25

    current = sum(
        1
        for p in people.values()
        if p["inside"]
    )

    cv2.putText(
        frame,
        f"Visits Today: {enter_count}",
        (400, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        f"Exited: {exit_count}",
        (400, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 255),
        2
    )

    cv2.putText(
        frame,
        f"Current Occupancy: {current}",
        (390, 90),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 0),
        2
    )

    return current