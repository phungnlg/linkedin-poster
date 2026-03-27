"""Shared test fixtures."""

import json
import os
import tempfile
from pathlib import Path

import pytest

from linkedin_poster.models.poc import PocProject


@pytest.fixture
def sample_poc() -> PocProject:
    return PocProject(
        name="Test Project",
        github_url="https://github.com/test/test-project",
        description="A test POC project for unit testing.",
        keywords=["Python", "Testing", "CLI"],
        screenshots=[],
        tech_stack=["Python", "pytest", "httpx"],
        demo_url=None,
    )


@pytest.fixture
def sample_poc_config(sample_poc, tmp_path) -> str:
    config_path = tmp_path / "test_poc.json"
    config_path.write_text(json.dumps(sample_poc.model_dump()))
    return str(config_path)


@pytest.fixture
def tmp_json_path(tmp_path) -> str:
    return str(tmp_path / "test_data.json")
