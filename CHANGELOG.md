# 変更履歴

本データセットは [Keep a Changelog](https://keepachangelog.com/) と
[セマンティックバージョニング](https://semver.org/) に従います。

## [1.0.3] - 2026-11-12

- datapackage.json の `created` を、Data Package の規格どおり日時（RFC 3339）の形に直した
  （`2026-07-23` → `2026-07-23T00:00:00Z`）。記録の中身は 1.0.2 と同一（JSON・GeoJSON は版の表示だけを変えた）。
- リリースの手順（GitHub Actions）を、AIP（BagIt・METS/PREMIS）を作って Zenodo に置き、その記録と
  照らした DIP を GitHub Pages に公開する形に改めた。公開の前に、元データを Frictionless で、
  公開一式の HTML・CSS を Nu Html Checker で、リンクを機械で確かめる。
- 作成者の所属の表記を「The University of Tokyo」にそろえた（CITATION.cff・.zenodo.json）。

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
