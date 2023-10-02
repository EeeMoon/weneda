from itertools import cycle
from weneda import FG, BG, ST


# Example 1
text = FG.RED + "red text " + BG.YELLOW + "on yellow bg" + ST.RESET
print("Example 1:", text)


# Example 2
text = FG.BLUE + ST.BOLD + "blue bold text" + ST.RESET
print("Example 2:", text)


# Example 3
text = "rainbow text on white bg"
colors = cycle((FG.RED, FG.YELLOW, FG.GREEN, FG.CYAN, FG.BLUE, FG.MAGENTA))

result = [next(colors) + i for i in text]
result.insert(0, BG.WHITE)
result.append(ST.RESET)

print("Example 3:", ''.join(result))