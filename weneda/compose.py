from .utils import get_width


class Placeholder:
    """
    Base class for placeholders.

    ### Example usage
    ```
    class MyPlaceholder(Placeholder):
        async def replace(self, placeholder: str, depth: int) -> str:
            if placeholder.startswith('upper_'):
                return placeholder.removeprefix('upper_').upper()
            

    ph = MyPlaceholder()
    await ph.process("{upper_hello}") # HELLO
    ```
    """
    def __init__(self, opener: str = '{', closer: str = '}') -> None:
        """
        Parameters
        ----------
        opener: `str`
            Left placeholder identifier.
        closer: `str`
            Right placeholder identifier.
        """
        self.opener: str = opener
        self.closer: str = closer

    async def replace(self, placeholder: str, depth: int) -> str:
        """
        Replace the placeholder with the value.

        Parameters
        ----------
        placeholder: `str`
            Placeholder without identifiers.
        depth: `int`
            Nested level. Starts with `0`. 
        """
        raise NotImplementedError()

    async def process(self, text: str) -> str:
        """
        Process a text with placeholders.

        Parameters
        ----------
        text: `str`
            Text.
        """
        opener_len = len(self.opener)
        closer_len = len(self.closer)

        stack = []
        cache = {}
        index = 0
        while index < len(text):
            if text[index : index + opener_len] == self.opener:
                # track open braces
                stack.append(index)
                index += opener_len
            elif text[index : index + closer_len] == self.closer:
                # are there open braces?
                if stack:
                    start_index = stack.pop()
                    ph = text[start_index + opener_len : index]
                    
                    # get placeholder value from cache if exist
                    replacement = cache.get(ph)
                    if replacement is None:
                        value = await self.replace(ph, len(stack))
         
                        # if value is None keep placeholder
                        replacement = (
                            str(value) 
                            if value is not None else 
                            self.opener + ph + self.closer
                        )
                        cache[ph] = replacement
                    
                    # replace actual placeholder
                    text = text[:start_index] + replacement + text[index + closer_len:]
                    index = start_index + len(replacement)
                else:
                    index += closer_len
            else:
                index += 1

        return text


def noun_form(amount: float, f1: str, f2to4: str, f5to9: str) -> str:
    """
    Returns a singular or plural form based on the amount.

    Parameters
    ----------
    amount: `float`
        Exact amount.
    f1: `str`
        1 item form.
    f2to4: `str`
        2-4 items form. This also will be returned if amount is `float`.
    f5to9: `str`
        0 and 5-9 items form.

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


def strfseconds(
    seconds: float, 
    *, 
    join: str = " ", 
    required: tuple[str] = (),
    empty: str = "",
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
    **periods: `str` | `tuple[str]`
        Period formats. If `tuple`, uses `noun_form`. Identifier can be either
        `y`, `mo`, `w`, `d`, `h`, `m`, `s`, `ms`.

    ### Example usage
    ```
    text = strfseconds(
        4125, 
        required=('d'),
        empty="0 год.",
        d="{} дн.", 
        h="{} год.",
        # uses noun_form(minutes, "{} хвилина", "{} хвилини", "{} хвилин")
        m=("{} хвилина", "{} хвилини", "{} хвилин") 
    )
    print(text) # 0 дн. 1 год. 8 хвилин
    ```
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
                raise ValueError(f"'{key}' must have 3 forms instead of {len(value)}")
            
        if key in result and (key in required or result[key] != 0):
            display_parts.append(value.replace('{}', str(result[key])))
    
    if not display_parts:
        return empty

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
        If `None`, all characters will have width of 64 (monospace font).
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
    font: str | bytes, 
    width: int, 
    placeholder: str = "..."
) -> str:
    """
    Crop text if it exceeds the width limit.

    Parameters
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