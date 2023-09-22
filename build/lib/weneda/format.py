import re

from .utils import text_width


def placeholder(left: str = "{", right: str = "}"):
    """
    Decorator that tranforms a function into a placeholder formatter.

    ## Attributes
    left: `str`
        Left character to identificate a placeholder.
    right: `str`
        Right character to identificate a placeholder.

    ### Example usage
    ```
    class MyClass:
        @placeholder()
        def format(self, ph: str, data: dict):
            if ph == "name":
                return data.get("name")
            if ph == "day":
                return "monday"
    
    obj = MyClass()
    text = obj.format("Hello, {name}! Today is {day}!", {"name": "Alex"}) 
    print(text)
    # Hello, Alex! Today is monday!
    ```
    """
    if not isinstance(left, str) or not isinstance(right, str):
        raise ValueError("identifiers must be of type 'str'")


    def helper(func):
        def wrapper(self, text: str, data: dict | None = None) -> str:
            """
            |coro|

            Formats string with placeholders based on given data.

            Attributes
            ----------
            text: `str`
                Text to format.
            data: `dict`
                Extra data for placeholders.
            """
            pattern = re.escape(left) + r'(\w+)' + re.escape(right)

            def replace(match):
                name = match.group(1)

                replacement = func(self, name, data or {})

                return replacement if replacement else left + name + right
            
            return re.sub(pattern, replace, text)

        return wrapper
    
    return staticmethod(helper)


def get_form(value: int, 
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
    Returns a string form of the time.

    ## Attributes
    seconds: `float`
        Time in seconds.
    pattern: `dict`
        Time identifier and display string pairs. `{}` will be replaced by actual value.
    joiner: `str`
        String to join all times by.

    Available keys:
        - `y` - years
        - `m` - months
        - `w` - weeks
        - `d` - days
        - `H` - hours
        - `M` - minutes
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
        "m": 2_629_746,
        "w": 608_400,
        "d": 86_400,
        "H": 3_600,
        "M": 60,
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
                value: str = get_form(result[key], *value)
            else:
                raise ValueError(f"{key} must have 3 forms instead of {len(value)}")
            
        if key in result and (result[key] != 0 or value.startswith("!")):
            display_parts.append(value.strip("!").replace("{}", str(result[key])))

    return joiner.join(display_parts)


def space_between(elements: list[str] | tuple[str], 
                  width: int = 2340, 
                  placeholder: str = " ", 
                  font: str | bytes | None = None):
    el_space = text_width(''.join(elements), font) if font else 64*len(''.join(elements))
    ph_space = text_width(placeholder, font) if font else 64

    ph_len = int((width - el_space) / (len(elements)-1) / ph_space)

    return (placeholder*ph_len).join(elements)
