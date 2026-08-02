"""Tests for structured EUR-Lex XML parsing."""

from eke.application.eurlex import (
    EurLexDocumentNodeKind,
)
from eke.infrastructure.eurlex import (
    XmlEurLexDocumentStructureParser,
)

PAYLOAD = b"""<DOCUMENT>
 <PREAMBLE id="preamble">
  <RECITAL id="recital-1">
   <NUMBER>(1)</NUMBER>
   <TEXT>Financial stability should be protected.</TEXT>
  </RECITAL>
 </PREAMBLE>
 <CHAPTER id="chapter-1">
  <NUMBER>I</NUMBER>
  <HEADING>General provisions</HEADING>
  <ARTICLE id="article-1">
   <NUMBER>Article 1</NUMBER>
   <HEADING>Subject matter</HEADING>
   <PARAGRAPH id="article-1-paragraph-1">
    <NUMBER>1.</NUMBER>
    <TEXT>This Regulation lays down uniform rules.</TEXT>
    <FOOTNOTE id="fn-1">
     <TEXT>See also Article 2.</TEXT>
    </FOOTNOTE>
   </PARAGRAPH>
  </ARTICLE>
 </CHAPTER>
 <ANNEX id="annex-1">
  <NUMBER>Annex I</NUMBER>
  <HEADING>Reporting template</HEADING>
  <TABLE id="table-1">
   <TR><TD>Field</TD><TD>Value</TD></TR>
  </TABLE>
  <FORMULA id="formula-1">CET1 / RWA</FORMULA>
  <FIGURE id="figure-1" />
 </ANNEX>
</DOCUMENT>"""


def test_parser_preserves_hierarchy_and_embedded_content() -> None:
    structure = (
        XmlEurLexDocumentStructureParser()
        .parse(PAYLOAD)
    )

    assert tuple(
        node.kind for node in structure.nodes
    ) == (
        EurLexDocumentNodeKind.PREAMBLE,
        EurLexDocumentNodeKind.RECITAL,
        EurLexDocumentNodeKind.CHAPTER,
        EurLexDocumentNodeKind.ARTICLE,
        EurLexDocumentNodeKind.PARAGRAPH,
        EurLexDocumentNodeKind.FOOTNOTE,
        EurLexDocumentNodeKind.ANNEX,
        EurLexDocumentNodeKind.TABLE,
        EurLexDocumentNodeKind.FORMULA,
        EurLexDocumentNodeKind.VISUAL,
    )

    article = structure.node_by_id("article-1")
    assert article is not None
    assert article.parent_id == "chapter-1"
    assert article.heading == "Subject matter"

    paragraph = structure.node_by_id(
        "article-1-paragraph-1"
    )
    assert paragraph is not None
    assert paragraph.text == (
        "This Regulation lays down uniform rules."
    )
    assert paragraph.embedded_content_ids == (
        "fn-1",
    )

    annex = structure.node_by_id("annex-1")
    assert annex is not None
    assert annex.embedded_content_ids == (
        "table-1",
        "formula-1",
        "figure-1",
    )
