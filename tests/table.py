from collections.abc import Iterator
import re


#TODO move to utils
class ExceptDict(dict):
    def __init__(self, value) -> None:
        self.value = value

    def __getitem__(self, __key: object):
        try:
            res = super().__getitem__(__key)
        except:
            res = self.value

        return res
    

class AlwaysIn(list):
    def __contains__(self, __key: object) -> bool:
        return True


class Item:
    def __init__(self,
                 content: str,
                 align: str = 'l') -> None:
        self.align: str = align

        self._from_content(content)

    def _from_content(self, content):
        ansi_pattern = r'\033\[[0-9;]*m'

        self.colors: dict[int, str] = {match.start(): match.group() for match in re.finditer(ansi_pattern, content)}
        self.content: str = re.sub(ansi_pattern, '', content.replace('\n', ''))

    def formatted(self):
        content_list = list(self.content)

        for i in self.colors:
            content_list.insert(i, self.colors[i])

        return ''.join(content_list)
    
    def copy(self, content: str):
        new = Item(content, self.align)
        new.colors = self.colors
        return new


class Table:
    def __init__(self, col_widths: int | list[int] | dict[int, int] | None = None) -> None:
        self._rows: list[list[Item]] = []
        self._chars: list[str] = [' ', '-', '|', '+']
        self._num_cols: int = 0

        if isinstance(col_widths, int):
            self._col_widths = ExceptDict(max(1, col_widths))
            self._fixed_widths = AlwaysIn()

        elif isinstance(col_widths, list):
            self._fixed_widths = range(len(col_widths))
            self._col_widths = {i: int(col_widths[i]) for i in self._fixed_widths}

        elif isinstance(col_widths, dict):
            self._col_widths = {int(i): int(col_widths[i]) for i in col_widths}
            self._fixed_widths = list(col_widths.keys())

        elif col_widths is None:
            self._col_widths = ExceptDict(0)
            self._fixed_widths = []

        else:
            raise ValueError("attribute 'col_widths' is of unsupported type")

    def __getitem__(self, key: int):
        return [i.content for i in self._rows[key]]

    def _fit_cols(self, items: list[Item]):
        result = []

        for num, item in enumerate(items):
            content = item.content
            width = self._col_widths.get(num, 0)

            if width <= 0:
                result.append([item.copy(content)])
            else:
                result.append(
                    [item.copy(content[i:i+width]) for i in range(0, len(content), width)]
                )

        result = [
            sublist + [Item('')] * (max(len(sublist) for sublist in result) - len(sublist)) 
            for sublist in result
        ]

        return [list(row) for row in zip(*result)]

    def set_deco(self, chars: list):
        self._chars = chars
 
    def add_row(self, items: list):
        row_items = [Item(str(i)) for i in items]

        self._rows.append(row_items)

        # update max items widths
        for num, item in enumerate(row_items):
            item_width = len(item.content)

            if isinstance(self._col_widths, ExceptDict):
                self._col_widths[num] = self._col_widths.value
            elif (item_width > self._col_widths.get(num, 0) 
                and num not in self._fixed_widths):
                self._col_widths[num] = item_width

        self._num_cols = max((len(i) for i in self._rows))

        for row in self._rows:
            if len(row) < self._num_cols:
                row += [Item('')] * (self._num_cols - len(row))

    def draw_lines(self):
        lines = []
        n_rows = len(self._rows)
        ph_c, hz_c, vt_c, cr_c = self._chars

        for num_row, row in enumerate(self._rows):
            border = cr_c.join(hz_c * self._col_widths[w] for w in sorted(self._col_widths)[:self._num_cols])
            inner_border = vt_c + border + vt_c
            outer_border = cr_c + border + cr_c

            if num_row == 0 and border != "":
                lines.append(outer_border)

            for new_row in self._fit_cols(row):
                line_items = []

                for num_item, item in enumerate(new_row):
                    content = item.formatted()
                    free = max(0, self._col_widths.get(num_item, 0) - len(item.content))

                    if item.align == "r":
                        content = ph_c * free + content
                    elif item.align == "c":
                        left_padding = free // 2
                        right_padding = free - left_padding
                        content = ph_c * left_padding + content + ph_c * right_padding
                    else:
                        content += ph_c * free

                    line_items.append(content)

                lines.append(vt_c + vt_c.join(line_items) + vt_c)

            if num_row + 1 < n_rows and border != "":
                lines.append(inner_border)

            elif num_row + 1 == n_rows and border != "":
                lines.append(outer_border)

        return lines

    def draw(self):
        return '\n'.join(self.draw_lines())
