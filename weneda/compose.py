import inspect
import functools

from .utils import get_width


def placeholder(opener: str = "{", closer: str = "}"):
    """
    Decorator that transforms a function or coroutine into a placeholder formatter.
    Function can have as many `args` and `kwargs` you want, 
    but first argument must be a placeholder string.

    Attributes
    ----------
    opener: `str`
        Identifies a placeholder start.
    closer: `str`
        Identifies a placeholder end.

    ### Example usage
    ```
    @placeholder()
    def greetings(ph: str, *, name: str | None = None) -> str:
        if ph == "name":
            return name or "someone"
        if ph == "day":
            return "Monday"

    text = greetings("Hello, {name}! Today is {day}!", name="Alex")

    print(text) # Hello, Alex! Today is Monday!
    ```
    """
    if not isinstance(opener, str) or not isinstance(closer, str):
        raise ValueError("identifiers must be of type 'str'")

    opener_len = len(opener)
    closer_len = len(closer)

    def helper(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> str:
            is_method = True
            if isinstance(args[0], str):
                is_method = False

            text: str = args[1] if is_method else args[0]
            stack = []
            index = 0

            while index < len(text):
                if text[index : index + opener_len] == opener:
                    stack.append(index)
                    index += opener_len
                elif text[index : index + closer_len] == closer:
                    if stack:
                        start_index = stack.pop()
                        ph = text[start_index + opener_len : index]

                        value = func(ph, *args[2 if is_method else 1:], **kwargs)
                        if inspect.iscoroutinefunction(func):
                            value = await value

                        replacement = str(value) if value is not None else opener + ph + closer
                        text = text[:start_index] + replacement + text[index + closer_len:]

                        index = start_index + len(replacement)
                    else:
                        index += closer_len
                else:
                    index += 1

            return text

        return wrapper

    return helper


def noun_form(amount: float, f1: str, f2to4: str, f5to9: str):
    """
    Returns a singular or plural form based on the amount.

    Attributes
    ----------
    amount: `float`
        Exact amount.
    f1: `str`
        1 item form.
    f2to4: `str`
        2-4 items form. This also will be returned if amount is `float`.
    f5to9: `str`
        0, 5-9 items form.

    ### Example usage
    ```
    count = 4
    text = form(count, "груша", "груші", "груш")

    print(f"{count} {text}") # 4 груші
    ```
    """
    if not isinstance(amount, int):
        return f2to4
    
    amount = abs(amount)

    last_digit = amount % 10
    second_last_digit = (amount // 10) % 10

    if last_digit == 1 and second_last_digit != 1:
        return f1
    elif 2 <= last_digit <= 4 and second_last_digit != 1:
        return f2to4

    return f5to9


def strfseconds(seconds: float, *, join: str = " ", **periods: str):
    """
    Returns a formatted time string.

    Attributes
    ----------
    seconds: `float`
        Time in seconds.
    **periods
        Identifier: format pairs.

    Indentifiers:
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
    text = strfseconds(
        4125, 
        # text will be displayed even if it equals zero
        d="!{} дн.", 
        h="{} год.",
        # equals to noun_form(minutes, "{} хвилина", "{} хвилини", "{} хвилин")
        m=("{} хвилина", "{} хвилини", "{} хвилин") 
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

    for k, v in values.items():
        if k not in periods:
            continue

        if current > v:
            result[k] = int(current / v)
            current %= v

    display_parts = []

    for key, value in periods.items():
        if isinstance(value, (tuple, list)):
            if len(value) == 3:
                value: str = noun_form(result[key], *value)
            else:
                raise ValueError(f"{key} must have 3 forms instead of {len(value)}")
            
        if key in result and (result[key] != 0 or value.startswith("!")):
            display_parts.append(value.removeprefix("!").replace("{}", str(result[key])))

    return join.join(display_parts)


def space_between(
    *items: str, 
    width: int = 2340, 
    space: str = " ", 
    font: str | bytes | None = None
):
    """
    Distributes space between the strings. Works as CSS `space-between`.

    Attributes
    ----------
    *items: `str`
        Strings to join.
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
    filled_width = get_width(joined, font) if font else 64 * len(joined)
    ph_width = get_width(space, font) if font else 64
    empty_width = int((width - filled_width) / (len(items) - 1) / ph_width)

    return (space * empty_width).join(items)


def crop(text: str, font: str | bytes, width: int, placeholder: str = "..."):
    """
    Crop text if it exceeds the width limit.

    Attributes
    ----------
    text: `str`
        String to trim.
    font: `str` | `bytes`
        Font name or bytes-like object.
    width: `int`
        Max text width.
    placeholder: `str`
        String to add to the end of the text if it goes beyond.
    """
    text_width = get_width(text, font)
    ph_width = get_width(placeholder, font)
    result = text
    
    while text_width + ph_width > width and width > 0:
        result = result[:-1]
        text_width = get_width(result, font)

    if text == result:
        placeholder = ""

    return result + placeholder