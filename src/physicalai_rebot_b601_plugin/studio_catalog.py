"""Studio catalog plugin for Physical AI Studio.

Exposes :func:`register_physicalai_studio_plugin` as the entry-point callable
for the ``physicalai.studio.catalog_plugins`` group.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Protocol

from loguru import logger

import physicalai_rebot_b601_plugin
from physicalai_rebot_b601_plugin import get_urdf_path


class _SerialPortInfo(Protocol):
    connection_string: str
    serial_number: str
    robot_type: str


@dataclass(frozen=True)
class _CatalogEntry:
    type: str
    display_name: str
    role: str
    urdf_path: str | None
    package_map: dict[str, str]
    joint_map: dict[str, list[str]]


_AssetSource = Literal["builtin", "plugin"]
_DiscoverDevicesCallable = Callable[[list[_SerialPortInfo]], Awaitable[list[_SerialPortInfo]]]
_AssetRootResolver = Callable[[], Path]


@dataclass(frozen=True)
class _CatalogDefinition:
    entry: _CatalogEntry
    urdf_relative_path: Path | None
    package_root: Path | None
    asset_source: _AssetSource
    asset_root_resolver: _AssetRootResolver | None
    discover_devices: _DiscoverDevicesCallable

    @property
    def robot_type(self) -> str:
        return self.entry.type


if TYPE_CHECKING:

    class _RobotCatalogRegistry(Protocol):
        def register(self, definition: _CatalogDefinition) -> None: ...
        def register_many(self, definitions: list[_CatalogDefinition]) -> None: ...


_REBOT_B601_DM_TO_URDF: dict[str, list[str]] = {
    "shoulder_pan.pos": ["joint1"],
    "shoulder_lift.pos": ["joint2"],
    "elbow_flex.pos": ["joint3"],
    "wrist_flex.pos": ["joint4"],
    "wrist_yaw.pos": ["joint5"],
    "wrist_roll.pos": ["joint6"],
    "gripper.pos": [],
}

_REBOT_ARM102_TO_URDF: dict[str, list[str]] = {
    "shoulder_pan.pos": ["joint1"],
    "shoulder_lift.pos": ["joint2"],
    "elbow_flex.pos": ["joint3"],
    "wrist_flex.pos": ["joint4"],
    "wrist_yaw.pos": ["joint5"],
    "wrist_roll.pos": ["joint6"],
    "gripper.pos": ["joint7_left", "joint7_right"],
}


def _get_rebot_urdf_root() -> Path:
    configured_root = get_urdf_path()
    if configured_root.exists():
        return configured_root

    plugin_package_root = Path(physicalai_rebot_b601_plugin.__file__).resolve().parent
    site_packages_urdf_root = plugin_package_root.parent / "urdf"
    if site_packages_urdf_root.exists():
        logger.warning(
            "ReBot plugin get_urdf_path() returned missing path={}; falling back to {}",
            configured_root,
            site_packages_urdf_root,
        )
        return site_packages_urdf_root

    return configured_root


async def _discover_rebot_devices(devices: list[_SerialPortInfo]) -> list[_SerialPortInfo]:
    await asyncio.sleep(0)
    return devices


def _definitions() -> list[_CatalogDefinition]:
    return [
        _CatalogDefinition(
            entry=_CatalogEntry(
                type="ReBot_B601_DM_Follower",
                display_name="ReBot B601 DM Follower",
                role="follower",
                urdf_path="/api/robots/catalog/ReBot_B601_DM_Follower/urdf",
                package_map={
                    "rebot-b601-dm": "/api/robots/catalog/ReBot_B601_DM_Follower",
                },
                joint_map=_REBOT_B601_DM_TO_URDF,
            ),
            urdf_relative_path=Path("rebot-b601-dm/urdf/reBot-DevArm_fixend.urdf"),
            package_root=Path("rebot-b601-dm"),
            asset_source="plugin",
            asset_root_resolver=_get_rebot_urdf_root,
            discover_devices=_discover_rebot_devices,
        ),
        _CatalogDefinition(
            entry=_CatalogEntry(
                type="ReBot_Arm102_Leader",
                display_name="ReBot Arm102 Leader",
                role="leader",
                urdf_path="/api/robots/catalog/ReBot_Arm102_Leader/urdf",
                package_map={
                    "stararm102": "/api/robots/catalog/ReBot_Arm102_Leader",
                },
                joint_map=_REBOT_ARM102_TO_URDF,
            ),
            urdf_relative_path=Path("stararm102/urdf/stararm102_description.urdf"),
            package_root=Path("stararm102"),
            asset_source="plugin",
            asset_root_resolver=_get_rebot_urdf_root,
            discover_devices=_discover_rebot_devices,
        ),
    ]


def register_physicalai_studio_plugin(registry: _RobotCatalogRegistry) -> None:
    """Register ReBot robot catalog entries with the Physical AI Studio registry.

    Args:
        registry: The Studio robot catalog registry instance.
    """
    registry.register_many(_definitions())
