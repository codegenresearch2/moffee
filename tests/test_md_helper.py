import pytest
from moffee.utils.md_helper import (
    is_comment,
    is_empty,
    get_header_level,
    is_divider,
    contains_image,
    contains_deco,
    extract_title,
    rm_comments,
)


def test_is_comment():
    assert is_comment('<!-- This is a comment -->')
    assert not is_comment('This is not a comment')


def test_is_empty():
    assert is_empty('<!-- This is a comment -->')
    assert is_empty(' ')
    assert is_empty('\n')


def test_get_header_level():
    assert get_header_level('# Header 1') == 1
    assert get_header_level('### Header 3') == 3
    assert get_header_level('Normal text') == 0
    assert get_header_level('####### Not a valid header') == 0


def test_is_divider():
    assert is_divider('---')
    assert is_divider('***')
    assert is_divider('___')
    assert is_divider('  ----  ')
    assert not is_divider('--')
    assert not is_divider('- - -')
    assert not is_divider('This is not a divider')
    assert is_divider('***', type='*')
    assert not is_divider('***', type='-')
    assert not is_divider('* * *', type='*')
    assert is_divider('<->')
    assert is_divider('===')


def test_contains_image():
    assert contains_image('![Alt text](image.jpg)')
    assert contains_image('This is an image: ![Alt text](image.jpg)')
    assert not contains_image('This is not an image')
    assert contains_image('![](image.jpg)')
    assert contains_image('![]()')


def test_contains_deco():
    assert contains_deco('@(layout=split, background=blue)')
    assert contains_deco('  @(layout=default)  ')
    assert not contains_deco('This is not a deco')
    assert not contains_deco('@(key=value) Some text')
    assert contains_deco('@()')


def test_extract_title():
    assert extract_title('# Main Title\nSome content') == 'Main Title'
    assert extract_title('## Secondary Title\nSome content') == 'Secondary Title'
    assert extract_title('# Main Title\n## Secondary Title\nSome content') == 'Main Title'
    assert extract_title('## Secondary Title\n# Main Title\nSome content') == 'Secondary Title'
    assert extract_title('Some content without headings') is None
    assert extract_title('') is None
    assert extract_title('#  Title with spaces  \nContent') == 'Title with spaces'


def multi_strip(text):
    return '\n'.join([t.strip() for t in text.split('\n') if t.strip() != ''])


def test_remove_html_comments():
    markdown = '''\n    # Title\n    <!-- This is a comment -->\n    Normal text.\n    <!--\n    This is a\n    multi-line comment\n    -->\n    More text.\n    '''
    expected = '''\n    # Title\n    Normal text.\n    More text.\n    '''
    assert multi_strip(rm_comments(markdown)) == multi_strip(expected)


def test_remove_single_line_comments():
    markdown = '''\n    # Title\n    %% This is a comment\n    Normal text.\n    %% Another comment\n    More text.\n    '''
    expected = '''\n    # Title\n    Normal text.\n    More text.\n    '''
    assert multi_strip(rm_comments(markdown)) == multi_strip(expected)


def test_remove_all_types_of_comments():
    markdown = '''\n    # Title\n    <!-- HTML comment -->\n    Normal text.\n    %% Single line comment\n    <!--\n    Multi-line\n    HTML comment\n    -->\n    More text.\n    Final text.\n    '''
    expected = '''\n    # Title\n    Normal text.\n    More text.\n    Final text.\n    '''
    assert multi_strip(rm_comments(markdown)) == multi_strip(expected)


def test_no_comments():
    markdown = '''\n    # Title\n    This is a normal Markdown\n    document with no comments.\n    '''
    assert multi_strip(rm_comments(markdown)) == multi_strip(markdown)
