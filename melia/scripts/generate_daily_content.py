"""
Melia Daily Content Generator
Markus Seitz Immobilien — täglich 06:00 Uhr automatisch

Generiert 5 CI-konforme Hooks mit Captions auf Basis von
Markttrends für Worms, Mannheim, Heidelberg, Darmstadt,
Mainz, Speyer, Bad Dürkheim und Ludwigshafen.
"""

import os
import json
import datetime
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

PROVEN_HOOKS = [
    "Du verlierst gerade Geld. Ohne es zu merken.",
    "Der Markt hat sich verändert.",
    "Kein Makler. Eine Strategie.",
    "Für den bestmöglichen Preis. Für dich.",
]

HOOK_FORMULAS = """
FORMEL 1 — Diagnose:
"Du [verb] gerade [problem]. [Konsequenz in 1 Satz]."
Beispiel: "Du verlierst gerade Geld. Ohne es zu merken."

FORMEL 2 — Kontrast:
"[Alte Annahme] war gestern. [Neue Realität] ist heute."
Beispiel: "Einfach inserieren war gestern. Inszenierung ist heute."

FORMEL 3 — Provokation:
"[Kurze Aussage.] [Ein-Wort-Verstärker oder Frage.]"
Beispiel: "Kein Makler. Eine Strategie."

FORMEL 4 — Zahl:
"[Zahl] [überraschende Aussage]."
Beispiel: "8 Sekunden. So lang schaut ein Käufer auf dein Inserat."

FORMEL 5 — Lokal:
"[Stadt/Region] hat sich verändert. [Was das für Dich bedeutet.]"
Beispiel: "Mannheim 2025: Wer jetzt verkauft, braucht Strategie."
"""

# ── Trend-Quellen (RSS) ────────────────────────────────────────────────────────

RSS_FEEDS = [
    "https://www.wormser-zeitung.de/feed",
    "https://www.rnz.de/rss/feed.rss",          # Rhein-Neckar-Zeitung
    "https://www.allgemeine-zeitung.de/feed",
    "https://www.immobilienscout24.de/ratgeber/feed/",
]

def fetch_trend_headlines() -> str:
    """Versucht, aktuelle Schlagzeilen aus RSS-Feeds zu laden."""
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


# ── Prompt ────────────────────────────────────────────────────────────────────

def build_prompt(date_str: str, weekday: str, month_name: str, trend_headlines: str) -> str:
    cities_str = ", ".join(CITIES)

    return f"""Du bist Melia, die Marketing-KI von {BRAND['name']}.
Tagline: "{BRAND['tagline']}"
Kern-Hook: "{BRAND['hook_core']}"

Heute ist {weekday}, {date_str} ({month_name}).

DEINE AUFGABE:
Erstelle genau 5 tagesaktuelle Marketing-Hooks mit vollständigen Captions.
Jeder Hook muss anders sein — verschiedene Formeln, verschiedene Städte, verschiedene Themen.

ZIELREGION: {cities_str}

CI-REGELN (absolut einzuhalten):
- Ton: Du-Form, direkt, kurz, kein Makler-Sprech
- Headline: MAX 5 Wörter — [TEAL: Schlüsselwort] markieren
- Subline: Genau 1 Satz
- Caption: Hook → Problem (2 Sätze, lokal) → Lösung (1-2 Sätze) → CTA
- Hashtags: 6-8, immer #MaklerWorms oder Regionalhashtag dabei
- CTA rotieren: Telefon / Website / "Link in Bio"

HOOK-FORMELN:
{HOOK_FORMULAS}

BEWÄHRTE HOOKS (NICHT kopieren, aber ähnliche Energie):
{chr(10).join(f'- {h}' for h in PROVEN_HOOKS)}

AKTUELLE MARKTLAGE ({month_name}):
{trend_headlines}

KONTAKTDATEN (in CTAs verwenden):
- Tel: {BRAND['phone']}
- Web: {BRAND['website']}
- Wertermittlung: {BRAND['valuation']}

AUSGABE-FORMAT (JSON, exakt so):
{{
  "datum": "{date_str}",
  "posts": [
    {{
      "nr": 1,
      "plattform": "Instagram",
      "formel": "Diagnose",
      "stadt_bezug": "Worms",
      "headline": "Du [X] gerade [Y].",
      "teal_wort": "[Y]",
      "subline": "Ein Satz.",
      "caption": "Vollständige Caption mit Hook, Problem, Lösung, CTA.",
      "hashtags": "#Tag1 #Tag2 #Tag3 #Tag4 #Tag5 #Tag6"
    }},
    ... (5 Posts total)
  ]
}}

Wichtig: Gib NUR valides JSON zurück, kein Text davor oder danach."""


# ── Generator ─────────────────────────────────────────────────────────────────

def generate_content(date_str: str, weekday: str, month_name: str) -> dict:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    trend_headlines = fetch_trend_headlines()

    prompt = build_prompt(date_str, weekday, month_name, trend_headlines)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = message.content[0].text.strip()

    # JSON aus der Antwort extrahieren
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()

    return json.loads(raw)


# ── Markdown-Ausgabe ──────────────────────────────────────────────────────────

def format_markdown(data: dict, trend_headlines: str) -> str:
    date = data["datum"]
    lines = []

    lines.append(f"# Melia Daily Content — {date}")
    lines.append(f"*Automatisch generiert · Markus Seitz Immobilien*")
    lines.append("")
    lines.append("---")
    lines.append("")

    for post in data["posts"]:
        nr = post["nr"]
        lines.append(f"## Post {nr} · {post.get('plattform', 'Instagram')} · {post.get('stadt_bezug', '')}")
        lines.append(f"**Formel:** {post.get('formel', '')}  ")
        lines.append("")
        lines.append(f"### Visual")
        lines.append("```")
        headline = post['headline']
        teal = post.get('teal_wort', '')
        if teal:
            headline = headline.replace(teal, f"[TEAL: {teal}]")
        lines.append(f"HEADLINE:  {headline}")
        lines.append(f"SUBLINE:   {post['subline']}")
        lines.append(f"LOGO:      MS-Monogramm + MARKUS SEITZ IMMOBILIEN")
        lines.append("```")
        lines.append("")
        lines.append(f"### Caption")
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

    lines.append(f"*Generiert: {date} · Melia v1.1 · claude-sonnet-4-6*")

    return "\n".join(lines)


def format_latest_json(data: dict) -> str:
    """Speichert auch eine 'latest.json' für das Dashboard."""
    return json.dumps(data, ensure_ascii=False, indent=2)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    now = datetime.datetime.now()
    date_str   = now.strftime("%Y-%m-%d")
    weekday    = ["Montag","Dienstag","Mittwoch","Donnerstag",
                  "Freitag","Samstag","Sonntag"][now.weekday()]
    month_name = ["Januar","Februar","März","April","Mai","Juni",
                  "Juli","August","September","Oktober","November",
                  "Dezember"][now.month - 1]

    print(f"Melia generiert Content für {date_str}...")

    trend_headlines = fetch_trend_headlines()
    data = generate_content(date_str, weekday, month_name)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Tages-Datei
    md_path = os.path.join(OUTPUT_DIR, f"{date_str}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(format_markdown(data, trend_headlines))

    # latest.json für Dashboard
    json_path = os.path.join(OUTPUT_DIR, "latest.json")
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(format_latest_json(data))

    print(f"✓ {md_path}")
    print(f"✓ {json_path}")
    print(f"✓ {len(data['posts'])} Posts generiert")

    # Kurze Vorschau
    for post in data["posts"]:
        print(f"  Post {post['nr']}: {post['headline']}")


if __name__ == "__main__":
    main()
