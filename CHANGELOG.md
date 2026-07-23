# 変更履歴

本データセットは [Keep a Changelog](https://keepachangelog.com/) と
[セマンティックバージョニング](https://semver.org/) に従います。

## [1.0.2] - 2026-07-23

- Zenodo メタデータを拡充: 著者 ORCID (0000-0001-8245-7925)・所属、`language: jpn`、
  作成方法 (method)、地理座標 (locations)、参考文献 (references)、記事への
  related identifier (isDocumentedBy) を追加。データ内容は 1.0.1 と同一。
- CITATION.cff に ORCID・所属を追加。

## [1.0.1] - 2026-07-23

- README・datapackage・Zenodo 説明に**位置づけ・免責**を明記: 本データセットは NDL
  公開ページの HTML から機械抽出してデータセット形式へ変換・整形した**非公式の二次
  データセット**であり、内容そのものは国立国会図書館によるもの、という点を明確化。
- Zenodo の説明文の件数を実データ（名所 534 / 画像 4155）に修正。

## [1.0.0] - 2026-07-23

初版。

- 名所 534 件（全件に緯度経度あり）を、NDL 電子展示会のクロスリンクを
  幅優先巡回して網羅的に収集。
- 画像 4155 点（ユニーク書物 1081 件）。IIIF URL・書誌情報・
  権利表示を付与。到達不能な画像は除外。
- その他の資料（書物参照）373 件。
- 形式: GeoJSON / CSV(名所・画像・その他資料) / JSON / IIIF Collection /
  Frictionless datapackage。
- ライセンス: 編纂データ CC BY 4.0 / 画像は各 rights / 解説は © 国立国会図書館。
