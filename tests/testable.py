from math import ceil

class Item:
    def __init__(self, content):
        self.content = content


def split_columns(items: list[Item], widths: dict[int, int]):
    result = []

    for num, item in enumerate(items):
        content = item.content
        width = widths.get(num, 0)

        if width <= 0:
            result.append([content])
        else:
            result.append(
                [content[i:i+width] for i in range(0, len(content), width)]
            )

    result = [
        sublist + [''] * (max(len(sublist) for sublist in result) - len(sublist)) 
        for sublist in result
    ]

    return [list(row) for row in zip(*result)]



items = [Item("first"), Item("second"), Item("longestttext")]
max_widths = {0: 4, 2: 3}

result = split_columns(items, max_widths)

print(result)
