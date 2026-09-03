# rundown-feed

Static host for one file: `feed.xml`, the RSS feed for The Rundown.
Served by GitHub Pages at https://daneisluno-netizen.github.io/rundown-feed/

Read `docs/claude/WORKING-AGREEMENT.md` before making changes.
Read `docs/claude/GOTCHAS.md` before debugging anything that looks familiar.

## Branching

One branch per session. `main` is the integration branch — never commit to it
directly.

```sh
git fetch origin main && git checkout -B "claude/<short-task-slug>" origin/main
# ...first commit...
git push -u origin HEAD          # push on the FIRST commit, not the last
```

Merge back into `main` before the session ends, then delete the branch.
Full protocol: `docs/claude/WORKING-AGREEMENT.md` section 2.

## Hard rules

1. **Never hand-edit `feed.xml`.** It is generated wholesale by
   `tools/rundown/publish.py`, which lives outside this repo. Editing it here is
   overwritten on the next publish. If the feed is wrong, the bug is in
   `publish.py` — fix it there, republish, and let it push.
2. **Never change the enclosure URL shape.** Audio is on Google Drive and only
   works in the `drive.usercontent.google.com/download?id=...&export=download&confirm=t`
   form. Other Drive URL forms return an HTML interstitial, not audio, and
   podcast clients fail silently.
3. **The feed must stay `.xml` and stay here.** Drive serves XML as
   `application/octet-stream` with `Content-Disposition: attachment`, which
   clients reject. That is why this repo exists. Do not "simplify" by moving
   the feed to Drive.

## Verify before you claim it works

One implementation, in `scripts/verify_feed.py`. CI runs exactly these commands
(`.github/workflows/verify-feed.yml`), so what passes locally passes there.

```sh
python3 scripts/verify_feed.py --structure     # offline: XML, guid, pubDate, enclosure shape
python3 scripts/verify_feed.py --enclosures    # network: every audio URL serves audio
python3 scripts/verify_feed.py --live          # network: Pages serves this feed as XML
python3 scripts/verify_feed.py --all
```

Exit 0 is a pass. Run `--structure --enclosures` before pushing; `--live` only
means anything after a deploy, so run it after your merge to `main` lands.

If you add a rule to this file that can be checked mechanically, add it to the
script too. A rule only prose enforces is a rule that gets skipped.

## Facts worth not rediscovering

- `<guid isPermaLink="false">` is the MP3 filename (`2026-09-02-rundown.mp3`).
  Changing a GUID makes clients re-download an episode as if it were new.
- `pubDate` is RFC 2822 with an explicit offset (`Wed, 02 Sep 2026 00:00:00 +0000`).
  Clients silently drop items with malformed dates.
- `length` on `<enclosure>` is the byte size. Wrong values break seeking in
  some clients.
- `index.html` is a one-line placeholder so the Pages root is not a 404.
  It is not a website and does not need to become one.
