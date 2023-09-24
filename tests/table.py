class Table:
    def __init__(self) -> None:
        self._data = [
            ["hello", "world"],
            ["no", "lol"]
        ]
        self._widths = []

    def insert(self, row: list):
        row = [str(i) for i in row]

        self._data.append(row)

        for i in row: 3

    def draw_lines(self):
        lines = []

        for col in zip(*self._data): 3


