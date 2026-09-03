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

Any change touching `feed.xml` must pass all three:

```sh
# 1. Well-formed XML
python3 -c "import xml.dom.minidom; xml.dom.minidom.parse('feed.xml'); print('OK')"

# 2. Every enclosure is reachable and is audio (not an HTML interstitial)
python3 - <<'PY'
import re, urllib.request
for url in re.findall(r'<enclosure url="([^"]+)"', open('feed.xml').read()):
    r = urllib.request.Request(url.replace('&amp;', '&'), method='HEAD')
    with urllib.request.urlopen(r) as resp:
        ct = resp.headers.get('Content-Type', '')
        print(('OK  ' if 'audio' in ct else 'FAIL'), ct, url[:70])
PY

# 3. After push, Pages serves it as XML (allow ~60s for the deploy)
curl -sI https://daneisluno-netizen.github.io/rundown-feed/feed.xml | grep -i content-type
```

`content-type: application/xml` or `text/xml` is a pass. `octet-stream` is a fail.

## Facts worth not rediscovering

- `<guid isPermaLink="false">` is the MP3 filename (`2026-09-02-rundown.mp3`).
  Changing a GUID makes clients re-download an episode as if it were new.
- `pubDate` is RFC 2822 with an explicit offset (`Wed, 02 Sep 2026 00:00:00 +0000`).
  Clients silently drop items with malformed dates.
- `length` on `<enclosure>` is the byte size. Wrong values break seeking in
  some clients.
- `index.html` is a one-line placeholder so the Pages root is not a 404.
  It is not a website and does not need to become one.
