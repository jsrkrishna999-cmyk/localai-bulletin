# headlines_local.py — extract headlines from a generated bulletin WITHOUT any API / key.
#
# The bulletin already contains every headline as the BOLD title of each news item. The model
# formats them differently across runs, so we try several known patterns and keep the one that
# yields the most matches (each file is internally consistent -> that pattern is the right one).
# Output obeys the same rules as the Gemini path: clean, one line, joined by exactly ten spaces.
import re

SEP = " " * 10

# non-headline bold spans to ignore (anchor cues, section markers, music/logo/visual lines)
_STOP = re.compile(
    r"(యాంకర్|అంకర్|ANCHOR|న్యూస్\s*రీడర్|వార్తలు|HEADLINES|ముఖ్యాంశ|BULLETIN|"
    r"MAIN NEWS|OPENING|CLOSING|మ్యూజిక్|లోగో|LOGO|MUSIC|GRAPHIC|Local AI TV|నమస్తే|"
    r"ఇక వివరంగా|ముందుగా|విజువల్|Screen|Duration|Approx|సమయం|టైటిల్|కార్డ్|"
    r"News Bulletin|న్యూస్ బులిటెన్|ముగింపు|మొత్తం వ్యవధి|వ్యవధి అంచనా|"
    r"వాతావరణ నివేదిక|ధన్యవాదాలు)",
    re.IGNORECASE)

# each pattern captures the headline text; order doesn't matter (we pick the best by count)
_PATTERNS = [
    re.compile(r"\*\*\[\s*\d+\s*\]\s*(.+?)\s*:?\*\*"),            # **[1] X:**   (Ananthapur)
    re.compile(r"\*\*\(\s*(?:NEWS ITEM|న్యూస్\s*ఐటెమ్)\s*\d+\s*[-–]\s*(.+?)\)\*\*", re.I),  # **(NEWS ITEM 1 - X)** (Kadapa/Rajahmundry)
    re.compile(r"\*\*\s*\d+[.)]\s*(.+?)\s*:?\*\*"),               # **1. X:**    (Elluru main)
    re.compile(r"(?m)^\s*\d+[.)]\s*\*\*(.+?)\s*:?\*\*"),          # 1. **X:**    (Guntur)
    re.compile(r"(?m)^\s*[*\-]\s*\*\*(.+?)\s*:?\*\*"),            # *  **X:**    (bullet headlines, bold)
    re.compile(r"(?m)^\s*\*\*\s*([^*\n]{4,150}?)\s*:?\*\*\s*$"),  # **X** alone on a line (Nalgonda)
    re.compile(r"(?m)^#{1,4}\s*(.+?)\s*$"),                       # ### X        (markdown headings)
]


def _clean(h):
    """Apply the formatting rules to a single headline."""
    h = h.replace("*", " ").replace("#", " ")
    h = re.sub(r"^[\s\d.)\-•*:：>#–—\[\]]+", "", h)   # strip leading markers/numbers/symbols
    h = re.sub(r"\s*\([^)]*\)\s*$", "", h)             # drop a trailing (…) timing/duration note
    h = re.sub(r"[\s]+", " ", h).strip()
    return h.rstrip(":：").strip()


def extract(text):
    """Return (headline_line, count). headline_line = one line, ten-space separated."""
    text = text or ""
    best = []
    for pat in _PATTERNS:
        hits = []
        for m in pat.findall(text):
            h = _clean(m)
            if h and not _STOP.search(h) and 2 <= len(h) <= 160:
                hits.append(h)
        # de-dupe within this pattern, keep order
        seen, uniq = set(), []
        for h in hits:
            if h not in seen:
                seen.add(h); uniq.append(h)
        if len(uniq) > len(best):
            best = uniq
    return SEP.join(best), len(best)


if __name__ == "__main__":
    import sys, glob, os
    for f in (sys.argv[1:] or sorted(glob.glob("Gemini_outs/city/*.txt"))):
        line, n = extract(open(f, encoding="utf-8", errors="ignore").read())
        print(f"{os.path.basename(f):22} {n:3d} headlines")
