"""DSA-oriented examples of dataclasses and method types."""

from dataclasses import dataclass, field
from typing import ClassVar


@dataclass(frozen=True, order=True)
class PriorityItem:
    """Immutable, hashable heap-ready value object with O(1) comparisons."""

    priority: int
    sequence: int
    value: object = field(compare=False)


@dataclass
class Vertex:
    """Mutable vertex demonstrating class, instance, and static methods."""

    label: str
    created: ClassVar[int] = 0

    def __post_init__(self) -> None:
        type(self).created += 1

    def renamed(self, label: str) -> "Vertex":
        """Return a new vertex in O(1) time without mutating this one."""
        return type(self)(label)

    @classmethod
    def from_value(cls, value: object) -> "Vertex":
        return cls(str(value))

    @staticmethod
    def valid_label(label: object) -> bool:
        return isinstance(label, str) and bool(label.strip())

    def __len__(self) -> int:
        return len(self.label)
