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
- **On `main`, or on a shared feature branch** → do not start work here. Cut
  your own session branch first (section 2).
- **On a `claude/…` branch you did not create this session** → a previous
  session left it. Read its diff before adding to it, or start fresh.

## 2. One branch per session

Never commit to `main` or to a shared long-lived branch. Every session works on
its own branch and merges back. This is not a preference — several sessions
often run at once, and a shared branch means two of them edit the same files
with neither aware of the other.

**Start of session:**

```sh
TARGET=main                       # or the feature branch you were told to target
git fetch origin "$TARGET"
git checkout -B "claude/<short-task-slug>" "origin/$TARGET"
```

Web and mobile sessions create a `claude/…` branch automatically. CLI and
bridge sessions do not — they land on whatever branch was last checked out, so
you must do this explicitly.

**Push on your first commit, not your last:**

```sh
git push -u origin HEAD
```

Use `-u origin HEAD`, not a bare `git push`. `checkout -B` set your upstream to
`$TARGET`, so a bare push would send your work straight to the integration
branch with no warning. Confirm with `git rev-parse --abbrev-ref @{u}` — it must
name your own branch.

This is the rule that makes the whole scheme work. An unpushed commit is
invisible to every other session; a pushed branch is the signal that this work
exists. Do not batch commits locally and push at the end.

**Finish in the session that started it.** Verify (section 5), merge back into
`$TARGET` — or open a PR if it's large or you want it reviewed — then delete
the branch.

**Never:**

- Commit directly to `main` or a shared feature branch
- Force-push, rebase, amend or reset a branch another session might hold
- Resume a branch from a previous session without re-reading its diff first

**If `$TARGET` moved while you worked**, merge it in — do not rebase. A merge
commit keeps every other checkout valid; a rebase breaks them.

```sh
git fetch origin "$TARGET" && git merge "origin/$TARGET"
```

**Keep branches short-lived.** The cost of this scheme is merge overhead, and
it stays small only if a branch is one session, one coherent unit of work,
merged back before the session ends. A branch that lives for days recreates
the exact problem it was meant to solve.

## 3. Get to something runnable early

The expensive failure is building for an hour and then finding out you cannot
run it. Two situations lead there, and they need different responses. Work out
which one you are in before you start.

### A. Changing code that already exists

A way to check it already exists too — a test, a build, a linter, a script, a
request you can make. **Run it before you touch anything.**

- **Passes** → you now have a known-good baseline and will know if you break it.
- **Fails** → pre-existing failure. Say so now. Do not adopt it as yours, and do
  not quietly fix it as a side quest.
- **Will not run** — missing env var, no database, no credentials, service
  unreachable → **stop and say so in your first reply, before doing the work.**

Check prerequisites explicitly rather than assuming: `printenv NAME`, a
connection attempt, `--version`. Assuming is how a session gets an hour in
before discovering a connection string was never set.

### B. Building something that does not exist yet

There is no check to run first, so "verify before you build" is meaningless as
written. The equivalent discipline is: **get to something that executes within
the first few minutes, run it, then grow it.**

- Write the smallest version that runs end to end — one function, one real
  input, one real output — and run it.
- Add the rest in increments, re-running as you go.
- Do not write two hundred lines and execute them for the first time at the end.
  That is the same failure as A, just self-inflicted: when it breaks you are
  debugging two hundred unfamiliar lines instead of twenty.

### Both cases: say what "working" means before you build it

One line, at the top of your first reply:

> This is done when `<command>` produces `<observable result>`.

If you cannot finish that sentence, you do not understand the task well enough
to start — ask instead. And if the command in it turns out not to be runnable,
you have found that out in minute one rather than hour two, which is the whole
point.

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
- Prefer a command the repo already provides (a script, a make target, a CI job)
  over an ad-hoc one you compose. If you find yourself writing a fresh check,
  consider whether it belongs in the repo permanently — a check that only exists
  in one session's scrollback gets rewritten by the next session.
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
