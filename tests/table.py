class Item:
    def __init__(self,
                 content: str,
                 align: chr = 'c') -> None:
        self.content: str = content
        self.align: chr = align


class Table:
    def __init__(self) -> None:
        self._rows: list[list[Item]] = []
        self._col_widths: dict = {}
        self._width: int = 0
        self._chars: list[chr] = [' ', '-', '|', '+']

    def add_row(self, items: list):
        row_items = [Item(str(i).replace('\n', '')) for i in items]

        self._rows.append(row_items)

        # update max items widths
        for num, item in enumerate(row_items):
            item_width = len(item.content)

            if item_width > self._col_widths.get(num, 0):
                self._col_widths[num] = item_width

                if item.content.startswith('\033'):
                    self._col_widths[num] -= 5

        max_row_width = max((len(i) for i in self._rows))

        for items in self._rows:
            if len(items) < max_row_width:
                items += [Item('')] * (max_row_width - len(items))

    def draw_lines(self):
        lines = []

        n_rows = len(self._rows)

        ph_c, hz_c, vt_c, cr_c = self._chars

        for num_row, row in enumerate(self._rows):
            line_items = []

            for num_item, item in enumerate(row):
                content = item.content
                col_width = self._col_widths.get(num_item, 0)
                free = max(0, col_width - len(content))

                if item.align == "r":
                    content = ph_c * free + content
                elif item.align == "c":
                    left_padding = free // 2
                    right_padding = free - left_padding
                    content = ph_c * left_padding + content + ph_c * right_padding
                else:
                    content += ph_c * free

                line_items.append(content)

            line = vt_c + vt_c.join(line_items) + vt_c

            border = cr_c.join(hz_c * len(li) for li in line_items)
            inner_border = vt_c + border + vt_c
            outer_border = cr_c + border + cr_c

            if num_row == 0 and border != "":
                lines.append(outer_border)

            lines.append(line)

            if num_row + 1 < n_rows and border != "":
                lines.append(inner_border)

            elif num_row + 1 == n_rows and border != "":
                lines.append(outer_border)

        return lines

    def draw(self):
        return '\n'.join(self.draw_lines())
