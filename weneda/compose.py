import re
from typing import Iterable

from .utils import get_width, has_glyph


def placeholder(li: str = "{", ri: str = "}"):
    """
    Decorator that tranforms a function into a placeholder formatter.

    ## Attributes
    li: `str`
        Left pattern to identificate a placeholder.
        
    ri: `str`
        Right pattern to identificate a placeholder.

    ### Example usage
    ```
    @placeholder()
    def format_text(ph: str, **kwargs):
        if ph == "name":
            return kwargs.get("name", default="someone")
        if ph == "day":
            return "monday"
    
    text = format_text("Hello, {name}! Today is {day}!", name="Alex"}) 
    print(text)
    # Hello, Alex! Today is monday!
    ```
    """
    if not isinstance(li, str) or not isinstance(ri, str):
        raise ValueError("identifiers must be of type 'str'")


    def helper(func):
        def wrapper(text: str, **kwargs) -> str:
            """
            Formats string with placeholders based on given data.

            ## Attributes
            text: `str`
                Text to format.

            kwargs: `dict`
                Extra data for placeholders.
            """
            pattern = re.escape(li) + r'(\w+)' + re.escape(ri)

            def replace(match):
                name = match.group(1)

                replacement = func(name, **kwargs)

                return str(replacement) if replacement else li + name + ri
            
            return re.sub(pattern, replace, text)
        
        wrapper.__name__ = func.__name__
        
        return wrapper
    
    return helper


def form(value: int, 
         singlef: str, 
         doublef: str, 
         quintuplef: str):
    """
    Returns a word form based on the amount.

    ## Attributes
    value: `int`
        Exact amount.

    singlef: `str`
        1 item form.

    doublef: `str`
        2-4 items form.

    quintuplef: `str`
        5-9 items form.

    ### Example usage
    ```
    count = 4
    text = form(count, "груша", "груші", "груш")

    print(f"{count} {text}")
    # 4 груші
    ```
    """
    if value < 0:
        value = -value 

    if value == 1:
        return singlef
    
    for i in range(19, 1, -1):
        if value % 10 == i:
            if (i >= 2 and i <= 4):
                return doublef
            
            return quintuplef


def format_time(seconds: float, pattern: dict, joiner: str = " "):
    """
    Returns a formatted time string.

    ## Attributes
    seconds: `float`
        Time in seconds.

    pattern: `dict`
        Time identifier and display string pairs. `{}` will be replaced by actual value.

    joiner: `str`
        String to join all times by.

    Available keys:
        - `y` - years
        - `mo` - months
        - `w` - weeks
        - `d` - days
        - `h` - hours
        - `m` - minutes
        - `s` - seconds
        - `ms` - milliseconds

    ### Example usage
    ```
    time = ftime(4125, {
        "d": "!{} дн.", # text will be displayed even if it equals zero
        "h": "{} год.", # 1 form
        "m": ("{} хвилина", "{} хвилини", "{} хвилин") # 3 forms
    })
    print(text)
    # 0 дн. 1 год. 8 хвилин
    ```
    """        
    values = {
        "y": 31_556_952,
        "mo": 2_629_746,
        "w": 608_400,
        "d": 86_400,
        "h": 3_600,
        "m": 60,
        "s": 1,
        "ms": 0.001
    }

    result = {i: 0 for i in values}
    current = seconds

    for k, v in values.items():
        if k not in pattern:
            continue

        if current > v:
            result[k] = int(current / v)
            current %= v

    display_parts = []

    for key, value in pattern.items():
        if isinstance(value, (tuple, list)):
            if len(value) == 3:
                value: str = form(result[key], *value)
            else:
                raise ValueError(f"{key} must have 3 forms instead of {len(value)}")
            
        if key in result and (result[key] != 0 or value.startswith("!")):
            display_parts.append(value.strip("!").replace("{}", str(result[key])))

    return joiner.join(display_parts)


def space_between(items: Iterable[str], 
                  width: int = 2340, 
                  space: str = " ", 
                  font: str | bytes | None = None):
    """
    Distributes space between the strings. Works as CSS space-between.

    ## Attributes
    items: `Iterable[str]`
        List of strings.
        
    width: `int`
        Container width. Uses relative points that depends on specified font. 
        One character can have `0-64` length.
        For example, console full-screen window has 10880 width with `font = None`.
        Discord embed footer has 2340 width with `ggsans font`.

    space: `str`
        Placeholder to use between elements.

    font: `str` | `bytes` | `None`
        Font name or bytes-like object.
        If `None`, all characters will have width of 64 (monospace font).
    """
    if len(items) == 1:
        return items[0]
    
    joined = ''.join(items)
    
    el_space = get_width(joined, font) if font else 64*len(joined)
    ph_space = get_width(space, font) if font else 64

    ph_len = int((width - el_space) / (len(items)-1) / ph_space)

    return (space*ph_len).join(items)


def crop_text(text: str, font: str | bytes, max_width: int, placeholder: str = "...") -> str:
    ph_width = get_width(placeholder, font)
    text_width = get_width(text, font)

    if text_width <= max_width:
        return text

    left = 0
    right = len(text)

    while left < right:
        mid = (left + right) // 2
        current_width = get_width(text[:mid], font)
        current_width += ph_width

        if current_width <= max_width:
            left = mid + 1
        else:
            right = mid

    crop_point = left

    if crop_point == len(text):
        placeholder = ""

    return text[:crop_point] + placeholder


def replace_no_glyph(text: str, font: str, placeholder: chr = "?") -> str:
    """
    Replaces unsupported characters by font with placeholder.

    Atrtibutes
    ----------
    text: `str`
        String to validate.
    """
    for i, char in enumerate(text):
        if has_glyph(char, font): 
            continue

        text[i] = placeholder
          
    return text


def urlify(text: str):
    return re.sub(r"\s+", '-', text.lower())
