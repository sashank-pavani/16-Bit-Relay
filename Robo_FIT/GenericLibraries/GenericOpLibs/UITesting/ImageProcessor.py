import cv2


def get_icon_circle(img: str, x: int, y: int, radius: int) -> list:
    image = cv2.imread(img)
    crop = cv2.circle(image, (x, y), radius, (255, 0, 0), 3)
    return crop


def get_icon_rect(image: str, x1: int, y1: int, x2: int, y2: int) -> list:
    # image = cv2.imread(img)
    crop = cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 0), cv2.FILLED)
    return crop
