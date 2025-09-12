import pyautogui
from utils.load_images import load_images_from_path

SPACEBAR_PATH = "assets/SpaceBar"
spacebar_imgs = load_images_from_path(SPACEBAR_PATH, "SpaceBar_")

CONFIDENCE = 0.95
MAX_ATTEMPTS = 10
region = (886, 324, 148, 46)

def detect_spacebar():
    """
    Detecta SpaceBar en la región específica calculada
    """
    count = 0
    while count < MAX_ATTEMPTS:
        for img_name, image_path in spacebar_imgs.items():
            try:
                # Intentar sin confidence primero
                location = pyautogui.locateOnScreen(image_path, region=region)
                count += 1
                if location:
                    return True
            except Exception as e:
                count += 1
                continue
    return False
