from typing import List
import json
import re

import google.generativeai as genai

from app.config import settings
from app.schemas.analyze import CollectedData, AIAnalysis

# Configure Gemini client using API key from config
genai.configure(api_key=settings.gemini_api_key)

DEFAULT_MODEL_NAME = "gemini-2.5-flash"


def _build_prompt(collected: CollectedData) -> str:
    """
    Build a structured prompt for Gemini using collected web data.
    """
    lines: List[str] = []

    lines.append(
        f"You are a financial markets analyst focused on Indian sectors. Analyze the '{collected.sector}' sector in {collected.country}."
    )
    lines.append(
        "I will provide you a list of recent web search results (titles, snippets, URLs). "
        "Use them as noisy signals: do NOT quote them verbatim, but synthesize a clean overview."
    )
    lines.append("")
    lines.append("Search Results:")
    for idx, item in enumerate(collected.items, start=1):
        lines.append(
            f"{idx}. Title: {item.title}\n   Snippet: {item.snippet}\n   URL: {item.url or 'N/A'}"
        )
    lines.append("")
    lines.append(
        "Your job: produce a structured assessment specifically for *trading opportunities* in this sector in India."
    )
    lines.append("Please include:")
    lines.append("1. A concise summary of the current situation and trend.")
    lines.append(
        "2. 4–6 concrete trade opportunity ideas (e.g., themes, catalysts, time horizons)."
    )
    lines.append(
        "3. 3–5 key risks or uncertainties that traders should watch for (policy, macro, sector-specific)."
    )
    lines.append(
        "4. A suggested time horizon classification (e.g., 'short-term 3-6 months' or 'medium-term 6-18 months')."
    )
    lines.append(
        "5. 4–6 key evidence points in bullet form (you can loosely reference ideas from the snippets but do not copy sentences)."
    )
    lines.append("")
    lines.append(
        "Respond ONLY with a single JSON object, no surrounding text, no explanation, no markdown fences."
    )
    lines.append(
        'The JSON keys MUST be exactly: "summary" (string), '
        '"opportunities" (array of strings), '
        '"risks" (array of strings), '
        '"time_horizon" (string), '
        '"evidence_points" (array of strings).'
    )

    return "\n".join(lines)


def _extract_json(text: str) -> dict:
    """
    Try to robustly extract a JSON object from the model output.
    Handles cases like:
    - plain JSON
    - wrapped in ```json ... ```
    - some text before/after JSON
    """

    text = text.strip()

    # 1. Try plain JSON first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2. Try to extract content inside ```json ... ``` or ``` ... ```
    fence_match = re.search(r"```json(.*)```", text, re.DOTALL | re.IGNORECASE)
    if not fence_match:
        fence_match = re.search(r"```(.*)```", text, re.DOTALL)
    if fence_match:
        inner = fence_match.group(1).strip()
        try:
            return json.loads(inner)
        except json.JSONDecodeError:
            # fall through
            pass

    # 3. Try to find the first '{' and last '}' and parse that substring
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = text[start : end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    # If all attempts fail, raise explicit error
    raise RuntimeError("Gemini response was not valid JSON")


async def analyze_with_gemini(collected: CollectedData) -> AIAnalysis:
    """
    Call Gemini to analyze the collected data and return structured AIAnalysis.
    """

    prompt = _build_prompt(collected)

    model = genai.GenerativeModel(DEFAULT_MODEL_NAME)
    response = await model.generate_content_async(prompt)

    if not response or not response.candidates:
        raise RuntimeError("Empty response from Gemini")

    # Concatenate all text parts just in case
    texts: List[str] = []
    for part in response.candidates[0].content.parts:
        if hasattr(part, "text") and part.text:
            texts.append(part.text)
    full_text = "\n".join(texts).strip()

    data = _extract_json(full_text)

    return AIAnalysis(
        summary=data.get("summary", "").strip(),
        opportunities=data.get("opportunities", []) or [],
        risks=data.get("risks", []) or [],
        time_horizon=data.get("time_horizon"),
        evidence_points=data.get("evidence_points", []) or [],
    )
