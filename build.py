#!/usr/bin/env python3
"""Genera le firme email FASHION.INC da config.json.

Uso:  python3 build.py
Output:
  firme/<slug>.htm   firma singola (per Outlook classico, Thunderbird, webmail)
  index.html         pagina di installazione con anteprime e pulsanti "Copia"
"""
import json
import os
import re
from html import escape

ROOT = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(os.path.join(ROOT, "config.json"), encoding="utf-8"))
# FIRME_BASE_URL=. permette l'anteprima in locale prima di pubblicare le immagini
BASE = os.environ.get("FIRME_BASE_URL", cfg["base_url"]).rstrip("/")
CO = cfg["company"]
SOCIAL = cfg["social"]

# Font: i font del PDF (Acumin Condensed, Darker Grotesque) non esistono nei client
# email, quindi si usano fallback installati su Mac/Windows.
F_NAME = "'Acumin Pro Condensed','Arial Narrow','Helvetica Neue Condensed',Arial,Helvetica,sans-serif"
F_BODY = "'Helvetica Neue',Helvetica,Arial,sans-serif"
WHITE = "#ffffff"
BLACK = "#000000"


def tel(num):
    digits = re.sub(r"\D", "", num)
    return "tel:+39" + digits


def img(name, w, h, alt):
    return (f'<img src="{BASE}/img/{name}.png" width="{w}" height="{h}" alt="{escape(alt)}" '
            f'style="display:block;border:0;outline:none;text-decoration:none;width:{w}px;height:{h}px;'
            f'color:{WHITE};font-family:{F_BODY};font-size:10px;" />')


def link(href, text, extra=""):
    return (f'<a href="{escape(href)}" style="color:{WHITE};text-decoration:none;{extra}">'
            f'<span style="color:{WHITE};text-decoration:none;">{text}</span></a>')


def text_td(content, size, lh, extra=""):
    return (f'<td style="font-family:{F_BODY};font-size:{size}px;line-height:{lh}px;mso-line-height-rule:exactly;'
            f'font-weight:300;color:{WHITE};{extra}">{content}</td>')


def contact_row(icon, alt, href, label):
    return (
        '<tr><td style="padding:0;">'
        '<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="border-collapse:collapse;">'
        '<tr>'
        f'<td width="16" valign="middle" style="width:16px;vertical-align:middle;padding:0;">{img(icon, 16, 16, alt)}</td>'
        '<td width="10" style="width:10px;font-size:1px;line-height:1px;">&nbsp;</td>'
        + text_td(link(href, escape(label)), 12, 20, "vertical-align:middle;white-space:nowrap;")
        + '</tr></table></td></tr>'
    )


def social_cell(key, icon, alt):
    url = SOCIAL.get(key, "").strip()
    pic = img(icon, 12, 12, alt)
    inner = f'<a href="{escape(url)}" style="text-decoration:none;border:0;">{pic}</a>' if url else pic
    return f'<td width="12" valign="middle" style="width:12px;vertical-align:middle;padding:0 6px 0 0;">{inner}</td>'


def signature(p):
    rows = []
    rows.append(
        '<tr><td style="font-family:' + F_NAME + ';font-size:23px;line-height:26px;mso-line-height-rule:exactly;'
        'font-weight:bold;font-stretch:condensed;letter-spacing:-0.2px;color:' + WHITE + ';padding:0;">'
        + escape(p["name"]) + '</td></tr>')
    rows.append('<tr>' + text_td(escape(p["role"]), 12, 16, "padding:1px 0 9px 0;") + '</tr>')
    if p.get("mobile"):
        rows.append(contact_row("ico-mobile", "Cellulare", tel(p["mobile"]), p["mobile"]))
    rows.append(contact_row("ico-phone", "Telefono", tel(CO["phone"]), CO["phone"]))
    rows.append(contact_row("ico-mail", "Email", "mailto:" + p["email"], p["email"]))

    socials = (social_cell("linkedin", "ico-linkedin", "LinkedIn")
               + social_cell("instagram", "ico-instagram", "Instagram")
               + social_cell("facebook", "ico-facebook", "Facebook")
               + social_cell("tiktok", "ico-tiktok", "TikTok"))
    address = (link(CO["maps_url"], escape(CO["address"])) + '<br />'
               + f'<span style="color:{WHITE};">P.IVA {escape(CO["piva"])}&nbsp;&nbsp;|&nbsp;&nbsp;{escape(CO["name"])}</span>')
    rows.append(
        f'<tr><td style="padding:11px 0 0 0;border-top:1px solid {WHITE};">'
        '<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="border-collapse:collapse;">'
        f'<tr>{socials}'
        + text_td(address, 9.5, 12, f"vertical-align:middle;white-space:nowrap;border-left:1px solid {WHITE};padding:0 0 0 6px;")
        + '</tr></table></td></tr>')
    # spazio sotto le righe contatti, prima della linea orizzontale
    rows.insert(len(rows) - 1, '<tr><td height="11" style="height:11px;font-size:1px;line-height:1px;">&nbsp;</td></tr>')

    right = ('<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="280" '
             'style="border-collapse:collapse;width:280px;">' + "".join(rows) + '</table>')

    return (
        f'<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="584" bgcolor="{BLACK}" '
        f'style="border-collapse:collapse;width:584px;background-color:{BLACK};mso-table-lspace:0pt;mso-table-rspace:0pt;">'
        f'<tr><td bgcolor="{BLACK}" style="background-color:{BLACK};padding:30px 23px 30px 22px;">'
        '<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="border-collapse:collapse;">'
        '<tr>'
        f'<td width="216" align="center" valign="middle" style="width:216px;vertical-align:middle;padding:0;">'
        + link(CO["website"], img("logo", 216, 36, "FASHION.INC – Made for brands")) +
        '</td>'
        '<td width="22" style="width:22px;font-size:1px;line-height:1px;">&nbsp;</td>'
        f'<td valign="top" style="vertical-align:top;border-left:1px solid {WHITE};padding:0 0 0 22px;">'
        + right +
        '</td></tr></table>'
        '</td></tr></table>'
    )


def plain(p):
    lines = [p["name"], p["role"]]
    if p.get("mobile"):
        lines.append("Cell. " + p["mobile"])
    lines += ["Tel. " + CO["phone"], p["email"], "", CO["name"] + " – " + CO["address"], "P.IVA " + CO["piva"]]
    return "\n".join(lines)


def standalone(p, sig):
    return ('<!DOCTYPE html>\n<html lang="it"><head><meta charset="utf-8">'
            f'<title>Firma {escape(p["name"])}</title></head>'
            '<body style="margin:0;padding:0;">\n' + sig + '\n</body></html>\n')


os.makedirs(os.path.join(ROOT, "firme"), exist_ok=True)
built = []
for p in cfg["people"]:
    sig = signature(p)
    with open(os.path.join(ROOT, "firme", p["slug"] + ".htm"), "w", encoding="utf-8") as f:
        f.write(standalone(p, sig))
    built.append({"slug": p["slug"], "name": p["name"], "role": p["role"], "html": sig, "text": plain(p)})

tpl = open(os.path.join(ROOT, "index.template.html"), encoding="utf-8").read()
data = json.dumps(built, ensure_ascii=False).replace("</", "<\\/")
with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
    f.write(tpl.replace("/*__DATA__*/[]", data))

missing = [k for k, v in SOCIAL.items() if not v.strip()]
print(f"OK: {len(built)} firme generate. Immagini da: {BASE}/img/")
if missing:
    print("ATTENZIONE: link social mancanti (icone non cliccabili):", ", ".join(missing))
