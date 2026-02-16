# 第30章：AIで爆速テンプレ化して卒業🎓🚀🤖

この章のゴールはシンプル！
**「新しいプロジェクトを作るたびに、リバプロまわり（Compose / Caddy / Traefik / ネットワーク）を“毎回同じ品質”で最速セットアップできる」**状態に持っていくよ〜✅✨

---

## 1) “卒業”って何を指すの？🎓👀

卒業できてる状態は、だいたいこれ👇

* 新PJを作ったら **5〜10分**で入口（80/443）にぶら下げられる🚪✨
* **ポート直打ち**（localhost:5173…）が増えない🧠💤
* トラブルが起きても、**ログとチェックリストで自力で切り分け**できる🕵️‍♂️
* AIに作らせても、**危ない設定を混ぜない**（ガードレールがある）🧯✅

---

## 2) AIテンプレ化の基本戦略🧩🧠

ポイントは「AIに全部丸投げ」じゃなくて、**“型”を固定して、毎回その型に沿って生成させる**ことだよ😺✨

### 型（テンプレ）を3つに分ける📦📦📦

1. **入口スタック**（proxy専用Compose）🚪
2. **アプリスタック**（各PJのCompose）🧱
3. **運用チェックリスト**（人間の最終確認）✅

こうすると、AIが作る範囲が狭くなって事故りにくい！🚑💦

---

## 3) “AIに渡す情報”は最小でOK✍️🧠

AIに渡すべき情報はだいたいこの7つだけで回るよ👇

* 入口方式：**Caddy** or **Traefik**（どっちの雛形を吐くか）
* 外に出すURL：例 `front.localhost` / `api.localhost` 🏷️
* 内部ポート：例 フロント `5173` / API `3000` 🔌
* 共有ネットワーク名：例 `proxy-net` 🧵
* 公開方針：**原則 80/443 以外は外に出さない**🔒
* ログの見方：入口ログ＋アプリログの2段階👂
* 完了条件（テスト）：ブラウザ / curl / 502時の確認ポイント🧪

※Composeの書き方は **Compose Specification** が推奨の前提でOKだよ〜🧩
([Docker Documentation][1])

---

## 4) VS Code + Copilot/Codexで勝つコツ💻🧠✨

AIの出力精度は「コンテキスト」で決まることが多いよ！

* **関係ファイルだけ開く**（proxyのcompose、Caddyfile、appのcompose など）
* 逆に関係ないファイルは閉じる（ノイズ減らす）🙈
* “お願い”じゃなく **仕様として命令**する（後述のプロンプト型）📜
* 出力は **ファイル単位**で要求（コピペしやすい）📄✨

これは GitHub の公式ベストプラクティスでも推されてるやつ👍
([GitHub Docs][2])

---

## 5) コピペで使える「プロンプトの型」📦🤖

ここが本体！この型を固定すると、毎回の品質が安定するよ✅✨

## 5-1) “入口スタック（proxy）”を作らせるプロンプト🚪🤖

* **Caddy版**は「設定が短い」「ローカルHTTPSがラク」寄り
* **Traefik版**は「ラベルで増やせる」「自動化が強い」寄り

Caddyはローカル/内部ホストも含めてHTTPSを自動で扱える（無効化しない限り）って方針が明確だよ🔐✨
([Caddy Web Server][3])

### ✅ プロンプト（Caddy入口スタック生成）

```text
あなたはDocker/Composeの設定職人です。目的は「proxy専用スタック」を作ること。
次の要件を満たすファイル一式を生成してください。

要件:
- docker-compose.yml に caddy を1サービスで定義
- 外部公開は 80/443 のみ
- 設定は Caddyfile で管理
- app 側コンテナは同一 external network (proxy-net) に参加して reverse_proxy で振り分ける
- サンプルとして front.localhost -> http://front:5173, api.localhost -> http://api:3000 を設定
- 生成物は「ファイル名」と「内容」を分けて提示
- 最後に動作確認コマンド（docker compose up -d、ログ確認、curl例）を提示

出力形式:
1) infra/proxy/docker-compose.yml
2) infra/proxy/Caddyfile
3) README.md（起動手順とトラブル時の見方）
```

---

## 5-2) “アプリスタック（各PJ）”を作らせるプロンプト🧱🤖

TraefikはDocker providerで **コンテナのlabels** を見てルーティングするのが基本だよ🏷️✨
([Traefik Docs][4])

### ✅ プロンプト（Traefikで公開されるアプリ側Compose生成）

```text
あなたはDocker Compose設計者です。既に別スタックでTraefikが動いています。
次の要件の「アプリ側docker-compose.yml」を生成してください。

要件:
- services: front (Vite想定:5173), api (Node API想定:3000)
- どちらも ports で外部公開しない（exposeはOK）
- external network proxy-net に参加
- Traefikのlabelsで host routing を定義:
  - front.localhost -> front:5173
  - api.localhost -> api:3000
- 生成物はファイル1つ（apps/sample/docker-compose.yml）
- 最後に動作確認手順（起動、curl、502のときの確認）を出す
```

---

## 5-3) “差分レビュー前提”にして事故を減らす🧯🔍

AI生成は便利だけど、**レビュー観点が固定されてないと事故る**💥
だから、AIにこう言うのが強い👇

### ✅ プロンプト（危険チェック込み）

```text
次のdocker-compose.yml / Caddyfile(or Traefik labels) をレビューして、
危険な点・改善点を「重大度:高/中/低」で箇条書きしてください。

特にチェック:
- 不要なports公開がないか（DB/Redisなど）
- insecure設定（dashboard公開、api insecureなど）が入ってないか
- external network名のズレ
- service名とルーティング先名の不一致
- 502が起きる典型ミス（port違い/起動順/healthcheck不足）
- ログ確認コマンドが妥当か
```

---

## 6) “テンプレの完成形”はこう置くと強い📁✨

おすすめ構成（このまま真似でOK）👇

* `infra/proxy/`（入口スタック）🚪

  * `docker-compose.yml`
  * `Caddyfile`（またはTraefik用のcompose/設定）
* `apps/<project>/`（各アプリ）🧱

  * `docker-compose.yml`
* `docs/`（運用の知恵）📚

  * `CHECKLIST.md`（次の章で作る）
  * `TROUBLESHOOTING.md`

---

## 7) 最終兵器：固定チェックリスト✅✨（これで毎回勝つ）

新PJを入口に追加したら、これだけ確認すればOK！🎉

## ✅ 入口（proxy）チェック

* 80/443以外の公開が増えてない？🔒
* ルーティング先の **service名** が合ってる？（`front` / `api` など）🏷️
* 入口ログでリクエストが見えてる？👂

## ✅ アプリ側チェック

* アプリが同じネットワークに参加してる？🧵
* `ports:` をうっかり生やしてない？（外公開してない？）🙅
* 502が出たら「アプリが起動してるか」「ポート合ってるか」を最初に見る👀

## ✅ 切り分け最短ルート（困ったらこの順）

1. ブラウザでアクセス → 何番エラー？（404/502/証明書）🌐
2. 入口ログを見る（到達してる？）👂
3. アプリログを見る（起動してる？）📜
4. コンテナ内から疎通（名前解決＆ポート）🧪

---

## 8) よくあるミス集（AI生成でも起きる）😇💥

* **service名とホスト名が混ざる**（`front.localhost` を service名だと思っちゃう）🌀
* **Traefikのlabelsが router/service でズレる**🏷️💥
* **Caddyfileで upstream のポートが違う**（5173/3000の打ち間違い）🔌
* **external network の名前が違う**（`proxy-net` vs `proxy_net`）🧵😵‍💫
* **DBをportsで外に出しちゃう**（これ地味に危ない）🚨

---

## 9) ミニ課題：テンプレ化して“卒業証書”ゲット🎓✨

## 課題A（10分）⏱️

* AIに **入口スタック（Caddy or Traefik）**を作らせる
* `front.localhost` と `api.localhost` が通るところまでやる🎯

## 課題B（15分）⏱️

* 新しく `admin.localhost` を追加（管理画面想定）🧑‍💻
* 追加のとき、**チェックリストだけ**で作業してみる✅

## 合格ライン🎉

* 追加が **“怖くない作業”**になってること😺
* もし壊れても、**ログ→チェック**で戻せること🧯

---

## 10) まとめ：AIは“高速化装置”、勝敗は“型”で決まる🚀🧠

* Composeは仕様ベースで書く（参照先も揃う）🧩 ([Docker Documentation][1])
* Traefikはlabels中心、Docker providerで自動化が強い🏷️ ([Traefik Docs][4])
* Caddyはreverse proxyが速くて、ローカルHTTPSも扱いやすい🔐 ([Caddy Web Server][3])
* AIは「プロンプトの型」＋「固定チェックリスト」で、毎回同じ品質にできる✅ ([GitHub Docs][2])

---

次に進むなら、ここで作った **プロンプト型**をそのまま `docs/ai-prompts.md` に固定して、
「新PJ追加の儀式」を完全テンプレ化しよう〜📦✨

[1]: https://docs.docker.com/reference/compose-file/?utm_source=chatgpt.com "Compose file reference"
[2]: https://docs.github.com/en/copilot/get-started/best-practices?utm_source=chatgpt.com "Best practices for using GitHub Copilot"
[3]: https://caddyserver.com/docs/automatic-https?utm_source=chatgpt.com "Automatic HTTPS — Caddy Documentation"
[4]: https://doc.traefik.io/traefik/providers/docker/?utm_source=chatgpt.com "Traefik Docker Documentation"
