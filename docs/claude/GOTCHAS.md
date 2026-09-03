# Gotchas

Append-only. Things that failed once for a non-obvious reason, so they do not
cost a second cycle.

**Format** — newest first, three lines each:

```
## <short symptom>
- **Cause:** what was actually wrong
- **Fix:** what to do instead
```

Rules: one entry per real failure. No entries for ordinary bugs you fixed in the
normal course of work — only for things where the *cause was not visible from
the symptom*. If an entry stops being true, delete it; a stale gotcha is worse
than none.

---

## Podcast clients silently reject the feed when served from Google Drive
- **Cause:** Drive serves any `.xml` as `application/octet-stream` with
  `Content-Disposition: attachment`. There is no setting to change it. Clients
  read that as "download this file", not "here is a feed", and fail with no
  useful error.
- **Fix:** Host `feed.xml` on GitHub Pages, which serves `application/xml`.
  Audio can stay on Drive — the `<enclosure>` URL is independent of the feed host.

## Audio enclosure returns HTML instead of an MP3
- **Cause:** Most Google Drive share/view URL forms return an interstitial HTML
  page, not the file. The feed still validates as XML, so the failure only shows
  up in the podcast client, well after publish.
- **Fix:** Use the direct download form only —
  `https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t`.
  Verify with a HEAD request and check `Content-Type: audio/mpeg` before pushing
  (see the verify block in `CLAUDE.md`).

## An episode re-downloads for every subscriber after a feed edit
- **Cause:** `<guid>` changed. Clients key episodes on GUID, not title or URL.
- **Fix:** GUID is the MP3 filename and is permanent. Change the title, the
  description, the enclosure URL — never the GUID of a published item.
