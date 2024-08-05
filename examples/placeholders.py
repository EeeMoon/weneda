import asyncio
from weneda import Placeholder



class MyPlaceholder(Placeholder):
    async def replace(self, placeholder: str, depth: int) -> str:
        if placeholder.startswith('upper_'):
            return placeholder.removeprefix('upper_').upper()
        if placeholder == 'name':
            return "Alex"
        

async def main():
    # Example 1: Basic usage
    ph = MyPlaceholder()
    print(await ph.process("{upper_{name}}"))

    # Example 2: Custom identifiers
    custom = MyPlaceholder('$[', ']')
    print(await custom.process("$[upper_$[name]]"))


if __name__ == '__main__':
    asyncio.run(main())