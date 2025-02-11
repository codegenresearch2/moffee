import pytest
from moffee.compositor import parse_deco, PageOption

def test_basic_deco():
    line = "@(layout=split, background=blue)"
    option = parse_deco(line)
    assert option.layout == "split"
    assert option.styles == {"background": "blue"}

def test_empty_deco():
    line = "@()"
    option = parse_deco(line)
    assert option == PageOption()

def test_invalid_deco():
    line = "This is not a deco"
    with pytest.raises(ValueError) as exc_info:
        parse_deco(line)
    assert str(exc_info.value) == "Invalid decoration string"

def test_deco_with_base_option():
    line = "@(layout=split, default_h1=true, custom_key=value)"
    base_option = PageOption(
        layout="content", default_h1=False, default_h2=True, default_h3=True
    )
    updated_option = parse_deco(line, base_option)

    assert updated_option.styles == {"custom_key": "value"}
    assert updated_option.layout == "split"
    assert updated_option.default_h1 is True
    assert updated_option.default_h2 is True
    assert updated_option.default_h3 is True

def test_deco_with_type_conversion():
    line = "@(default_h1=true, default_h2=false, layout=centered, custom_int=42, custom_float=3.14)"
    base_option = PageOption()
    updated_option = parse_deco(line, base_option)

    assert updated_option.styles == {"custom_int": 42, "custom_float": 3.14}
    assert updated_option.default_h1 is True
    assert updated_option.default_h2 is False
    assert updated_option.layout == "centered"

def test_deco_with_spaces():
    line = "@(  layout = split,   background = blue  )"
    option = parse_deco(line)
    assert option.layout == "split"
    assert option.styles == {"background": "blue"}

def test_deco_with_quotes():
    line = "@(layout = \"split\",length='34px')"
    option = parse_deco(line)
    assert option.layout == "split"
    assert option.styles == {"length": "34px"}

def test_deco_with_hyphen():
    line = "@(background-color='red')"
    option = parse_deco(line)
    assert option.styles == {"background-color": "red"}

def test_computed_slide_size():
    page_option = PageOption(width=1024, height=768)
    assert page_option.computed_slide_size == (1024, 768)

def test_computed_slide_size_aspect_ratio():
    page_option = PageOption(width=1600, height=900)
    assert page_option.computed_slide_size == (1600, 900)
    assert page_option.aspect_ratio == 1.78

def test_computed_slide_size_default():
    page_option = PageOption()
    assert page_option.computed_slide_size == (1920, 1080)
    assert page_option.aspect_ratio == 1.78

def test_computed_slide_size_incorrect_aspect_ratio():
    with pytest.raises(ValueError):
        PageOption(width=1024, height=768, aspect_ratio=1.5)

def test_computed_slide_size_missing_parameters():
    with pytest.raises(ValueError):
        PageOption(width=1024)

if __name__ == "__main__":
    pytest.main()