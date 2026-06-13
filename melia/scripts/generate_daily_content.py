"""
Melia Daily Content Generator
Markus Seitz Immobilien — täglich 06:00 Uhr automatisch

Generiert 5 CI-konforme Hooks mit Captions und erstellt
automatisch Canva-Posts via Brand-Template-Autofill-API.

Canva-Automatisierung läuft, wenn folgende GitHub Secrets gesetzt sind:
  CANVA_CLIENT_ID, CANVA_CLIENT_SECRET,
  CANVA_REFRESH_TOKEN, CANVA_BRAND_TEMPLATE_ID
"""

import os
import json
import time
import datetime
import requests
import anthropic

# ── Konfiguration ─────────────────────────────────────────────────────────────

CITIES = [
    "Worms", "Mannheim", "Heidelberg", "Darmstadt",
    "Mainz", "Speyer", "Bad Dürkheim", "Ludwigshafen"
]

OUTPUT_DIR = "melia/daily-content"

BRAND = {
    "name":      "Markus Seitz Immobilien",
    "tagline":   "Ihre Immobilie verdient eine Strategie.",
    "hook_core": "Kein Makler. Eine Strategie.",
    "ton_social":"Du-Form — direkt, kein Makler-Sprech",
    "ton_formal":"Sie-Form — Google Business, Flyer",
    "farben":    "Hintergrund #0a1628 · Teal-Akzent #1abcbc · Weiß",
    "phone":     "+49 176 158 585 11",
    "website":   "markus-seitz.immobilien",
    "valuation": "wertermittlung-rheinhessen.de",
}

KERNBOTSCHAFTEN = [
    "Ihre Immobilie verdient eine Strategie.",
    "Strategie statt Bauchgefühl.",
    "Kein Makler. Eine Strategie.",
    "Für den bestmöglichen Preis. Für dich.",
]

HOOK_FORMULAS = """
FORMEL 1 — Diagnose:
"Du [verb] gerade [problem]. [Konsequenz in 1 Satz]."
Beispiel: "Du verschenkst gerade Rendite. Ohne Plan ist das fast unvermeidlich."

FORMEL 2 — Kontrast:
"[Alte Annahme] war gestern. [Neue Realität] ist heute."
Beispiel: "Bauchgefühl war gestern. Strategie gewinnt heute."

FORMEL 3 — Provokation / Kurzformel:
"[Starke Aussage.] [Verstärker oder Gegensatz.]"
Beispiel: "Strategie statt Bauchgefühl. Immer."

FORMEL 4 — Zahl / Fakt:
"[Zahl oder Zeitraum]. [Überraschende Konsequenz.]"
Beispiel: "3 Wochen. So lang bleibt ein schlechtes Inserat online — bevor der Preis fällt."

FORMEL 5 — Lokal / Markt:
"[Stadt] [konkrete Marktbeobachtung]. [Was das für Verkäufer bedeutet.]"
Beispiel: "Heidelberg 2026: Käufer sind wählerischer. Dein Objekt muss überzeugen."

FORMEL 6 — Frage:
"[Unbequeme Frage, die Eigentümer sich stellen sollten]?"
Beispiel: "Weißt du wirklich, was deine Immobilie heute wert ist?"

FORMEL 7 — Emotion / Story:
"[Nachvollziehbare Situation]. [Wendepunkt.] [Lösung.]"
Beispiel: "Monatelang kein Angebot. Dann eine Strategie. Dann der Abschluss."

FORMEL 8 — Fehler benennen:
"Fehler Nr. [X]: [Was viele Eigentümer tun]. [Was das kostet.]"
Beispiel: "Fehler Nr. 1: Zu früh den Preis nennen. Käufer springen ab."
"""

THEMEN_POOL = """
THEMEN FÜR DIE 5 POSTS — jeden Tag andere Kombination wählen:

PREISFINDUNG & BEWERTUNG:
- Warum Online-Schätzer systematisch falsch liegen
- Der Unterschied zwischen Angebotspreis und Verkaufspreis
- Wann ein zu hoher Startpreis zum Bumerang wird
- Kostenlosen Wert jetzt ermitteln lassen

KÄUFERPSYCHOLOGIE:
- Warum der erste Eindruck (online) alles entscheidet
- Wie Emotionen Kaufentscheidungen treffen (nicht Zahlen)
- Warum Käufer Objekte ohne Strategie meiden
- 8-Sekunden-Regel beim Scrollen

TIMING & MARKT:
- Wann ist der richtige Moment zum Verkaufen?
- Was steigende/sinkende Zinsen für Verkäufer bedeuten
- Sommer, Winter, Herbst — wann verkauft es sich besser?
- Warum zu langes Warten teuer wird

HÄUFIGE FEHLER VON EIGENTÜMERN:
- Renovieren vor dem Verkauf — ja oder nein?
- Selbst verkaufen ohne Strategie
- Zu viele Informationen im Inserat
- Besichtigungen ohne Vorbereitung
- Den falschen Käufer zu lange begleiten

EMOTIONALE ASPEKTE:
- Das Elternhaus loslassen — wie ein Verkauf gelingt
- Wenn Erbschaft zur Aufgabe wird
- Scheidung & Immobilie — was jetzt zählt
- Erinnerungen vs. Marktwert

INSZENIERUNG & VERMARKTUNG:
- Warum Fotos über Tausende Euro entscheiden
- Homestaging: kleiner Aufwand, große Wirkung
- Exposé als Verkaufswerkzeug — nicht nur Beschreibung
- Digitale Reichweite gezielt einsetzen

LOKAL & REGIONAL:
- Marktlage konkret in Worms / Mannheim / Heidelberg etc.
- Nachbarschaftsentwicklung als Verkaufsargument
- Infrastruktur-News als Preistreiber nutzen
- Was Käufer in der Region wirklich suchen

VERHANDLUNG & ABSCHLUSS:
- Warum Strategie in der Verhandlung mehr zählt als der Preis
- Wann man ein Angebot ablehnen sollte
- Wie man Bieterverfahren richtig aufbaut
- Der Unterschied zwischen Makler und Stratege
"""

CANVA_API_BASE = "https://api.canva.com/rest/v1"

# ── Trend-Quellen (RSS) ────────────────────────────────────────────────────────

RSS_FEEDS = [
    "https://www.wormser-zeitung.de/feed",
    "https://www.rnz.de/rss/feed.rss",
    "https://www.allgemeine-zeitung.de/feed",
    "https://www.immobilienscout24.de/ratgeber/feed/",
]

def fetch_trend_headlines() -> str:
    try:
        import feedparser
        headlines = []
        for url in RSS_FEEDS:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:3]:
                    title = entry.get("title", "")
                    if any(kw in title.lower() for kw in [
                        "immobil", "wohn", "preis", "markt", "zins",
                        "haus", "wohnung", "makler", "kauf", "verkauf"
                    ]):
                        headlines.append(f"- {title}")
            except Exception:
                continue
        return "\n".join(headlines[:10]) if headlines else "Keine aktuellen Schlagzeilen verfügbar."
    except Exception:
        return "RSS nicht verfügbar — generiere auf Basis von Markt-Kontext."


# ── Canva API ─────────────────────────────────────────────────────────────────

def canva_get_access_token() -> str:
    """Tauscht den Refresh Token gegen einen neuen Access Token."""
    resp = requests.post(
        f"{CANVA_API_BASE}/oauth/token",
        data={
            "grant_type":    "refresh_token",
            "refresh_token": os.environ["CANVA_REFRESH_TOKEN"],
            "client_id":     os.environ["CANVA_CLIENT_ID"],
            "client_secret": os.environ["CANVA_CLIENT_SECRET"],
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def canva_create_post(access_token: str, brand_template_id: str,
                      title: str, headline: str, subline: str) -> dict:
    """
    Erstellt einen Canva-Post via Autofill-API.
    Gibt {"design_id": "...", "edit_url": "..."} zurück.
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type":  "application/json",
    }

    # Autofill-Job starten
    resp = requests.post(
        f"{CANVA_API_BASE}/autofills",
        headers=headers,
        json={
            "brand_template_id": brand_template_id,
            "title": title,
            "data": {
                "headline": {"type": "text", "text": headline},
                "subline":  {"type": "text", "text": subline},
            },
        },
        timeout=30,
    )
    resp.raise_for_status()
    job_id = resp.json()["job"]["id"]

    # Job pollen bis fertig (max. 60 Sekunden)
    for _ in range(30):
        time.sleep(2)
        poll = requests.get(
            f"{CANVA_API_BASE}/autofills/{job_id}",
            headers=headers,
            timeout=30,
        )
        poll.raise_for_status()
        job = poll.json()["job"]

        if job["status"] == "success":
            design = job["result"]["design"]
            return {
                "design_id": design["id"],
                "edit_url":  design.get("url", f"https://www.canva.com/design/{design['id']}/edit"),
            }
        if job["status"] == "failed":
            raise RuntimeError(f"Canva Autofill fehlgeschlagen: {job}")

    raise RuntimeError("Canva Autofill Timeout (>60s)")


def canva_active() -> bool:
    required = ["CANVA_CLIENT_ID", "CANVA_CLIENT_SECRET",
                "CANVA_REFRESH_TOKEN", "CANVA_BRAND_TEMPLATE_ID"]
    return all(os.environ.get(k) for k in required)


# ── Prompt ────────────────────────────────────────────────────────────────────

def build_prompt(date_str: str, weekday: str, month_name: str, trend_headlines: str) -> str:
    cities_str = ", ".join(CITIES)
    kernbotschaften = "\n".join(f'- "{k}"' for k in KERNBOTSCHAFTEN)

    return f"""Du bist Melia, die Marketing-KI von {BRAND['name']}.
Heute ist {weekday}, {date_str} ({month_name}).

DEINE AUFGABE:
Erstelle genau 5 Instagram-Posts für Immobilieneigentümer in der Region.
Jeder Post muss ein ANDERES Thema, eine ANDERE Formel und eine ANDERE Stadt haben.
Denk aus der Perspektive eines Eigentümers, der verkaufen möchte oder überlegt — was beschäftigt ihn wirklich?

ZIELREGION: {cities_str}

KERNBOTSCHAFTEN (mindestens 1-2 davon täglich einweben — in Subline oder Caption, NICHT zwingend als Headline):
{kernbotschaften}

HOOK-FORMELN (alle 8 stehen zur Verfügung — heute mindestens 4 verschiedene nutzen):
{HOOK_FORMULAS}

THEMEN-POOL (jeden Tag andere Kombination — heute 5 möglichst verschiedene Bereiche wählen):
{THEMEN_POOL}

CI-REGELN:
- Ton: Du-Form, direkt, menschlich, kein Makler-Sprech, keine Floskeln
- Headline: MAX 5 Wörter, trifft einen Nerv
- Subline: Genau 1 Satz — schärft die Headline, zeigt den Nutzen
- Caption: Hook-Satz → konkretes Problem (2 Sätze, lokal) → Lösung/Perspektive (1-2 Sätze) → klarer CTA
- Hashtags: 6-8, immer mind. 1 Regions-Hashtag
- CTA über die 5 Posts rotieren: Tel / Website / Wertermittlung / "Link in Bio"

STRIKTE VERBOTE (führen zu schlechten Posts):
- Keine zwei Posts mit ähnlicher Headline-Energie
- Nicht jeden Post mit "Du verschenkst..." oder "war gestern" beginnen
- Keine generischen Sätze wie "Wir helfen dir" oder "Kontaktiere uns"
- Nicht alle 5 Posts über Preis/Geld — Themenvielfalt ist Pflicht

AKTUELLE MARKTLAGE ({month_name}):
{trend_headlines}

KONTAKTDATEN:
- Tel: {BRAND['phone']}
- Web: {BRAND['website']}
- Wertermittlung: {BRAND['valuation']}

AUSGABE-FORMAT (JSON, exakt so, NUR JSON):
{{
  "datum": "{date_str}",
  "posts": [
    {{
      "nr": 1,
      "plattform": "Instagram",
      "formel": "Diagnose",
      "thema": "Preisfindung",
      "stadt_bezug": "Worms",
      "headline": "Max 5 Wörter.",
      "teal_wort": "Schlüsselwort",
      "subline": "Ein präziser Satz.",
      "caption": "Vollständige Caption.",
      "hashtags": "#Tag1 #Tag2 #Tag3 #Tag4 #Tag5 #Tag6"
    }}
  ]
}}"""


# ── Generator ─────────────────────────────────────────────────────────────────

def extract_json(raw: str) -> dict:
    """Extrahiert und parst JSON robust aus dem Modell-Output."""
    import re

    # Code-Block entfernen falls vorhanden
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()

    # Erstes { bis letztes } ausschneiden
    start = raw.find("{")
    end   = raw.rfind("}") + 1
    if start != -1 and end > start:
        raw = raw[start:end]

    return json.loads(raw)


def generate_content(date_str: str, weekday: str, month_name: str) -> tuple:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    trend_headlines = fetch_trend_headlines()
    prompt = build_prompt(date_str, weekday, month_name, trend_headlines)

    for attempt in range(3):
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = message.content[0].text.strip()
        try:
            data = extract_json(raw)
            return data, trend_headlines
        except json.JSONDecodeError as e:
            print(f"  JSON-Fehler (Versuch {attempt + 1}/3): {e}")
            print(f"  Rohtext (erste 300 Zeichen): {raw[:300]}")
            if attempt == 2:
                raise RuntimeError(f"JSON nach 3 Versuchen ungültig: {e}") from e

    raise RuntimeError("Unerwarteter Fehler in generate_content")


# ── Markdown-Ausgabe ──────────────────────────────────────────────────────────

def format_markdown(data: dict, trend_headlines: str) -> str:
    date = data["datum"]
    lines = [
        f"# Melia Daily Content — {date}",
        "*Automatisch generiert · Markus Seitz Immobilien*",
        "", "---", "",
    ]

    for post in data["posts"]:
        nr = post["nr"]
        canva_link = ""
        if post.get("canva_edit_url"):
            canva_link = f" · [In Canva öffnen]({post['canva_edit_url']})"

        lines.append(f"## Post {nr} · {post.get('plattform','Instagram')} · {post.get('stadt_bezug','')}{canva_link}")
        lines.append(f"**Formel:** {post.get('formel','')}  ")
        lines.append("")
        lines.append("### Visual")
        lines.append("```")
        headline = post["headline"]
        teal = post.get("teal_wort", "")
        if teal:
            headline = headline.replace(teal, f"[TEAL: {teal}]")
        lines.append(f"HEADLINE:  {headline}")
        lines.append(f"SUBLINE:   {post['subline']}")
        lines.append(f"LOGO:      MS-Monogramm + MARKUS SEITZ IMMOBILIEN")
        lines.append("```")
        lines.append("")
        lines.append("### Caption")
        lines.append(post["caption"])
        lines.append("")
        lines.append(f"**Hashtags:** {post['hashtags']}")
        lines.append("")
        lines.append("---")
        lines.append("")

    if trend_headlines and trend_headlines != "Keine aktuellen Schlagzeilen verfügbar.":
        lines.append("## Trend-Quellen heute")
        lines.append(trend_headlines)
        lines.append("")

    lines.append(f"*Generiert: {date} · Melia v1.2 · claude-sonnet-4-6*")
    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    now        = datetime.datetime.now()
    date_str   = now.strftime("%Y-%m-%d")
    weekday    = ["Montag","Dienstag","Mittwoch","Donnerstag",
                  "Freitag","Samstag","Sonntag"][now.weekday()]
    month_name = ["Januar","Februar","März","April","Mai","Juni",
                  "Juli","August","September","Oktober","November",
                  "Dezember"][now.month - 1]

    print(f"Melia generiert Content für {date_str}...")

    data, trend_headlines = generate_content(date_str, weekday, month_name)

    # ── Canva-Posts automatisch erstellen ──────────────────────────────────
    if canva_active():
        print("Canva-Integration aktiv — erstelle Posts...")
        try:
            access_token      = canva_get_access_token()
            brand_template_id = os.environ["CANVA_BRAND_TEMPLATE_ID"]

            for post in data["posts"]:
                nr       = post["nr"]
                city     = post.get("stadt_bezug", f"Post{nr}")
                headline = post["headline"]
                subline  = post["subline"]
                title    = f"Melia Post {nr} — {city} — {date_str}"

                print(f"  Erstelle Canva Post {nr} ({city})...")
                result = canva_create_post(
                    access_token, brand_template_id,
                    title, headline, subline
                )
                post["canva_design_id"] = result["design_id"]
                post["canva_edit_url"]  = result["edit_url"]
                print(f"  ✓ Post {nr}: {result['design_id']}")

        except Exception as e:
            print(f"  ⚠ Canva-Fehler (Text-Content wurde trotzdem gespeichert): {e}")
    else:
        print("Canva-Integration nicht konfiguriert — nur Text-Content wird gespeichert.")
        print("  → Secrets CANVA_CLIENT_ID / CANVA_CLIENT_SECRET /")
        print("    CANVA_REFRESH_TOKEN / CANVA_BRAND_TEMPLATE_ID in GitHub hinterlegen.")

    # ── Dateien speichern ──────────────────────────────────────────────────
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    md_path   = os.path.join(OUTPUT_DIR, f"{date_str}.md")
    json_path = os.path.join(OUTPUT_DIR, "latest.json")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(format_markdown(data, trend_headlines))

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✓ {md_path}")
    print(f"✓ {json_path}")
    print(f"✓ {len(data['posts'])} Posts generiert")

    for post in data["posts"]:
        canva_id = post.get("canva_design_id", "—")
        print(f"  Post {post['nr']}: {post['headline']}  [{canva_id}]")


if __name__ == "__main__":
    main()
