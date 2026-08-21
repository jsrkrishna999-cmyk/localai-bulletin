# prompts.py — the exact City and District bulletin prompt templates (from City_news.py /
# Dist_code.py), plus the default place list. The literal "Guntur"/"గుంటూరు" and the date
# "11-08-2026" are placeholders that get swapped per place / per run.

DEFAULT_PLACES = ("Guntur, Nellore, Tirupati, Warangal, Nalgonda, Kakinada, Karimnagar, "
                  "Khammam, Kurnool, Mahabubnagar, Siddipet, Rajahmundry, Nizamabad, "
                  "Elluru, Ongole, Vizianagaram, Ananthapur, Kadapa, "
                  # new 18 channels
                  "Nandyal, Chittoor, Machilipatnam, Bapatla, Amalapuram, Anakapalli, "
                  "Bhimavaram, Narasaraopet, Srikakulam, Proddatur, Sangareddy, Ramagundam, "
                  "Manchiryala, Kothagudem, Adilabad, Kamareddy, Jagityal, Nirmal, "
                  # newest 18 channels
                  "Adoni, Madanapalle, Tenali, Hindupur, Tadepalligudem, Guntakal, "
                  "Gudivada, Dharmavaram, Chirala, Tadipatri, Suryapet, Miryalaguda, "
                  "Bhuvanagiri, Vikarabad, Wanaparthy, Nagarkurnool, Mahabubabad, Jangaon")

DEFAULT_DATE = "11-08-2026"

CITY_PROMPT = """Generate a professional Telugu video news bulletin script for “Guntur Local News Bulletin – 11-08-2026” for Local AI TV.

IMPORTANT REQUIREMENTS:

1. TOTAL DURATION
- Total bulletin duration must be approximately 9 minutes only.
- Minimum duration: 8 minutes 40 seconds
- Maximum duration: 9 minutes 20 seconds
- Do NOT generate less or more than this duration.

2. NEWS BULLETIN TITLE
   Use this title format:
“Guntur Local News Bulletin – 11-08-2026”


Example:
“Guntur Local News Bulletin – 11-08-2026”

3. OPENING INTRODUCTION
   Start the bulletin with a professional Telugu welcome greeting like this:
“నమస్తే… Local AI TV కి స్వాగతం.
ఈరోజు 11-08-2026 గుంటూరు లోకల్ న్యూస్ బులిటెన్ మీకు సమర్పిస్తున్నాము.”

The opening should:
- Mention Local AI TV
- Mention today’s date
- Mention bulletin name
- Sound professional, warm, and engaging

4. TOTAL NEWS ITEMS
- Generate approximately 20 to 25 news items.
- Number of items may vary depending on news length.
- Final total duration must remain approximately 9 minutes.

5. VERY IMPORTANT – NEWS DATE CONDITION
- Use ONLY TODAY’S NEWS.
- Do NOT use old news.
- Do NOT include yesterday’s news unless still officially active today.
- All information must be latest and current as of today’s date only.

6. VERY IMPORTANT – LOCATION CONDITION
   This bulletin is ONLY for:
- Guntur Town
- Guntur City
- Guntur Constituency

STRICTLY AVOID:
- Andhra Pradesh state-wide news
- National news
- International news
- Other district news
- General political debates unrelated to Guntur city

Every news item must directly relate to:
- Guntur city public
- Guntur local administration
- Guntur local events
- Guntur constituency developments
- Guntur town traffic, weather, business, civic issues, public alerts, jobs, education, markets, health, power cuts, water supply, municipal activities, police updates, local political updates, local cultural/religious events, etc.

7. NEWS SOURCES
   Collect and summarize today’s news from Telugu newspapers, TV channels, digital platforms, social media, and government releases.

REFERRED SOURCES INCLUDE:
TELUGU NEWSPAPERS:
- Eenadu, Sakshi, Andhra Jyothi, Andhra Prabha, Andhra Bhoomi, Vaartha, Prajasakti, Suryaa, Janam Sakshi, Visalandhra, Telugu Velugu, Rayalaseema Samayam, Namasthe Telangana, Mana Telangana, Nava Telangana

TELUGU TV CHANNELS:
- TV9 Telugu, TV5 News, NTV, ABN Andhra Jyothi, Sakshi TV, ETV Andhra Pradesh, ETV Telangana, V6 News, 10TV, 99TV, hmtv, Q News, T News, iNews, Mahaa News, Bharat Today, Studio N, CVR News, Raj News Telugu, AP 24x7, 6TV, BBC Telugu, India Today Telugu, Samayam Telugu

DIGITAL & YOUTUBE NEWS SOURCES:
- Way2News Telugu, Public App Telugu, Lokal App Telugu, Great Andhra, Telugu Scribe, Other reliable Telugu local digital media

GOVERNMENT & OFFICIAL SOURCES:
- Andhra Pradesh Government press releases, Telangana Government releases if relevant locally, District Collector press releases, Police department press releases, Municipal Corporation releases, Municipality notices, Revenue department updates, Electricity department alerts, Water supply notifications, Public transport alerts, PIB Telugu releases, Government scheme announcements, Job notifications, Disaster/weather/public alerts, Minister speeches relevant to Guntur, Official social media announcements from government departments"""

DIST_PROMPT = """Generate a professional Telugu video news bulletin script for “Guntur District News Bulletin – 11-08-2026” for Local AI TV.

IMPORTANT REQUIREMENTS:

1. TOTAL DURATION
- Total bulletin duration must be approximately 9 minutes only.
- Minimum duration: 8 minutes 40 seconds
- Maximum duration: 9 minutes 20 seconds.
- Do NOT generate less or more than this duration.

2. NEWS BULLETIN TITLE
Use this title format:
“Guntur District News Bulletin – 11-08-2026”

3. OPENING INTRODUCTION
Start the bulletin with a professional Telugu welcome greeting like this:
“నమస్తే… Local AI TV కి స్వాగతం.
ఈరోజు 11-08-2026 గుంటూరు జిల్లా న్యూస్ బులిటెన్ మీకు సమర్పిస్తున్నాము.”

The opening should:
- Mention Local AI TV
- Mention today’s date
- Mention district bulletin name
- Sound professional, warm, and engaging

4. TOTAL NEWS ITEMS
- Generate approximately 20 to 25 news items.
- Number of items may vary depending on news length.
- Final total duration must remain approximately 9 minutes.

5. VERY IMPORTANT – NEWS DATE CONDITION
- Use ONLY TODAY’S NEWS.
- Do NOT use old news.
- Do NOT include yesterday’s news unless still officially active today.
- All information must be latest and current as of today’s date only.

6. VERY IMPORTANT – LOCATION CONDITION
This bulletin is ONLY for:
- Guntur District
- All Mandals in Guntur District
- Guntur City
- Guntur Rural Areas
- Guntur Constituencies

STRICTLY AVOID:
- Andhra Pradesh/Telangana state-wide news unless directly connected to Guntur District
- National news
- International news
- Other district news unrelated to the target district
- General political debates unrelated to the district

Every news item must directly relate to:
- Guntur district public
- Guntur district administration
- Guntur district events
- Guntur district constituency developments
- Mandal-level updates
- Rural and urban developments
- Traffic, weather, markets, education, health, jobs, police, civic issues, power cuts, water supply, transport, agriculture, temples, local events

7. NEWS SOURCES
Collect and summarize today’s news from Telugu newspapers, TV channels, digital platforms, social media, and government releases.

REFERRED SOURCES INCLUDE:
TELUGU NEWSPAPERS:
- Eenadu, Sakshi, Andhra Jyothi, Andhra Prabha, Andhra Bhoomi, Vaartha, Prajasakti, Suryaa, Janam Sakshi, Visalandhra, Telugu Velugu, Rayalaseema Samayam, Namasthe Telangana, Mana Telangana, Nava Telangana

TELUGU TV CHANNELS:
- TV9 Telugu, TV5 News, NTV, ABN Andhra Jyothi, Sakshi TV, ETV Andhra Pradesh, ETV Telangana, V6 News, 10TV, 99TV, hmtv, Q News, T News, iNews, Mahaa News, Bharat Today, Studio N, CVR News, Raj News Telugu, AP 24x7, 6TV, BBC Telugu, India Today Telugu, Samayam Telugu

DIGITAL & YOUTUBE NEWS SOURCES:
- Way2News Telugu, Public App Telugu, Lokal App Telugu, Great Andhra, Telugu Scribe, Other reliable Telugu local digital media

GOVERNMENT & OFFICIAL SOURCES:
- District Collector press releases
- Police department press releases
- Municipal Corporation releases
- Municipality notices
- Revenue department updates
- Electricity department alerts
- Water supply notifications
- Public transport alerts
- Government scheme announcements
- Job notifications
- Disaster/weather/public alerts
- Minister speeches relevant to Guntur District
- Official social media announcements from government departments

8. OUTPUT STYLE
- Write in clear professional Telugu.
- Use TV news anchor reading style.
- Each news item should have a headline and short explanation.
- Avoid fake dramatic language.
- Keep the tone credible, local, and useful for district audience.

9. FINAL CLOSING
End with:
“ఇవి ఈరోజు గుంటూరు జిల్లా ప్రధాన వార్తలు.
తాజా అప్‌డేట్స్ కోసం Local AI TV చూస్తూ ఉండండి.
ధన్యవాదాలు.”
"""


# ---- Headlines extraction ----
HEADLINE_PROMPT = """You are an expert TELUGU news editor for a Telugu television channel.
Read the provided news content below and extract the most important, catchy headlines from it.

*** LANGUAGE RULE — THIS OVERRIDES EVERYTHING ELSE ***
Write EVERY headline in TELUGU SCRIPT ONLY (అ-ఱ, Unicode 0C00-0C7F).
- NEVER translate to English. NEVER write in Hindi/Devanagari (क-ह). NEVER transliterate.
- Do NOT output Latin/Roman letters at all — not for place names, not for
  organisation names, not for anything. Write them in Telugu script instead
  (e.g. write రాజమండ్రి, not "Rajahmundry"; రోడ్డు, not "Road").
- Even if the source content is written in English or Hindi, your OUTPUT must
  still be 100% Telugu.
- Digits: write numerals as Telugu words or standard digits (0-9) only.
If you cannot write a word in Telugu, omit that headline entirely rather than
using another language.

You must follow these strict formatting rules for the final output:

1. Remove all numbers, bullet points, symbols (like •, -, *), or any prefixes from the headlines.

2. Clean and trim any leading or trailing spaces from each headline.

3. Merge all the generated headlines into one single, continuous line of text.

4. Separate each headline using exactly ten standard spaces (          ) — use plain spaces only, NOT tabs.

5. Do not include any introductory or concluding conversational text (e.g., do NOT say "Here are the headlines:"). Output ONLY the single line of formatted headlines.

NEWS CONTENT:
"""

HEADLINE_SEP = " " * 10          # exactly ten standard spaces (rule 4)


def build_headline_prompt(content):
    return HEADLINE_PROMPT + (content or "")


def format_headlines(raw):
    """Guarantee rules 2-5 no matter how the model spaced things: split into headlines
    (on newlines OR any run of 2+ spaces = the intended separator), strip each, drop any
    leading list markers/symbols, collapse inner whitespace, then rejoin with EXACTLY ten
    spaces on ONE line."""
    import re
    parts = re.split(r"\n+|\s{2,}", raw or "")
    out = []
    for p in parts:
        h = re.sub(r"^[\s\d.)\-•*:>#•–—]+", "", p.strip())   # kill leading markers
        h = re.sub(r"[ \t]+", " ", h).strip()                              # collapse inner runs
        if h:
            out.append(h)
    return HEADLINE_SEP.join(out)


def build_city_prompt(place, date=DEFAULT_DATE):
    """Match City_news.py exactly: swap the date first, then guntur/Guntur -> place."""
    t = CITY_PROMPT.replace(DEFAULT_DATE, date)
    return t.replace("guntur", place).replace("Guntur", place)


def build_dist_prompt(place, date=DEFAULT_DATE):
    """Match Dist_code.py exactly: swap the date, then Guntur/guntur/గుంటూరు -> place."""
    t = DIST_PROMPT.replace(DEFAULT_DATE, date)
    return (t.replace("Guntur", place)
             .replace("guntur", place.lower())
             .replace("గుంటూరు", place))

# ---------- Telugu-only guard ----------
def telugu_ratio(text):
    """Share of *letters* that are Telugu script. Digits/punctuation/spaces ignored,
    so '33 డిగ్రీలు' still counts as 100% Telugu."""
    tel = lat = dev = 0
    for ch in (text or ""):
        o = ord(ch)
        if 0x0C00 <= o <= 0x0C7F: tel += 1
        elif 0x0900 <= o <= 0x097F: dev += 1          # Hindi / Devanagari
        elif ("a" <= ch <= "z") or ("A" <= ch <= "Z"): lat += 1
    total = tel + lat + dev
    return 1.0 if total == 0 else tel / total


def is_telugu(text, min_ratio=0.92):
    """True when the text is Telugu enough to publish. Rejects English translations
    and any Devanagari at all."""
    if not (text or "").strip():
        return False
    for ch in text:
        if 0x0900 <= ord(ch) <= 0x097F:               # any Hindi char -> reject
            return False
    return telugu_ratio(text) >= min_ratio


RETRY_TELUGU_NOTE = (
    "\n\nYOUR PREVIOUS ANSWER WAS REJECTED because it was not written in Telugu script. "
    "Rewrite ALL headlines in TELUGU SCRIPT ONLY. No English words, no Roman letters, "
    "no Hindi. Transliterate every place and organisation name into Telugu script.\n"
)
