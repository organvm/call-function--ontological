#!/usr/bin/env python3
"""
Tests for validate_naming.py - the file naming convention validator.

Run with: python -m pytest tools/test_validate_naming.py -v
"""

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

# Import the validator module for direct function testing
sys.path.insert(0, str(Path(__file__).parent))
from validate_naming import (
    validate_name,
    is_excluded,
    LAYERS,
    LAYER_ALIASES,
    ALL_LAYERS,
    NAMING_PATTERN,
)


VALIDATOR_PATH = "tools/validate_naming.py"


class TestValidNamePatterns:
    """Tests for valid file name patterns."""

    def test_canonical_layer_names(self):
        """All canonical layer names should be valid."""
        canonical_layers = ["core", "interface", "logic", "application"]
        for layer in canonical_layers:
            filename = f"{layer}.role.domain.ext"
            is_valid, message = validate_name(filename)
            assert is_valid, f"'{filename}' should be valid: {message}"

    def test_alias_layer_names(self):
        """All alias layer names should be valid."""
        alias_layers = ["bones", "skins", "breath", "body"]
        for layer in alias_layers:
            filename = f"{layer}.role.domain.ext"
            is_valid, message = validate_name(filename)
            assert is_valid, f"'{filename}' should be valid: {message}"

    def test_spec_examples(self):
        """Examples from the spec should all be valid."""
        spec_examples = [
            "bones.router.network.c",
            "skins.layout.dashboard.css",
            "skins.portal.entry.html",
            "breath.agent.analysis.py",
            "breath.script.runtime.lua",
            "body.app.mobile.swift",
            "body.bridge.legacy.m",
        ]
        for filename in spec_examples:
            is_valid, message = validate_name(filename)
            assert is_valid, f"Spec example '{filename}' should be valid: {message}"

    def test_canonical_equivalents(self):
        """Canonical equivalents of spec examples should be valid."""
        canonical_examples = [
            "core.router.network.c",
            "interface.layout.dashboard.css",
            "interface.portal.entry.html",
            "logic.agent.analysis.py",
            "logic.script.runtime.lua",
            "application.app.mobile.swift",
            "application.bridge.legacy.m",
        ]
        for filename in canonical_examples:
            is_valid, message = validate_name(filename)
            assert is_valid, f"'{filename}' should be valid: {message}"

    def test_various_extensions(self):
        """Various file extensions should be valid."""
        extensions = ["c", "cpp", "rs", "go", "py", "js", "ts", "html", "css", "json", "md", "swift", "m", "java", "kt"]
        for ext in extensions:
            filename = f"core.role.domain.{ext}"
            is_valid, message = validate_name(filename)
            assert is_valid, f"Extension '.{ext}' should be valid: {message}"


class TestInvalidNamePatterns:
    """Tests for invalid file name patterns."""

    def test_missing_layer(self):
        """Missing layer should be invalid."""
        is_valid, message = validate_name("role.domain.ext")
        assert not is_valid, "Missing layer should be invalid"

    def test_invalid_layer(self):
        """Invalid layer name should be invalid."""
        is_valid, message = validate_name("invalid.role.domain.ext")
        assert not is_valid, "Invalid layer should be invalid"

    def test_missing_role(self):
        """Missing role should be invalid."""
        is_valid, message = validate_name("core.domain.ext")
        assert not is_valid, "File with only 3 parts should be invalid"

    def test_missing_domain(self):
        """Missing domain should be invalid (only 3 parts)."""
        # With only 3 parts, it becomes Layer.Role.ext which is invalid
        is_valid, message = validate_name("core.role.ext")
        assert not is_valid, "File with only 3 parts should be invalid"

    def test_missing_extension(self):
        """Missing extension should be invalid."""
        is_valid, message = validate_name("core.role.domain")
        assert not is_valid, "Missing extension should be invalid"

    def test_uppercase_layer(self):
        """Uppercase layer should still be valid (case insensitive)."""
        # The regex has re.IGNORECASE, so this should pass
        is_valid, message = validate_name("CORE.role.domain.ext")
        assert is_valid, "Uppercase layer should be valid (case insensitive)"

    def test_numeric_role_start(self):
        """Role starting with number should be invalid."""
        is_valid, message = validate_name("core.123role.domain.ext")
        assert not is_valid, "Role starting with number should be invalid"

    def test_numeric_domain_start(self):
        """Domain starting with number should be invalid."""
        is_valid, message = validate_name("core.role.123domain.ext")
        assert not is_valid, "Domain starting with number should be invalid"


class TestEdgeCases:
    """Edge case tests for naming validation."""

    def test_multi_segment_role(self):
        """Multi-segment role should be valid."""
        is_valid, message = validate_name("core.sub.role.domain.ext")
        assert is_valid, "Multi-segment role should be valid"

    def test_multi_segment_domain(self):
        """Multi-segment domain should be valid."""
        is_valid, message = validate_name("core.role.sub.domain.ext")
        assert is_valid, "Multi-segment domain should be valid"

    def test_alphanumeric_role(self):
        """Role with numbers (not at start) should be valid."""
        is_valid, message = validate_name("core.role2.domain.ext")
        assert is_valid, "Alphanumeric role should be valid"

    def test_alphanumeric_domain(self):
        """Domain with numbers (not at start) should be valid."""
        is_valid, message = validate_name("core.role.domain3.ext")
        assert is_valid, "Alphanumeric domain should be valid"

    def test_single_char_segments(self):
        """Single character segments should be valid."""
        is_valid, message = validate_name("core.a.b.c")
        assert is_valid, "Single character segments should be valid"

    def test_long_segments(self):
        """Long segment names should be valid."""
        long_role = "a" * 50
        long_domain = "b" * 50
        is_valid, message = validate_name(f"core.{long_role}.{long_domain}.ext")
        assert is_valid, "Long segments should be valid"


class TestLayerNormalization:
    """Tests for layer alias to canonical name normalization."""

    def test_alias_to_canonical_mapping(self):
        """Verify alias to canonical mapping is correct."""
        assert LAYER_ALIASES["bones"] == "core"
        assert LAYER_ALIASES["skins"] == "interface"
        assert LAYER_ALIASES["breath"] == "logic"
        assert LAYER_ALIASES["body"] == "application"

    def test_canonical_to_alias_mapping(self):
        """Verify canonical to alias mapping is correct."""
        assert LAYERS["core"] == "bones"
        assert LAYERS["interface"] == "skins"
        assert LAYERS["logic"] == "breath"
        assert LAYERS["application"] == "body"

    def test_all_layers_set(self):
        """ALL_LAYERS should contain all canonical and alias names."""
        expected = {"core", "interface", "logic", "application", "bones", "skins", "breath", "body"}
        assert ALL_LAYERS == expected


class TestExclusionRules:
    """Tests for file exclusion rules."""

    def test_dotfiles_excluded(self):
        """Dotfiles should be excluded."""
        root = Path("/fake/root")
        path = root / ".gitignore"
        assert is_excluded(path, root), ".gitignore should be excluded"

    def test_underscore_files_excluded(self):
        """Underscore-prefixed files should be excluded."""
        root = Path("/fake/root")
        path = root / "_private.py"
        assert is_excluded(path, root), "_private.py should be excluded"

    def test_readme_excluded(self):
        """README files should be excluded."""
        root = Path("/fake/root")
        for name in ["README.md", "README", "README.txt"]:
            path = root / name
            assert is_excluded(path, root), f"{name} should be excluded"

    def test_license_excluded(self):
        """LICENSE files should be excluded."""
        root = Path("/fake/root")
        for name in ["LICENSE", "LICENSE.md", "LICENSE.txt"]:
            path = root / name
            assert is_excluded(path, root), f"{name} should be excluded"

    def test_makefile_excluded(self):
        """Makefile should be excluded."""
        root = Path("/fake/root")
        path = root / "Makefile"
        assert is_excluded(path, root), "Makefile should be excluded"

    def test_meta_json_excluded(self):
        """*.meta.json files should be excluded."""
        root = Path("/fake/root")
        path = root / "core.role.domain.ext.meta.json"
        assert is_excluded(path, root), "*.meta.json should be excluded"

    def test_template_files_excluded(self):
        """Template files should be excluded."""
        root = Path("/fake/root")
        for name in ["template.py", "template.js", "template.html"]:
            path = root / name
            assert is_excluded(path, root), f"{name} should be excluded"

    def test_schema_files_excluded(self):
        """Schema files should be excluded."""
        root = Path("/fake/root")
        path = root / "something.schema.json"
        assert is_excluded(path, root), "*.schema.json should be excluded"

    def test_tools_directory_excluded(self):
        """Files in tools/ directory should be excluded."""
        root = Path("/fake/root")
        path = root / "tools" / "validate_meta.py"
        assert is_excluded(path, root), "Files in tools/ should be excluded"

    def test_logs_directory_excluded(self):
        """Files in logs/ directory should be excluded."""
        root = Path("/fake/root")
        path = root / "logs" / "agents" / "opencode.json"
        assert is_excluded(path, root), "Files in logs/ should be excluded"

    def test_venv_directory_excluded(self):
        """Files in .venv/ directory should be excluded."""
        root = Path("/fake/root")
        path = root / ".venv" / "lib" / "something.py"
        assert is_excluded(path, root), "Files in .venv/ should be excluded"

    def test_claude_md_excluded(self):
        """CLAUDE.md should be excluded."""
        root = Path("/fake/root")
        path = root / "CLAUDE.md"
        assert is_excluded(path, root), "CLAUDE.md should be excluded"


class TestCLIInterface:
    """Tests for the CLI interface."""

    def test_cli_with_valid_file(self):
        """CLI should succeed with valid filename."""
        result = subprocess.run(
            [sys.executable, VALIDATOR_PATH, "core.role.domain.ext"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "✅" in result.stdout

    def test_cli_with_invalid_file(self):
        """CLI should fail with invalid filename."""
        result = subprocess.run(
            [sys.executable, VALIDATOR_PATH, "invalid-filename.ext"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 1
        assert "❌" in result.stdout

    def test_cli_with_multiple_files(self):
        """CLI should handle multiple files."""
        result = subprocess.run(
            [sys.executable, VALIDATOR_PATH,
             "core.role.domain.c",
             "logic.agent.analysis.py"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert result.stdout.count("✅") == 2

    def test_cli_with_mixed_valid_invalid(self):
        """CLI should fail if any file is invalid."""
        result = subprocess.run(
            [sys.executable, VALIDATOR_PATH,
             "core.role.domain.c",
             "invalid-file.txt"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 1
        assert "✅" in result.stdout
        assert "❌" in result.stdout


class TestRealWorldExamples:
    """Tests with real-world example filenames."""

    def test_project_example_files(self):
        """The renamed example files should be valid."""
        valid_files = [
            "interface.portal.entry.html",
            "logic.agent.analysis.py",
        ]
        for filename in valid_files:
            is_valid, message = validate_name(filename)
            assert is_valid, f"Project file '{filename}' should be valid: {message}"

    def test_common_invalid_patterns(self):
        """Common invalid patterns should fail."""
        invalid_files = [
            "index.html",  # No layer
            "main.py",  # No layer/role/domain
            "utils.js",  # No structure
            "my-component.tsx",  # Hyphens, no structure
            "README.md",  # Actually excluded, but pattern-wise invalid
        ]
        for filename in invalid_files:
            is_valid, message = validate_name(filename)
            # README.md is excluded from validation, so it won't be checked
            if filename != "README.md":
                assert not is_valid, f"'{filename}' should be invalid"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
