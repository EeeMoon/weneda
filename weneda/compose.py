import re
from typing import Iterable

from .utils import get_width


def placeholder(li: str = "{", ri: str = "}"):
    """
    Decorator that tranforms a function into a placeholder formatter.

    Attributes
    ----------
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

    print(text) # Hello, Alex! Today is monday!
    ```
    """
    if not isinstance(li, str) or not isinstance(ri, str):
        raise ValueError("identifiers must be of type 'str'")


    def helper(func):
        def wrapper(text: str, **kwargs) -> str:
            """
            Formats string with placeholders based on given data.

            Attributes
            ----------
            text: `str`
                Text to format.

            kwargs: `dict`
                Extra data for placeholders.
            """
            pattern = re.compile(re.escape(li) + r'(\w+)' + re.escape(ri))

            def replace(match):
                placeholder = match.group(1)
                replacement = func(placeholder, **kwargs)

                return (str(replacement).replace(li, '').replace(ri, '') 
                        if replacement is not None else placeholder)
            
            while True:
                match = pattern.search(text)
                if not match: break

                replacement = replace(match)
                
                start, end = match.start(), match.end()
                text = text[:start] + replacement + text[end:]
                
            return text
            
        wrapper.__name__ = func.__name__
        return wrapper
    
    return staticmethod(helper)


def aplaceholder(li: str = "{", ri: str = "}"):
    """
    Decorator that tranforms a coroutine function into a placeholder formatter.

    Attributes
    ----------
    li: `str`
        Left pattern to identificate a placeholder.
        
    ri: `str`
        Right pattern to identificate a placeholder.

    ### Example usage
    ```
    @placeholder()
    async def format_text(ph: str, **kwargs):
        if ph == "name":
            return kwargs.get("name", default="someone")
        if ph == "day":
            return "monday"
    
    text = await format_text("Hello, {name}! Today is {day}!", name="Alex"}) 

    print(text) # Hello, Alex! Today is monday!
    ```
    """
    if not isinstance(li, str) or not isinstance(ri, str):
        raise ValueError("identifiers must be of type 'str'")


    def helper(func):
        async def wrapper(text: str, **kwargs) -> str:
            """
            |coro|

            Formats string with placeholders based on given data.

            Attributes
            ----------
            text: `str`
                Text to format.

            kwargs
                Extra data for placeholders.
            """
            pattern = re.compile(re.escape(li) + r'(\w+)' + re.escape(ri))

            async def replace(match):
                placeholder = match.group(1)
                replacement = await func(placeholder, **kwargs)

                return (str(replacement).replace(li, '').replace(ri, '') 
                        if replacement is not None else placeholder)
            
            while True:
                match = pattern.search(text)
                if not match: break

                replacement = await replace(match)
                
                start, end = match.start(), match.end()
                text = text[:start] + replacement + text[end:]
                
            return text
            
        wrapper.__name__ = func.__name__
        return wrapper
    
    return staticmethod(helper)


def noun_form(amount: int, f1: str, f2to4: str, f5to9: str):
    """
    Returns a singular or plural form based on the amount.

    Attributes
    ----------
    amount: `int`
        Exact amount.

    f1: `str`
        1 item form.

    f2to4: `str`
        2-4 items form.

    f5to9: `str`
        0, 5-9 items form.

    ### Example usage
    ```
    count = 4
    text = form(count, "груша", "груші", "груш")

    print(f"{count} {text}") # 4 груші
    ```
    """
    amount = abs(amount)

    if amount == 0:
        return f5to9
    
    if amount == 1:
        return f1
    
    for i in range(19, 1, -1):
        if amount % 10 == i:
            if (2 <= i and i <= 4):
                return f2to4
            
            return f5to9


def format_time(seconds: float, **kwargs: dict):
    """
    Returns a formatted time string.

    Attributes
    ----------
    seconds: `float`
        Time in seconds.

    kwargs
        Time format per indentifier or additional settings.

    Indentifiers:
        - `y` - years
        - `mo` - months
        - `w` - weeks
        - `d` - days
        - `h` - hours
        - `m` - minutes
        - `s` - seconds
        - `ms` - milliseconds
    Settings:
        - `join` - string to join with

    ### Example usage
    ```
    text = format_time(4125, 
        d="!{} дн.", # text will be displayed even if it equals zero
        h="{} год.", # 1 form
        m=("{} хвилина", "{} хвилини", "{} хвилин") # 3 forms (uses noun_form())
    )
    print(text) # 0 дн. 1 год. 8 хвилин
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
    joiner = kwargs.get('join', ' ')

    for k, v in values.items():
        if k not in kwargs:
            continue

        if current > v:
            result[k] = int(current / v)
            current %= v

    display_parts = []

    for key, value in kwargs.items():
        if isinstance(value, (tuple, list)):
            if len(value) == 3:
                value: str = noun_form(result[key], *value)
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

    Attributes
    ----------
    items: `Iterable[str]`
        List of strings.
        
    width: `int`
        Container width. Uses relative points that depends on specified font. 
        One character can have `0-64` length.
        For example, console full-screen window has 10880 width if 'font' is `None`.

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


