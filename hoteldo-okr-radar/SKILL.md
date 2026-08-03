# hoteldo-okr-radar — Radar de OKRs HotelDO B2B

## 1. Propósito y cuándo activar

Activar cuando el usuario:

- Pide analizar el progreso de OKRs del trimestre
- Quiere saber qué KRs están en riesgo
- Necesita un resumen ejecutivo del estado de los OKRs
- Pide proyecciones de cumplimiento de objetivos
- Quiere generar datos estructurados para un dashboard de OKRs
- Pregunta "¿cómo van los OKRs?" o "¿qué KR está en riesgo?"
- Recibe resultados de queries del datalake y quiere que se conviertan en insights

## 2. Qué hace

Toma datos de OKRs (JSON, CSV o entrada manual) y genera:

1. **Progreso calculado**: porcentaje de avance vs target, con tendencia semanal
2. **Velocidad y proyección**: ritmo actual de avance y fecha estimada de cumplimiento
3. **Semáforo de riesgo**: 🟢 en camino, 🟡 atrasado, 🔴 en riesgo crítico
4. **Narrativa ejecutiva**: resumen en español listo para compartir con stakeholders
5. **Output estructurado**: JSON con todos los indicadores, listo para alimentar dashboards

## 3. Formatos de input

### JSON

```json
{
  "objective": "Escalar ventas de agencias via API y HTML",
  "squad": "API",
  "quarter": "H1 2026",
  "krs": [
    {
      "id": "kr21",
      "description": "Hotel Net Revenue via API",
      "current_value": 4500000,
      "target_value": 6000000,
      "baseline_value": 3000000,
      "weekly_history": [
        {"week": "2026-01-06", "value": 3100000},
        {"week": "2026-01-13", "value": 3300000},
        {"week": "2026-01-20", "value": 3600000},
        {"week": "2026-01-27", "value": 3900000},
        {"week": "2026-02-03", "value": 4200000},
        {"week": "2026-02-10", "value": 4500000}
      ]
    }
  ]
}
```

### CSV

```csv
kr_id,description,current,target,baseline,week_1,week_2,week_3
kr21,Hotel Net Revenue via API,4500000,6000000,3000000,3100000,3300000,3600000
```

### Entrada manual

El usuario describe los KRs verbalmente y el agente estructura los datos antes de aplicar el análisis.

## 4. Algoritmo de análisis

### Progreso

```
progress_pct = (current_value - baseline_value) / (target_value - baseline_value) * 100
```

Se clampea entre 0% y 100%+ (permite superar el target).

### Velocidad

```
weeks_elapsed = semanas transcurridas desde el inicio del trimestre
weeks_total  = semanas totales del trimestre
expected_progress = weeks_elapsed / weeks_total * 100
velocity = progress_pct / expected_progress
```

### Semáforo

| Color | Condición | Significado |
|-------|-----------|-------------|
| 🟢 Verde | `progress_pct >= expected_progress * 0.95` | En camino |
| 🟡 Amarillo | `progress_pct >= expected_progress * 0.75` | Atrasado |
| 🔴 Rojo | `progress_pct < expected_progress * 0.75` | En riesgo crítico |

### Proyección

- Ajusta una regresión lineal sobre `weekly_history`
- Proyecta la semana en la que se alcanzaría el `target_value`
- Si la proyección supera el fin del trimestre → "No se proyecta cumplimiento"

### Detección de anomalías

- **Cambio brusco**: variación > 20% en una semana → flag de investigación
- **Estancamiento**: 0% de crecimiento en 3+ semanas consecutivas → flag de alerta
- **Declive**: valor actual < valor de la semana anterior → flag crítico

## 5. Output

### Narrativa ejecutiva (español)

```
📊 RADAR DE OKRs — H1 2026 — Squad API

Objetivo: Escalar ventas de agencias via API y HTML

KR 2.1 — Hotel Net Revenue via API
🟡 Atrasado (75% de progreso vs 83% esperado)
Actual: $4.5M / Target: $6.0M (75% del camino)
Velocidad: 0.91x — levemente por debajo del ritmo necesario
Proyección: cumplimiento estimado en semana 12 (1 semana tarde)
⚠️ Crecimiento estable pero insuficiente. Revisar mix de agencias activas.
```

### JSON estructurado (para dashboards)

```json
{
  "objective": "Escalar ventas de agencias via API y HTML",
  "squad": "API",
  "quarter": "H1 2026",
  "generated_at": "2026-02-10T10:00:00Z",
  "summary": {
    "total_krs": 1,
    "green": 0,
    "yellow": 1,
    "red": 0,
    "overall_health": "yellow"
  },
  "krs": [
    {
      "id": "kr21",
      "description": "Hotel Net Revenue via API",
      "current_value": 4500000,
      "target_value": 6000000,
      "baseline_value": 3000000,
      "progress_pct": 75.0,
      "expected_progress_pct": 83.0,
      "velocity": 0.91,
      "status": "yellow",
      "status_label": "Atrasado",
      "projected_completion_week": 12,
      "on_track": false,
      "anomalies": [],
      "weekly_trend": "stable_growth",
      "recommendation": "Crecimiento estable pero insuficiente. Revisar mix de agencias activas."
    }
  ]
}
```

## 6. Reglas de formato

- **Idioma**: español (neutro argentino)
- **Moneda**: USD con formato $X.XM para millones, $XOK para miles
- **Semanas**: formato legible (ej: "Semana del 10-Feb") en lugar de "W26"
- **Niveles de OKR**: nomenclatura KR X.Y (ej: KR 2.1, KR 3.2)
- **Squads**: API, B2B Commercial & Engagement, B2B Efficiency & Support, Rewards B2B2C

## 7. Integración con otros skills

- **hoteldo-sql**: Generar las queries para obtener los datos crudos del datalake, luego pasarlos a este skill para análisis
- **hoteldo-arquetipos**: Clasificar agencias por arquetipo y cruzar con performance de OKRs
- **hoteldo-backlog**: Vincular iniciativas del backlog con KRs específicos

## 8. Flujo recomendado

1. El usuario pide un análisis de OKRs (o se ejecuta en automatización diaria/semanal)
2. Si hay queries SQL involucradas, usar hoteldo-sql para generarlas
3. Ejecutar las queries en Metabase / datalake
4. Estructurar los resultados como JSON (formato del punto 3)
5. Aplicar el algoritmo de análisis del punto 4 — usar `okr_radar.py` si está disponible
6. Generar la narrativa + JSON del punto 5
7. Si hay dashboard, escribir el JSON a `data/` para que `build_html.py` lo consuma

## 9. Ejemplo de uso

```
Usuario: ¿Cómo van los OKRs del squad API este trimestre?

Agente:
  1. Obtiene los datos de los KRs (via hoteldo-sql o input manual)
  2. Ejecuta okr_radar.py con los datos
  3. Devuelve la narrativa ejecutiva + JSON estructurado
  4. Marca los KRs en riesgo con recomendaciones accionables
```
