# WORKFLOW.md — The Delegation Loop

Every CRM task runs through this loop. No exceptions.

## The Loop

1. **Pick & brief.** The Architect picks the next task from `PLAN.md` and writes a
   brief to `tasks/T<NNN>-<slug>.md` containing:
   - goal (one endpoint / one component / one test file — never more)
   - exact file paths
   - function/component signatures
   - interfaces to conform to (pass those files via `--context-file`)
   - acceptance criteria

2. **Delegate.** The Architect runs:

   ```
   python scripts/delegate.py --agent <backend|frontend|qa-db> \
       --task-file tasks/T<NNN>-<slug>.md \
       [--context-file <existing code>...]
   ```

   Then reads the output in `logs/`. **Review before applying:**
   - correctness
   - contract compliance (FILE: lines + SELF-REVIEW present, only briefed files)
   - security: authz on every endpoint, no secrets, parameterized queries
   - consistency with existing code

3. **Retry policy.** Output fails review → revise the brief (be MORE specific) and
   re-delegate ONCE. Fails twice → the Architect implements it directly and notes
   why in the report.

4. **Apply & test.** Apply accepted code to files. Run `pytest -q` and (where
   applicable) `npm run build` in `frontend/`.

5. **Commit & report.** Commit on a feature branch `feat/T<NNN>-<slug>`. Write
   `reports/T<NNN>.md`: what was delegated, to whom, review verdict, test results,
   token usage.

6. **PR.** Open a PR (`gh pr create`, or the GitHub compare URL if `gh` is not
   installed) with the report as the PR body. **The human reviews and merges.
   Never merge yourself. Never push to main.**

## Hard rules

- `.env` is never committed.
- Briefs are small and fully specified — the workers run at LOW thinking and are
  weak at ambiguity.
- Always send `reasoning_effort: "low"` (delegate.py does this). Never send
  `thinking_budget` alongside it.
- Sub-agents never touch files or run commands; the Architect owns git, files,
  and PRs.
