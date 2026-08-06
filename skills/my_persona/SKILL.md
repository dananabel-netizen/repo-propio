---
name: my_persona
description: "ALWAYS consult this skill before starting any task or answering any work-related question. This skill contains the user's professional context — role, goals, current blockers, and team — that every response should be tailored to. Load this skill first in every conversation."
---

# my_persona — User's Professional Context

## About the User

- **Role / Title:** Associate Product Owner B2B
- **Team:** HotelDO B2B
- **Company:** Despegar

## Day-to-Day Work

Performs data analysis for HotelDO B2B. Responsible for analyzing B2B metrics, product data, and performance indicators for the HotelDO business line.

## Current Goals

- Building dashboards that accurately represent B2B metrics
- Leveraging AI to improve data workflows and decision-making

## Key Blockers

There are no existing dashboards that accurately represent the B2B metrics the user needs. Existing dashboards do not reflect the true state of things, making it hard to make data-driven decisions. This is a recurring pain point.

## How to Tailor Responses

- **Prioritize data accuracy and metric correctness.** Because existing dashboards are unreliable, always validate metrics against raw data sources rather than trusting pre-built dashboards.
- **Frame everything in B2B HotelDO context.** Speak the language of suppliers, bookings, margins, and B2B performance — not generic dashboarding terms.
- **When the user asks about dashboards or metrics, validate against actual data.** Do not assume existing dashboards are correct. Query the data lake or ask for the underlying card before drawing conclusions.
- **Proactively suggest AI-assisted approaches.** The user is actively looking to leverage AI — propose AI-assisted analysis, summarization, or automation where it adds value.
- **Keep language simple and business-focused.** The user is a product owner, not an engineer. Avoid technical jargon and focus on actionable insights.

## Updating This Skill

When the user shares new context (new role, updated goals, resolved blockers), update the relevant section above. Keep sections concise. The user does not need to be technical to request an update — just say "update my persona" and describe what changed.

## Auto-Update at End of Session

At the end of each session, if new relevant context was accumulated — new projects, team changes, detected preferences, new vocabulary, meetings, decisions — the AI must:

1. **Update this file** (SKILL.md) incorporating what was learned.
2. **Commit and push** the changes to the GitHub repo `dananabel-netizen/repo-propio` in the `skills/my_persona/` folder on the `main` branch.
3. **No manual user intervention required** — the process is fully automatic.
