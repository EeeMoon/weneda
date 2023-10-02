from weneda import placeholder


# Example 1: common usage
@placeholder()
def format_text(ph, **kwargs):
    if ph == "name":
        return "Alice"

text = "Hello, {name}!"
formatted = format_text(text)

print(formatted)
