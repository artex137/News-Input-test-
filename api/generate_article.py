import os
import json
from datetime import datetime
from pathlib import Path
from openai import OpenAI
from jinja2 import Template

# === Configuration ===
UPLOAD_DIR = "static/images/uploaded"
ARTICLE_DIR = "articles"
TEMPLATE_FILE = "templates/article_template.html"
INDEX_FILE = "templates/data/article_index.json"
IMAGE_OUTPUT_DIR = "static/images/article-images"

# === Setup OpenAI ===
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# === Ensure required folders exist ===
os.makedirs(ARTICLE_DIR, exist_ok=True)
os.makedirs(IMAGE_OUTPUT_DIR, exist_ok=True)

def get_newest_file():
    files = list(Path(UPLOAD_DIR).glob("*.*"))
    return max(files, key=os.path.getctime) if files else None

def analyze_image_with_gpt(image_path):
    print(f"📡 Analyzing image: {image_path.name}")

    # Replace this stub with real OpenAI Vision when available
    return (
        "Mystery Man in Cloak Summons Frogs on Parliament Hill",
        "<p>A cloaked figure summoned frogs onto Parliament Hill, shocking visitors.</p>"
        "<p>Chants in an unknown language preceded the frog swarm, leaving experts baffled.</p>"
        "<p>RCMP found no suspect, only strange footprints and a charred book.</p>"
        "<p>Officials say the frogs were unharmed and released into the Ottawa River.</p>",
        "A hooded figure reportedly summoned frogs in downtown Ottawa on October 31, 2025."
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

    print(f"✅ Article saved: {article_path}")
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

    print("✅ article_index.json updated")

def main():
    print("🚀 Starting article generation...")

    newest = get_newest_file()
    if not newest:
        print("❌ No uploaded image found in static/images/uploaded/")
        return

    print(f"📷 Found uploaded image: {newest.name}")

    try:
        title, body, caption = analyze_image_with_gpt(newest)
        print(f"📰 Title: {title}")
        print(f"📄 First paragraph preview: {body.split('</p>')[0]}")

        slug = slugify(title)
        new_image_filename = f"{slug}.png"
        new_image_path = os.path.join(IMAGE_OUTPUT_DIR, new_image_filename)

        os.rename(newest, new_image_path)
        print(f"✅ Image moved to: {new_image_path}")

        create_article_html(title, body, caption, new_image_filename)
        update_index(slug, title, new_image_filename)

        print(f"✅ Finished: {slug}.html generated and index updated")

    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    main()
