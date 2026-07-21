#!/usr/bin/env python3
"""Build banner_v15 - Dynamic portrait integration, large fonts, cinzel logo"""
import base64, os

SCRAP = "/tmp/claude-0/-home-user-Flyer-DIN-A5-MSI/42111a4b-b448-50ff-8059-949f7f97c189/scratchpad"

def rb64(name):
    p = os.path.join(SCRAP, name)
    return open(p).read().strip()

portrait_b64  = rb64("portrait_clean_b64.txt")
cinzel_b64    = rb64("cinzel_b64.txt")
cg_b64        = rb64("cormorant_b64.txt")
mont800_b64   = rb64("montserrat_800_b64.txt")
mont700_b64   = rb64("montserrat_700_b64.txt")
os400_b64     = rb64("opensans_400_b64.txt")
os600_b64     = rb64("opensans_600_b64.txt")
qr_b64        = rb64("qr_b64.txt")

# SVG icons (phone, mail, globe) as data URIs
ICON_PHONE = """<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%231abcbc' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07A19.5 19.5 0 013.07 9.6a19.79 19.79 0 01-3.07-8.68A2 2 0 012 0h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L6.09 7.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45 12.84 12.84 0 002.81.7A2 2 0 0122 14.92z'/></svg>"""
ICON_MAIL  = """<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%231abcbc' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z'/><polyline points='22,6 12,13 2,6'/></svg>"""
ICON_WEB   = """<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%231abcbc' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><circle cx='12' cy='12' r='10'/><line x1='2' y1='12' x2='22' y2='12'/><path d='M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10A15.3 15.3 0 0112 2z'/></svg>"""

def icon_uri(svg_str):
    import urllib.parse
    return "data:image/svg+xml," + urllib.parse.quote(svg_str.replace('\n',''))

# Build the MS logo SVG with Cinzel Bold
def build_logo_svg(cinzel_b64_data):
    return f"""<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      @font-face {{
        font-family: 'CZ';
        src: url('data:font/woff2;base64,{cinzel_b64_data}') format('woff2');
        font-weight: 700;
      }}
    </style>
    <linearGradient id="sg15" x1="0.2" y1="0" x2="0.8" y2="1">
      <stop offset="0%" stop-color="#10a0b8"/>
      <stop offset="100%" stop-color="#20d4d4"/>
    </linearGradient>
    <clipPath id="cc15"><circle cx="100" cy="100" r="97"/></clipPath>
  </defs>
  <!-- Outer ring: slightly lighter navy than main banner bg for intentional differentiation -->
  <circle cx="100" cy="100" r="100" fill="#1a2d4a"/>
  <!-- Inner face slightly lighter -->
  <circle cx="100" cy="100" r="97" fill="#0f2240"/>
  <!-- Subtle inner gradient for depth -->
  <g clip-path="url(#cc15)">
    <!-- M slightly larger, white, positioned left-center -->
    <text x="8" y="145"
      font-family="'CZ','Cinzel','Cormorant Garamond',Georgia,serif"
      font-weight="700"
      font-size="122"
      fill="white"
      letter-spacing="-2">M</text>
    <!-- S smaller, teal gradient, overlapping M at right -->
    <text x="106" y="164"
      font-family="'CZ','Cinzel','Cormorant Garamond',Georgia,serif"
      font-weight="700"
      font-size="98"
      fill="url(#sg15)"
      letter-spacing="-1">S</text>
  </g>
  <!-- Subtle teal ring accent at edge -->
  <circle cx="100" cy="100" r="97" fill="none" stroke="#1abcbc" stroke-width="2.5" opacity="0.5"/>
</svg>"""

logo_svg = build_logo_svg(cinzel_b64)
import base64 as b64m
logo_data_uri = "data:image/svg+xml;base64," + b64m.b64encode(logo_svg.encode()).decode()

HTML = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}

@font-face {{
  font-family: 'Mont';
  src: url('data:font/woff2;base64,{mont800_b64}') format('woff2');
  font-weight: 800;
}}
@font-face {{
  font-family: 'Mont';
  src: url('data:font/truetype;base64,{mont700_b64}') format('truetype');
  font-weight: 700;
}}
@font-face {{
  font-family: 'OS';
  src: url('data:font/truetype;base64,{os400_b64}') format('truetype');
  font-weight: 400;
}}
@font-face {{
  font-family: 'OS';
  src: url('data:font/truetype;base64,{os600_b64}') format('truetype');
  font-weight: 600;
}}

/* ============================================================
   BANNER CONTAINER  3030 × 1230 px  (including 15px bleed)
   ============================================================ */
.banner {{
  position: relative;
  width: 3030px;
  height: 1230px;
  overflow: hidden;
  background: #0a1628;
  font-family: 'Mont', 'Montserrat', Arial, sans-serif;
}}

/* ---- PORTRAIT ---- */
.portrait-zone {{
  position: absolute;
  left: 0;
  top: 0;
  width: 1180px;
  height: 1230px;
  overflow: hidden;
}}
.portrait-img {{
  position: absolute;
  left: 0;
  top: 0;
  width: 1133px;
  height: 1230px;
  object-fit: cover;
  object-position: 50% 8%;
}}
/* Fade the RIGHT edge of portrait into navy background */
.portrait-fade-right {{
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(to right,
    rgba(10,22,40,0.00)  0%,
    rgba(10,22,40,0.00) 48%,
    rgba(10,22,40,0.30) 58%,
    rgba(10,22,40,0.72) 72%,
    rgba(10,22,40,0.95) 85%,
    rgba(10,22,40,1.00) 95%
  );
}}
/* Darken the TOP of portrait (gray studio bg above head) */
.portrait-fade-top {{
  position: absolute;
  top: 0; left: 0; right: 0; height: 280px;
  background: linear-gradient(to bottom,
    rgba(10,22,40,1.00)  0%,
    rgba(10,22,40,0.70) 35%,
    rgba(10,22,40,0.00) 100%
  );
}}
/* Subtle darkening of portrait bottom */
.portrait-fade-bottom {{
  position: absolute;
  bottom: 0; left: 0; right: 0; height: 200px;
  background: linear-gradient(to top,
    rgba(10,22,40,0.85)  0%,
    rgba(10,22,40,0.00) 100%
  );
}}

/* ---- DIAGONAL TEAL ACCENT (between portrait and content) ---- */
.diagonal-accent-1 {{
  position: absolute;
  left: 1000px;
  top: -80px;
  width: 6px;
  height: 1450px;
  background: linear-gradient(to bottom,
    rgba(26,188,188,0.00)  0%,
    rgba(26,188,188,0.55) 12%,
    rgba(26,188,188,0.55) 88%,
    rgba(26,188,188,0.00) 100%
  );
  transform: rotate(-7deg);
  transform-origin: top center;
}}
.diagonal-accent-2 {{
  position: absolute;
  left: 1020px;
  top: -80px;
  width: 3px;
  height: 1450px;
  background: linear-gradient(to bottom,
    rgba(26,188,188,0.00)  0%,
    rgba(26,188,188,0.25) 12%,
    rgba(26,188,188,0.25) 88%,
    rgba(26,188,188,0.00) 100%
  );
  transform: rotate(-7deg);
  transform-origin: top center;
}}

/* ---- CONTENT ZONE ---- */
.content-zone {{
  position: absolute;
  left: 1060px;
  top: 0;
  width: 1955px;
  height: 1230px;
}}

/* LOGO + BRAND NAME */
.brand-block {{
  position: absolute;
  top: 58px;
  left: 14px;
  display: flex;
  align-items: center;
  gap: 28px;
}}
.logo-img {{
  width: 150px;
  height: 150px;
  flex-shrink: 0;
}}
.brand-text-wrap {{
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 4px;
}}
.brand-name {{
  font-family: 'Mont','Montserrat',Arial,sans-serif;
  font-weight: 800;
  font-size: 50px;
  color: #ffffff;
  letter-spacing: 3px;
  text-transform: uppercase;
  line-height: 1.05;
}}
.brand-sub {{
  font-family: 'OS','Open Sans',Arial,sans-serif;
  font-weight: 400;
  font-size: 30px;
  color: #1abcbc;
  letter-spacing: 5px;
  text-transform: uppercase;
}}

/* TEAL HORIZONTAL RULE after brand */
.brand-rule {{
  position: absolute;
  top: 238px;
  left: 14px;
  right: 60px;
  height: 3px;
  background: linear-gradient(to right, #1abcbc, rgba(26,188,188,0.0));
}}

/* MAIN HEADLINE */
.headline-zone {{
  position: absolute;
  top: 262px;
  left: 14px;
  right: 40px;
}}
.hl-eyebrow {{
  font-family: 'OS','Open Sans',Arial,sans-serif;
  font-weight: 600;
  font-size: 38px;
  color: #1abcbc;
  letter-spacing: 7px;
  text-transform: uppercase;
  margin-bottom: 20px;
}}
.hl-main {{
  font-family: 'Mont','Montserrat',Arial,sans-serif;
  font-weight: 800;
  font-size: 152px;
  color: #ffffff;
  line-height: 0.90;
  letter-spacing: -2px;
  text-transform: uppercase;
  margin-bottom: 0px;
}}
.hl-main .teal {{ color: #1abcbc; }}
.hl-sub {{
  font-family: 'Mont','Montserrat',Arial,sans-serif;
  font-weight: 800;
  font-size: 114px;
  color: #ffffff;
  line-height: 0.92;
  letter-spacing: -1px;
  text-transform: uppercase;
  margin-bottom: 24px;
}}
.hl-sub .teal {{ color: #1abcbc; }}
.hl-tagline {{
  font-family: 'Mont','Montserrat',Arial,sans-serif;
  font-weight: 700;
  font-size: 56px;
  color: #c8d8e8;
  letter-spacing: 1px;
  line-height: 1.2;
}}

/* CONTACT ZONE */
.contact-zone {{
  position: absolute;
  bottom: 80px;
  left: 14px;
  right: 40px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}}
.contact-row {{
  display: flex;
  align-items: center;
  gap: 22px;
}}
.contact-icon {{
  width: 52px;
  height: 52px;
  flex-shrink: 0;
}}
.contact-text {{
  font-family: 'Mont','Montserrat',Arial,sans-serif;
  font-weight: 700;
  font-size: 50px;
  color: #ffffff;
  letter-spacing: 0.5px;
  line-height: 1;
}}

/* QR + Tagline block, right side of contact zone */
.qr-block {{
  position: absolute;
  bottom: 56px;
  right: 52px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
}}
.qr-img {{
  width: 200px;
  height: 200px;
  border: 6px solid white;
  border-radius: 12px;
  background: white;
  padding: 4px;
}}
.qr-label {{
  font-family: 'OS','Open Sans',Arial,sans-serif;
  font-weight: 600;
  font-size: 24px;
  color: #c8d8e8;
  letter-spacing: 2px;
  text-align: center;
}}

/* ---- TEAL GEOMETRIC ACCENTS ---- */

/* Left bleed bar */
.left-bar {{
  position: absolute;
  left: 0; top: 0;
  width: 15px; height: 1230px;
  background: #1abcbc;
}}

/* Bottom bar */
.bottom-bar {{
  position: absolute;
  left: 0; bottom: 0;
  width: 3030px; height: 42px;
  background: linear-gradient(to right, #0d8eaa, #1abcbc 30%, #1abcbc 70%, #0d8eaa);
}}

/* Top-left corner teal dot accent */
.corner-tl {{
  position: absolute;
  left: 15px; top: 15px;
  width: 60px; height: 60px;
  border-top: 5px solid #1abcbc;
  border-left: 5px solid #1abcbc;
}}

/* Bottom-right teal bracket in content area */
.corner-br {{
  position: absolute;
  right: 15px; bottom: 42px;
  width: 60px; height: 60px;
  border-bottom: 5px solid #1abcbc;
  border-right: 5px solid #1abcbc;
}}

/* CROP MARKS */
.crop {{
  position: absolute;
  background: rgba(0,0,0,0.4);
}}
/* top-left */
.cm-tl-h {{ left:0; top:15px; width:10px; height:1px; }}
.cm-tl-v {{ left:15px; top:0; width:1px; height:10px; }}
/* top-right */
.cm-tr-h {{ right:0; top:15px; width:10px; height:1px; }}
.cm-tr-v {{ right:15px; top:0; width:1px; height:10px; }}
/* bottom-left */
.cm-bl-h {{ left:0; bottom:15px; width:10px; height:1px; }}
.cm-bl-v {{ left:15px; bottom:0; width:1px; height:10px; }}
/* bottom-right */
.cm-br-h {{ right:0; bottom:15px; width:10px; height:1px; }}
.cm-br-v {{ right:15px; bottom:0; width:1px; height:10px; }}

</style>
</head>
<body>
<div class="banner">

  <!-- PORTRAIT with gradient overlays -->
  <div class="portrait-zone">
    <img class="portrait-img" src="data:image/jpeg;base64,{portrait_b64}" alt="Markus Seitz"/>
    <div class="portrait-fade-top"></div>
    <div class="portrait-fade-right"></div>
    <div class="portrait-fade-bottom"></div>
  </div>

  <!-- DIAGONAL TEAL ACCENT LINES -->
  <div class="diagonal-accent-1"></div>
  <div class="diagonal-accent-2"></div>

  <!-- CONTENT ZONE -->
  <div class="content-zone">

    <!-- Logo + Brand Name -->
    <div class="brand-block">
      <img class="logo-img" src="{logo_data_uri}" alt="MS Logo"/>
      <div class="brand-text-wrap">
        <div class="brand-name">Markus Seitz</div>
        <div class="brand-sub">Immobilien &nbsp;·&nbsp; iad</div>
      </div>
    </div>

    <!-- Horizontal teal rule -->
    <div class="brand-rule"></div>

    <!-- Main Headline -->
    <div class="headline-zone">
      <div class="hl-eyebrow">Ihr Makler für Worms &amp; Region</div>
      <div class="hl-main">Strategie</div>
      <div class="hl-sub">schlägt <span class="teal">Zufall.</span></div>
      <div class="hl-tagline">Professionell · Persönlich · Erfolgreich</div>
    </div>

    <!-- Contact -->
    <div class="contact-zone">
      <div class="contact-row">
        <img class="contact-icon" src="{icon_uri(ICON_PHONE)}" alt=""/>
        <span class="contact-text">+49 176 158 585 11</span>
      </div>
      <div class="contact-row">
        <img class="contact-icon" src="{icon_uri(ICON_MAIL)}" alt=""/>
        <span class="contact-text">markus.seitz@iaddeutschland.de</span>
      </div>
      <div class="contact-row">
        <img class="contact-icon" src="{icon_uri(ICON_WEB)}" alt=""/>
        <span class="contact-text">www.markus-seitz.immobilien</span>
      </div>
    </div>

  </div>

  <!-- QR Code block -->
  <div class="qr-block">
    <img class="qr-img" src="data:image/png;base64,{qr_b64}" alt="QR"/>
    <div class="qr-label">JETZT SCANNEN</div>
  </div>

  <!-- GEOMETRIC ACCENTS -->
  <div class="left-bar"></div>
  <div class="corner-tl"></div>
  <div class="corner-br"></div>
  <div class="bottom-bar"></div>

  <!-- CROP MARKS -->
  <div class="crop cm-tl-h"></div>
  <div class="crop cm-tl-v"></div>
  <div class="crop cm-tr-h"></div>
  <div class="crop cm-tr-v"></div>
  <div class="crop cm-bl-h"></div>
  <div class="crop cm-bl-v"></div>
  <div class="crop cm-br-h"></div>
  <div class="crop cm-br-v"></div>

</div>
</body>
</html>"""

out_path = os.path.join(SCRAP, "banner_final_v15.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(HTML)

size_kb = os.path.getsize(out_path) // 1024
print(f"Written: {out_path}  ({size_kb} KB)")
print("Done!")
