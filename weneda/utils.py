import re
from fontTools.ttLib import TTFont


def get_width(text: str, font: str | bytes) -> int:
    """
    Returns a text width for given font with size of 64 px.

    Attributes
    ----------
    string: `str`
        Text to calculate length.
        
    font: `str` | `bytes`
        Font name or bytes-like object.
    """
    def chr_width(character: str):
        with TTFont(font) as f:
            glyph_id = f.getBestCmap().get(ord(character), 0)
            
        return f['hmtx'][glyph_id][0] * (64 / f['head'].unitsPerEm)
    
    return sum((chr_width(c) for c in text))


def has_glyph(char: chr, font: str | bytes) -> bool:
    """
    Checks if the font has a glyph for the character.

    Attributes
    ----------
    character: `chr`
        Character to check.

    font: `str` | `bytes`
        Font name or bytes-like object.
    """
    with TTFont(font) as f:
        checks = (ord(char) in table.cmap.keys() for table in f['cmap'].tables)

    return any(checks)


def fix_display(text: str, font: str, placeholder: chr = "?") -> str:
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


def urlify(text: str) -> str:
    """
    Converts the string to readable URL version.

    Attributes
    ----------
    text: `str`
        String to format.

    ### Example usage
    ```
    text = urlify("Hello, world!")

    print(text) # hello-world
    ```
    """
    return re.sub(r'[^a-zA-Z0-9]+', '-', text).strip('-').lower()
