def main():
    newest = get_newest_file()
    if not newest:
        print("❌ No image uploaded.")
        return

    print(f"📷 Found uploaded image: {newest.name}")

    try:
        title, body, caption = analyze_image_with_gpt(newest)
        slug = slugify(title)
        print(f"📰 Generated title: {title}")
        print(f"🔗 Slug: {slug}")

        new_image_filename = f"{slug}.png"
        new_image_path = os.path.join(IMAGE_OUTPUT_DIR, new_image_filename)
        os.rename(newest, new_image_path)
        print(f"✅ Moved image to: {new_image_path}")

        create_article_html(title, body, caption, new_image_filename)
        print(f"✅ Article HTML created at: articles/{slug}.html")

        update_index(slug, title, new_image_filename)
        print("✅ article_index.json updated")

    except Exception as e:
        print(f"❌ ERROR during article generation: {e}")
