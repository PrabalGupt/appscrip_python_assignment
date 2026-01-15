from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import with_rate_limit
from app.schemas.auth import UserInDB
from app.schemas.analyze import AnalyzeResponse
from app.services.collector import collect_sector_info
from app.services.ai_client import analyze_with_gemini
from app.services.report_builder import build_markdown_report

router = APIRouter(tags=["analysis"])


@router.get(
    "/analyze/{sector}",
    response_model=AnalyzeResponse,
    summary="Analyze a sector and return a markdown trade opportunities report",
)
async def analyze_sector(
    sector: str,
    current_user: UserInDB = Depends(with_rate_limit),
):
    """
    Analyze a given sector in India and return a structured markdown report.

    Steps:
    1. Validate sector input.
    2. Collect recent web information about the sector (India-focused).
    3. Use Gemini to analyze the collected data.
    4. Build a markdown report from the AI analysis.
    """

    sector_clean = sector.strip().lower()
    if not sector_clean or len(sector_clean) > 60:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid sector name.",
        )

    try:
        # Step 1: Collect data
        collected = await collect_sector_info(sector_clean, country="India")

        # Step 2: AI analysis (Gemini)
        analysis = await analyze_with_gemini(collected)

        # Step 3: Build markdown report
        markdown = build_markdown_report(collected, analysis)

        return AnalyzeResponse(
            sector=sector_clean,
            markdown_report=markdown,
        )

    except HTTPException:
        # Let FastAPI handle explicit HTTP errors as-is
        raise
    except Exception as exc:
        # Wrap unexpected errors as 502 (bad gateway)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to generate analysis: {exc}",
        ) from exc
