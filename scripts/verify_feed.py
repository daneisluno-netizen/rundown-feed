#!/usr/bin/env python3
"""Verify the Rundown podcast feed.

One implementation, used by CI and by humans. Stdlib only - no install step.

    python3 scripts/verify_feed.py --structure    # offline: XML + required fields
    python3 scripts/verify_feed.py --enclosures   # network: audio URLs serve audio
    python3 scripts/verify_feed.py --live         # network: Pages serves this feed as XML
    python3 scripts/verify_feed.py --all

Exit 0 = pass, 1 = fail. Failures are printed as GitHub annotations when
running under Actions, plain text otherwise.
"""

import argparse
import hashlib
import os
import re
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

FEED = "feed.xml"
LIVE_URL = "https://daneisluno-netizen.github.io/rundown-feed/feed.xml"

# Google Drive only serves the file itself from this URL shape. Every other
# form returns an HTML interstitial that validates fine but plays as nothing.
DRIVE_RE = re.compile(
    r"^https://drive\.usercontent\.google\.com/download"
    r"\?id=[\w-]+&export=download&confirm=t$"
)

ITUNES = "{http://www.itunes.com/dtds/podcast-1.0.dtd}"
CI = os.environ.get("GITHUB_ACTIONS") == "true"

failures: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)
    print(f"::error::{msg}" if CI else f"FAIL  {msg}")


def ok(msg: str) -> None:
    print(f"ok    {msg}")


def load_items():
    try:
        root = ET.parse(FEED).getroot()
    except ET.ParseError as e:
        fail(f"{FEED} is not well-formed XML: {e}")
        sys.exit(1)
    ok(f"{FEED} is well-formed XML")
    channel = root.find("channel")
    if channel is None:
        fail("no <channel> element")
        sys.exit(1)
    return channel, channel.findall("item")


def check_structure() -> None:
    channel, items = load_items()

    for tag in ("title", "link", "description"):
        if channel.findtext(tag, "").strip() == "":
            fail(f"<channel> is missing a non-empty <{tag}>")
    if not items:
        fail("feed contains no <item> elements")
    ok(f"{len(items)} item(s) found")

    seen: dict[str, int] = {}
    for n, item in enumerate(items, 1):
        label = item.findtext("title", f"item {n}")[:50]

        for tag in ("title", "description"):
            if item.findtext(tag, "").strip() == "":
                fail(f"[{label}] missing a non-empty <{tag}>")

        guid = item.findtext("guid", "").strip()
        if not guid:
            fail(f"[{label}] missing <guid>")
        elif guid in seen:
            fail(f"[{label}] duplicate <guid> {guid!r}, also on item {seen[guid]}")
        else:
            seen[guid] = n

        # A malformed pubDate makes clients drop the item silently.
        raw = item.findtext("pubDate", "").strip()
        if not raw:
            fail(f"[{label}] missing <pubDate>")
        else:
            try:
                dt = parsedate_to_datetime(raw)
            except (TypeError, ValueError) as e:
                fail(f"[{label}] unparseable <pubDate> {raw!r}: {e}")
            else:
                if dt.tzinfo is None:
                    fail(f"[{label}] <pubDate> {raw!r} has no timezone offset")

        enc = item.find("enclosure")
        if enc is None:
            fail(f"[{label}] missing <enclosure>")
            continue

        url = enc.get("url", "")
        if not DRIVE_RE.match(url):
            fail(
                f"[{label}] enclosure URL is not the Drive direct-download form "
                f"(...&export=download&confirm=t): {url}"
            )

        mime = enc.get("type", "")
        if not mime.startswith("audio/"):
            fail(f"[{label}] enclosure type is {mime!r}, expected audio/*")

        length = enc.get("length", "")
        if not length.isdigit() or int(length) <= 0:
            fail(f"[{label}] enclosure length is {length!r}, expected a positive integer")

    if not failures:
        ok("all items have valid guid, pubDate and enclosure")


def head(url: str, attempts: int = 3):
    """HEAD with backoff. Returns (headers, None) or (None, last_error)."""
    err = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, method="HEAD")
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.headers, None
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            err = e
            if i < attempts - 1:
                time.sleep(2 ** i)
    return None, err


def check_enclosures() -> None:
    _, items = load_items()
    for item in items:
        enc = item.find("enclosure")
        if enc is None:
            continue
        url = enc.get("url", "")
        label = item.findtext("title", url)[:50]

        headers, err = head(url)
        if headers is None:
            # Unreachable is a real failure, not a pass. Distinct wording so the
            # cause is obvious: this is the network, not the feed's contents.
            fail(f"[{label}] enclosure unreachable after 3 attempts: {err}")
            continue

        ct = headers.get("Content-Type", "")
        if "audio" not in ct:
            fail(
                f"[{label}] enclosure served as {ct!r}, not audio. "
                "Drive is returning an interstitial page, not the file."
            )
        else:
            ok(f"[{label}] {ct}")


def check_live(timeout: int = 240) -> None:
    """Assert Pages serves THIS feed, as XML. Polls until the deploy lands."""
    local = hashlib.sha256(open(FEED, "rb").read()).hexdigest()
    deadline = time.time() + timeout
    last_ct = served = None

    while time.time() < deadline:
        try:
            with urllib.request.urlopen(LIVE_URL, timeout=30) as resp:
                last_ct = resp.headers.get("Content-Type", "")
                served = hashlib.sha256(resp.read()).hexdigest()
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last_ct, served = f"error: {e}", None

        if served == local:
            break
        time.sleep(10)

    if served != local:
        fail(
            f"Pages did not serve the committed feed within {timeout}s "
            f"(last content-type: {last_ct}). Deploy may still be running, "
            "or the deploy failed."
        )
        return
    ok("Pages is serving the committed feed")

    # The whole reason this repo exists: Drive serves XML as octet-stream and
    # clients reject it. Pages must serve it as XML.
    if "xml" not in (last_ct or ""):
        fail(f"Pages served the feed as {last_ct!r}, expected an XML content type")
    else:
        ok(f"content-type: {last_ct}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--structure", action="store_true", help="offline checks")
    p.add_argument("--enclosures", action="store_true", help="audio URLs serve audio")
    p.add_argument("--live", action="store_true", help="Pages serves this feed as XML")
    p.add_argument("--all", action="store_true", help="all of the above")
    a = p.parse_args()

    if not any([a.structure, a.enclosures, a.live, a.all]):
        p.print_help()
        return 2

    if a.all or a.structure:
        check_structure()
    if a.all or a.enclosures:
        check_enclosures()
    if a.all or a.live:
        check_live()

    print()
    if failures:
        print(f"{len(failures)} check(s) failed")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
