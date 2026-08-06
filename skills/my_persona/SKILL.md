---
name: my_persona
description: "ALWAYS consult this skill before starting any task or answering any work-related question. This skill contains the user's professional context — role, goals, current blockers, and team — that every response should be tailored to. Load this skill first in every conversation."
---

# my_persona — User's Professional Context

## About the User

- **Role / Title:** Associate Product Owner B2B
- **Team:** HotelDO B2B
- **Company:** Despegar
- **Email:** dana.nabel@despegar.com

## Day-to-Day Work

Performs data analysis for HotelDO B2B. Responsible for analyzing B2B metrics, product data, and performance indicators for the HotelDO business line.

## Current Goals

- Building dashboards that accurately represent B2B metrics
- Leveraging AI to improve data workflows and decision-making
- OKRs Dashboard: mantener y evolucionar el dashboard de OKRs de Tribu B2B en producción

## Key Blockers

There are no existing dashboards that accurately represent the B2B metrics the user needs. Existing dashboards do not reflect the true state of things, making it hard to make data-driven decisions. This is a recurring pain point.

## How to Tailor Responses

- **Prioritize data accuracy and metric correctness.** Because existing dashboards are unreliable, always validate metrics against raw data sources rather than trusting pre-built dashboards.
- **Frame everything in B2B HotelDO context.** Speak the language of suppliers, bookings, margins, and B2B performance — not generic dashboarding terms.
- **When the user asks about dashboards or metrics, validate against actual data.** Do not assume existing dashboards are correct. Query the data lake or ask for the underlying card before drawing conclusions.
- **Proactively suggest AI-assisted approaches.** The user is actively looking to leverage AI — propose AI-assisted analysis, summarization, or automation where it adds value.
- **Keep language simple and business-focused.** The user is a product owner, not an engineer. Avoid technical jargon and focus on actionable insights.

---

## Active Projects

### OKRs Dashboard B2B (en producción)

Dashboard de OKRs para Tribu B2B (HotelDO B2B).

**URL:** `https://script.google.com/a/macros/despegar.com/s/AKfycbzcZ870mVvp95guN8EV1c03kR9FvdmspJL88lFOB6moWgq3ltY-cd7cKY9wcEuPRvfDUQ/exec`

**Arquitectura:**
Python (local, VPN) → queries Trino → `okrs_dashboard.html` (HTML standalone JSON embebido) → git push → rama `tablero-live` en `dananabel-netizen/tribu-b2b-dana-` → Apps Script sirve el HTML.

**Archivos clave:**
- Script principal: `tribu-b2b-dana/data-analytics/okrs-html/build_dashboard.py`
- Output: `tribu-b2b-dana/okrs_dashboard.html` → `tablero-live/okrs_dashboard.html`

**Conexión Trino:** `datalake.despegar.com:443` (requiere VPN), catalog `data.`  
**Auth:** `.env` con `TRINO_USER` + `TRINO_AUTH` — NUNCA loguear ni imprimir (Base64 reversible)

**Queries disponibles:**

| key | descripción |
|-----|-------------|
| kr21 | mensual cancelaciones por timeout |
| kr22 | mensual agencias únicas |
| kr31 | mensual net revenue (FULL JOIN con forecast) |
| kr32 | mensual activación comercial |
| kr33 | mensual frecuencia de compra |
| kr21_sem | semanal deadlines por semana (91 filas, incluye futuros) |
| kr21_sem_cum | acumulado por (semana, mes_deadline) — 106 filas |
| kr22_sem | semanal agencias únicas por semana (18 filas) |
| kr22_sem_cum | acumulado unique agencies desde inicio mes |
| kr31_sem | semanal net revenue por semana (18 filas) |
| kr31_sem_cum | acumulado net revenue (coincide con mensual) |
| kr32_sem | semanal activación por semana (18 filas) |
| kr32_sem_cum | acumulado activación cross-week |

**Tab Semanal — estructura:**
- Tarjeta 1: "Progreso semanal" — chips % compliance por semana (verde/amarillo/rojo)
- Tarjeta 2: Por cada KR → fila header KR (lila), fila "Actual" sin colores, fila "Target" gris

**Lógica acumulados en `renderSemanal()`:**
- `acum21(w)`: `kr21_sem_cum.find(semana===w && mes_deadline month===today)` → pct_timeout_acum
- `acum22(w)`: `kr22_sem_cum.find(semana===w)` → cant_agencias_acum_mes
- `acum31(w)`: `kr31_sem_cum.find(semana===w)` → net_revenue_acum_mes
- `acum32(w)`: `kr32_sem_cum.find(semana===w)` → pct_activacion_acum
- `acum33(w)`: valor mensual repetido (kr33 mensual)

Eje de semanas: `weeks` de `kr22_sem` filtrado a `semMes(w)===today`

**Evolución pendiente:**
Agregar debajo de la tarjeta de compliance una tabla con DOS filas por KR:
1. **"Semana"** — valor solo de esa semana cerrada (snapshot, NO acumulado)
2. **"Acumulado"** — valor acumulado desde el 1ro del mes

---

## Workflow conocido — Auto-update de my_persona

Dana estableció que al final de cada sesión, si surgió contexto nuevo (proyectos, decisiones, preferencias), el AI debe actualizar este SKILL.md y pushear al repo `dananabel-netizen/repo-propio` en `main`, sin intervención manual.

---

## Updating This Skill

When the user shares new context (new role, updated goals, resolved blockers), update the relevant section above. Keep sections concise. The user does not need to be technical to request an update — just say "update my persona" and describe what changed.

## Auto-Update at End of Session

At the end of each session, if new relevant context was accumulated — new projects, team changes, detected preferences, new vocabulary, meetings, decisions — the AI must:

1. **Update this file** (SKILL.md) incorporating what was learned.
2. **Commit and push** the changes to the GitHub repo `dananabel-netizen/repo-propio` in the `skills/my_persona/` folder on the `main` branch.
3. **No manual user intervention required** — the process is fully automatic.
