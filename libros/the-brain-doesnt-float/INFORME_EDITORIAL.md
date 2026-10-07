# The Brain Doesn’t Float — Informe editorial (edición KDP, inglés académico estadounidense)

## 1. Análisis de las traducciones

| Archivo | Contenido | Valoración |
|---|---|---|
| `gemini-code-1_.md` | Fragmento de 95 líneas (portada, índice y prólogo hasta «We live in…»). Truncado. | Prácticamente idéntico al CORREGIDO. Solo aporta una variante estilística mejor («On some mornings, I catch myself counting them»), que se ha incorporado. |
| `…_american_english_CORREGIDO.md` | Libro completo (≈52.000 palabras). | Base de la edición. Inglés estadounidense fluido y bien puntuado, pero con problemas de rigor, repeticiones y restos de briefing de diseño. |

## 2. Cambios aplicados al texto maestro (`manuscrito/the_brain_doesnt_float_EN.md`)

**Registro académico**
- Citas en el texto en formato APA 7 (autor, año) en todas las afirmaciones científicas y nueva sección **References** con 52 obras completas.
- La «Annotated Bibliography» pasa a **Recommended Reading** (normalizada en APA).
- Se matizan con lenguaje académico las afirmaciones de evidencia débil o debatida (Polyvagal Theory, «adrenal fatigue», craneosacral, fascia como «mayor órgano sensorial», power posing, epigenética).

**Correcciones científicas**
- Psoas: no es «el único músculo que une columna y piernas» (el piriforme une sacro y fémur) → «único que une la columna lumbar directamente al fémur».
- Plexo sacro: L4–S3 → **L4–S4** (y coherencia con el resumen del cap. 6, que decía S1–S4 + coccígeo).
- Cortisol: no «activa» el sistema inmune → lo **modula** (y lo suprime de forma crónica).
- «Adrenal fatigue»: no es diagnóstico reconocido (Cadegiani & Kater, 2016); se sustituye «agotamiento adrenal» por hipocortisolismo (Fries et al., 2005).
- «Robo de colesterol»: sustituido por el mecanismo documentado (supresión del eje HPG por CRH y glucocorticoides).
- Sistema nervioso entérico: «cien millones» → 200–600 millones (Furness, 2006).
- Hipocampo y TEPT: atribuido a Bremner et al. (1995), no a van der Kolk.
- Ínsula/interocepción: modelo de A. D. Craig, además de Damasio.
- William James (1884) no era «obsesionado con la mente»: es el gran precursor de la emoción corporal.
- Chakras: no aparecen como sistema en los Vedas; elaboración tántrica (Ṣaṭ-cakra-nirūpaṇa). Pétalos de Muladhara: sílabas *vaṃ, śaṃ, ṣaṃ, saṃ*.
- «Lo no simbolizado tiende a repetirse» atribuido correctamente a Freud (1914).
- Piriforme: «15 %» → «una de cada seis personas» (Smoll, 2010). Pie: «7.000 terminaciones» → «miles de mecanorreceptores».
- Kapalabhati: añadidas contraindicaciones (embarazo, HTA, epilepsia, cirugía abdominal).

**Coherencia y estilo**
- Eliminadas repeticiones casi literales (prólogo/2.1, Reich-Lowen 1.2/1.11, Ida Rolf 3.6/3.8, Myers 3.4/3.10, glúteos 4.5, señales de progreso 14.5).
- Contradicción en el epílogo («me sigue sorprendiendo» / «no me sorprende») resuelta.
- Joan y Damián compartían el mismo hito (sentir hambre): diferenciados.
- Adaptación al lector estadounidense: «in this country», referencia al español en «pelvic floor», «Dr. Carballo» (en EE. UU. implica doctorado) → «Lluís».
- Nueva sección 6.8 (caminar descalzo, antes sin título); cierre añadido a 3.13; «tensegrity» explicado (figuraba como concepto clave sin desarrollo).
- Los 15 bloques «[INFOGRAPHIC]» (briefings de diseño con errores y contenido genérico) se sustituyen por recuadros **Chapter at a Glance** fieles al capítulo; añadido el del cap. 13.
- Página de créditos adaptada a KDP («Independently published», excepción de cita, aviso de salud ampliado) y nueva sección **About the Author**.

## 3. Archivos para KDP (`kdp/`)

| Archivo | Uso en KDP |
|---|---|
| `the_brain_doesnt_float_KDP_6x9_interior.pdf` | Interior de tapa blanda/dura · 6 × 9 in · sin sangrado · 184 páginas · EB Garamond incrustada · márgenes espejo (interior 0,875 in, exterior 0,65 in) · capítulos en página impar · índice con paginación real · cabeceras vivas. |
| `the_brain_doesnt_float_KDP_ebook.epub` | Kindle eBook (índice navegable). |
| `the_brain_doesnt_float_KDP_6x9.docx` | Copia editable 6 × 9. |

**Nota para la portada:** con 184 páginas en papel blanco el lomo mide 184 × 0,002252 = **0,414 in** (crema: 184 × 0,0025 = 0,46 in). Ancho total de la cubierta con sangrado (blanco): 12,664 in × 9,25 in.

Regenerar todo: `python3 build/build.py`
