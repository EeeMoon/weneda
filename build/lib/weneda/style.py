class FG:
    """
    Adds foreground color to text. Shows in ANSI-supported environments (terminal, Discord) 

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

    @staticmethod
    def rgb(r: int, g: int, b: int):
        """
        RGB foreground color. Not widely supported.

        ## Attributes
        r: `int`
            Red value.
        g: `int`
            Green value.
        b: `int`
            Blue value.
        """
        return f"\033[38;2;{r};{g};{b}m"

class BG:
    """
    Adds background color to text. Shows in ANSI-supported environments (terminal, Discord) 

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

    @staticmethod
    def rgb(r: int, g: int, b: int):
        """
        RGB background color. Not widely supported.

        ## Attributes
        r: `int`
            Red value.
        g: `int`
            Green value.
        b: `int`
            Blue value.
        """
        return f"\033[48;2;{r};{g};{b}m"

class ST:
    """
    Adds some style to text. Shows in ANSI-supported environments (terminal, Discord) 

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

