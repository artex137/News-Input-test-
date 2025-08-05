import os
import json
from datetime import datetime
from pathlib import Path
from openai import OpenAI
from jinja2 import Template

# === Config ===
UPLOAD_DIR = "static/images/uploaded"
ARTICLE_DIR = "articles"
TEMPLATE_FILE = "templates/article_template.html"
INDEX_FILE = "templates/data/article_index.json"
IMAGE_OUTPUT_DIR = "static/images/article-images"

# === OpenAI Setup ===
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# === Ensure required folders exist ===
os.makedirs(ARTICLE_DIR, exist_ok=True)
os.makedirs(IMAGE_OUTPUT_DIR, exist_ok=True)

def get_newest_file():
    files = list(Path(UPLOAD_DIR).glob("*.*"))
    return max(files, key=os.path.getctime) if files else None

def analyze_image_with_gpt(image_path):
    print(f"Analyzing image: {image_path.name}")

    prompt = (
        "You're a surreal dark satire news reporter. "
        "Based only on this image, generate:\n"
        "- A clickbait headline\n"
        "- A 4-paragraph fictional news article (HTML <p> tags)\n"
        "- An image caption\n"
        "Tone: Bizarre, ominous, or conspiratorial. Humor optional."
    )

    # Note: Here we simulate API for GitHub-only environment.
    # Replace this with real GPT-4 Vision call when hosted elsewhere.
    return (
        "Mystery Man in Cloak Summons Frogs on Parliament Hill",
        "<p>A figure in a dark cloak reportedly summoned frogs en masse on Parliament Hill late Tuesday night. "
        "The incident began with chanting heard across the Rideau Canal, followed by an eerie green mist.</p>"
        "<p>Eyewitnesses claimed the man raised his hands and bellowed in an unknown language before amphibians "
        "began pouring from the sky. Many fled; others filmed the spectacle on their phones.</p>"
        "<p>The RCMP arrived to find the Parliament steps slick with frogs and slime, but the summoner had vanished, "
        "leaving only a charred book and sandal footprints.</p>"
        "<p>Some speculate the event was a climate protest; others call it a ritualistic warning. "
        "The frogs were unharmed and relocated to the Ottawa River.</p>",
        "Security footage captures cloaked man moments before frog downpour — Oct 31, 2025"
    )

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
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            index_data = json.load(f)

    new_entry = {
        "title": title,
        "slug": slug,
        "date": datetime.now().isoformat(),
        "image": f"static/images/article-images/{image_filename}"
    }

    index_data.insert(0, new_entry)

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2)

def main():
    newest = get_newest_file()
    if not newest:
        print("❌ No image uploaded.")
        return

    title, body, caption = analyze_image_with_gpt(newest)
    slug = slugify(title)

    new_image_filename = f"{slug}.png"
    new_image_path = os.path.join(IMAGE_OUTPUT_DIR, new_image_filename)
    os.rename(newest, new_image_path)

    create_article_html(title, body, caption, new_image_filename)
    update_index(slug, title, new_image_filename)

    print(f"✅ New article generated: {slug}.html")

if __name__ == "__main__":
    main()
