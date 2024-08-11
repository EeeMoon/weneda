[![pypi](https://img.shields.io/pypi/v/weneda)](https://pypi.org/project/weneda)
[![python](https://img.shields.io/badge/python-3.10+-blue)](https://www.python.org/downloads)
[![support](https://img.shields.io/badge/support-yellow)](https://www.buymeacoffee.com/eeemoon)

# Weneda
Modern way to edit and format text.

## Installation
To install this module, run the following command:
```
pip install weneda
```

## Examples
### Placeholders
```python
import asyncio
from weneda import Formatter, placeholder


class MyFormatter(Formatter):
    @placeholder(
        name="upper",
        syntax="upper_<text>",
        pattern=r"upper_(?P<text>.*)"
    )
    async def upper_handler(self, text: str) -> str:
        return text.upper()
    

async def main():
    formatter = MyFormatter()
    result = await formatter.format("Hello {upper_world}")
    print(result) # Hello WORLD


asyncio.run(main())
```
