# ローカル公開の整理（リバースプロキシ/複数アプリ共存）：30章アウトライン📚✨

（Compose は “Compose Specification” 前提で進める想定だよ〜🧩）([Docker Documentation][1])

---

## 01. まずは困りごとを言語化しよう😵‍💫🔌

* 「localhost:3000 / 5173 / 8787 …」が増えて地獄になる理由
* ゴールは「URLが人間の脳にやさしい」こと🧠💕

## 02. 完成形のイメージ図を作る🗺️✨

* “入口は1個（80/443）＋中にいくつもアプリ” の形
* 例：app1.localhost / app2.localhost / api.localhost 🎯

## 03. “公開の整理”の3大パターンを知る🧠🔀

* ポートで分ける（簡単だけど増える）
* パスで分ける（/app1 みたいに）
* サブドメインで分ける（app1.localhost みたいに）

## 04. ルーティング超入門：URLのどこで振り分ける？🔍🍰

* ホスト名（サブドメイン）で分ける
* パスで分ける
* “どっちを選ぶと幸せ？”の判断軸🌱

## 05. Windowsでローカルドメインを扱う基本🪟📝

* hostsファイルの役割（名前解決ってなに？）
* 手動編集の「やりがちミス」あるある😇([レンタルサーバー CORESERVER（コアサーバー）][2])

## 06. .localhostの最強さを知る💪🏠

* .localhost は特殊用途として予約されてる（外DNSに出にくい）
* “ローカル用の名前”として扱いやすい理由✨([rfc-editor.org][3])

## 07. サブドメイン運用のコツ🌈📛

* app1.localhost / app2.localhost を使うと何が楽？
* CookieやCORSが絡むときの注意ポイントも先に軽く👀

## 08. “とりあえず動く”用の命名ルールを決める📏✅

* 例：front.localhost / api.localhost / admin.localhost
* プロジェクトが増えても破綻しないコツ🧱

## 09. Dockerネットワークの超復習🌐🐳

* “コンテナ同士は名前で通信できる”の感覚
* ここが分かるとリバプロが急に楽になる✨

## 10. Composeでのサービス間通信の基本🧩🔗

* サービス名＝DNS名っぽく使える感覚
* “外から入る入口”と“中の通信”を分けて考える🧠

## 11. リバースプロキシって結局なに？🚪➡️🏠

* 入口で受けて、中に振り分ける人
* 「開発環境の交通整理係」だと思えばOK🚥

## 12. リバプロ候補をざっくり比較する🆚😺

* Nginx：定番だけど設定はやや硬め
* Caddy：設定が素直＆ローカルHTTPSも得意
* Traefik：Docker/Composeと相性よく“自動化寄り”
  （Traefikはv3系が主流ルートの一つになってるよ）([Traefik Labs][4])

## 13. 最短ルート：Caddyで“入口1個”を作る🚀🍞

* まずは1ファイルで動く成功体験
* パス振り分けで2アプリ共存を達成🎉

## 14. Caddyの基本ルール（読むだけで怖くなくなる）📘🙂

* “このホスト名に来たら、ここへ流す”
* “このパスはこっち” みたいな超基本だけ

## 15. フロント（Vite等）をリバプロ越しに見る🌬️🖥️

* devサーバーの特徴（HMRとか）
* リバプロ越しで詰まりやすいポイント（WebSocket）👻

## 16. APIを同じドメイン配下に寄せてCORSを減らす🧹✨

* “CORS地獄”が起きる仕組みをやさしく
* 入口でまとめると何が消える？😌

## 17. Cookieとセッションの地雷を避ける🍪💣

* SameSite / Secure / ドメイン属性の超ざっくり
* “なぜログインが飛ぶの？”を先に潰す🛠️

## 18. パス方式の設計ミニ練習：/app1 /app2 /api 🧪🧩

* どれをパスに向けると事故りにくい？
* 静的配信・SPA・APIの住み分け感覚🌿

## 19. サブドメイン方式の設計ミニ練習：app1.localhost など🏷️🎯

* “本番に近い感覚”になりやすい
* CookieやOAuthがあるときのメリットも👀

## 20. ここから自動化ルート：Traefik入門🚦🤖

* “ラベルでルーティングが増える”感覚
* Composeに書いていくだけで勝手に増える嬉しさ✨([Traefik Labs Docs][5])

## 21. Traefikのダッシュボードを安全に使う🧯📊

* 見える化は超便利
* でも公開しちゃダメな設定もあるので “ローカル限定”ルール💡

## 22. “共通の入口”を別スタックとして切り出す📦🚪

* proxy用Composeを1つ作って、各アプリを接続する
* 「毎回コピペで事故」を減らす設計🎁

## 23. 複数プロジェクトを同居させるためのネットワーク設計🧵🧠

* external network の考え方（超やさしく）
* “AプロジェクトとBプロジェクトが喧嘩しない”を作る🥊🚫

## 24. ポート競合を永久に起こさないコツ📛🔒

* 入口の80/443以外は “基本、外に出さない”方針
* DBやRedisを外公開しないのが標準🧊

## 25. ローカルHTTPSの必要性を知る

* “最近のWeb機能はHTTPS前提が増える”問題
* だからローカルでもHTTPSが欲しくなる場面がある😅

## 26. CaddyのローカルHTTPSを使ってみる🌟🔒

* ローカル/内部名に対してHTTPSを提供できる仕組み
* “証明書まわりの苦しさ”が軽くなる方向性✨([Caddy Web Server][6])

## 27. mkcertで「信頼されたローカル証明書」を作る🪄📜

* ブラウザ警告を減らしやすい
* ワイルドカードも作れて便利（例：*.example系）([GitHub][7])

## 28. ありがちトラブル辞典：404/502/つながらない📕🧯

* 404：ルールが合ってない
* 502：中のサービスが死んでる/ポート違い
* つながらない：名前解決 or ネットワーク接続ミス👀

## 29. ログと観測の最小セット👂📈

* 入口（リバプロ）のアクセスログを見る
* “どこまで届いて、どこで落ちた？”の切り分け🕵️

## 30. AIで爆速テンプレ化して卒業🎓🚀🤖

* Copilot/Codexに「Caddy設定」「Traefikラベル」「Compose分離」を作らせる型
* 仕上げに“チェックリスト”を固定して、毎回勝つ✅✨

  * 新PJ作ったら：名前ルール、入口追加、疎通、ログ確認、完了🎉

---

### ざっくり補足（2026っぽい前提の裏取りメモ）🧾✨

* WindowsでのDockerは Docker Desktop＋WSL2エンジンが基本ルートになってるよ🐳🪟([Docker Documentation][8])
* Nodeは v24 がActive LTS、v25 がCurrent という整理（2026-02時点）🟢([Node.js][9])
* TypeScriptは 5.9系が最新ノート更新されていて、6.0 Betaも出てきてる流れだよ🧠✨([typescriptlang.org][10])

---

次は、この30章の中身を「各章：目的→図→手順→よくあるミス→AIに聞く例→ミニ課題」で、テンプレ化した“本文フォーマット”も作れるよ📦✨

[1]: https://docs.docker.com/reference/compose-file/?utm_source=chatgpt.com "Compose file reference | Docker Docs"
[2]: https://help.coreserver.jp/manual/hosts-win/?utm_source=chatgpt.com "hostsファイルの設定方法（Windows） | マニュアル | サポート"
[3]: https://www.rfc-editor.org/rfc/rfc6761.html?utm_source=chatgpt.com "RFC 6761: Special-Use Domain Names"
[4]: https://traefik.io/blog/traefik-proxy-3-6-ramequin?utm_source=chatgpt.com "Traefik Proxy 3.6 \"Ramequin\": Where Every Layer Counts"
[5]: https://doc.traefik.io/traefik/setup/docker/?utm_source=chatgpt.com "Setup Traefik Proxy in Docker Standalone"
[6]: https://caddyserver.com/docs/automatic-https?utm_source=chatgpt.com "Automatic HTTPS — Caddy Documentation"
[7]: https://github.com/FiloSottile/mkcert?utm_source=chatgpt.com "FiloSottile/mkcert: A simple zero-config tool to make locally ..."
[8]: https://docs.docker.com/desktop/features/wsl/?utm_source=chatgpt.com "Docker Desktop WSL 2 backend on Windows"
[9]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[10]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"
