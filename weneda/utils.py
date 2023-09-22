from fontTools.ttLib import TTFont


def text_width(string: str, font: str | bytes):
    """
    Returns a text width for given font with size of 64 px.

    ## Attributes
    string: `str`
        Text to calculate length.
        
    font: `str` | `bytes`
        Font name or bytes-like object.
    """
    def chr_width(character: str):
        with TTFont(font) as f:
            glyph_id = f.getBestCmap().get(ord(character), 0)
            
            return f['hmtx'][glyph_id][0] * (64 / f['head'].unitsPerEm)
    
    return sum((chr_width(c) for c in string))
