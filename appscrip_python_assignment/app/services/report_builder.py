from datetime import datetime

from app.schemas.analyze import CollectedData, AIAnalysis


def build_markdown_report(collected: CollectedData, analysis: AIAnalysis) -> str:
    """
    Format the AIAnalysis into a structured markdown report.
    """

    sector_title = collected.sector.title()
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    lines: list[str] = []

    # Title
    lines.append(f"# Trade Opportunities Report — {sector_title} (India)")
    lines.append("")
    lines.append(f"_Generated at: {timestamp}_")
    lines.append("")

    # Executive summary
    lines.append("## 1. Executive Summary")
    lines.append("")
    lines.append(analysis.summary or "No summary available.")
    lines.append("")

    # Time horizon
    if analysis.time_horizon:
        lines.append("### Suggested Time Horizon")
        lines.append("")
        lines.append(f"- {analysis.time_horizon}")
        lines.append("")

    # Opportunities
    lines.append("## 2. Key Trade Opportunities")
    lines.append("")
    if analysis.opportunities:
        for idx, opp in enumerate(analysis.opportunities, start=1):
            lines.append(f"{idx}. {opp}")
    else:
        lines.append("- No specific opportunities identified.")
    lines.append("")

    # Risks
    lines.append("## 3. Key Risks & Watchpoints")
    lines.append("")
    if analysis.risks:
        for idx, risk in enumerate(analysis.risks, start=1):
            lines.append(f"{idx}. {risk}")
    else:
        lines.append("- No major risks identified.")
    lines.append("")

    # Evidence
    lines.append("## 4. Evidence & Supporting Signals")
    lines.append("")
    if analysis.evidence_points:
        for point in analysis.evidence_points:
            lines.append(f"- {point}")
    else:
        lines.append("- Evidence not available from current data.")
    lines.append("")

    # Raw sources section
    lines.append("## 5. Source Snippets (from web search)")
    lines.append("")
    for item in collected.items:
        lines.append(f"### {item.title}")
        if item.url:
            lines.append(f"- URL: {item.url}")
        if item.snippet:
            lines.append(f"- Note: {item.snippet}")
        lines.append("")

    lines.append("---")
    lines.append(
        "_This report was generated automatically by the Trade Opportunities API using web search and Gemini._"
    )

    return "\n".join(lines)
