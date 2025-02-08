import re\\\\\ndef is_comment(line: str) -> bool:\\\"""\\\\\nDetermines if a given line is a Markdown comment.\\\\\nMarkdown comments are in the format <!-- comment -->\\\\\n\\\\\n:param line: The line to check\\\\\n:return: True if the line is a comment, False otherwise\\\\\n"""\\\\\n    return bool(re.match(r"^\s*<!--.*-->\s*$", line))