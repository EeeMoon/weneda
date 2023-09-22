from fontTools.ttLib import TTFont

def text_width(string: str, font_path: str | bytes):
    def chr_width(character: str):
        with TTFont(font_path) as f:
            cmap = f.getBestCmap()
            glyph_name = cmap.get(ord(character))
            if glyph_name:
                glyph = f['glyf'][glyph_name]
                return (glyph.xMax - glyph.xMin) // 10
            else:
                return 0
    
    return sum((chr_width(c) for c in string))
