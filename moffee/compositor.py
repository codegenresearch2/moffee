'):
                    current_escaped = not current_escaped
                if is_divider(line, type) and not current_escaped:
                    strs.append('')
                else:
                    strs[-1] += line + '\n'
            return [Chunk(paragraph=s) for s in strs]

        vchunks = split_by_div(self.raw_md, '_')
        for i in range(len(vchunks)):
            hchunks = split_by_div(vchunks[i].paragraph, '*')
            if len(hchunks) > 1:
                vchunks[i] = Chunk(children=hchunks, type=Type.NODE)

        if len(vchunks) == 1:
            return vchunks[0]

        return Chunk(children=vchunks, direction=Direction.VERTICAL, type=Type.NODE)

    def _preprocess(self):
        lines = self.raw_md.split('\n')
        lines = [l for l in lines if not (1 <= get_header_level(l) <= 3)]
        self.raw_md = '\n'.join(lines).strip()


def parse_frontmatter(document: str) -> Tuple[str, PageOption]:
    document = document.strip()
    front_matter = ''
    content = document

    if document.startswith('---\n'):
        parts = document.split('---\n', 2)
        if len(parts) >= 3:
            front_matter = parts[1].strip()
            content = parts[2].strip()

    try:
        yaml_data = yaml.safe_load(front_matter) if front_matter else {}
    except yaml.YAMLError:
        yaml_data = {}

    option = PageOption()
    for field in fields(option):
        name = field.name
        if name in yaml_data:
            setattr(option, name, yaml_data.pop(name))
    option.styles = yaml_data

    return content, option


def parse_deco(line: str, base_option: PageOption = None) -> PageOption:
    def parse_key_value_string(s: str) -> dict:
        pattern = r'([\"\w-]+)\s*=\s*((?:"(?:[^"\\]|\\.)*"|\"(?:[^"\\]|\\.)*\"|[^,]+))'
        matches = re.findall(pattern, s)

        result = {}
        for key, value in matches:
            if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                value = value[1:-1].replace('\\"', '"').replace("\"", "")
            result[key] = value.strip()

        return result

    deco_match = re.match(r'^\s*@\((.*?)\)\s*$', line)
    if not deco_match:
        raise ValueError(f'Input line should contain a deco, {line} received.')

    deco_content = deco_match.group(1)
    deco = parse_key_value_string(deco_content)

    if base_option is None:
        base_option = PageOption()

    updated_option = deepcopy(base_option)

    for key, value in deco.items():
        if hasattr(updated_option, key):
            setattr(updated_option, key, parse_value(value))
        else:
            updated_option.styles[key] = parse_value(value)

    return updated_option


def parse_value(value: str):
    if value.lower() == 'true':
        return True
    elif value.lower() == 'false':
        return False
    elif value.isdigit():
        return int(value)
    elif value.replace('.', '', 1).isdigit():
        return float(value)
    return value


def composite(document: str) -> List[Page]:
    pages = []
    current_page_lines = []
    current_escaped = False
    current_h1 = current_h2 = current_h3 = None
    prev_header_level = 0

    document = rm_comments(document)
    document, options = parse_frontmatter(document)

    lines = document.split('\n')

    def create_page():
        nonlocal current_page_lines, current_h1, current_h2, current_h3, options
        if all(l.strip() == '' for l in current_page_lines):
            return

        raw_md = ''
        local_option = deepcopy(options)
        for line in current_page_lines:
            if contains_deco(line):
                local_option = parse_deco(line, local_option)
            else:
                raw_md += '\n' + line

        page = Page(raw_md=raw_md, option=local_option, h1=current_h1, h2=current_h2, h3=current_h3)
        pages.append(page)
        current_page_lines = []
        current_h1 = current_h2 = current_h3 = None

    for line in lines:
        if line.strip().startswith('