from typing import Any
from functools import partial

from .font import get_width, has_glyph


def noun_form(
    amount: int | float, 
    f1: str, 
    f2to4: str, 
    f5to9: str | None = None
) -> str:
    """
    Returns a singular or plural form based on the amount.

    Parameters
    ----------
    amount: `int` | `float`
        Exact amount.
    f1: `str`
        1 item form.
    f2to4: `str`
        2-4 items form. This will also be returned if amount is `float`.
    f5to9: `str` | `None`
        0 and 5-9 items form. If `None`, equals to `f2to4`.

    Examples
    --------
    >>> count = 4
    >>> text = noun_form(count, "груша", "груші", "груш")
    >>> f"{count} {text}"
    '4 груші'
    """
    if not isinstance(amount, int):
        return f2to4
    
    if f5to9 is None:
        f5to9 = f2to4

    last_digit = amount % 10
    second_last_digit = (amount // 10) % 10

    if last_digit == 1 and second_last_digit != 1:
        return f1
    elif 2 <= last_digit <= 4 and second_last_digit != 1:
        return f2to4

    return f5to9


def strfseconds(
    seconds: float, 
    *, 
    join: str = " ", 
    required: tuple[str] = (),
    default: Any = None,
    **periods: str | tuple[str],
) -> str:
    """
    Returns a formatted time string.

    Parameters
    ----------
    seconds: `float`
        Time in seconds.
    join: `str`
        String joiner.
    required: `tuple[str]`
        Identifiers that will be displayed even if they equal zero.
    default: `str`
        Default value if no identifier was used.
    **periods: `str` | `tuple[str]`
        Period formats. If `tuple`, uses `noun_form`. Identifier can be either
        `y`, `mo`, `w`, `d`, `h`, `m`, `s`, `ms`.

    Examples
    --------
    >>> strfseconds(
    ...     4125, 
    ...     required=('d'),
    ...     default="0 год.",
    ...     d="{} дн.", 
    ...     h="{} год.",
    ...     # use 'noun_form' function
    ...     m=("{} хвилина", "{} хвилини", "{} хвилин") 
    ... )
    '0 дн. 1 год. 8 хвилин'
    """        
    weights = {
        'y': 31_556_952,
        'mo': 2_629_746,
        'w': 608_400,
        'd': 86_400,
        'h': 3_600,
        'm': 60,
        's': 1,
        'ms': 0.001
    }
    result = {i: 0 for i in weights}
    current = seconds
    for identifier, weight in weights.items():
        if identifier not in periods:
            continue

        if current > weight:
            result[identifier] = int(current / weight)
            current %= weight

    display_parts = []
    for key, value in periods.items():
        if isinstance(value, (tuple, list)):
            if len(value) == 3:
                value = noun_form(result[key], *value)
            else:
                raise ValueError(f"'{key}' should have 3 values")
            
        if key in result and (key in required or result[key] != 0):
            display_parts.append(value.replace('{}', str(result[key])))
    
    if not display_parts:
        return default

    return join.join(display_parts)


def space_between(
    *items: str, 
    width: int = 2340, 
    space: str = " ", 
    font: str | bytes | None = None
) -> str:
    """
    Distributes space between the strings. Works as CSS `space-between`.

    Parameters
    ----------
    *items: `str`
        Strings to join.
    width: `int`
        Container width. Uses relative points that depends on specified font. 
        One character can have `0-64` length.
        For example, full-screen console window has 10880 width if 'font' is `None`.
    space: `str`
        Placeholder to use between elements.
    font: `str` | `bytes` | `None`
        Font name or bytes-like object.
        If `None`, all characters will have the width of 64 (monospace font).
    """
    if len(items) == 1:
        return items[0]
    
    joined = ''.join(items)
    filled_width = get_width(joined, font) if font else 64 * len(joined)
    ph_width = get_width(space, font) if font else 64
    empty_width = int((width - filled_width) / (len(items) - 1) / ph_width)

    return (space * empty_width).join(items)


def crop(
    text: str, 
    width: int, 
    font: str | bytes | None = None, 
    placeholder: str = "..."
) -> str:
    """
    Crop text if it exceeds the width limit.

    Parameters
    ----------
    text: `str`
        String to trim.
    font: `str` | `bytes` | `None`
        Font name or bytes-like object. 
        If `None`, `width` should be character count, not pixels.
    width: `int`
        Max text width.
    placeholder: `str`
        String to add to the end of the text if it goes beyond.
    """
    _get_width = (
        partial(get_width, font=font) 
        if font else 
        lambda x: len(x)
    )
    text_width = _get_width(text, font)
    ph_width = _get_width(placeholder, font)
    current = text
    
    while text_width + ph_width > width and width > 0:
        current = current[:-1]
        text_width = _get_width(current, font)

    if text == current:
        placeholder = ""

    return current + placeholder


def fix_display(text: str, font: str | bytes, missing: str = '?') -> str:
    """
    Replace unsupported characters by font with placeholder.

    Parameters
    ----------
    text: `str`
        String to validate.
    font: `str` | `bytes`
        Font name or bytes-like object.
    missing: `str`
        Missing character placeholder.
    """
    missing_len = len(missing)
    current = text
    index = 0

    while index < len(current):
        if has_glyph(current[index], font):
            index += 1
        else:
            current = ''.join((
                current[:index],
                missing,
                current[index + 1 :]
            ))
            index += missing_len
          
    return current