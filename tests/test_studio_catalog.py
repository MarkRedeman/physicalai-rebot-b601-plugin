from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from physicalai_rebot_b601_plugin.studio_catalog import _CatalogDefinition


class _FakeRegistry:
    def __init__(self) -> None:
        self.definitions: list = []

    def register(self, definition: object) -> None:
        self.definitions.append(definition)

    def register_many(self, definitions: list[object]) -> None:
        self.definitions.extend(definitions)


def test_definitions_count() -> None:
    from physicalai_rebot_b601_plugin.studio_catalog import _definitions

    defs = _definitions()
    assert len(defs) == 2


def test_definitions_have_expected_types() -> None:
    from physicalai_rebot_b601_plugin.studio_catalog import _definitions

    types = {d.entry.type for d in _definitions()}
    assert types == {"ReBot_B601_DM_Follower", "ReBot_Arm102_Leader"}


def test_register_physicalai_studio_plugin() -> None:
    from physicalai_rebot_b601_plugin.studio_catalog import register_physicalai_studio_plugin

    registry = _FakeRegistry()
    register_physicalai_studio_plugin(registry)
    assert len(registry.definitions) == 2


def test_dm_follower_structure() -> None:
    from physicalai_rebot_b601_plugin.studio_catalog import _definitions

    dm = [d for d in _definitions() if d.entry.type == "ReBot_B601_DM_Follower"][0]

    assert dm.entry.display_name == "ReBot B601 DM Follower"
    assert dm.entry.role == "follower"
    assert dm.urdf_relative_path == Path("rebot-b601-dm/urdf/reBot-DevArm_fixend.urdf")
    assert dm.package_root == Path("rebot-b601-dm")
    assert dm.asset_source == "plugin"
    assert dm.asset_root_resolver is not None
    assert dm.discover_devices is not None


def test_arm102_leader_structure() -> None:
    from physicalai_rebot_b601_plugin.studio_catalog import _definitions

    arm102 = [d for d in _definitions() if d.entry.type == "ReBot_Arm102_Leader"][0]

    assert arm102.entry.display_name == "ReBot Arm102 Leader"
    assert arm102.entry.role == "leader"
    assert arm102.urdf_relative_path == Path("stararm102/urdf/stararm102_description.urdf")
    assert arm102.package_root == Path("stararm102")
    assert arm102.asset_source == "plugin"


def test_definition_robot_type_property() -> None:
    from physicalai_rebot_b601_plugin.studio_catalog import _definitions

    for d in _definitions():
        assert d.robot_type == d.entry.type


def test_get_rebot_urdf_root_returns_path() -> None:
    from physicalai_rebot_b601_plugin.studio_catalog import _get_rebot_urdf_root

    root = _get_rebot_urdf_root()
    assert isinstance(root, Path)
    assert root.exists()
