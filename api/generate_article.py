import os
import json
from datetime import datetime
from pathlib import Path
from openai import OpenAI
from jinja2 import Template
from PIL import Image

# Load API Key from GitHub Secrets or config.py
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

UPLOADS_DIR = "static/images/uploaded"
ARTICLE_DIR = "articles"
INDEX_FILE = "data/article_index.json"
TEMPLATE_FILE = "templates/article_template.html"

def analyze_file(file_path):
    filename = os.path.basename(file_path)

    if filename.lower().endswith((".jpg", ".jpeg", ".png")):
        # Use GPT-4 Vision for image
        with open(file_path, "rb") as image_file:
            response = client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {"role": "user", "content": [
                        {"type": "text", "text": "Describe this image and infer what kind of news story could be based on it. Return a short title, a fictional but realistic article body (4 paragraphs), and a caption."},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_file.read().hex()}"}}  # placeholder format
                    ]}
                ],
                max_tokens=800
            )
            return response.choices[0].message.content

    elif filename.lower().endswith(".txt"):
        # Use GPT-4 for text
        with open(file_path, "r", encoding="utf-8") as f:
            user_text = f.read()

        prompt = f"""
        You're a journalist. Based on the following user-submitted notes, generate:
        - A realistic and engaging headline
        - A 4-paragraph fictional article in dark satire or surreal tone
        - An image caption for a photo that might accompany it

        Notes: {user_text}
        """

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        return response.choices[0].message.content

    return None


def generate_html_from_ai_output(ai_output, slug):
    lines = ai_output.split("\n")
    title = lines[0].strip()
    body = "\n".join(lines[1:-1]).strip()
    caption = lines[-1].strip()

    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        template = Template(f.read())

    html = template.render(
        title=title,
        date=datetime.now().strftime("%B %d, %Y at %I:%M %p"),
        body=body,
        image_filename=f"{slug}.png",
        caption=caption
    )

    article_path = os.path.join(ARTICLE_DIR, f"{slug}.html")
    with open(article_path, "w", encoding="utf-8") as f:
        f.write(html)

    # Update index
    if not os.path.exists(INDEX_FILE):
        articles = []
    else:
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            articles = json.load(f)

    articles.insert(0, {
        "title": title,
        "slug": slug,
        "date": datetime.now().isoformat(),
        "image": f"static/images/article-images/{slug}.png"
    })

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=2)

    return article_path
