import os
import tempfile
import pytest
import re
from moffee.builder import build, render_jinja2, read_options, retrieve_structure
from moffee.compositor import composite


def template_dir(name="base"):
    return os.path.join(os.path.dirname(__file__), "..", "moffee", "templates", name)


@pytest.fixture(scope="module", autouse=True)
def setup_test_env():
    doc = """
    ---
    resource_dir: \"resources\"
    default_h1: true
    theme: beam
    background-color: 'red'
    ---
    # Test page
    Other Pages
    ![Image-1](image.png)
    ---
    Paragraph 1
    ___
    Paragraph 2
    ***
    Paragraph 3
    ***
    ![Image-2](image2.png)
    """
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
    html = render_jinja2(doc, template_dir())
    assert appeared(html, '\"chunk \"') == 7


def test_read_options(setup_test_env):
    _, doc_path, _, _ = setup_test_env
    options = read_options(doc_path)
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

    # output dir integrity
    assert os.path.exists(j(output_dir, "css"))
    assert os.path.exists(j(output_dir, "js"))
    assert os.path.exists(j(output_dir, "assets"))
    asset_dir = os.listdir(j(output_dir, "assets"))
    assert len(asset_dir) == 2
    for name in asset_dir:
        assert name in output_html


if __name__ == "__main__":
    pytest.main()