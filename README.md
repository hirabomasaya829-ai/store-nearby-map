# お店の近さマップ

Cloudflare Pages用のWebアプリです。

- public/index.html：地図・店舗距離計算
- functions/api/stores.js：OpenStreetMap Overpass APIへの中継

## Cloudflare Pagesの設定
GitHubリポジトリをCloudflare Pagesに接続し、Framework preset: None、Build command: 空欄、Build output directory: public に設定してください。Functionsフォルダはリポジトリのルートに置きます。

## 注意
地図と店舗情報はOpenStreetMap由来。店舗データには欠落があります。距離は直線距離。公開Overpass APIとOSMタイルの利用規約・利用制限に注意してください。大量アクセス向けには別途データ配信が必要です。