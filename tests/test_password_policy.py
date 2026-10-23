"""Startup warning for a dashboard password below the minimum length."""

from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from esphome_device_builder.controllers.config.settings import (
    MIN_PASSWORD_LENGTH,
    DashboardSettings,
)

_LOGGER_NAME = "esphome_device_builder.controllers.config.settings"


def _parse(tmp_path: Path, password: str) -> DashboardSettings:
    settings = DashboardSettings()
    with patch.dict(os.environ, {}, clear=True):
        settings.parse_args(
            SimpleNamespace(configuration=str(tmp_path), username="admin", password=password)
        )
    return settings


def test_short_password_warns(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level("WARNING", logger=_LOGGER_NAME):
        settings = _parse(tmp_path, "a" * (MIN_PASSWORD_LENGTH - 1))

    assert settings.using_password is True
    assert any("shorter than" in rec.message for rec in caplog.records)


def test_long_password_is_silent(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level("WARNING", logger=_LOGGER_NAME):
        settings = _parse(tmp_path, "a" * MIN_PASSWORD_LENGTH)

    assert settings.using_password is True
    assert not any("shorter than" in rec.message for rec in caplog.records)


def test_no_password_is_silent(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level("WARNING", logger=_LOGGER_NAME):
        settings = _parse(tmp_path, "")

    assert settings.using_password is False
    assert not any("shorter than" in rec.message for rec in caplog.records)
