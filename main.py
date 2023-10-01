import asyncio
import re
import inspect




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
            pattern = re.escape(li) + r'(\w+)' + re.escape(ri)

            def replace(match):
                name = match.group(1)

                replacement = func(name, **kwargs)

                return str(replacement) if replacement else li + name + ri
            
            return re.sub(pattern, replace, text)
        
        wrapper.__name__ = func.__name__
        
        return wrapper
    
    return staticmethod(helper)



@placeholder()
def format_greeting(ph: str, **kwargs):
    if ph.startswith("user_"):
        return "hello " + ph.removeprefix("user_")
    if ph == "name":
        return "ALice"


async def main():
    greeting = await format_greeting("text:   {user_{name}_hellow}!")
    print(greeting)

# Run the main asynchronous function
asyncio.run(main())