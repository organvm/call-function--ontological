"""Unit tests for application/grounding_report.py.

Covers the two private helpers (_section_header, _indent) and the three
public formatters (format_text_report, format_json_report, format_summary)
using hand-built FullAnalysis fixtures so tests are fast and isolated from
the full analysis pipeline.
"""

from __future__ import annotations

import json

import pytest

from application.analyzer import FullAnalysis
from application.grounding_report import (
    _indent,
    _section_header,
    format_json_report,
    format_summary,
    format_text_report,
)
from core.dasein import BreakdownCondition, DaseinAnalysis, WorldAssumption
from core.four_causes import CauseAnalysis, FourCausesReport
from core.grounding import GroundingMapping, GroundingReport
from core.ontology import (
    CONCEPTS_BY_KEY,
    Domain,
    MATERIAL_CAUSE,
    FORMAL_CAUSE,
    EFFICIENT_CAUSE,
    FINAL_CAUSE,
    DASEIN,
    ZUHANDENHEIT,
    VORHANDENHEIT,
    REPRESENTAMEN,
    OBJECT,
    INTERPRETANT,
    GROUNDING,
    TELOS_BRIDGE,
)
from core.semiotics import SemioticAnalysis, SignAnalysis


# ---------------------------------------------------------------------------
# Helpers for building fixture objects
# ---------------------------------------------------------------------------

def _make_four_causes(
    fn: str = "test_fn",
    material_evidence: list[str] | None = None,
    final_summary: str = "The purpose is testing.",
    final_confidence: str = "high",
) -> FourCausesReport:
    return FourCausesReport(
        function_name=fn,
        material=CauseAnalysis(
            cause_type="material",
            summary=f"{fn} has one string parameter.",
            evidence=material_evidence if material_evidence is not None else ["param: query"],
            confidence="high",
        ),
        formal=CauseAnalysis(
            cause_type="formal",
            summary=f"{fn} is an object schema with no additional constraints.",
            evidence=[],
            confidence="medium",
        ),
        efficient=CauseAnalysis(
            cause_type="efficient",
            summary=f"{fn} is triggered by an external caller.",
            evidence=["caller", "event"],
            confidence="medium",
        ),
        final=CauseAnalysis(
            cause_type="final",
            summary=final_summary,
            evidence=["description"],
            confidence=final_confidence,
        ),
    )


def _make_dasein(
    fn: str = "test_fn",
    world_assumptions: list[WorldAssumption] | None = None,
    transparency_conditions: list[str] | None = None,
    breakdown_conditions: list[BreakdownCondition] | None = None,
) -> DaseinAnalysis:
    return DaseinAnalysis(
        function_name=fn,
        world_assumptions=world_assumptions if world_assumptions is not None else [
            WorldAssumption(
                aspect="data_availability",
                description="Database is reachable.",
                derived_from="parameter: query",
            ),
        ],
        transparency_conditions=transparency_conditions if transparency_conditions is not None else [
            "Valid inputs provided.",
            "Service is online.",
        ],
        breakdown_conditions=breakdown_conditions if breakdown_conditions is not None else [
            BreakdownCondition(
                trigger="connection timeout",
                consequence="function raises exception",
                severity="major",
            ),
        ],
    )


def _make_semiotics(fn: str = "test_fn") -> SemioticAnalysis:
    return SemioticAnalysis(
        function_name=fn,
        representamen=SignAnalysis(
            component="representamen",
            summary=f"The sign is the identifier '{fn}'.",
            evidence=["function name", "parameter names"],
        ),
        object=SignAnalysis(
            component="object",
            summary="The referent is the data being queried.",
            evidence=["description mentions 'query'"],
        ),
        interpretant=SignAnalysis(
            component="interpretant",
            summary="The caller understands this function fetches data.",
            evidence=[],
        ),
    )


def _make_grounding(
    fn: str = "test_fn",
    include_non_applicable: bool = True,
) -> GroundingReport:
    mappings = [
        GroundingMapping(concept=MATERIAL_CAUSE, applies=True,
                         anchor="parameters: query", explanation="Has query param."),
        GroundingMapping(concept=FORMAL_CAUSE, applies=True,
                         anchor="object schema", explanation="Formal shape exists."),
        GroundingMapping(concept=EFFICIENT_CAUSE, applies=True,
                         anchor="caller invocation", explanation="Triggered by caller."),
        GroundingMapping(concept=FINAL_CAUSE, applies=True,
                         anchor="description", explanation="Purpose is stated."),
        GroundingMapping(concept=DASEIN, applies=True,
                         anchor="world context", explanation="Assumes runtime."),
        GroundingMapping(concept=ZUHANDENHEIT, applies=True,
                         anchor="happy path", explanation="Transparent when working."),
        GroundingMapping(concept=VORHANDENHEIT, applies=True,
                         anchor="breakdown", explanation="Object on failure."),
        GroundingMapping(concept=REPRESENTAMEN, applies=True,
                         anchor=f"identifier: '{fn}'", explanation="Name is the sign."),
        GroundingMapping(
            concept=OBJECT,
            applies=False if include_non_applicable else True,
            anchor="no identifiable referent" if include_non_applicable else "referent: data",
            explanation="No referent found." if include_non_applicable else "Has referent.",
        ),
        GroundingMapping(concept=INTERPRETANT, applies=True,
                         anchor="name + description", explanation="Meaning derivable."),
        GroundingMapping(concept=GROUNDING, applies=True,
                         anchor="9/10 concepts", explanation="Analysis complete."),
        GroundingMapping(
            concept=TELOS_BRIDGE,
            applies=False if include_non_applicable else True,
            anchor="no explicit telos" if include_non_applicable else "final cause",
            explanation="No bridge." if include_non_applicable else "Bridge present.",
        ),
    ]
    return GroundingReport(function_name=fn, mappings=mappings)


def _make_analysis(
    fn: str = "test_fn",
    material_evidence: list[str] | None = None,
    final_summary: str = "The purpose is testing.",
    final_confidence: str = "high",
    world_assumptions: list[WorldAssumption] | None = None,
    transparency_conditions: list[str] | None = None,
    breakdown_conditions: list[BreakdownCondition] | None = None,
    include_non_applicable: bool = True,
) -> FullAnalysis:
    return FullAnalysis(
        function_name=fn,
        four_causes=_make_four_causes(fn, material_evidence, final_summary, final_confidence),
        dasein=_make_dasein(fn, world_assumptions, transparency_conditions, breakdown_conditions),
        semiotics=_make_semiotics(fn),
        grounding=_make_grounding(fn, include_non_applicable),
    )


# ---------------------------------------------------------------------------
# Tests for _section_header
# ---------------------------------------------------------------------------

class TestSectionHeader:
    def test_default_char_equals(self) -> None:
        result = _section_header("Hello")
        assert result == "\nHello\n====="

    def test_custom_char(self) -> None:
        result = _section_header("Title", char="-")
        assert result == "\nTitle\n-----"

    def test_underline_length_matches_title(self) -> None:
        title = "A Longer Title Here"
        result = _section_header(title)
        lines = result.split("\n")
        assert len(lines[2]) == len(title)

    def test_empty_string(self) -> None:
        result = _section_header("")
        assert result == "\n\n"

    def test_single_char_title(self) -> None:
        result = _section_header("X")
        assert result == "\nX\n="

    def test_starts_with_newline(self) -> None:
        result = _section_header("Foo")
        assert result.startswith("\n")


# ---------------------------------------------------------------------------
# Tests for _indent
# ---------------------------------------------------------------------------

class TestIndent:
    def test_single_line_default_level(self) -> None:
        result = _indent("hello")
        assert result == "  hello"

    def test_custom_level(self) -> None:
        result = _indent("text", level=4)
        assert result == "    text"

    def test_zero_level(self) -> None:
        result = _indent("no indent", level=0)
        assert result == "no indent"

    def test_multiline(self) -> None:
        result = _indent("line1\nline2\nline3", level=2)
        assert result == "  line1\n  line2\n  line3"

    def test_multiline_all_lines_indented(self) -> None:
        result = _indent("a\nb", level=3)
        for line in result.split("\n"):
            assert line.startswith("   ")

    def test_empty_string(self) -> None:
        result = _indent("", level=2)
        assert result == ""

    def test_indented_content_contains_original_text(self) -> None:
        original = "my content"
        result = _indent(original)
        assert original in result


# ---------------------------------------------------------------------------
# Tests for format_text_report
# ---------------------------------------------------------------------------

class TestFormatTextReport:
    @pytest.fixture()
    def analysis(self) -> FullAnalysis:
        return _make_analysis()

    def test_returns_non_empty_string(self, analysis: FullAnalysis) -> None:
        text = format_text_report(analysis)
        assert isinstance(text, str) and len(text) > 0

    def test_contains_function_name_in_title(self, analysis: FullAnalysis) -> None:
        text = format_text_report(analysis)
        assert "ONTOLOGICAL ANALYSIS: test_fn" in text

    def test_contains_four_causes_header(self, analysis: FullAnalysis) -> None:
        text = format_text_report(analysis)
        assert "ARISTOTELIAN FOUR CAUSES" in text

    def test_contains_heideggerian_header(self, analysis: FullAnalysis) -> None:
        text = format_text_report(analysis)
        assert "HEIDEGGERIAN PHENOMENOLOGY" in text

    def test_contains_peircean_header(self, analysis: FullAnalysis) -> None:
        text = format_text_report(analysis)
        assert "PEIRCEAN SEMIOTICS" in text

    def test_contains_grounding_header(self, analysis: FullAnalysis) -> None:
        text = format_text_report(analysis)
        assert "SYNTHETIC GROUNDING" in text

    def test_all_four_cause_types_labeled(self, analysis: FullAnalysis) -> None:
        text = format_text_report(analysis)
        for cause_type in ("MATERIAL", "FORMAL", "EFFICIENT", "FINAL"):
            assert f"[{cause_type} CAUSE]" in text

    def test_cause_confidence_appears(self, analysis: FullAnalysis) -> None:
        text = format_text_report(analysis)
        assert "high confidence" in text

    def test_material_cause_evidence_listed(self) -> None:
        analysis = _make_analysis(material_evidence=["param: location", "param: unit"])
        text = format_text_report(analysis)
        assert "param: location" in text
        assert "param: unit" in text

    def test_empty_evidence_skipped(self) -> None:
        analysis = _make_analysis(material_evidence=[])
        text = format_text_report(analysis)
        assert "MATERIAL CAUSE" in text
        assert "Evidence:" not in text.split("FORMAL CAUSE")[0].split("MATERIAL CAUSE")[1]

    def test_world_assumptions_listed(self) -> None:
        wa = [WorldAssumption("auth", "User is authenticated.", "header param")]
        analysis = _make_analysis(world_assumptions=wa)
        text = format_text_report(analysis)
        assert "[auth]" in text
        assert "User is authenticated." in text
        assert "header param" in text

    def test_transparency_conditions_listed(self) -> None:
        analysis = _make_analysis(transparency_conditions=["Input is valid.", "API is up."])
        text = format_text_report(analysis)
        assert "Input is valid." in text
        assert "API is up." in text

    def test_breakdown_conditions_with_severity(self) -> None:
        bcs = [
            BreakdownCondition("timeout", "raises exception", severity="major"),
            BreakdownCondition("bad input", "validation error", severity="minor"),
        ]
        analysis = _make_analysis(breakdown_conditions=bcs)
        text = format_text_report(analysis)
        assert "[MAJOR]" in text
        assert "[MINOR]" in text
        assert "timeout" in text
        assert "bad input" in text

    def test_breakdown_consequence_in_report(self) -> None:
        bcs = [BreakdownCondition("crash", "system halts", severity="major")]
        analysis = _make_analysis(breakdown_conditions=bcs)
        text = format_text_report(analysis)
        assert "system halts" in text

    def test_grounding_coverage_ratio_formatted(self, analysis: FullAnalysis) -> None:
        text = format_text_report(analysis)
        assert "Coverage:" in text
        assert "%" in text

    def test_grounding_applies_status(self) -> None:
        analysis = _make_analysis(include_non_applicable=True)
        text = format_text_report(analysis)
        assert "[APPLIES]" in text
        assert "[N/A]" in text

    def test_grounding_all_applicable_shows_no_na(self) -> None:
        analysis = _make_analysis(include_non_applicable=False)
        text = format_text_report(analysis)
        assert "[APPLIES]" in text
        assert "[N/A]" not in text

    def test_footer_contains_function_name(self, analysis: FullAnalysis) -> None:
        text = format_text_report(analysis)
        assert "End of ontological analysis for 'test_fn'." in text

    def test_footer_has_separator(self, analysis: FullAnalysis) -> None:
        text = format_text_report(analysis)
        assert "-" * 60 in text

    def test_semiotic_component_labels(self, analysis: FullAnalysis) -> None:
        text = format_text_report(analysis)
        for comp in ("REPRESENTAMEN", "OBJECT", "INTERPRETANT"):
            assert f"[{comp}]" in text

    def test_semiotic_evidence_in_report(self, analysis: FullAnalysis) -> None:
        text = format_text_report(analysis)
        assert "function name" in text

    def test_different_function_names(self) -> None:
        for fn in ("get_weather", "send_message", "ping"):
            text = format_text_report(_make_analysis(fn=fn))
            assert fn in text

    def test_dasein_section_heading(self, analysis: FullAnalysis) -> None:
        text = format_text_report(analysis)
        assert "DASEIN" in text

    def test_zuhandenheit_section_heading(self, analysis: FullAnalysis) -> None:
        text = format_text_report(analysis)
        assert "ZUHANDENHEIT" in text

    def test_vorhandenheit_section_heading(self, analysis: FullAnalysis) -> None:
        text = format_text_report(analysis)
        assert "VORHANDENHEIT" in text

    def test_grounding_domains_labeled(self, analysis: FullAnalysis) -> None:
        text = format_text_report(analysis)
        for domain in Domain:
            assert domain.value.upper() in text


# ---------------------------------------------------------------------------
# Tests for format_json_report
# ---------------------------------------------------------------------------

class TestFormatJsonReport:
    @pytest.fixture()
    def analysis(self) -> FullAnalysis:
        return _make_analysis()

    def test_returns_valid_json(self, analysis: FullAnalysis) -> None:
        j = format_json_report(analysis)
        parsed = json.loads(j)
        assert isinstance(parsed, dict)

    def test_contains_function_name(self, analysis: FullAnalysis) -> None:
        parsed = json.loads(format_json_report(analysis))
        assert parsed["function_name"] == "test_fn"

    def test_contains_expected_top_level_keys(self, analysis: FullAnalysis) -> None:
        parsed = json.loads(format_json_report(analysis))
        for key in ("function_name", "four_causes", "dasein", "semiotics", "grounding"):
            assert key in parsed

    def test_default_indent_two(self, analysis: FullAnalysis) -> None:
        j = format_json_report(analysis)
        assert "  " in j

    def test_custom_indent(self, analysis: FullAnalysis) -> None:
        j4 = format_json_report(analysis, indent=4)
        j2 = format_json_report(analysis, indent=2)
        assert "    " in j4
        assert len(j4) > len(j2)

    def test_roundtrip_equals_to_dict(self, analysis: FullAnalysis) -> None:
        parsed = json.loads(format_json_report(analysis))
        assert parsed == analysis.to_dict()

    def test_different_function_name_reflected(self) -> None:
        analysis = _make_analysis(fn="delete_record")
        parsed = json.loads(format_json_report(analysis))
        assert parsed["function_name"] == "delete_record"


# ---------------------------------------------------------------------------
# Tests for format_summary
# ---------------------------------------------------------------------------

class TestFormatSummary:
    @pytest.fixture()
    def analysis(self) -> FullAnalysis:
        return _make_analysis()

    def test_returns_non_empty_string(self, analysis: FullAnalysis) -> None:
        s = format_summary(analysis)
        assert isinstance(s, str) and len(s) > 0

    def test_contains_function_name(self, analysis: FullAnalysis) -> None:
        s = format_summary(analysis)
        assert "test_fn" in s

    def test_contains_grounding_fraction(self, analysis: FullAnalysis) -> None:
        s = format_summary(analysis)
        total = len(analysis.grounding.mappings)
        count = analysis.grounding.applicable_count
        assert f"{count}/{total}" in s

    def test_contains_coverage_percentage(self, analysis: FullAnalysis) -> None:
        s = format_summary(analysis)
        assert "%" in s

    def test_contains_material_confidence(self) -> None:
        analysis = _make_analysis(final_confidence="high")
        s = format_summary(analysis)
        assert "high" in s

    def test_contains_final_cause_excerpt(self) -> None:
        final_text = "Finds documents matching a search term."
        analysis = _make_analysis(final_summary=final_text)
        s = format_summary(analysis)
        assert final_text[:80] in s

    def test_long_final_summary_truncated(self) -> None:
        long_summary = "x" * 200
        analysis = _make_analysis(final_summary=long_summary)
        s = format_summary(analysis)
        assert len(s) < 500

    def test_contains_world_assumption_count(self) -> None:
        wa = [
            WorldAssumption("auth", "Auth required.", "header"),
            WorldAssumption("db", "DB up.", "param"),
            WorldAssumption("network", "Network accessible.", "description"),
        ]
        analysis = _make_analysis(world_assumptions=wa)
        s = format_summary(analysis)
        assert "3" in s

    def test_contains_breakdown_count(self) -> None:
        bcs = [
            BreakdownCondition("timeout", "error", severity="major"),
            BreakdownCondition("bad param", "validation error", severity="minor"),
        ]
        analysis = _make_analysis(breakdown_conditions=bcs)
        s = format_summary(analysis)
        assert "2" in s

    def test_summary_is_single_paragraph(self, analysis: FullAnalysis) -> None:
        s = format_summary(analysis)
        assert "\n" not in s

    def test_summary_mentions_material_confidence_label(self) -> None:
        analysis = _make_analysis()
        s = format_summary(analysis)
        assert "Material:" in s

    def test_summary_mentions_final_cause_label(self) -> None:
        analysis = _make_analysis()
        s = format_summary(analysis)
        assert "Final cause:" in s

    def test_summary_mentions_world_assumptions_label(self) -> None:
        analysis = _make_analysis()
        s = format_summary(analysis)
        assert "World assumptions:" in s

    def test_summary_mentions_breakdown_label(self) -> None:
        analysis = _make_analysis()
        s = format_summary(analysis)
        assert "Breakdown conditions:" in s
