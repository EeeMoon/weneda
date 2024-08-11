import inspect
from functools import partial
from typing import Any

from .placeholder import Placeholder, PlaceholderData


class Formatter:
    """
    Placeholder formatter.

    Parameters
    ----------
    opener: `str`
        Left placeholder identifier.
    closer: `str`
        Right placeholder identifier.
    escape: `str`
        Escape string. 
        If opener or closer follows it, they are not identified.

    Examples
    --------
    >>> class CountFormatter(Formatter):
    ...     def __init__(self, count: int) -> None:
    ...         super().__init__()
    ...
    ...         self.count: int = count
    ...
    ...     @placeholder(name="count", pattern="count")
    ...     async def count_handler(self) -> int:
    ...         return self.count
    ...
    >>> formatter = CountFormatter(5)
    >>> await formatter.format("Count is {count}")
    'Count is 5'
    """

    def __init_subclass__(cls) -> None:
        cls.__placeholder_methods__ = [
            member
            for base in reversed(cls.__mro__)
            for member in base.__dict__.values()
            if hasattr(member, '__placeholder_args__')
        ]

    def __init__(
        self, 
        opener: str = '{', 
        closer: str = '}',
        *,
        escape: str | None = '\\'
    ) -> None:
        if not isinstance(opener, str) or not opener:
            raise ValueError("'opener' should be a non-empty string")
        if not isinstance(closer, str) or not closer:
            raise ValueError("'closer' should be a non-empty string")
        if (isinstance(escape, str) and not escape) and escape is not None:
            raise ValueError("'escape' should be a non-empty string or None")
        if escape in {opener, closer}:
            raise ValueError("'escape' should not equal to 'opener' or 'closer'")
        
        self.opener: str = opener
        self.closer: str = closer
        self.escape: str | None = escape
        self.placeholders: dict[str, Placeholder] = {}

        for func in self.__placeholder_methods__:
            ph = Placeholder(
                **func.__placeholder_args__, 
                func=partial(func, self)
            )
            ph.formatter = self
            self.placeholders[ph.name] = ph 
    
    def add_placeholder(self, ph: Placeholder, /) -> None:
        """
        Add a placeholder handler.

        Parameters
        ----------
        ph: `Placeholder`
            Placeholder to add.
        """
        if not isinstance(ph, Placeholder):
            raise TypeError(
                f"Expected {Placeholder.__name__!r}, not {ph.__class__!r}"
            )

        ph.formatter = self
        self.placeholders[ph.name] = ph

    def remove_placeholder(self, ph: Placeholder, /) -> None:
        """
        Remove the placeholder handler.

        Parameters
        ----------
        ph: `Placeholder`
            Placeholder to remove.
        """
        if not isinstance(ph, Placeholder):
            raise TypeError(
                f"Expected {Placeholder.__name__!r}, not {ph.__class__!r}"
            )
        
        del self.placeholders[ph.name]

    async def process(self, data: PlaceholderData) -> Any:
        """
        Get a value from the first matched placeholder.

        Parameters
        ----------
        data: `PlaceholderData`
            Placeholder data.

        Returns
        -------
        `Any`
            If returned by placeholder.
        `None`
            If placeholder was not found.
        """
        raw = data.raw
        for ph in self.placeholders.values():
            if ph.pattern is None:
                kwargs = {}
            elif m := ph.pattern.fullmatch(raw):
                kwargs = m.groupdict()
            else:
                continue
            
            skip = False
            signature = inspect.signature(ph.func)

            for param in signature.parameters.values():
                if param.name in kwargs:
                    base = param.annotation
                    try:
                        kwargs[param.name] = base(kwargs[param.name])
                    except Exception:
                        skip = True 
                elif param.annotation is PlaceholderData:
                    kwargs[param.name] = data
            
            if skip:
                continue

            return await ph.func(**kwargs)

        return None

    async def format(self, text: str) -> str:
        """
        Replace placeholders in the text.

        Parameters
        ----------
        text: `str`
            Text to format.
        """
        opener = self.opener
        closer = self.closer
        escape = self.escape
        opener_len = len(opener)
        closer_len = len(closer)
        escape_len = len(escape) if escape else 0
        same = self.opener == self.closer
        current = text
        prev_escape = False
        stack: list[PlaceholderData] = []
        index = 0

        while index < len(current):
            # check for escape string
            if escape and current[index : index + escape_len] == escape:
                # previously found escape string, keep only one
                if prev_escape:
                    current = ''.join((
                        current[: index - escape_len],
                        current[index:]
                    ))

                prev_escape = not prev_escape
                index += escape_len
            # check for opener 
            # if opener and closer are the same and there
            # is not opened brace, trigger closer 'elif'
            elif (
                current[index : index + opener_len] == opener 
                and not (same and stack)
            ):
                # save opener if escape string not found before
                if not prev_escape:
                    stack.append(PlaceholderData(start_index=index))
                else:
                    prev_escape = False
                    current = ''.join((
                        current[: index - escape_len],
                        current[index:]
                    ))

                index += opener_len
            # check for closer
            elif current[index : index + closer_len] == closer:
                # process placeholder if there is open brace
                # and escape string not found before
                if not prev_escape:
                    if stack:
                        open_ph = stack.pop()
                        start_index = open_ph.start_index
                        ph = current[start_index + opener_len : index]

                        # process the placeholder
                        open_ph.raw = ph
                        open_ph.depth = len(stack)
                        open_ph.end_index = index + closer_len
                        value = await self.process(open_ph)
                        open_ph.value = value

                        if stack:
                            stack[-1].children.append(open_ph)
            
                        # if value is None keep original placeholder
                        replacement = (
                            str(value) 
                            if value is not None else 
                            ''.join((opener, ph, closer))
                        )
                        
                        # replace placeholder in the text
                        current = ''.join((
                            current[:start_index],
                            replacement,
                            current[index + closer_len :]
                        ))
                        index = start_index + len(replacement)
                    else:
                        index += closer_len
                else:
                    prev_escape = False
                    current = ''.join((
                        current[: index - len(escape)],
                        current[index:]
                    ))
            # skip any other character
            else:
                index += 1

        return current