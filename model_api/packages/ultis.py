from PIL import Image
import base64
import cv2
import numpy as np

def base64_2_img(base64_img) -> Image.Image:
    image_data = base64.b64decode(base64_img.split(',')[1])
    img_array = np.frombuffer(image_data, dtype=np.uint8)

    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    return img

def img_2_base64(img) -> str:
    _, buffer = cv2.imencode('.jpg', img)
    image_bytes = buffer.tobytes()

    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    return image_base64