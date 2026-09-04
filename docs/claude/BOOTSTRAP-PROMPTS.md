# Bootstrap prompts

Paste-ready prompts for rolling this system out beyond this repo.

Each one is self-contained: a fresh Claude Code session has none of the context
that produced these docs, so the prompt has to carry the reasoning, not just the
instruction. A prompt that only says what to do gets a plausible guess at why,
and the why is what determines whether the result is any good.

Two prompts, because the jobs have very different risk profiles:

| | Prompt | Where to run it | Risk |
|---|---|---|---|
| 1 | Global config and hooks | A session on your own machine | Low — new files, backed up |
| 2 | Roll out to another repo | A session with that repo checked out | Higher — touches real work in flight |

Run 1 first. It is quick and its result makes 2 safer.

---

## Prompt 1 — global rules and hooks on the local machine

Run this in a Claude Code session **on your own machine**. A cloud session
cannot do this: it runs in a throwaway container and cannot reach your
`~/.claude/` directory.

```text
Context — read this before doing anything.

I run several Claude Code sessions at once, across a few repos. They keep
redoing work. The three causes I have identified, from session metadata:

1. Concurrent sessions share one long-lived branch. Unpushed commit counts
   climbed 19 -> 68 over five days with dirty worktrees throughout, so two
   sessions edited the same files with neither aware of the other.
2. Sessions discover blockers mid-task. One finished its work and only then
   reported it could not test anything, because a database connection string
   was never set — knowable in the first minute.
3. "Done" has meant "written and plausible" rather than "observed working",
   because no verification step was defined up front.

I already have repo-level docs that address this, in the repo
daneisluno-netizen/rundown-feed under docs/claude/ — WORKING-AGREEMENT.md,
GOTCHAS.md and CLAUDE.md.template. Read WORKING-AGREEMENT.md first; it is the
source of the rules below. Fetch it from GitHub, or from a local clone if I
have one.

That tier only helps sessions that clone that specific repo. I want the same
rules to apply in every repo I open, and I want the parts that can be enforced
to be enforced rather than merely requested.

Your task, in this order:

1. Report what already exists before changing anything. Show me the contents of
   ~/.claude/CLAUDE.md (if any), ~/.claude/settings.json, and any hook scripts
   already in ~/.claude/. Do not overwrite anything until I have seen this.

2. Create or update ~/.claude/CLAUDE.md with the global rules, adapted from
   rundown-feed's WORKING-AGREEMENT.md. Keep it under about 60 lines: it loads
   on every session in every repo, so its length is a recurring token cost, and
   a long file gets skimmed rather than followed. It must cover, at minimum:
   - Orient first: git status, unpushed count, current branch, before any edit.
   - One branch per session: claude/<slug> cut from the integration branch,
     pushed with `git push -u origin HEAD` on the FIRST commit, merged back
     before the session ends. Never commit directly to a shared branch. Never
     force-push, rebase or reset a branch another session might hold. Merge, do
     not rebase, when the target moves.
   - Before building: if the code exists, run its check first and report a
     check that will not run as a blocker in the first reply, not after the
     work. If the code does not exist yet, get to something that executes
     within minutes and grow it — do not write two hundred lines and run them
     for the first time at the end.
   - State what "working" means as a runnable command before starting.
   - Report failures as failures, with the actual output.
   If a ~/.claude/CLAUDE.md already exists, show me a diff and let me approve it
   rather than replacing it.

3. Add hooks so the rules that can be automated do not depend on a model
   remembering them. Use the update-config skill if it is available to you.
   I want, at minimum:
   - A SessionStart hook that prints the current branch, whether the tree is
     dirty, and the unpushed commit count. This makes step 1 of the rules
     happen automatically instead of relying on the session choosing to look.
   - A Stop hook that warns when a session ends with unpushed commits or a
     dirty tree, naming what is unpushed.
   Check what the installed Claude Code version actually supports before
   writing the config — do not assume a hook API from memory. Back up
   settings.json first. Show me the config before applying it.

4. Prove it works. Verification is the point of the whole exercise, so do not
   skip it here. Open a scratch git repo, make a commit, and show me the
   SessionStart and Stop hooks actually firing with real output. If you cannot
   demonstrate them firing, say so plainly rather than reporting success.

Constraints:
- Do not modify anything outside ~/.claude/ and a scratch directory.
- Back up any file you change, and tell me the backup path.
- If a rule cannot be enforced by a hook in this version, say so instead of
  writing a hook that silently does nothing.
```

---

## Prompt 2 — roll out to another repo

Run this in a session with the target repo checked out. Written for
`quontiant-v3`; change the names for any other repo.

This one touches work in flight. The prompt is deliberately heavy on things the
session must **not** do — the failure mode here is a helpful session "tidying"
someone else's uncommitted work.

```text
Context — read this before doing anything.

Several Claude Code sessions have been working this repo at the same time, on
the same long-lived branch (feat/licence-preflight-domain-taxonomy). Session
metadata showed unpushed commit counts climbing 19 -> 20 -> 37 -> 53 -> 62 -> 68
across five days, with a dirty worktree nearly throughout. That means sessions
were editing the same files with no visibility of each other, and a lot of work
has been redone as a result.

Those numbers are from session metadata dated 1-2 September and may be stale.
Check the current reality yourself; do not trust the figures above.

There is a fix already written and tested in daneisluno-netizen/rundown-feed
under docs/claude/ — WORKING-AGREEMENT.md, GOTCHAS.md and CLAUDE.md.template.
Read all three before starting. I want them installed here.

Your task, in this order. Do not skip ahead.

1. Report state. Change nothing yet. Tell me:
   - current branch, and whether the working tree is dirty
   - how many commits are unpushed, and on which branches
   - what the uncommitted changes actually are (a diffstat, and your read of
     whether they look like finished work, work in progress, or debris)
   - whether any other claude/* branches exist locally or on the remote
   Then stop and wait for me.

2. Get the existing work safe, non-destructively. Pushing already-made commits
   is safe and is the priority — an unpushed commit is invisible to every other
   session and is the single biggest cause of the duplicated work above. Push
   the existing branch as it stands. Do not reorganise, squash, split or
   rewrite the history to make it tidier first. Ask me about the uncommitted
   changes rather than deciding for me.

3. Install the docs. Copy WORKING-AGREEMENT.md, GOTCHAS.md and
   CLAUDE.md.template from rundown-feed into docs/claude/ here, unchanged.

4. Write this repo's CLAUDE.md from the template. This is the part that matters
   most, so do not rush it — everything else is generic and this is the bit that
   is specific to this repo. Fill in every section from what is actually in the
   repo, not from assumption. In particular the prerequisites table: every env
   var, secret, DSN and service needed to RUN and TEST this repo, not just to
   build it. I know DATABASE_URL_MIGRATE is one, because a session got all the
   way through a task before discovering it was unset and could not verify
   anything. Find the rest by reading the code, the compose files, the CI
   config and any .env.example. For each: the exact name, what it is for, where
   the value comes from, and what fails if it is missing. Where you cannot
   determine a value's source, write that down explicitly rather than guessing —
   "source unknown, ask Dane" is useful; a plausible invention is not.

5. Record the integration branch by name in the branch section, and note that
   session work goes on claude/<slug> branches that merge back into it.

6. Verify before reporting: confirm the commands you put in the CLAUDE.md
   actually run, and paste the real output. If one cannot run in this
   environment, say which and why.

Then commit on a claude/* branch of your own, push it, and open a draft PR.

Never, regardless of what would be tidier:
- rebase, amend, force-push, or reset a shared branch
- git stash, checkout . or reset --hard over uncommitted changes you did not make
- squash or reorder existing commits
- delete any branch
- "fix" unrelated failing tests or lint you find along the way — report them

If the repo state does not match what I described above, stop and tell me what
you actually found. My description is inference from metadata, not fact.
```

---

## Why these are shaped this way

**The context block comes first and is longer than the instruction.** A session
told only *what* to do will invent a *why*, and the invented why drives every
judgement call it then makes.

**"Report first, wait" is a real step, not politeness.** Both prompts stop the
session before it changes anything in a state I described from stale metadata.

**The nevers are listed explicitly.** "Be careful with git" is not actionable.
"Do not force-push, stash, or reset a branch you did not create" is.

**Each prompt ends with a demonstrable check.** Prompt 1 asks for the hooks to
be seen firing; prompt 2 asks for real command output. Reporting the rule and
then not following it in the same breath is the failure this whole system is
meant to prevent.
