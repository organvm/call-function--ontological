"""Tests for the FUNCTIONcalled naming validator."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from tools import validate_naming as naming


@pytest.mark.parametrize(
    ("filename", "expected_layer"),
    [
        ("core.router.network.c", "core"),
        ("interface.portal.entry.html", "interface"),
        ("logic.agent.analysis.py", "logic"),
        ("application.bridge.mobile.swift", "application"),
        ("bones.router.network.c", "core"),
        ("skins.portal.entry.html", "interface"),
        ("breath.agent.analysis.py", "logic"),
        ("body.bridge.mobile.swift", "application"),
    ],
)
def test_validate_name_accepts_canonical_and_alias_layers(
    filename: str, expected_layer: str
) -> None:
    is_valid, message = naming.validate_name(filename)

    assert is_valid
    assert f"layer={expected_layer}" in message


@pytest.mark.parametrize(
    "filename",
    [
        "router.network.c",
        "invalid.router.network.c",
        "core.9router.network.c",
        "core.router.9network.c",
        "core.router.network",
        "core.router.network.g7",
    ],
)
def test_validate_name_rejects_malformed_names(filename: str) -> None:
    is_valid, message = naming.validate_name(filename)

    assert not is_valid
    assert "{Layer}.{Role}.{Domain}.{Extension}" in message


def test_is_excluded_skips_project_scaffolding_and_excluded_dirs(tmp_path: Path) -> None:
    root = tmp_path

    assert naming.is_excluded(root / "README.md", root)
    assert naming.is_excluded(root / "core.router.network.c.meta.json", root)
    assert naming.is_excluded(root / "docs" / "bad-name.md", root)
    assert naming.is_excluded(root / "tests" / "test_anything.py", root)


def test_is_excluded_skips_python_import_files_inside_layer_packages(
    tmp_path: Path,
) -> None:
    core_dir = tmp_path / "core"
    core_dir.mkdir()
    (core_dir / "__init__.py").write_text("")
    source_file = core_dir / "ontology.py"

    assert naming.is_excluded(source_file, tmp_path)


def test_is_excluded_checks_python_files_outside_layer_packages(tmp_path: Path) -> None:
    logic_dir = tmp_path / "logic"
    logic_dir.mkdir()
    source_file = logic_dir / "worker.py"

    assert not naming.is_excluded(source_file, tmp_path)


def test_validate_directory_reports_only_non_excluded_invalid_files(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "notes.md").write_text("")
    (tmp_path / "core").mkdir()
    (tmp_path / "core" / "__init__.py").write_text("")
    (tmp_path / "core" / "ontology.py").write_text("")
    (tmp_path / "core.router.network.c").write_text("")
    (tmp_path / "bad-name.txt").write_text("")

    errors = naming.validate_directory(str(tmp_path))
    output = capsys.readouterr().out

    assert errors == [
        (
            "bad-name.txt",
            "Does not match pattern {Layer}.{Role}.{Domain}.{Extension}",
        )
    ]
    assert "bad-name.txt" in output
    assert "1 of 2 files do not follow the naming convention" in output


def test_validate_directory_verbose_reports_valid_and_skipped_files(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "README.md").write_text("")
    (tmp_path / "core.router.network.c").write_text("")

    errors = naming.validate_directory(str(tmp_path), verbose=True)
    output = capsys.readouterr().out

    assert errors == []
    assert "Skipped: README.md" in output
    assert "core.router.network.c: Valid: layer=core" in output
    assert "All 1 checked files follow the naming convention" in output


def test_main_validates_explicit_files(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["validate_naming.py", "core.router.network.c", "logic.agent.analysis.py"],
    )

    naming.main()
    output = capsys.readouterr().out

    assert "core.router.network.c: Valid: layer=core" in output
    assert "logic.agent.analysis.py: Valid: layer=logic" in output


def test_main_exits_nonzero_for_invalid_explicit_file(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["validate_naming.py", "core.router.network.c", "bad-name.txt"],
    )

    with pytest.raises(SystemExit) as exc_info:
        naming.main()

    output = capsys.readouterr().out
    assert exc_info.value.code == 1
    assert "core.router.network.c: Valid: layer=core" in output
    assert "bad-name.txt: Does not match pattern" in output


def test_main_exits_nonzero_when_root_scan_finds_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "bad-name.txt").write_text("")
    monkeypatch.setattr(sys, "argv", ["validate_naming.py", "--root", str(tmp_path)])

    with pytest.raises(SystemExit) as exc_info:
        naming.main()

    assert exc_info.value.code == 1
