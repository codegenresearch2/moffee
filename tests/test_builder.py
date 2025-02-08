import os\nimport tempfile\nimport re\nimport pytest\nimport requests\nfrom moffee.builder import build, render_jinja2, read_options, retrieve_structure\nfrom moffee.compositor import composite\n\n\ndef template_dir(name='base'):\n    return os.path.join(os.path.dirname(__file__), '..', 'moffee', 'templates', name')\\\n\n\ndef appeared(text, pattern):\n    return len(re.findall(pattern, text))\n\n\n@pytest.fixture(scope='module', autouse=True)\ndef setup_test_env():\n    doc = '''\n    ---\n    resource_dir: 'resources'\n    default_h1: true\n    theme: beam\n    background-color: 'red'\n    ---\n    # Test page\n    Other Pages\n    ![Image-1](image.png)\n    ---\n    Paragraph 1\n    ___\n    Paragraph 2\n    ***\n    Paragraph 3\n    ***\n    ![Image-2](image2.png)\n    '''\n    with tempfile.TemporaryDirectory() as temp_dir:\n        # Setup test files and directories\n        doc_path = os.path.join(temp_dir, 'test.md')\n        res_dir = os.path.join(temp_dir, 'resources')\n        output_dir = os.path.join(temp_dir, 'output')\n        os.mkdir(res_dir)\n\n        # Create various test files\n        with open(doc_path, 'w', encoding='utf8') as f:\n            f.write(doc)\n\n        with open(os.path.join(temp_dir, 'image.png'), 'w') as f:\n            f.write('fake image content')\n\n        with open(os.path.join(res_dir, 'image2.png'), 'w') as f:\n            f.write('fake image content')\n\n        yield temp_dir, doc_path, res_dir, output_dir\n\n\n# Additional test functions can be added here\n\n# Main block to run tests\nif __name__ == '__main__':\n    pytest.main()\n