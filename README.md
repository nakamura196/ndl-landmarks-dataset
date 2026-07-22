# 錦絵と写真でめぐる日本の名所（データセット）

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

日本全国の名所と、各名所に紐づく江戸〜明治大正期の錦絵・写真の一覧データセット。
国立国会図書館の電子展示会「錦絵と写真でめぐる日本の名所」を地図データ化したもの。

- 名所: **323** 件（全件に緯度経度あり / 解説 135 件）
- 画像: **2671** 点（ユニーク書物 504 件 / パブリックドメイン **2405** 点）

## ダウンロード

| 形式 | リンク |
|---|---|
| GeoJSON | [`ndl-landmarks.geojson`](./ndl-landmarks.geojson) |
| CSV（名所） | [`sights.csv`](./sights.csv) |
| CSV（画像） | [`images.csv`](./images.csv) |

GeoJSON は GitHub 上でそのまま地図表示され、CSV は表としてプレビューされます。

## 引用例

> 国立国会図書館「錦絵と写真でめぐる日本の名所」データセット, 2026,
> https://github.com/nakamura196/ndl-landmarks-dataset （CC BY 4.0）.

## 出典・ライセンス

- **出典**: 国立国会図書館「錦絵と写真でめぐる日本の名所」  
  https://www.ndl.go.jp/landmarks
- 画像原本: 国立国会図書館デジタルコレクション（各レコードの `ndl_viewer_url` / `iiif_image_url`）
- **編纂データ（座標・分類・CSV/GeoJSON 構造）**: CC BY 4.0。利用時は上記出典を明示してください。
- **画像**: 各レコードの `rights` 列を参照（`PDM` = パブリックドメイン等）。権利状態は資料ごとに異なります。
- **解説文（`description`）**: 国立国会図書館が執筆したテキストであり著作権は同館に帰属します（`© 国立国会図書館`）。転載時は引用の範囲と出典明示にご留意ください。

権利表示の内訳（画像点数）: {"PDM":2405,"(不明)":266}

## ファイル

| ファイル | 形式 | 用途 |
|---|---|---|
| `ndl-landmarks.geojson` | GeoJSON | 地図/GIS。1名所=1 Point、`properties.images[]` に画像 |
| `sights.csv` | CSV | 名所テーブル（`slug` 主キー） |
| `images.csv` | CSV | 画像明細（`sight_slug` で sights に結合） |
| `ndl-landmarks.json` | JSON | 書物メタ結合済みの構造化データ |
| `iiif-collection.json` | IIIF | Mirador 等の標準ビューア用 Collection |
| `datapackage.json` | Frictionless | スキーマ/ライセンス/出典の機械可読記述 |

## 生成方法

```
node scripts/ndl-landmarks/scrape.mjs    # NDL 各ページから抽出
node scripts/ndl-landmarks/enrich.mjs    # IIIF manifest で書名/権利を補完
node scripts/ndl-landmarks/export.mjs    # 本データセットを生成
```
