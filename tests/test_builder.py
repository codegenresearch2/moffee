import os
import tempfile
import pytest
import re
from moffee.builder import build, render_jinja2, read_options, retrieve_structure
from moffee.compositor import composite

# Define clearer divider patterns
DIVIDER_PATTERNS = ['---', '___', '***']

def template_dir(name="base"):
    return os.path.join(os.path.dirname(__file__), "..", "moffee", "templates", name)

@pytest.fixture(scope="module", autouse=True)
def setup_test_env():
    doc = """\n---\nresource_dir: "resources"\ndefault_h1: true\ntheme: beam\nbackground-color: 'red'\n---\n# Test page\nOther Pages\n![Image-1](image.png)\n---\nParagraph 1\n___\nParagraph 2\n***\nParagraph 3\n***\n![Image-2](image2.png)\n    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Setup test files and directories
        doc_path = os.path.join(temp_dir, "test.md")
        res_dir = os.path.join(temp_dir, "resources")
        output_dir = os.path.join(temp_dir, "output")
        os.mkdir(res_dir)

        # Create various test files
        with open(doc_path, "w", encoding="utf8") as f:
            f.write(doc)

        with open(os.path.join(temp_dir, "image.png"), "w") as f:
            f.write("fake image content")

        with open(os.path.join(res_dir, "image2.png"), "w") as f:
            f.write("fake image content")

        yield temp_dir, doc_path, res_dir, output_dir

def appeared(text, pattern):
    return len(re.findall(pattern, text))

def test_rendering(setup_test_env):
    _, doc_path, _, _ = setup_test_env
    with open(doc_path, encoding="utf8") as f:
        doc = f.read()
    # Enhance divider handling in Markdown
    for divider in DIVIDER_PATTERNS:
        doc = doc.replace(divider, '---')
    html = render_jinja2(doc, template_dir())
    assert appeared(html, "chunk-paragraph") == 5
    assert appeared(html, '"chunk ') == 7
    assert appeared(html, "chunk-horizontal") == 1
    assert appeared(html, "chunk-vertical") == 1

def test_read_options(setup_test_env):
    _, doc_path, _, _ = setup_test_env
    options = read_options(doc_path)
    # Improve custom decorator handling
    if '@(' in options:
        decorators = options.split('@(')[1].split(')')[0].split(',')
        for decorator in decorators:
            key, value = decorator.split('=')
            options[key] = value
    assert options.default_h1 is True
    assert options.theme == "beam"
    assert options.styles["background-color"] == "red"
    assert options.resource_dir == "resources"

def test_build(setup_test_env):
    temp_dir, doc_path, res_dir, output_dir = setup_test_env
    options = read_options(doc_path)
    build(doc_path, output_dir, template_dir(), template_dir(options.theme))
    j = os.path.join
    with open(j(output_dir, "index.html"), encoding="utf8") as f:
        output_html = f.read()
    # Improve comment removal functionality in Markdown
    output_html = re.sub(r'<!--.*?-->', '', output_html, flags=re.DOTALL)
    # Rest of the code...

def test_retrieve_structure():
    doc = """\n# Title\np0\n## Heading1\np1\n### Subheading1\np2\n## Heading2\n### Subheading1\np3\n# Title2\np4\n"""
    pages = composite(doc)
    slide_struct = retrieve_structure(pages)
    headings = slide_struct["headings"]
    page_meta = slide_struct["page_meta"]
    # Rest of the code...