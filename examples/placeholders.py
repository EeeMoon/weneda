import asyncio
from weneda import placeholder, aplaceholder


# Example 1: common usage
@placeholder()
def format_text(ph: str, **kwargs):
    if ph == "name":
        return kwargs.get("name", "someone")

text = "Hello, {name}!"

formatted = format_text(text, name="Alice")
print("Example 1.1:", formatted) # Hello, Alice!

formatted = format_text(text)
print("Example 1.2:", formatted) # Hello, someone!


# Example 2: custom identifiers
@placeholder('((', '))')
def format_text(ph: str, **kwargs):
    if ph == "amount":
        return kwargs.get("amount", 0)

text = "This costs ((amount))$"

formatted = format_text(text, amount=15)
print("Example 2.1:", formatted) # This costs 15$


# Example 3: nested placeholders
@placeholder()
def format_text(ph: str, **kwargs):
    if ph.startswith("num"):
        return kwargs.get(ph, 0)
    
    if ph.startswith("sum_"):
        action, *nums = ph.split("_")
        return sum((int(i) for i in nums))

text = "{num1} + {num2} = {sum_{num1}_{num2}}"

formatted = format_text(text, num1=3, num2=4)
print("Example 3.1:", formatted) # 3 + 4 = 7

text = "{num1} + {num2} + {5} + {num3} = {sum_{num1}_{num2}_{5}_{num3}}"

formatted = format_text(text, num1=3, num2=4, num3=2)
print("Example 3.2:", formatted) # 3 + 4 + 5 + 2 = 14


# Example 4: async formatter
@aplaceholder()
async def format_text(ph: str, **kwargs):
    if ph == "name":
        return kwargs.get("name", "someone")

async def main():
    text = "Hello, {name}!"

    formatted = await format_text(text, name="Bob")
    print("Example 4.1:", formatted) # Hello, Bob!

asyncio.run(main())