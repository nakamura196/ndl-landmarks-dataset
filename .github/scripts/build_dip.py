#!/usr/bin/env python3
"""release.yml の dip の段から呼ぶ、DIP（公開用の一式）の組み立てと点検（標準ライブラリだけで動く）。

  build  AIP から取り出したソース（タグの版）から、DIP のディレクトリを作る
  check  DIP に必要なファイルがそろい、中身が数として合っているかを確かめる

DIP の中身:
  データのファイル（CSV・JSON・GeoJSON・datapackage.json・LICENSE）… ソースのものをそのまま写す
  iiif-collection.json … @id だけを、GitHub Pages に置いたときの URL に書き換える
  index.html           … 題名・版・各ファイルへのリンク・IIIF Kasane で開くリンクだけの静的なページ（JS なし）
  build-info.json      … 来歴。この台本ではなく、release.yml の「Record provenance in the DIP」が書く
"""

import argparse
import csv
import html
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


def pages_url(repo):
    owner, name = repo.split('/', 1)
    return f'https://{owner}.github.io/{name}/'


def cmd_build(a):
    src, out = a.src, a.out
    os.makedirs(out, exist_ok=True)
    for f in DATA:
        shutil.copy2(os.path.join(src, f), os.path.join(out, f))

    base = pages_url(a.repo)
    coll_url = base + COLLECTION
    coll = json.load(open(os.path.join(src, COLLECTION), encoding='utf-8'))
    coll['@id'] = coll_url
    with open(os.path.join(out, COLLECTION), 'w', encoding='utf-8') as fh:
        json.dump(coll, fh, ensure_ascii=False, indent=2)

    dp = json.load(open(os.path.join(src, 'datapackage.json'), encoding='utf-8'))
    e = html.escape
    title = dp.get('title') or a.repo
    links = ''.join(f'<li><a href="{e(f)}">{e(f)}</a></li>\n' for f in DATA)
    record = f'<li>Zenodo の記録（AIP）: <a href="{e(a.record_url)}">{e(a.record_url)}</a></li>\n' if a.record_url else ''
    page = f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} {e(a.tag)}</title>
</head>
<body>
<h1>{e(title)}</h1>
<p>版: {e(a.tag)}</p>
<h2>IIIF Collection</h2>
<ul>
<li><a href="{e(COLLECTION)}">{e(COLLECTION)}</a>（{len(coll.get('manifests') or [])} 件のマニフェスト）</li>
<li><a href="{e(KASANE + urllib.parse.quote(coll_url, safe=''))}">IIIF Kasane で開く</a></li>
</ul>
<h2>地図</h2>
<ul>
<li><a href="{e(GEOJSON)}">{e(GEOJSON)}</a> ・ <a href="{e(GEOJSON_IO + urllib.parse.quote(base + GEOJSON, safe=''))}">geojson.io で地図に表示する</a></li>
</ul>
<h2>データ</h2>
<ul>
{links}</ul>
<h2>来歴</h2>
<ul>
<li><a href="build-info.json">build-info.json</a>（この一式を作った AIP の SHA-256・コミット・道具の版）</li>
{record}<li>ソース: <a href="https://github.com/{e(a.repo)}/tree/{e(a.tag)}">https://github.com/{e(a.repo)}/tree/{e(a.tag)}</a></li>
</ul>
</body>
</html>
'''
    with open(os.path.join(out, 'index.html'), 'w', encoding='utf-8') as fh:
        fh.write(page)
    print(f'DIP: {out}（{len(DATA) + 2} ファイル）')


def csv_rows(path, dialect):
    with open(path, encoding='utf-8', newline='') as fh:
        r = csv.reader(fh, delimiter=dialect.get('delimiter', ','), quotechar=dialect.get('quoteChar', '"'))
        header = next(r)
        return header, sum(1 for _ in r)


def cmd_check(a):
    out, problems, lines = a.dip, [], []
    need = DATA + [COLLECTION, 'index.html']
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
