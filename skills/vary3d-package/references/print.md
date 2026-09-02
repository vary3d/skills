# Print notes in `README.md`

For printable parts, write a `## Print` section in the package README (Import maps the whole README to Documentation). Do not put `print` on `info.json` — `validate-info.py` rejects that key. Do not dump every slicer setting, and do not leave notes only in chat.

```markdown
## Print

- **Settings:** PLA, 0.2mm layer, 2 walls, 15% gyroid infill, no supports.
- **Orientation:** Place a flange on the bed.
- **Why:** Keeps honeycomb walls near vertical.
```

`generate-readme.py` **preserves** this section when it regenerates listing facts. If it is missing, add it after generate (printable parts). Omit the section for non-printable sculpture.

If the source has a `part` enum (split for print): keep it. Orientation / why name each printable token and the count (`Print 1× base, 1× lid`). `part="all"` is assembled preview only — not the print export. Do not invent a split when packaging. Do not add `variants.json` presets that only switch `part`. Listing **`cover.py`** uses the file default (`all`) so the card shows the assembly; do not render the cover from a single token unless the user asked.

Assembly steps MAY continue under the same `## Print` heading.

Starting numbers (0.4 mm nozzle) if the source did not already specify:

| Quantity | Default |
|---|---|
| Wall | ≥ 1.2 mm (2.0 better) |
| Layer | 0.2 mm |
| Sliding clearance | 0.3–0.5 mm (print-in-place 0.4–0.5) |
| Overhang | ≤ 45° or declare supports |
| Bed edge | Chamfer 0.4–0.8 mm, not a bed fillet |
| Clearance holes | M3→3.2, M4→4.3, M5→5.3 |

Load-bearing: 3–4 walls, 25–40% infill, maybe PETG. Vase: 1 wall. Tall skinny: brim. Outdoor / heat: PETG or ASA. TPU: slow, extra clearance.

Do not promise food-contact or IP waterproof ratings unless the user only wants splash resistance.

This skill does not redesign for printability. If the part cannot print as-is, say so in README `## Print` / the reply; do not silently thicken walls (that changes shape — see [normalize.md](normalize.md)).
