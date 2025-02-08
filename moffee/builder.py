from typing import List\\\nimport os\\\nfrom jinja2 import Environment, FileSystemLoader\\\nfrom moffee.compositor import Page, PageOption, composite, parse_frontmatter\\\nfrom moffee.markdown import md\\\nfrom moffee.utils.md_helper import extract_title\\\nfrom moffee.utils.file_helper import redirect_paths, copy_assets, merge_directories\\\n\\ndef read_options(document_path) -> PageOption:\\"""Read frontmatter options from the document path"""\\\\\n    with open(document_path, "r") as f:\\\n        document = f.read()\\\n    _, options = parse_frontmatter(document)\\\\\n    return options\\\\\n\\\\\ndef retrieve_structure(pages: List[Page]) -> dict:\\\\\n    current_h1 = None\\\n    current_h2 = None\\\n    current_h3 = None\\\n    last_h1_idx = -1\\\n    last_h2_idx = -1\\\n    last_h3_idx = -1\\\n    page_meta = []\\\n    headings = []\\\n    for i, page in enumerate(pages):\\\n        if page.h1 and page.h1 != current_h1:\\\n            current_h1 = page.h1\\\n            current_h2 = None\\\n            current_h3 = None\\\n            last_h1_idx = len(headings) - 1\\\n            headings.append({\"level\": 1, \"content\": page.h1, \"page_ids\": []})\\\n\\\\\n        if page.h2 and page.h2 != current_h2:\\\n            current_h2 = page.h2\\\n            current_h3 = None\\\n            last_h2_idx = len(headings) - 1\\\n            headings.append({\"level\": 2, \"content\": page.h2, \"page_ids\": []})\\\n\\\\\n        if page.h3 and page.h3 != current_h3:\\\n            current_h3 = page.h3\\\n            last_h3_idx = len(headings) - 1\\\n            headings.append({\"level\": 3, \"content\": page.h3, \"page_ids\": []})\\\n\\\\\n        if page.h1 or page.h2 or page.h3:\\\n            headings[last_h1_idx][\"page_ids\"].append(i)\\\n        if page.h2 or page.h3:\\\n            headings[last_h2_idx][\"page_ids\"].append(i)\\\n        if page.h3:\\\n            headings[last_h3_idx][\"page_ids\"].append(i)\\\n\\\\\n        page_meta.append({\"h1\": current_h1, \"h2\": current_h2, \"h3\": current_h3})\\\n\\\\\n    return {\"page_meta\": page_meta, \"headings\": headings}\\\\\n\\\\\ndef render_jinja2(document: str, template_dir) -> str:\\"""Run jinja2 templating to create html"""\\\\\n    # Setup Jinja 2\\\\\n    env = Environment(loader=FileSystemLoader(template_dir))\\\n\\\\\n    env.filters[\"markdown\"] = md\\\n\\\\\n    template = env.get_template(\"index.html\")\\\n\\\\\n    # Fill template\\\\\n    pages = composite(document)\\\\\n    title = extract_title(document) or \"Untitled\"\\\n    slide_struct = retrieve_structure(pages)\\\\\n\\\\\n    data = {\"title\": title, \"struct\": slide_struct, \"slides\": [\\\\n        {\"h1\": page.h1, \"h2\": page.h2, \"h3\": page.h3, \"chunk\": page.chunk, \"layout\": page.option.layout, \"styles\": page.option.styles}\\\\n        for page in pages\"]}\\\n    return template.render(data)\\\\\n\\\\\ndef build(document_path: str, output_dir: str, template_dir: str, theme_dir: str = None):\\"""Render document, create output directories and write result html."""\\\\\n    with open(document_path) as f:\\\n        document = f.read()\\\n    asset_dir = os.path.join(output_dir, \"assets\")\\\n\\\\\n    merge_directories(template_dir, output_dir, theme_dir)\\\\\n    options = read_options(document_path)\\\\\n    output_html = render_jinja2(document, output_dir)\\\\\n    output_html = redirect_paths(output_html, document_path=document_path, resource_dir=options.resource_dir)\\\\\n    output_html = copy_assets(output_html, asset_dir).replace(asset_dir, \"assets\")\\\n\\\\\n    output_file = os.path.join(output_dir, \"index.html\")\\\n    with open(output_file, \"w\", encoding=\"utf-8\") as f:\\\n        f.write(output_html)\\\\\n