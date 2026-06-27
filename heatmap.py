import cv2
import numpy as np

heatmap = None


def initialize(width, height):
    global heatmap
    heatmap = np.zeros((height, width), dtype=np.float32)


def add_point(x, y):
    global heatmap

    if heatmap is None:
        return

    # Add only a tiny amount of heat
    radius = 8

    cv2.circle(
    heatmap,
    (int(x), int(y)),
    radius,
    0.08,
    -1
 )


def update():
    global heatmap

    if heatmap is None:
        return

    # Smooth the heat
    heatmap[:] = cv2.GaussianBlur(
    heatmap,
    (41,41),
    12
)

    # Slowly fade old activity
    heatmap *= 0.999


def get_heatmap():
    global heatmap

    if heatmap is None:
        return None

    normalized = cv2.normalize(
        heatmap,
        None,
        0,
        255,
        cv2.NORM_MINMAX
    ).astype(np.uint8)

    colored = cv2.applyColorMap(
        normalized,
        cv2.COLORMAP_TURBO
    )

    return colored
