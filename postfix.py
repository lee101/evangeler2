import json
from pathlib import Path

from downloader import download_image

# Open the file in binary mode and read all bytes
with open('affiliates.json', 'rb') as f:
    data = f.read()

# Decode the bytes to string using utf-8 encoding
data_str = data.decode('utf-8')

# Load the JSON data
affiliates = json.loads(data_str)

save_path = 'images/'
# ensure path exists
Path(save_path).mkdir(parents=True, exist_ok=True)

for affiliate in affiliates:
    name = affiliate['brand']
    save_full_path = save_path + name + '.webp'
    if Path(save_full_path).exists():
        print(f'{name} already exists')
        continue
    download_image(affiliate['imageUrl'], save_full_path)
    
