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


def test_dm_follower_has_robot_builder() -> None:
    from physicalai_rebot_b601_plugin.studio_catalog import _definitions

    dm = [d for d in _definitions() if d.entry.type == "ReBot_B601_DM_Follower"][0]
    assert callable(dm.robot_builder)
    assert dm.payload_model is not None
    assert dm.adapter_options.include_velocities is True
    assert dm.adapter_options.external_effort_gain is None
    assert dm.adapter_options.goal_time_scale == 1.0


def test_arm102_leader_has_robot_builder() -> None:
    from physicalai_rebot_b601_plugin.studio_catalog import _definitions

    arm102 = [d for d in _definitions() if d.entry.type == "ReBot_Arm102_Leader"][0]
    assert callable(arm102.robot_builder)
    assert arm102.payload_model is not None
    assert arm102.adapter_options.include_velocities is False
    assert arm102.adapter_options.external_effort_gain is None
    assert arm102.adapter_options.goal_time_scale == 1.0


def test_rebot_b601_dm_payload_defaults() -> None:
    from physicalai_rebot_b601_plugin.studio_catalog import ReBotB601DMPayload

    payload = ReBotB601DMPayload(serial_number="SN-001")
    assert payload.connection_string == ""
    assert payload.serial_number == "SN-001"
    assert payload.can_adapter == "damiao"
    assert payload.dm_serial_baud == 921600
    assert payload.disable_torque_on_disconnect is True
    assert payload.force_pos_torque_ratio == 0.1


def test_rebot_arm102_payload_defaults() -> None:
    from physicalai_rebot_b601_plugin.studio_catalog import ReBotArm102Payload

    payload = ReBotArm102Payload(serial_number="SN-002")
    assert payload.connection_string == ""
    assert payload.serial_number == "SN-002"
    assert payload.baudrate == 1_000_000
    assert payload.unlock_on_connect is True
    assert payload.reset_multi_turn_on_connect is True
    assert payload.zero_on_connect is False


def test_get_rebot_urdf_root_returns_path() -> None:
    from physicalai_rebot_b601_plugin.studio_catalog import _get_rebot_urdf_root

    root = _get_rebot_urdf_root()
    assert isinstance(root, Path)
    assert root.exists()
