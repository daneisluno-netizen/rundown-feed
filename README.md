# The Rundown — feed host

Hosts one file: `feed.xml`, the RSS feed for a personal podcast.

## Why this repo exists

The audio lives on Google Drive, which serves MP3s correctly
(`Content-Type: audio/mpeg`, and it honours Range requests so clients can seek
and resume). Drive **cannot** host the feed: it serves any XML as
`application/octet-stream` with `Content-Disposition: attachment`, which says
"download this file" rather than "here is a feed", and podcast clients reject it.
Drive gives no way to change that.

GitHub Pages serves `.xml` as `application/xml`, which clients accept. So the
feed is here and the audio is on Drive — the enclosure URL inside the feed can
point anywhere, so the two do not need to share a host.

Overwritten by `tools/rundown/publish.py` on every publish. Nothing here is
hand-edited.
