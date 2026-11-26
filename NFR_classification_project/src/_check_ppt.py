"""
Extract all text from PPT XML for consistency check
"""
import re

with open(r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\ppt_slides\final_v3.xml", 'r', encoding='utf-8') as f:
    xml = f.read()

# Extract all slides
slides = re.findall(r'<slide id="([^"]+)">(.*?)</slide>', xml, re.DOTALL)

for slide_id, content in slides:
    # Extract title
    title_match = re.search(r'textType="headline"[^>]*>\s*<p>(.*?)</p>', content)
    title = title_match.group(1) if title_match else "No title"
    
    print(f"\n{'='*70}")
    print(f"Slide {slide_id}: {title}")
    print(f"{'='*70}")
    
    # Extract all paragraphs
    paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', content, re.DOTALL)
    for p in paragraphs:
        # Remove XML tags
        clean = re.sub(r'<[^>]+>', '', p).strip()
        # Decode HTML entities
        clean = clean.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&apos;', "'")
        if clean:
            print(f"  {clean}")
