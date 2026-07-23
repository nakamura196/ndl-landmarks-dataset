# 錦絵と写真でめぐる日本の名所（データセット）

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21501348.svg)](https://doi.org/10.5281/zenodo.21501348)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

日本全国の名所と、各名所に紐づく江戸〜明治大正期の錦絵・写真の一覧データセット。
国立国会図書館「錦絵と写真でめぐる日本の名所」の公開ページから機械的に抽出し、地図データ形式へ変換・整形したものです (version 1.0.2)。

- 名所: **534** 件（全件に緯度経度あり）
- 画像: **4155** 点（ユニーク書物 1081 件 / パブリックドメイン **3885** 点）
- その他の資料（書物参照）: **373** 件
- ※ NDL 側で到達不能(404)だった **96** 画像はリンク検査で除外済み（記録は `broken-links.json`）

名所一覧は全ページのクロスリンクを幅優先で巡回して収集しています（索引ページのリストは不完全なため）。

## 位置づけ・免責

本データセットは、国立国会図書館「錦絵と写真でめぐる日本の名所」が公開している電子展示会の Web ページに埋め込まれた構造化データ（HTML）と、各資料の IIIF マニフェストから機械的に抽出し、データセット形式（GeoJSON / CSV 等）へ**変換・整形したもの**です。

- 名所の選定・画像・解説といった**内容そのものは国立国会図書館によるもの**です。本データセットはそれを第三者が扱いやすい形へ変換したものであり、座標・分類・地方区分・ファイル構造などの編纂部分を付加しています。
- **国立国会図書館が作成・提供・公認したものではありません**（非公式の二次データセット）。
- 一次情報（画像・書誌・解説）は、必ず出典元（各レコードの `ndl_viewer_url` / https://www.ndl.go.jp/landmarks）をご確認ください。

## ダウンロード

| 形式 | リンク |
|---|---|
| GeoJSON | [`ndl-landmarks.geojson`](./ndl-landmarks.geojson) |
| CSV（名所） | [`sights.csv`](./sights.csv) |
| CSV（画像） | [`images.csv`](./images.csv) |
| CSV（その他資料） | [`other-materials.csv`](./other-materials.csv) |

GeoJSON は GitHub 上でそのまま地図表示され、CSV は表としてプレビューされます。

## 引用例

> 国立国会図書館「錦絵と写真でめぐる日本の名所」データセット (version 1.0.2), 2026,
> https://doi.org/10.5281/zenodo.21501348 （CC BY 4.0）.

## 出典・ライセンス

- **出典**: 国立国会図書館「錦絵と写真でめぐる日本の名所」  
  https://www.ndl.go.jp/landmarks
- 画像原本: 国立国会図書館デジタルコレクション（各レコードの `ndl_viewer_url` / `iiif_image_url`）
- **編纂データ（座標・分類・地方・CSV/GeoJSON 構造）**: CC BY 4.0。利用時は上記出典を明示してください。
- **画像**: 各レコードの `rights` 列を参照（`PDM` = パブリックドメイン）。**空欄は IIIF manifest が無く権利未確認**であることを示し、パブリックドメインを意味しません。
- **解説文（`description`）**: 国立国会図書館が執筆したテキストであり著作権は同館に帰属します（`© 国立国会図書館`）。CC BY 4.0 の対象外です。

権利表示の内訳（画像点数）: {"PDM":3885,"(不明)":270}

## ファイル

| ファイル | 形式 | 用途 |
|---|---|---|
| `ndl-landmarks.geojson` | GeoJSON | 地図/GIS。1名所=1 Point、`properties.images[]` に画像 |
| `sights.csv` | CSV | 名所テーブル（`slug` 主キー） |
| `images.csv` | CSV | 画像明細（`sight_slug` で sights に結合） |
| `other-materials.csv` | CSV | その他の資料（書物単位の関連資料参照） |
| `ndl-landmarks.json` | JSON | 書物メタ結合済みの構造化データ |
| `iiif-collection.json` | IIIF | Mirador 等の標準ビューア用 Collection |
| `datapackage.json` | Frictionless | スキーマ/ライセンス/出典の機械可読記述 |
| `CITATION.cff` | CFF | 引用メタデータ |
| `broken-links.json` | JSON | NDL 側で到達不能だった画像の記録（除外済み） |

## 生成方法

```
node scripts/ndl-landmarks/scrape.mjs       # クロスリンクをBFS巡回して全名所を抽出
node scripts/ndl-landmarks/enrich.mjs       # IIIF manifest で書名/権利を補完
node scripts/ndl-landmarks/check-links.mjs  # 画像リンクの死活チェック
node scripts/ndl-landmarks/export.mjs       # 本データセットを生成（死リンク除外）
```
