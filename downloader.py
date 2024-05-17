from io import BytesIO
import requests
from PIL import Image

def download_image(url:str, path:str):

    response = requests.get(url)
    image = Image.open(BytesIO(response.content)).convert("RGB")
    image.save(path, format="webp", quality=85)

    return image
