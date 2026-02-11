"""Safety guardrails using LLM-based risk scoring."""
from dataclasses import dataclass
from app.providers.llm import get_llm_provider, Message
from app.config import get_settings


@dataclass
class GuardrailResult:
    """Result of a guardrail check."""
    passed: bool
    risk_score: int  # 0-100
    threshold: int
    affected_systems: list[str]
    worst_case_scenario: str
    rationale: str
    suggestion: str | None = None


SCORING_PROMPT = """You are a home automation safety evaluator. Score the risk level of the proposed action.

Your job is to evaluate whether a home automation request could cause:
1. Physical harm to people or pets
2. Property damage (fire, flood, freezing, etc.)
3. Security vulnerabilities (unauthorized access, disabled alarms)
4. Privacy concerns (cameras, microphones, presence detection)

IMPORTANT: Users give custom friendly names to their Home Assistant devices (e.g. "bob" for a vacuum, "sunshine" for a lamp). An unrecognized device name does NOT make a request dangerous. Score based on the ACTION being performed, not the device name. If the device type is mentioned (e.g. "vacuum cleaner named bob"), use that type for your assessment. If neither the type nor name is clear, default to a low score (10-20) since most home devices are safe to toggle.

Rate the risk from 0-100:
- 0-20: Safe (lights, TV, media, fans, vacuums, simple queries, unknown but likely safe devices)
- 21-50: Low risk (thermostats within normal range, schedules for safe devices)
- 51-70: Medium risk (garage doors, irrigation, HVAC extremes)
- 71-90: High risk (door locks, security systems, automations with safety implications)
- 91-100: Critical (disabling safety systems, unlocking based on single sensor)

Consider failure modes: What if sensors fail? What if someone is home unexpectedly? What if it triggers at the wrong time?

Respond in this exact JSON format only:
{"risk_score": <0-100>, "affected_systems": ["list"], "worst_case": "brief scenario", "rationale": "why this score", "suggestion": "how to make it safer" or null}"""


class SafetyGuardrails:
    """LLM-based safety guardrails with configurable threshold."""

    def __init__(self):
        self.llm = get_llm_provider()

    async def check(self, message: str) -> GuardrailResult:
        """Run LLM-based safety check on a message."""
        import json

        settings = get_settings()
        threshold = settings.guardrails_threshold

        # If threshold is 0, guardrails are disabled
        if threshold == 0:
            return GuardrailResult(
                passed=True,
                risk_score=0,
                threshold=0,
                affected_systems=[],
                worst_case_scenario="Guardrails disabled",
                rationale="Safety checks are disabled by configuration"
            )

        # Run LLM scoring
        messages = [
            Message(role="system", content=SCORING_PROMPT),
            Message(role="user", content=f"Evaluate this home automation request:\n\n{message}")
        ]

        try:
            response = await self.llm.chat(messages)

            # Parse JSON response
            content = response.content or "{}"
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            data = json.loads(content.strip())

            risk_score = int(data.get("risk_score", 50))
            passed = risk_score < threshold

            return GuardrailResult(
                passed=passed,
                risk_score=risk_score,
                threshold=threshold,
                affected_systems=data.get("affected_systems", []),
                worst_case_scenario=data.get("worst_case", "Unknown risk"),
                rationale=data.get("rationale", "Unable to assess"),
                suggestion=data.get("suggestion")
            )

        except Exception as e:
            # If safety check itself fails (LLM error, timeout, etc.),
            # let the request through rather than blocking the user.
            import logging
            logging.getLogger(__name__).warning(f"Safety check failed, allowing request: {e}")
            return GuardrailResult(
                passed=True,
                risk_score=0,
                threshold=threshold,
                affected_systems=[],
                worst_case_scenario="Safety check unavailable",
                rationale=f"Safety evaluation could not be completed: {str(e)}"
            )

    def format_rejection(self, result: GuardrailResult) -> str:
        """Format a user-friendly rejection message."""
        lines = [
            "**Safety Check Failed**",
            "",
            f"**Risk Score:** {result.risk_score}/100 (threshold: {result.threshold})",
            "",
            f"**Affected Systems:** {', '.join(result.affected_systems) or 'None identified'}",
            "",
            f"**Potential Risk:** {result.worst_case_scenario}",
            "",
            f"**Reason:** {result.rationale}"
        ]

        if result.suggestion:
            lines.extend([
                "",
                f"**Suggestion:** {result.suggestion}"
            ])

        lines.extend([
            "",
            "_Adjust the safety threshold in Settings if this seems too strict._"
        ])

        return "\n".join(lines)
