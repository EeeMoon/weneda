class FG:
    """
    Adds foreground color to text. Shows in ANSI-supported environments (terminal, Discord embeds).

    ### Example usage
    ```
    print(FG.RED + "Hello World")
    ```
    """

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    DEFAULT = "\033[39m"

    LIGHT_BLACK = "\033[90m"
    LIGHT_RED = "\033[91m"
    LIGHT_GREEN = "\033[92m"
    LIGHT_YELLOW = "\033[93m"
    LIGHT_BLUE = "\033[94m"
    LIGHT_MAGENTA = "\033[95m"
    LIGHT_CYAN = "\033[96m"
    LIGHT_WHITE = "\033[97m"

    @staticmethod
    def rgb(r: int, g: int, b: int):
        """
        RGB foreground color. Not widely supported.
        """
        return f"\033[38;2;{r};{g};{b}m"


class BG:
    """
    Adds background color to text. Shows in ANSI-supported environments (terminal, Discord embeds).

    ### Example usage
    ```
    print(BG.RED + "Hello World")
    ```
    """

    BLACK = "\033[40m"
    RED = "\033[41m"
    GREEN = "\033[42m"
    YELLOW = "\033[43m"
    BLUE = "\033[44m"
    MAGENTA = "\033[45m"
    CYAN = "\033[46m"
    WHITE = "\033[47m"

    DEFAULT = "\033[49m"

    LIGHT_BLACK = "\033[100m"
    LIGHT_RED = "\033[101m"
    LIGHT_GREEN = "\033[102m"
    LIGHT_YELLOW = "\033[103m"
    LIGHT_BLUE = "\033[104m"
    LIGHT_MAGENTA = "\033[105m"
    LIGHT_CYAN = "\033[106m"
    LIGHT_WHITE = "\033[107m"

    @staticmethod
    def rgb(r: int, g: int, b: int):
        """
        RGB background color. Not widely supported.
        """
        return f"\033[48;2;{r};{g};{b}m"


class ST:
    """
    Adds some style to text. Shows in ANSI-supported environments (terminal, Discord embeds).

    ### Example usage
    ```
    print(ST.UNDERLINE + "Hello World" + ST.RESET)
    ```
    """
    
    RESET = "\033[0m"
    BOLD = "\033[1m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"
    HIDDEN = "\033[8m"
    CROSS = "\033[9m"


class MV:
    """
    Moves cursor.
    """

    @staticmethod
    def up(n: int):
        "Move cursor up by `n` lines."
        return f"\033[{n}A"

    @staticmethod
    def down(n: int):
        "Move cursor down by `n` lines."
        return f"\033[{n}B"

    @staticmethod
    def right(n: int):
        "Move cursor right by `n` lines."
        return f"\033[{n}C"

    @staticmethod
    def left(n: int):
        "Move cursor left by `n` lines."
        return f"\033[{n}D"

    @staticmethod
    def pos(x: int, y: int):
        "Move cursor to specific `x`, `y` position."
        return f"\033[{x};{y}H"
