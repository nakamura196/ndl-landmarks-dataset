#!/usr/bin/env python3
"""release.yml の dip の段から呼ぶ、DIP（公開用の一式）の組み立てと点検（標準ライブラリだけで動く）。

  build  AIP から取り出したソース（タグの版）から、DIP のディレクトリを作る
  check  DIP に必要なファイルがそろい、中身が数として合っているかを確かめる。
         あわせて、JSON がすべて読めること、HTML の中のリンク（href・src）が DIP の中で切れていないこと、
         DIP の中を指すリンクが相対であること（公開先の URL を直に書いていないこと）を確かめる。
         外のサイトへのリンクは確かめない（周辺の機能で、切れても一式は使える）

DIP の中身:
  データのファイル（CSV・JSON・GeoJSON・datapackage.json・LICENSE）… ソースのものをそのまま写す
  iiif-collection.json … @id だけを、GitHub Pages に置いたときの URL に書き換える
  endings_logo_badge_dark_mono.svg … Endings Project のバッジ（.github/assets から写す。CC BY 4.0）
  index.html           … 題名・版・各ファイルへのリンク・IIIF Kasane で開くリンクだけの静的なページ（JS なし）
  build-info.json      … 来歴。この台本ではなく、release.yml の「Record provenance in the DIP」が書く
"""

import argparse
import datetime
import csv
import html
import html.parser
import json
import os
import shutil
import sys
import urllib.parse

# ソースから、そのまま写すファイル
DATA = ['images.csv', 'sights.csv', 'other-materials.csv',
        'ndl-landmarks.json', 'ndl-landmarks.geojson', 'broken-links.json',
        'datapackage.json', 'LICENSE']
COLLECTION = 'iiif-collection.json'
KASANE = 'https://kasane.ldas.jp/ja/browse/?u='
GEOJSON = 'ndl-landmarks.geojson'
GEOJSON_IO = 'https://geojson.io/#data=data:text/x-url,'
# Endings Project のバッジ（https://endings.uvic.ca/logos.zip の SVG をそのまま、CC BY 4.0）。
# 灰色の地に白の字なので、明るい画面でも暗い画面でも読める。外から読み込まず、DIP に入れる
BADGE = 'endings_logo_badge_dark_mono.svg'
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
ENDINGS = 'https://endings.uvic.ca/compliance.html'
FILE_NOTES = {
    'iiif-collection.json': '錦絵・写真の IIIF マニフェストをまとめた Collection',
    'images.csv': '名所ごとの錦絵・写真の一覧（出典・権利の欄つき）',
    'sights.csv': '名所の一覧（緯度経度・都道府県・地方）',
    'other-materials.csv': '名所に関連するその他の資料',
    'ndl-landmarks.json': '名所と画像をまとめた JSON',
    'ndl-landmarks.geojson': '名所の位置（GeoJSON、Point）',
    'broken-links.json': '公開元で表示できなかった画像の記録',
    'datapackage.json': 'Frictionless Data Package の記述（列の定義・ライセンス）',
    'LICENSE': 'ライセンス',
}


def pages_url(repo):
    owner, name = repo.split('/', 1)
    return f'https://{owner}.github.io/{name}/'


def cmd_build(a):
    src, out = a.src, a.out
    os.makedirs(out, exist_ok=True)
    for f in DATA:
        shutil.copy2(os.path.join(src, f), os.path.join(out, f))
    shutil.copy2(os.path.join(ASSETS, BADGE), os.path.join(out, BADGE))

    base = pages_url(a.repo)
    coll_url = base + COLLECTION
    coll = json.load(open(os.path.join(src, COLLECTION), encoding='utf-8'))
    coll['@id'] = coll_url
    with open(os.path.join(out, COLLECTION), 'w', encoding='utf-8') as fh:
        json.dump(coll, fh, ensure_ascii=False, indent=2)

    dp = json.load(open(os.path.join(src, 'datapackage.json'), encoding='utf-8'))
    e = html.escape
    title = dp.get('title') or a.repo
    n_manifests = len(coll.get('manifests') or [])
    gj = json.load(open(os.path.join(src, GEOJSON), encoding='utf-8'))
    n_points = len(gj.get('features') or [])
    _, n_images = csv_rows(os.path.join(src, 'images.csv'), {})

    def size(f):
        b = os.path.getsize(os.path.join(out, f))
        return f'{b / 1024:,.0f} KB' if b >= 1024 else f'{b} B'

    rows = ''.join(
        f'<tr><td><a href="{e(f)}"><code>{e(f)}</code></a></td><td>{e(FILE_NOTES.get(f, ""))}</td>'
        f'<td class="num">{size(f)}</td></tr>\n'
        for f in [COLLECTION] + DATA)
    desc = ''.join(f'<p>{e(x)}</p>\n' for x in (dp.get('description') or '').split('\n') if x.strip())
    doi = dp.get('doi')
    doi_html = f'<div><dt>DOI（全版）</dt><dd><a href="https://doi.org/{e(doi)}">{e(doi)}</a></dd></div>' if doi else ''
    record = (f'<li>Zenodo の記録（この版の AIP）: <a href="{e(a.record_url)}">{e(a.record_url)}</a></li>\n'
              if a.record_url else '')
    built = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')
    kasane = KASANE + urllib.parse.quote(coll_url, safe='')
    gjio = GEOJSON_IO + urllib.parse.quote(base + GEOJSON, safe='')
    src_url = f'https://github.com/{a.repo}/tree/{a.tag}'
    page = f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} {e(a.tag)}</title>
<style>
:root {{ --bg:#fbfaf7; --fg:#1f2328; --muted:#5b6270; --line:#e3e0d8; --card:#ffffff; --accent:#8a3b12; --accent-bg:#f6ece4; }}
@media (prefers-color-scheme: dark) {{
  :root {{ --bg:#16181c; --fg:#e8e6e1; --muted:#a3a8b2; --line:#30343b; --card:#1e2126; --accent:#f0a274; --accent-bg:#2c221c; }}
}}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--fg); font:16px/1.75 system-ui,-apple-system,"Hiragino Sans","Noto Sans JP",sans-serif; }}
main {{ max-width:860px; margin:0 auto; padding:40px 16px 64px; }}
a {{ color:var(--accent); }}
.eyebrow {{ color:var(--muted); font-size:.85rem; letter-spacing:.04em; margin:0 0 .25rem; }}
h1 {{ font-size:1.9rem; line-height:1.35; margin:0 0 1rem; }}
h2 {{ font-size:1.15rem; margin:2.5rem 0 .75rem; padding-bottom:.35rem; border-bottom:1px solid var(--line); }}
.lead p {{ margin:.4rem 0; color:var(--muted); }}
.stats {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px; margin:1.75rem 0 0; padding:0; }}
.stats div {{ background:var(--card); border:1px solid var(--line); border-radius:10px; padding:14px 16px; }}
.stats dt {{ color:var(--muted); font-size:.8rem; }}
.stats dd {{ margin:0; font-size:1.35rem; font-weight:600; font-variant-numeric:tabular-nums; }}
.actions {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:12px; }}
.actions a {{ display:block; text-decoration:none; color:var(--fg); background:var(--card); border:1px solid var(--line); border-left:4px solid var(--accent); border-radius:10px; padding:16px 18px; }}
.actions a:hover {{ background:var(--accent-bg); }}
.actions strong {{ display:block; color:var(--accent); font-size:1.05rem; }}
.actions span {{ color:var(--muted); font-size:.9rem; }}
.table {{ overflow-x:auto; border:1px solid var(--line); border-radius:10px; background:var(--card); }}
table {{ width:100%; border-collapse:collapse; font-size:.92rem; }}
th, td {{ text-align:left; padding:10px 14px; border-bottom:1px solid var(--line); vertical-align:top; }}
tr:last-child td {{ border-bottom:0; }}
th {{ color:var(--muted); font-weight:500; font-size:.8rem; }}
td.num, th.num {{ text-align:right; white-space:nowrap; font-variant-numeric:tabular-nums; }}
code {{ font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:.88em; }}
ul.plain {{ padding-left:1.2rem; }}
.meta {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:6px 24px; margin:0; }}
.meta dt {{ color:var(--muted); font-size:.8rem; }}
.meta dd {{ margin:0 0 .5rem; word-break:break-all; }}
footer {{ margin-top:3rem; padding-top:1rem; border-top:1px solid var(--line); color:var(--muted); font-size:.85rem; display:flex; gap:16px; align-items:flex-start; }}
footer p {{ margin:0 0 .4rem; }}
footer img {{ display:block; width:37px; height:auto; }}
.note {{ color:var(--muted); font-size:.9rem; }}
</style>
</head>
<body>
<main>
<p class="eyebrow">データセット ・ 版 {e(a.tag)}</p>
<h1>{e(title)}</h1>
<div class="lead">
{desc}</div>
<dl class="stats">
<div><dt>名所</dt><dd>{n_points:,} 地点</dd></div>
<div><dt>錦絵・写真</dt><dd>{n_images:,} 件</dd></div>
<div><dt>IIIF マニフェスト</dt><dd>{n_manifests:,} 件</dd></div>
</dl>

<h2>見る</h2>
<div class="actions">
<a href="{e(kasane)}"><strong>画像を見る</strong><span>IIIF Collection を IIIF Kasane で開きます</span></a>
<a href="{e(gjio)}"><strong>地図で見る</strong><span>名所の位置を geojson.io で地図に表示します</span></a>
</div>
<p class="note">錦絵・写真の画像そのものは、国立国会図書館（NDL）の IIIF サーバから配信されています。この一式には画像は含まれず、マニフェストへのリンクだけが入っています。</p>

<h2>ファイル</h2>
<div class="table">
<table>
<thead><tr><th>ファイル</th><th>内容</th><th class="num">大きさ</th></tr></thead>
<tbody>
{rows}</tbody>
</table>
</div>

<h2>来歴</h2>
<dl class="meta">
<div><dt>版</dt><dd>{e(a.tag)}</dd></div>
{doi_html}
<div><dt>ソース</dt><dd><a href="{e(src_url)}">{e(src_url)}</a></dd></div>
</dl>
<ul class="plain">
{record}<li><a href="build-info.json"><code>build-info.json</code></a> — この一式を組み立てた AIP の SHA-256・コミット・道具の版</li>
</ul>

<footer>
<a href="{ENDINGS}"><img src="{BADGE}" alt="Endings-compliant（Endings Project の原則に沿ったサイト）" title="Endings-compliant" width="37" height="51"></a>
<div>
<p>このページと一式は、保存用の AIP から自動で組み立てたものです（{e(a.tag)}、{built} 組み立て）。JavaScript を使わずに表示できます。</p>
<p>Endings のバッジ: © The Endings Project Team, <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>（<a href="{ENDINGS}">endings.uvic.ca</a>）</p>
</div>
</footer>
</main>
</body>
</html>
'''
    with open(os.path.join(out, 'index.html'), 'w', encoding='utf-8') as fh:
        fh.write(page)
    print(f'DIP: {out}（{len(DATA) + 3} ファイル）')


def csv_rows(path, dialect):
    with open(path, encoding='utf-8', newline='') as fh:
        r = csv.reader(fh, delimiter=dialect.get('delimiter', ','), quotechar=dialect.get('quoteChar', '"'))
        header = next(r)
        return header, sum(1 for _ in r)


class _Links(html.parser.HTMLParser):
    """HTML から href・src の値を、行番号つきで集める"""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.found = []

    def handle_starttag(self, tag, attrs):
        for k, v in attrs:
            if k in ('href', 'src') and v is not None:
                self.found.append((self.getpos()[0], tag, k, v))


def check_links(out, repo):
    """DIP の中の HTML のリンクを確かめ、(問題の一覧, 数えた結果) を返す"""
    base = urllib.parse.urlsplit(pages_url(repo))
    root = os.path.realpath(out)
    problems, n_int, n_ext = [], 0, 0
    for dirpath, _, files in os.walk(out):
        for fn in sorted(files):
            if not fn.endswith('.html'):
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, out)
            parser = _Links()
            parser.feed(open(path, encoding='utf-8').read())
            for line, tag, attr, v in parser.found:
                u = urllib.parse.urlsplit(v.strip())
                where = f'{rel}:{line} <{tag} {attr}="{v}">'
                if u.scheme in ('http', 'https') or (not u.scheme and u.netloc):
                    if u.netloc.lower() == base.netloc and (u.path + '/').startswith(base.path):
                        problems.append(f'DIP の中を絶対 URL で指している: {where}')
                    else:
                        n_ext += 1
                    continue
                if u.scheme in ('mailto', 'tel'):
                    n_ext += 1
                    continue
                if u.scheme:
                    problems.append(f'使えない種類のリンク: {where}')
                    continue
                if not u.path:          # 同じページの中（#…）
                    continue
                if u.path.startswith('/'):
                    problems.append(f'サイトの根から書いたリンク（公開先では DIP の外を指す）: {where}')
                    continue
                target = os.path.realpath(os.path.join(dirpath, urllib.parse.unquote(u.path)))
                if target != root and not target.startswith(root + os.sep):
                    problems.append(f'DIP の外を指している: {where}')
                elif not (os.path.isfile(target) or os.path.isfile(os.path.join(target, 'index.html'))):
                    problems.append(f'リンク先が DIP に無い: {where}')
                else:
                    n_int += 1
    return problems, n_int, n_ext


def check_json(out):
    """DIP の中の JSON・GeoJSON がすべて読めるかを確かめ、(問題の一覧, 数) を返す"""
    problems, n = [], 0
    for dirpath, _, files in os.walk(out):
        for fn in sorted(files):
            if fn.endswith(('.json', '.geojson')):
                path = os.path.join(dirpath, fn)
                n += 1
                try:
                    json.load(open(path, encoding='utf-8'))
                except (ValueError, UnicodeDecodeError) as ex:
                    problems.append(f'JSON として読めない: {os.path.relpath(path, out)}（{ex}）')
    return problems, n


def cmd_check(a):
    out, problems, lines = a.dip, [], []
    # build-info.json は release.yml の来歴の段が書く（点検はその後に行う）
    need = DATA + [COLLECTION, 'index.html', BADGE, 'build-info.json']
    for f in need:
        p = os.path.join(out, f)
        if not os.path.isfile(p) or os.path.getsize(p) == 0:
            problems.append(f'欠けているか空: {f}')
    if not problems:
        coll = json.load(open(os.path.join(out, COLLECTION), encoding='utf-8'))
        ms = [m.get('@id') for m in coll.get('manifests') or []]
        want = pages_url(a.repo) + COLLECTION
        if coll.get('@id') != want:
            problems.append(f'{COLLECTION} の @id が {coll.get("@id")!r}（期待 {want!r}）')
        if len(set(ms)) != len(ms) or not all(m and m.startswith('https://') for m in ms):
            problems.append(f'{COLLECTION} のマニフェストに重複か不正な @id がある')
        # 期待する件数は、images.csv の iiif_manifest_url の異なり数（版ごとに変わっても使える）
        with open(os.path.join(out, 'images.csv'), encoding='utf-8', newline='') as fh:
            uniq = {r['iiif_manifest_url'] for r in csv.DictReader(fh) if r.get('iiif_manifest_url')}
        if set(ms) != uniq:
            problems.append(f'{COLLECTION} の {len(ms)} 件が images.csv のマニフェスト {len(uniq)} 件と一致しない')
        lines.append(f'- {COLLECTION}: マニフェスト {len(ms)} 件（images.csv の異なり {len(uniq)} 件と一致: {set(ms) == uniq}）')

        # GeoJSON: 読めて、点の地物の数が sights.csv の行数（名所の数）と同じ
        geo = json.load(open(os.path.join(out, GEOJSON), encoding='utf-8'))
        feats = geo.get('features') or []
        points = sum(1 for f in feats if (f.get('geometry') or {}).get('type') == 'Point')
        _, n_sights = csv_rows(os.path.join(out, 'sights.csv'), {})
        if geo.get('type') != 'FeatureCollection' or points != len(feats) or points != n_sights:
            problems.append(f'{GEOJSON} の地物 {len(feats)} 件（Point {points} 件）が sights.csv の {n_sights} 行と合わない')
        lines.append(f'- {GEOJSON}: 地物 {len(feats)} 件、うち Point {points} 件（sights.csv {n_sights} 行と一致: {points == n_sights == len(feats)}）')

        dp = json.load(open(os.path.join(out, 'datapackage.json'), encoding='utf-8'))
        for res in dp.get('resources') or []:
            path = res.get('path')
            if not path or not os.path.isfile(os.path.join(out, path)):
                problems.append(f'datapackage.json の {path} が DIP に無い')
                continue
            if res.get('format') != 'csv':
                continue
            header, n = csv_rows(os.path.join(out, path), res.get('dialect') or {})
            fields = [fl['name'] for fl in (res.get('schema') or {}).get('fields') or []]
            if fields and header != fields:
                problems.append(f'{path} の見出しが datapackage.json の schema と違う')
            declared = (res.get('stats') or {}).get('rows', res.get('count'))
            if declared is not None and int(declared) != n:
                problems.append(f'{path} の行数 {n} が datapackage.json の宣言 {declared} と違う')
            lines.append(f'- {path}: {n} 行、見出しは schema と{"一致" if header == fields else "不一致"}、'
                         f'行数の宣言 {"なし" if declared is None else declared}')

        bad, n_json = check_json(out)
        problems += bad
        lines.append(f'- JSON: {n_json} ファイル、読めないもの {len(bad)} 件')
        bad, n_int, n_ext = check_links(out, a.repo)
        problems += bad
        lines.append(f'- HTML のリンク: DIP の中 {n_int} 件（切れ・絶対 URL {len(bad)} 件）、外のサイト {n_ext} 件（確かめない）')

    with open(os.environ.get('GITHUB_STEP_SUMMARY', os.devnull), 'a') as s:
        print(f'### DIP の点検: {"そろっている" if not problems else f"**{len(problems)} 件の問題**"}', file=s)
        print('\n'.join(lines), file=s)
        for p in problems:
            print(f'- 問題: {p}', file=s)
    print('\n'.join(lines))
    for p in problems:
        print('problem:', p)
    sys.exit(1 if problems else 0)


def main(argv=None):
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('build'); s.add_argument('--src', required=True); s.add_argument('--out', required=True)
    s.add_argument('--repo', required=True); s.add_argument('--tag', required=True); s.add_argument('--record-url', default='')
    s = sub.add_parser('check'); s.add_argument('--dip', required=True); s.add_argument('--repo', required=True)
    a = p.parse_args(argv)
    {'build': cmd_build, 'check': cmd_check}[a.cmd](a)


if __name__ == '__main__':
    main()
