#!/usr/bin/env python3
"""Build the translated site (ka/, fr/) from the English pages.

Edit index.html / projects.html in English, add new strings to i18n/<lang>.json,
then run:  python3 tools/build_i18n.py
It also refreshes the language menu and hreflang links in the English pages.
Strings with no translation are listed and left in English, so nothing breaks.
"""
import hashlib, html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = ['index.html', 'projects.html', 'dialyzeai.html']
LANGS = ['en', 'ka', 'fr']
NAMES = {'en': 'English', 'ka': 'ქართული', 'fr': 'Français'}
MENU_LABEL = {'en': 'Language', 'ka': 'ენა', 'fr': 'Langue'}
SITE = 'https://tskdev.org/'
EXTRA_HEAD = {
    'ka': ('<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Georgian:wght@400;500;700;800&display=swap" rel="stylesheet">\n'
           '<style>body, button { font-family: "Schibsted Grotesk", "Noto Sans Georgian", system-ui, sans-serif; }</style>'),
}
TOKEN = re.compile(r'(<!--.*?-->|<script\b.*?</script>|<style\b.*?</style>|<[^>]+>)', re.S)
ATTR = re.compile(r'(\b(?:alt|aria-label|title|content)=")([^"]*)(")')
PATH = re.compile(r'(\b(?:src|href|poster|data-video|data-poster)=")((?:img|video)/|style\.css|partners\.js)')
MENU = re.compile(r'<(details|div) class="langs"[^>]*>.*?</\1>', re.S)
ALTS = re.compile(r'(?:<link rel="alternate" hreflang="[a-z-]+" href="[^"]*">\n?)+')


def href(page, cur, target):
    if cur == 'en':
        base = '' if target == 'en' else target + '/'
    else:
        base = '../' if target == 'en' else ('' if target == cur else '../' + target + '/')
    if page == 'index.html':
        return base or './'
    return base + page


def _flag_version(l):
    return hashlib.sha1(open(os.path.join(ROOT, 'img', f'flag-{l}.svg'), 'rb').read()).hexdigest()[:8]


FLAGV = {l: _flag_version(l) for l in LANGS}


def menu(page, cur):
    img = 'img/' if cur == 'en' else '../img/'
    items = ''.join(
        f'<a href="{href(page, cur, l)}" hreflang="{l}" lang="{l}" title="{NAMES[l]}"{' aria-current="true"' if l == cur else ""}>'
        f'<img src="{img}flag-{l}.svg?v={FLAGV[l]}" alt="{NAMES[l]}" width="21" height="14"></a>'
        for l in LANGS)
    return f'<div class="langs" role="group" aria-label="{MENU_LABEL[cur]}">{items}</div>'


def alternates(page):
    tail = '' if page == 'index.html' else page
    return ''.join(f'<link rel="alternate" hreflang="{l}" href="{SITE}{"" if l == "en" else l + "/"}{tail}">\n' for l in LANGS)


def main():
    data = {l: json.load(open(os.path.join(ROOT, 'i18n', l + '.json'), encoding='utf-8')) for l in LANGS if l != 'en'}
    keep = set().union(*(set(d.get('keep', [])) for d in data.values()))

    # cache-busting: browsers keep style.css / partners.js for a while, so stamp them with a content hash
    stamps = {}
    for asset in ('style.css', 'partners.js'):
        stamps[asset] = hashlib.sha1(open(os.path.join(ROOT, asset), 'rb').read()).hexdigest()[:8]

    for page in PAGES:
        p = os.path.join(ROOT, page)
        src = open(p, encoding='utf-8').read()
        for asset, h in stamps.items():
            src = re.sub(r'"' + re.escape(asset) + r'(\?v=\w+)?"', f'"{asset}?v={h}"', src)
        src = MENU.sub(lambda m: menu(page, 'en'), src)
        src = ALTS.sub(lambda m: alternates(page), src, count=1)
        open(p, 'w', encoding='utf-8').write(src)

        for lang, d in data.items():
            strings, missing = d['strings'], []

            def tr(text):
                key = ' '.join(html.unescape(text).split())
                if key in strings:
                    return html.escape(strings[key], quote=False)
                if key and key not in keep and key not in done and re.search(r'[A-Za-z]{2}', key):
                    missing.append(key)
                return None

            def tr_attr(m):
                t = tr(m.group(2))
                return m.group(1) + (t.replace('"', '&quot;') if t is not None else m.group(2)) + m.group(3)

            s = MENU.sub('<div class="langs"></div>', src)
            done = set()
            for a, b in d.get('raw', {}).items():
                s = s.replace(a, b)
                done.update(' '.join(t.split()) for t in TOKEN.split(b) if t and not t.startswith('<'))
            out = []
            for tok in TOKEN.split(s):
                if not tok:
                    continue
                if tok.startswith('<style'):
                    out.append(tok.replace('url("img/', 'url("../img/'))
                elif tok.startswith('<script'):
                    out.append(PATH.sub(r'\1../\2', tok))
                elif tok.startswith('<!--'):
                    out.append(tok)
                elif tok.startswith('<'):
                    if not tok.startswith(('<link', '<meta name="viewport"', '<meta charset', '<details', '<summary')):
                        tok = ATTR.sub(tr_attr, tok)
                    out.append(PATH.sub(r'\1../\2', tok))
                else:
                    m = re.match(r'(\s*)(.*?)(\s*)$', tok, re.S)
                    t = tr(m.group(2)) if m.group(2).strip() else None
                    out.append(m.group(1) + t + m.group(3) if t is not None else tok)
            s = ''.join(out)
            s = MENU.sub(lambda m: menu(page, lang), s)
            s = s.replace('<html lang="en">', f'<html lang="{lang}">', 1)
            s = s.replace(f'property="og:url" content="{SITE}', f'property="og:url" content="{SITE}{lang}/')
            if lang in EXTRA_HEAD:
                s = re.sub(r'(<link rel="stylesheet" href="\.\./style\.css[^"]*">)', lambda m: m.group(1) + '\n' + EXTRA_HEAD[lang], s, count=1)
            s = s.replace('<!DOCTYPE html>', f'<!DOCTYPE html>\n<!-- Generated by tools/build_i18n.py from ../{page}. Do not edit by hand. -->', 1)
            os.makedirs(os.path.join(ROOT, lang), exist_ok=True)
            open(os.path.join(ROOT, lang, page), 'w', encoding='utf-8').write(s)
            if missing:
                print(f'{lang}/{page}: untranslated, left in English:')
                for x in dict.fromkeys(missing):
                    print('   ', x)
    print('built', ', '.join(f'{l}/{p}' for l in data for p in PAGES))


if __name__ == '__main__':
    sys.exit(main())
