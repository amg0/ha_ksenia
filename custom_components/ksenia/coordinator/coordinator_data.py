"""
Coordinator data types for ksenia.

Defines the structure of the data returned by the coordinator's
_async_update_data() method.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from custom_components.ksenia.api.client import KseniaLaresZone, KseniaPartition


@dataclass
class KseniaLaresCoordinatorData:
    """Data returned by the coordinator on every update."""

    zones: list[KseniaLaresZone] = field(default_factory=list)
    partitions: dict[str, KseniaPartition] = field(default_factory=dict)

    @property
    def _partitions(self) -> dict[str, KseniaPartition]:
        """Return the partition statuses."""
        return self.partitions
