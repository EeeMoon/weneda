import asyncio
from colorama import Fore, init
from weneda import Formatter, placeholder, PlaceholderData


class MyFormatter(Formatter):
    @placeholder(
        name="upper",
        pattern=r"upper_(?P<text>.*)"
    )
    async def upper_handler(self, text: str) -> str:
        return text.upper()
    
    @placeholder(
        name="repeat",
        pattern=r"repeat_(?P<num>\d+)_(?P<text>.*)"
    )
    async def repeat_handler(self, num: int, text: str) -> str:
        return text * num
    
    @placeholder(
        name="join",
        pattern=r"join_(?P<joiner>[^_]+)_(?P<text>.*)"
    )
    async def join_handler(self, joiner: str, text: str) -> str:
        return joiner.join(text.split('_'))


class ColorFormatter(Formatter):
    def __init__(self) -> None:
        super().__init__()

        self.colors = [Fore.YELLOW, Fore.MAGENTA, Fore.BLUE]

    @placeholder(name="color")
    async def color_handler(self, data: PlaceholderData) -> str:
        raw = data.raw
        depth = data.depth
        color = self.colors[depth % len(self.colors)] 
        last_color = (
            Fore.RESET 
            if depth == 0 else 
            self.colors[(depth-1) % len(self.colors)]
        )

        return ''.join((
            color,
            self.opener,
            raw,
            color,
            self.closer,
            last_color
        ))


async def main() -> None:
    init()

    my_formatter = MyFormatter()
    color_formatter = ColorFormatter()

    texts = [
        ("Upper: {upper_hello}", my_formatter),
        ("Repeat: {repeat_5_{upper_world}}", my_formatter),
        ("Join: {join_!_{repeat_2_{upper_world}}_{repeat_2_{upper_world}}}", my_formatter),
        ("Color: {join_!_{repeat_2_{upper_world}}_{repeat_2_{upper_world}}}", color_formatter)
    ]

    for text, formatter in texts:
        res = await formatter.format(text)
        print(res)


if __name__ == '__main__':    
    asyncio.run(main())
