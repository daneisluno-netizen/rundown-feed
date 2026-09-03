# Working agreement

Portable rules for any Claude session in Dane's repos. Copy this file into other
repos as-is. Repo-specific facts belong in that repo's `CLAUDE.md`, not here.

The point of this file is cost. Every rule below exists because skipping it has
produced work that had to be thrown away and redone.

---

## 1. Orient before you touch anything

Run this first, every session, before reading source or writing code:

```sh
git status --short                          # uncommitted work already here?
git log --oneline -5                        # what just happened?
git log --oneline @{u}..HEAD 2>/dev/null | wc -l   # unpushed commits
git branch --show-current
```

Then stop and read the result:

- **Uncommitted changes you did not make** → someone (Dane, or another session)
  is mid-flight. Do not build on top of it and do not clean it up. Say what you
  found and ask before proceeding.
- **More than ~5 unpushed commits** → this branch is drifting from the remote.
  Say so. Long-lived unpushed stacks are how work gets lost and duplicated.
- **A branch you were not told to work on** → stop. Ask.

## 2. Assume another session is running right now

Several sessions often share one branch. That is the single biggest source of
redone work: two sessions edit the same files, neither knows.

- Commit in small, complete units. Push as soon as a unit is coherent. An
  unpushed commit is invisible to every other session.
- Before a long edit to a shared file, re-check `git status` — a session that
  started ten minutes ago may already have changed it.
- Never `git checkout .`, `git reset --hard`, `git stash` someone else's work,
  or force-push a shared branch. If the tree is in a state you did not create,
  report it; do not tidy it.

## 3. Preflight: prove you can verify BEFORE you build

The expensive failure is doing the work and then discovering you cannot run it.
Before writing code, confirm you can run the thing that will prove it works.

- Identify the verification command (test, build, lint, script, curl).
- **Run it now, unchanged, and confirm it passes on current HEAD.** If it fails
  before your change, that is a pre-existing failure — say so and do not adopt it.
- Confirm the inputs it needs exist: env vars, DB connection strings, secrets,
  services, network access. Check with `printenv NAME` — do not assume.
- **Missing prerequisite → say so immediately, at the top of your reply, before
  doing the work.** Do not build for twenty minutes and then report you cannot
  test it. That is the pattern that costs the most.

## 4. Read the real thing, not your memory of it

- Read a file before editing it. Do not patch from an assumption about its shape.
- Do not invent flags, config keys, function names, or API fields. If you have
  not seen it in this repo or in fetched documentation, you do not know it exists.
- For any external API, library version, pricing, or model behaviour: look it up.
  Getting this wrong is not a small error — it produces code that fails on first
  run and takes a full cycle to find.

## 5. Verify before you report

"Done" means observed working, not written and plausible.

- Run the verification command. Paste the actual output.
- If it fails, say it failed and show it. Never report success you did not see.
- If you skipped a step, say which step and why.
- Partially done is a legitimate answer. Silently-narrowed scope is not — if
  part of the job is blocked, finish everything else and state plainly what is
  left and why.

## 6. Scale caution to blast radius

| Action | Rule |
|---|---|
| Read, search, run tests | Just do it |
| Edit code on the assigned branch | Do it, then verify |
| Delete files, rewrite history, drop DB objects | Look at the target first, then confirm with Dane |
| Push to a branch not assigned to you | Never |
| Anything outward-facing (publish, send, deploy) | Confirm first, every time |

## 7. When you hit a failure, write it down

A failure that gets fixed and forgotten will be paid for again next week.

When something fails for a non-obvious reason — a missing env var, a URL format
that silently returns HTML, a tool that needs a flag nobody documents — append
one entry to `docs/claude/GOTCHAS.md` in the same commit as the fix.

One entry. Three lines. Do not write an essay.

## 8. Ask early or not at all

Ask when two readings of the request would produce materially different work,
and ask **before** building, not after. Otherwise make the call, state the
assumption in one line, and carry on. A question asked after the work is done
costs more than a wrong assumption stated up front.
