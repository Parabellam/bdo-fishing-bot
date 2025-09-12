from glob import glob
import os


def load_images_from_path(path, prefix, suffix=".png"):
    return {
        f"img{index+1}": file
        for index, file in enumerate(glob(os.path.join(path, f"{prefix}*{suffix}")))
    }
