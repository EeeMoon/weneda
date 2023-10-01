import re


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