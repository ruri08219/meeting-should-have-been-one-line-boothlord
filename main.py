#!/usr/bin/env python3
"""The Meeting That Should Have Been One Line — one-line meeting-killer entry for make.fun.

Writes exactly one line (1-200 chars, no newline) to entry.txt in the
output directory ($OUTPUT_DIR, default /output).

Entry (116 chars, one sentence):
    We spent forty minutes deciding who should send the email, and the
    email was: this meeting could have been an email.

Judge criteria (deadpan office satirist, z-ai/glm-5.3-flash, pairwise):
  1. A single line, one sentence that could have replaced an entire
     pointless meeting, unmistakably office humor.
  2. Kills the meeting outright: after this line, no one could justify
     holding the meeting at all.
  3. Relatable to anyone who sat through a useless meeting, drawn from
     real office life.
  4. Lands as a joke, with a turn or a sting, funny not merely true.
  5. Stands alone, needing no context or explanation.

Angle: the meeting's entire output was one email — and the email's content
is the punchline. Concrete scene (forty minutes deciding who sends the
email) + reversal (the email itself says the meeting was unnecessary) +
landing final line (the punchline is the last clause). The line literally
IS the replacement for the meeting: send that email instead.

Gate rules enforced here, mirroring the competition gate:
  * UTF-8 text, 1 to 200 characters, not only whitespace.
  * Exactly one line (no newline characters inside the entry).
  * No control characters — including DEL (0x7F) and non-printable
    Unicode (categories C*, Zl, Zp), so stray format characters cannot
    slip past a plain ord() < 0x20 check.
  * UTF-8 byte length is reported as a sanity check (ASCII entry, so
    bytes == chars here); the gate itself is character-based.
  * The entry must actually encode as UTF-8: an unpaired surrogate
    (which _is_printable rejects, but which a future edit or a
    category-table difference could let through) would otherwise
    crash the write with an unhandled UnicodeEncodeError instead of
    a clean gate error. validate() therefore proves encodability
    up front and enforces a byte-length sanity bound of 4 * MAX_CHARS
    (the theoretical maximum for a <=200-char entry, so it can never
    reject a gate-passing entry).
Any violation exits 1 and writes nothing.
"""

import os
import sys
import unicodedata

ENTRY = (
    "We spent forty minutes deciding who should send the email, and the "
    "email was: this meeting could have been an email."
)

MAX_CHARS = 200


def _is_printable(ch: str) -> bool:
    """True if ch is a printable character.

    Rejects DEL (0x7F), all Unicode control/format/surrogate/private-use
    categories (C*), and line/paragraph separators (Zl, Zp). Ordinary
    spaces (Zs) are allowed.
    """
    cat = unicodedata.category(ch)
    return cat[0] != "C" and cat not in ("Zl", "Zp")


def validate(entry: str) -> None:
    """Exit 1 with a message on the first violated gate rule."""
    if not entry or not entry.strip():
        print("error: entry is empty or whitespace only", file=sys.stderr)
        sys.exit(1)
    if len(entry) > MAX_CHARS:
        print(
            "error: entry is %d chars, over the %d limit" % (len(entry), MAX_CHARS),
            file=sys.stderr,
        )
        sys.exit(1)
    if "\n" in entry or "\r" in entry:
        print("error: entry must be a single line", file=sys.stderr)
        sys.exit(1)
    bad = [ch for ch in entry if not _is_printable(ch)]
    if bad:
        print(
            "error: entry contains non-printable character U+%04X"
            % ord(bad[0]),
            file=sys.stderr,
        )
        sys.exit(1)
    # Prove UTF-8 encodability before any file is touched: a lone
    # surrogate would otherwise raise UnicodeEncodeError mid-write
    # (unhandled traceback, after makedirs) instead of a gate error.
    try:
        nbytes = len(entry.encode("utf-8"))
    except UnicodeEncodeError as exc:
        print(
            "error: entry is not encodable as UTF-8 (unpaired surrogate "
            "U+%04X)" % ord(exc.object[exc.start]),
            file=sys.stderr,
        )
        sys.exit(1)
    # Sanity bound: 4 bytes/char is the UTF-8 maximum, so a <=200-char
    # entry can never exceed 4 * MAX_CHARS bytes; anything above that
    # is pathological and is rejected rather than written.
    if nbytes > 4 * MAX_CHARS:
        print(
            "error: entry is %d UTF-8 bytes, over the %d-byte sanity bound"
            % (nbytes, 4 * MAX_CHARS),
            file=sys.stderr,
        )
        sys.exit(1)


def main() -> int:
    validate(ENTRY)
    out_dir = os.environ.get("OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(ENTRY)
    print(
        "wrote %s (%d chars, %d UTF-8 bytes)"
        % (path, len(ENTRY), len(ENTRY.encode("utf-8")))
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
