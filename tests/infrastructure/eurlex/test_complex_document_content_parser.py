"""Tests for complex EUR-Lex XML content parsing."""

from eke.application.eurlex import (
    EurLexVisualKind,
)
from eke.infrastructure.eurlex import (
    XmlEurLexComplexContentParser,
)

PAYLOAD = b"""<DOCUMENT>
 <ANNEX id="annex-1">
  <TABLE id="table-1">
   <CAPTION>Reporting template</CAPTION>
   <TR>
    <TH rowspan="2">Field</TH>
    <TH colspan="2">Values</TH>
   </TR>
   <TR>
    <TD>A</TD>
    <TD>B</TD>
   </TR>
  </TABLE>
  <FORMULA id="formula-1">
   <math xmlns="http://www.w3.org/1998/Math/MathML">
    <mi>x</mi><mo>=</mo><mn>1</mn>
   </math>
  </FORMULA>
  <FOOTNOTE id="fn-1">
   <MARKER>1</MARKER>
   <TEXT>See Article 2.</TEXT>
  </FOOTNOTE>
  <FIGURE
   id="figure-1"
   kind="CHART"
   src="chart.svg"
   type="image/svg+xml"
   alt="Capital ratio chart"/>
 </ANNEX>
</DOCUMENT>"""


def test_parser_extracts_complex_content() -> None:
    content = (
        XmlEurLexComplexContentParser()
        .parse(PAYLOAD)
    )

    assert len(content.tables) == 1
    assert len(content.formulas) == 1
    assert len(content.footnotes) == 1
    assert len(content.visuals) == 1

    table = content.tables[0]
    assert table.parent_node_id == "annex-1"
    assert table.caption == (
        "Reporting template"
    )
    assert table.cells[0].row_span == 2
    assert table.cells[1].column_span == 2

    formula = content.formulas[0]
    assert formula.mathml is not None
    assert "http://www.w3.org/1998/Math/MathML" in formula.mathml
    assert "<mi" in formula.mathml or "<ns0:mi" in formula.mathml

    footnote = content.footnotes[0]
    assert footnote.marker == "1"
    assert footnote.referenced_from == (
        "annex-1",
    )

    visual = content.visuals[0]
    assert visual.kind is (
        EurLexVisualKind.CHART
    )
    assert visual.source_uri == "chart.svg"
    assert visual.media_type == (
        "image/svg+xml"
    )
