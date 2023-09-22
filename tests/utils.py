import inspect
import asyncio
import functools
from typing import Callable
from datetime import datetime
import re
from PIL import ImageFont
from async_lru import alru_cache
from fontTools.ttLib import TTFont
from functools import lru_cache
import logging

from misc.default import TIMEZONE, DISCORD_FONT_PATH


class DictManager:
    def __init__(self, data: dict) -> None:
        self.__data = data
    
    def get(self, path: str, default = None):
        """
        Get nested value from dict.

        Attributes
        ----------
        path: `str`
            Dot separated path to value. 
            Example: "config.values.0.data"
        
        Returns
        -------
        Value or None if not found.
        """
        path_components = path.split('.')
        current = self.__data.copy()

        for component in path_components:
            if isinstance(current, dict):
                current = current.get(component)
            elif isinstance(current, list):
                try:
                    index = int(component)
                    current = current[index]
                except ValueError:
                    return default
            else:
                return default

        return current
    

class classproperty(property):
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()


def typecheck(func):
    """
    Decorator that checks all parameter types.

    ### Example usage
    ```
    @typecheck
    def foo(text: str, value: int):
        return len(text) + value

    foo("Hello World", 42) # pass
    foo("Welcome", "to party") # raises error
    
    # You can also specify 0 or 2+ types
    @typecheck
    def bar(text, value: int | float):
        return len(text) + value

    bar(value=152.63, text=14) # pass
    bar(value="ex", text=25) # raises error
    ```

    Raises
    ------
    `TypeError` if any parameter is instance of invalid type or if annotation is a parameterized generic.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        for arg_name, arg_value in bound_args.arguments.items():
            expected_type = func.__annotations__.get(arg_name, object)
            
            if not isinstance(arg_value, expected_type):
                raise TypeError(f"Argument '{arg_name}' should be of type '{expected_type.__name__}', not '{type(arg_value).__name__}'")
        
        return func(*args, **kwargs)
    return wrapper


class cachedproperty(property):
    """
    Property with caching mechanism. Class must be hashable.

    ### Example usage:
    ```
    class MyClass:
        def __init__(self):
            self.__var = 0

        @cachedproperty
        def var(self):
            return self.__var
        
        @var.setter
        def var(self, value):
            some_expensive_func()
            self.__var = value
    
    obj = MyClass()

    print(obj.var) # calculate result and set it to cache
    print(obj.var) # use cached result
    obj.var = 12 # clear cache
    print(obj.var) # calculate result and set it to cache
    ```
    """
    __cache: dict = {}

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        
        return self.__wrap_getter(self.fget)(instance)
    
    def __set__(self, instance, value):
        if self.fset is None:
            raise AttributeError("'{0}' is read-only".format(self.fget.__name__))
        
        return self.__wrap_setter(self.fset)(instance, value)

    @staticmethod
    def __get_key(instance, propname):
        return (hash(instance), propname)

    def __wrap_getter(self, func):
        if func is None: return func
        
        @functools.wraps(func)
        def wrapper(self):
            cache_key = cachedproperty.__get_key(self, func.__name__)

            if cache_key in cachedproperty.__cache:
                return cachedproperty.__cache[cache_key]

            result = func(self)

            cachedproperty.__cache[cache_key] = result

            return result
        return wrapper

    def __wrap_setter(self, func):
        if func is None: return func

        @functools.wraps(func)
        def wrapper(self, value):
            cachedproperty.clear(self, func.__name__)

            return func(self, value)
    
        return wrapper
    
    @staticmethod
    def clear(instance: object, propname: str):
        """
        Clear cache entry.

        Attributes
        ----------
        instance: `object`
            Instance of early cached property class.
        propname: `str`
            Name of the property.
        """
        try: 
            del cachedproperty.__cache[cachedproperty.__get_key(instance, propname)]
        except: pass
    

def coro(func: Callable):
    """
    Convert sync function to async.

    ### Example usage:
    ```
    def add(a, b):
        return a + b

    add(5, 24) # call synchronously
    await coro(add)(5, 24) # call asynchronously 
    ```
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
    return wrapper


@typecheck
def to_msg(obj: str | tuple | list):
    """
    Converts object to readable message.

    Attributes
    ----------
    obj: `str` | `tuple` | `list`
        String or iterable. 
    """
    if isinstance(obj, str): return obj

    elif isinstance(obj, (list, tuple)):
        return ''.join(obj)
    

def format_amount(value: int, 
                  first_form: str, 
                  second_form: str, 
                  third_form: str):
    if value < 0:
        value = value * (-1)

    string = str(value)

    if (value == 1):
        return first_form
    
    for i in range(19, -1, -1):
        if (i >= 2 and i <= 4):
            if (string.endswith(str(i))):
                return second_form
            
        if (string.endswith(str(i))):
            return third_form


async def format_time(seconds: int, pattern: dict, splitter = " "):
    """
    Example usage:
    ```
    await format_time(4125, {
        "h": "{h} год.", #1 form
        "m": ("{m} хвилина", "{m} хвилини", "{m} хвилин") #3 forms
        "d": "!{d} дн." #text will be displayed even if it equals zero
    })
    ```
    """
    time_parts = {
        'w': [seconds // (7 * 24 * 3600), "NULL", 1], 
        'd': [(seconds // (24 * 3600)), "w", 7], 
        'h': [(seconds // 3600), "d", 24], 
        'm': [(seconds // 60), "h", 60], 
        's': [seconds, "m", 60]
    }
    for k in time_parts:
        if time_parts[k][1] in pattern:
            time_parts[k][0] = time_parts[k][0] % time_parts[k][2]
    
    display_parts = []
    for key, value in pattern.items():
        if isinstance(value, tuple):
            value: str = await coro(format_amount)(time_parts[key][0], value[0], value[1], value[2])
        if key in time_parts and (time_parts[key][0] != 0 or value.startswith("!")):
            await coro(display_parts.append)(
                value.strip("!").format_map({i: time_parts[i][0] for i in time_parts})
            )
    
    return splitter.join(display_parts)


def strpseconds(time: str):
    time_parts = {
        'w': 604800,
        'd': 86400,
        'h': 3600,
        'm': 60,
        's': 1
    }

    seconds = 0
    timelist = re.split('(\d+)', time.strip())[1:]

    for i in range(0, len(timelist), 2):
        value = int(timelist[i])
        modifier = timelist[i+1]

        if modifier in time_parts:
            seconds += time_parts[modifier]*value

    return seconds


def rgb_to_hex(rgb: tuple[int, int, int]):
    return '{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])


def hex_to_rgb(hex: str):
    return tuple(int(hex.strip('#')[i:i+2], 16) for i in (0, 2, 4))


def nowts(offset: float = 0) -> float:
    """
    Get current timestamp for Kyiv timezone.

    Attributes
    ----------
    offset: `int`
        Offset in seconds from current timestamp.
    """
    return datetime.now(TIMEZONE).timestamp() + offset


class FormatDict(dict):
    def __missing__(self, key):
        return '{' + key + '}'


def ifnot(instance, obj):
    if not isinstance(instance, type(obj)):
        return obj
    
    return instance

async def __re_sub(pattern: str, repl, string: str):
    result = []
    index = 0

    while index < len(string):
        match: re.Match = await coro(re.search)(pattern, string[index:])
        if match:
            result.append(string[index:index + match.start()])
            result.append(str(await repl(match)))
            index += match.end()
        else:
            result.append(string[index:])
            break

    return ''.join(result)


def formatter(brackets: tuple[str, str] = ('{', '}')):
    """
    Converts `format(placeholder: str, data: dict)` 
    method to `format(text: str, data: dict = {})`

    ### Example usage
    ```
    class MyClass:
        @formatter()
        def format(self, placeholder: str, data: dict):
            if placeholder == "name":
                return "Alex"
    
    obj = MyClass()
    obj.format("Hello, {name}! Today is {day}!") # "Hello, Alex! Today is {day}!"
    ```
    """
    def helper(func):
        async def wrapper(self, text: str, data: dict | None = None) -> str:
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
            pattern = re.escape(brackets[0]) + r'(\w+)' + re.escape(brackets[1])

            async def replace(match):
                name = match.group(1)

                replacement = func(self, name, data or {})
                if inspect.iscoroutinefunction(func): replacement = await replacement

                return replacement if replacement else '{' + name + '}'
            
            return await __re_sub(pattern, replace, text)
        return wrapper
    return staticmethod(helper)


def self_formatter(attribute: str, brackets: tuple[str, str] = ('{', '}')):
    def helper(func):
        async def wrapper(self, data: dict | None = None) -> str:
            """
            |coro|

            Formats string with placeholders based on given data.

            Attributes
            ----------
            data: `dict`
                Extra data for placeholders.
            """
            pattern = re.escape(brackets[0]) + r'([^{}]+)' + re.escape(brackets[1])

            cached = {}

            async def format(text):
                async def replace(match):
                    name = match.group(1)

                    if name in cached:
                        return cached[name]
                    
                    try:
                        replacement = func(self, name, data or {})
                        if inspect.iscoroutinefunction(func): 
                            replacement = await replacement
                    except Exception as e:
                        logging.exception(e)
                        replacement = None
                    
                    if replacement is None:
                        replacement = '{' + name + '}'

                    cached[name] = replacement

                    return str(replacement)
                
                return await __re_sub(pattern, replace, text)
            
            result = await format(getattr(self, attribute, ""))
            while True:
                prev = result
                result = await format(result)
                if result == prev: break

            return result

        return wrapper
    return staticmethod(helper)


def space_between(elements: list[str] | tuple[str], 
                  width: int = 2340, 
                  placeholder: str = None, 
                  font: ImageFont.FreeTypeFont = None):
    """
    Fit elements in specified width with spaces between. 
    Footer text length on mobile: 2340
    """
    font = font or ImageFont.truetype(DISCORD_FONT_PATH, 100, layout_engine=ImageFont.Layout.BASIC)
    placeholder = placeholder or " "

    ph_len = (width - font.getlength(''.join(elements))) / (len(elements)-1) / font.getlength(placeholder)
    ph_len = int(ph_len)
    
    result = []
    for e in elements:
        result.append(e)
        result.append(placeholder*ph_len)
    result.pop()

    return ''.join(result)


@lru_cache()
def cropped(text: str, font: ImageFont.FreeTypeFont, max_width: int, placeholder: str = "..."):
    width = font.getlength(text)
    ph_width = font.getlength(placeholder)

    result = text
    
    while width + ph_width > max_width and max_width > 0:
        result = result[:-1]
        width = font.getlength(result)

    if text == result:
        placeholder = ""

    return result + placeholder


@alru_cache()
async def has_glyph(font: ImageFont.FreeTypeFont, glyph: chr):
    tfont = TTFont(font.path)

    for table in tfont['cmap'].tables:
        if await coro(ord)(glyph) in table.cmap.keys():
            return True
    return False


@alru_cache()
async def replace_no_glyph(text: str, font: ImageFont.FreeTypeFont, placeholder: str = "?") -> str:
    """
    text:str - text to format\n
    symbol:chr - symbol to replace with
    """
    result = text
    for let in text:
        if await has_glyph(font, let): continue
        result = await coro(result.replace)(let, placeholder)
          
    return result


class Style:
    def __init__(self,
                 *,
                 foreground: int = 8,
                 background: int = 8,
                 bold: bool = False,
                 underline: bool = False) -> None:
        self._foreground = foreground if foreground in range(9) else 8
        self._background = background if background in range(9) else 8
        self._bold = bold
        self._underline = underline

    def fg(self, color: int):
        self._foreground = color if color in range(7) else 0

    def bg(self, color: int):
        self._background = color if color in range(7) else 0

    def bold(self, enabled: bool = True):
        self._bold = enabled

    def underline(self, enabled: bool = True):
        self._underline = enabled

    def __str__(self) -> str:
        style_codes = []
        if self._bold == False and self._underline == False:
            style_codes.append("0")
        if self._bold:
            style_codes.append("1")
        if self._underline:
            style_codes.append("4")
        style_str = ";".join(style_codes)

        color_str = ""
        if self._foreground is not None:
            color_str += f"38;5;3{self._foreground}"
        if self._background is not None:
            if color_str:
                color_str += ";"
            color_str += f"48;5;4{self._background}"

        if style_str and color_str:
            return f"\033[{style_str};{color_str}m"
        elif style_str:
            return f"\033[{style_str}m"
        elif color_str:
            return f"\033[{color_str}m"
        
        return "\033[0m"
    

def urlify(text: str, default: str | None = None):
    text = re.sub(r"[^\w\sА-Я\Ґ\Є\І\Ї]", '', text)
    
    if not default and len(text.strip().replace('-', '')) == 0:
        return default
    
    text = re.sub(r"\s+", '-', text)
    return text.lower()