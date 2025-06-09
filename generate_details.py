import json
import re
from pathlib import Path

# Load affiliates
with open('affiliates.json') as f:
    affiliates = json.load(f)

details = []

for entry in affiliates:
    brand = entry.get('brand')
    description = entry.get('description', '')
    website = entry.get('website', '')
    slug = re.sub(r'[^a-z0-9]+', '-', brand.lower()).strip('-')
    faq = [
        {"q": f"What is {brand}?", "a": description},
        {"q": f"How do I join the {brand} affiliate program?", "a": f"Visit {website} to sign up."},
        {"q": f"What commission does {brand} offer?", "a": description},
    ]
    details.append({
        "brand": brand,
        "slug": slug,
        "description": description,
        "website": website,
        "faq": faq,
    })

Path('affiliate_details.json').write_text(json.dumps(details, indent=2))
