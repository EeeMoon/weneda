from fontTools.ttLib import TTFont

# Load your TrueType or OpenType font file
font = TTFont("ggsans-Semibold.ttf")

# Specify the text string you want to measure
text = "M"

# Define the font size (in points)
font_size = 64

# Get the font's unitsPerEm value
units_per_em = font['head'].unitsPerEm

# Create an empty list to store the advance widths of each character
advance_widths = []

# Iterate through each character in the text
for char in text:
    # Get the Unicode code point of the character
    code_point = ord(char)
    
    # Get the glyph ID for the character
    glyph_id = font.getBestCmap().get(code_point, 0)
    
    # Get the advance width of the glyph
    advance_width = font['hmtx'][glyph_id][0] * (font_size / units_per_em)
    
    advance_widths.append(advance_width)

# Calculate the total text length by summing the advance widths
text_length = sum(advance_widths)

print(f"Text Length (with 1/64 precision): {text_length} pixels")
