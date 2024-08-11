from fontTools.ttLib import TTFont


def char_width(char: str, font: str | bytes) -> float:
    """
    Get the character width for given font with size of 64 px.

    Parameters
    ----------
    char: `str`
        Text to calculate length.
    font: `str` | `bytes`
        Font name or bytes-like object.
    """
    if len(char) != 1:
        raise ValueError("'char' should be one-character string")
    
    with TTFont(font) as f:
        glyph_id = f.getBestCmap().get(ord(char), 0)
        return f['hmtx'][glyph_id][0] * (64 / f['head'].unitsPerEm)


def get_width(text: str, font: str | bytes) -> float:
    """
    Get the text width for given font with size of 64 px.

    Parameters
    ----------
    text: `str`
        Text to calculate length.
    font: `str` | `bytes`
        Font name or bytes-like object.
    """
    return sum((char_width(c, font) for c in text))


def has_glyph(char: str, font: str | bytes) -> bool:
    """
    Check if the font has a glyph for the character.

    Parameters
    ----------
    char: `str`
        Character to check.
    font: `str` | `bytes`
        Font name or bytes-like object.
    """
    with TTFont(font) as f:
        return any(
            ord(char) in table.cmap.keys() 
            for table in f['cmap'].tables
        )