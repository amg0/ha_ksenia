"""
Coordinator data types for ksenia.

Defines the structure of the data returned by the coordinator's
_async_update_data() method.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class KseniaLaresZone:
    """Represents a single alarm zone with its description and status."""

    index: int
    description: str
    status: str = "UNKNOWN"
    bypass: str = "UNKNOWN"

    @property
    def is_triggered(self) -> bool:
        """Return True if the zone is in a non-NORMAL state (motion detected)."""
        return self.status != "NORMAL"


@dataclass
class KseniaLaresCoordinatorData:
    """Data returned by the coordinator on every update."""

    zones: list[KseniaLaresZone] = field(default_factory=list)
    partitions: dict[str, str] = field(default_factory=dict)

    @property
    def _partitions(self) -> dict[str, str]:
        """Return the partition statuses."""
        return self.partitions
