import re
import inspect
from typing import Callable, Coroutine, TYPE_CHECKING
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from .formatter import Formatter


@dataclass
class PlaceholderData:
    """Placeholder data."""

    raw: str = ...
    """Raw placeholder value without identifiers."""
    depth: int = ...
    """Nesting level."""
    value: str | None = None
    """Processed value. Only available for children."""
    children: list['PlaceholderData'] = field(default_factory=list)
    """Inner placeholders."""
    start_index: int = ...
    """Start index including identifiers."""
    end_index: int = ...
    """End index including identifiers."""


class Placeholder:
    """
    Placeholder handler.

    Parameters
    ----------
    name: `str` | `None`
        Name of the placeholder. If `None`, equals to function name.
    pattern: `str` | `None`
        Regex pattern to match placeholder. If `None`, match any string.
    """

    def __init__(
        self, 
        *, 
        name: str, 
        pattern: str | None,
        func: Callable[..., Coroutine]
    ) -> None:
        self.formatter: 'Formatter | None' = None
        self.name: str = name
        self.pattern: re.Pattern | None = re.compile(pattern) if pattern else None

        if self.pattern:
            Placeholder.validate_func(func, self.pattern)

        self.func: Callable[..., Coroutine] = func

    def __str__(self) -> str:
        return self.name
    
    @classmethod
    def validate_func(cls, func: Callable, pattern: re.Pattern) -> None:
        signature = inspect.signature(func)
        for group_name in pattern.groupindex.keys():
            param = signature.parameters.get(group_name)

            if not param:
                raise ValueError(f"Missing '{group_name}' parameter")
            elif param.kind not in {
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            }:
                raise ValueError(
                    f"Parameter '{param.name}' should be either positional or keyword"
                )
    

def placeholder(
    *, 
    name: str | None = None,
    pattern: str | None = None
) -> Callable[[Callable[..., Coroutine]], Placeholder]:
    """
    Decorator to register method as placeholder.

    Parameters
    ----------
    name: `str` | `None`
        Name of the placeholder. If `None`, equals to function name.
    pattern: `str` | `None`
        Regex pattern to match placeholder. If `None`, match any string.
    """
    def helper(func: Callable[..., Coroutine]) -> Placeholder:
        func.__placeholder_args__ = {
            'name': name if name is not None else func.__name__,
            'pattern': pattern
        }
        return func

    return helper