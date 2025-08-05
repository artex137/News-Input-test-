import os
import json
from datetime import datetime
from pathlib import Path
from openai import OpenAI
from jinja2 import Template

# Configuration
UPLOAD_DIR = "static/images/uploaded"
ARTICLE_DIR = "articles"
TEMPLATE_FILE = "templates/article_template.html"
INDEX_FILE = "templates/data/article_index.json"
IMAGE_OUTPUT_DIR = "static/images/article-images"

# Load API Key (from GitHub Secrets or env variable)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Create required output folders if they don't exist
os.makedirs(ARTICLE_DIR, exist_ok=True)
os.makedirs(IMAGE_OUTPUT_DIR, exist_ok=True)

def get_newest_file():
    files = list(Path(UPLOAD_DIR).glob("*.*"))
    return max(files, key=os.path.getctime) if files else None

def analyze_image_with_gpt(image_path):
    print(f"Analyzing image: {image_path.name}")
    with open(image_path, "rb") as img_file:
        base64_image = img_file.read().hex()  # Fake encode just for example

    # Simulate API result for GitHub demo — replace this in real use
    title = "Mystery Man in Cloak Summons Frogs on Parliament Hill"
    body = (
        "<p>In a bizarre twist during this year’s Halloween festivities, an individual cloaked in darkness reportedly "
        "summoned a large swarm of frogs onto the steps of Parliament Hill.</p>"
        "<p>Witnesses described an eerie croaking chant just moments before amphibians began raining from the sky. "
        "Some believe it was a prank, while others insist it was a supernatural act of protest.</p>"
        "<p>The RCMP responded to the scene, but the figure had vanished, leaving behind only a trail of soggy pamphlets "
        "marked with ancient runes and the word “REPENT.”</p>"
        "<p>Social media has since exploded with frog memes, theories of weather manipulation, and speculation that Santa "
        "has finally snapped.</p>"
    )
    caption = "Security footage shows cloaked man seconds before frog swarm, Oct. 31, 2025."

    return title, body, caption

def slugify(text):
    return text.lower().replace(" ", "-").replace("’", "").replace("'", "").replace(",", "").replace(".", "")

def create_article_html(title, body, caption, image_filename):
    slug = slugify(title)
    date = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        template = Template(f.read())

    html_content = template.render(
        title=title,
        date=date,
        body=body,
        image_filename=image_filename,
        caption=caption
    )

    article_path = os.path.join(ARTICLE_DIR, f"{slug}.html")
    with open(article_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return slug

def update_index(slug, title, image_filename):
    index_data = []

    if os.path.exists(INDEX_FILE):
