# Bilingual Summary Format

Use this structure after running `scripts/collect_recent_work.py`.

## Required Sections

1. `Period`
   - State the date range and repository.
2. `English`
   - Start with a short business summary paragraph.
   - Add flat bullets for:
     - `Changes made`
     - `Features or areas affected`
     - `Codebase impact`
     - `Change volume`
     - `PR and issue context`
     - `Pending items`
3. `Spanish`
   - Mirror the English section with the same facts.
   - Keep wording natural in Spanish, but keep the meaning aligned.

## Content Rules

- Mention the number of commits, unique files changed, insertions, and
  deletions.
- Use path areas, PR titles, and issue titles to name the affected features or
  workflows.
- Mention open PRs, draft PRs, open issues, local uncommitted changes, and
  ahead-of-upstream commits as pending work when they appear in the payload.
- If GitHub data is missing, say that PR and issue history could not be
  checked and continue with the git evidence.
- Keep the tone business-facing, but do not remove meaningful technical
  detail.
- Do not say that work is complete if the payload contains open or draft
  items.

## Suggested Markdown Skeleton

```markdown
## Period
- Repo: <repo>
- Window: <since> to <until>

## English
<one short paragraph>

- Changes made: <specific change summary>
- Features or areas affected: <areas and feature names>
- Codebase impact: <architectural or operational effect>
- Change volume: <commits/files/+lines/-lines>
- PR and issue context: <relevant PRs/issues or note that none were found>
- Pending items: <open follow-ups or "No explicit pending items found.">

## Spanish
<one short paragraph>

- Cambios realizados: <mirror of English facts>
- Funcionalidades o areas afectadas: <mirror of English facts>
- Impacto en el codigo base: <mirror of English facts>
- Volumen del cambio: <mirror of English facts>
- Contexto de PRs e issues: <mirror of English facts>
- Pendientes: <mirror of English facts>
```
