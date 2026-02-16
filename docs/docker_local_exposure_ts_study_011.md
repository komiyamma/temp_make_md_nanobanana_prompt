# 第11章：リバースプロキシって結局なに？🚪➡️🏠

この章は「リバースプロキシ（逆プロキシ）」を **“感覚で理解”** して、次章以降（Caddy / Traefik で実装）にスッと入れる状態にするよ〜😊✨
コードも少しだけ触って「ほんとに入口が1個になるんだ！」を体験します🐳🧩

---

## 1) まず結論：リバースプロキシは「入口の係」🧑‍✈️🚪

一言でいうと👇

* **ブラウザからのリクエストを最初に受け取る“受付”**
* 受け取った後、**ルールに従って中のアプリへ振り分ける“交通整理”** 🚥

これが “リバースプロキシ” です✨
（NGINX でも「受けて→中へ渡して→返す」って説明されてるやつ！）([F5 NGINX Documentation][1])

---

## 2) 「逆」ってなにが逆？🤔🔁

普通のプロキシ（いわゆる“フォワードプロキシ”）は **クライアント側の代理** で、
「あなた（PC）→インターネット」へ出ていく時に代理してくれる感じ🧑‍💻➡️🌍

一方リバースプロキシは **サーバー側の代理** で、
「インターネット（ブラウザ）→サーバー群」へ入ってくる時に代理する感じ🌍➡️🏠🏠🏠

だから **“サーバー側の入口担当”** なんだね🚪✨

---

## 3) リバプロがやってること（超ざっくり）🧰✨

リバースプロキシは、だいたいこの仕事をするよ👇

* **受ける**：HTTP/HTTPS を入口で受信する（例：80/443）🚪
* **振り分ける**：ホスト名（サブドメイン）やパスで行き先を決める🧭
* **中に渡す**：選ばれた “中のサービス（バックエンド）” に転送する📮
* **返す**：バックエンドの返事をブラウザへ返す📦➡️🧑‍💻

NGINX なら `proxy_pass` がその代表、Caddy なら `reverse_proxy` がその代表、みたいな感じです🧠
Caddy の `reverse_proxy` は「上流（upstream）へプロキシする」って明確に書かれてるよ([Caddy Web Server][2])

---

## 4) リバプロが“しないこと”も知っておこう🙅‍♂️🧊

初心者が混乱しがちポイントを先に切るよ✂️✨

* ❌ リバプロは **アプリそのもの（Vite/Node/API）ではない**
* ❌ リバプロは **魔法の修復屋ではない**（中のアプリが落ちてたら普通に失敗する）
* ❌ ルーティングは **設定（ルール）しないと増えない**（自動化は Traefik の得意分野）

---

## 5) なんで「ローカル開発」でリバプロが効くの？💥🧠✨

ローカルでアプリが増えると…

* `localhost:3000`（フロント）
* `localhost:5173`（別フロント）
* `localhost:8787`（API）
* `localhost:6006`（Storybook）
* `localhost:5555`（管理画面）

みたいに **ポート地獄** になりがち😇🔌

そこでリバプロを入れると…

* **入口が1個（例：80/443）** になる🚪✨
* URL が **人間にやさしくなる**（`app1.localhost` / `api.localhost` とか）🧠💕
* **CORS / Cookie / OAuth の事故が減る**（同一オリジンに寄せやすい）🧹
* **バックエンドを“外に出さない”設計**にしやすい（入口だけ公開）🔒

  * 「中のサービスに直接つながると、プロキシをバイパスできちゃう」系の注意は多くの構成で語られるポイントだよ([GoToSocial Documenation][3])

---

## 6) ルールはこう考えるとラク！🧩📌

リバプロの本体はこれ👇

> **(Host, Path) → どのバックエンドへ？**

例：こういう “対応表” を作るだけ🗂️✨

| ブラウザが来たURL                   | 送り先（バックエンド）  |
| ---------------------------- | ------------ |
| `http://front.localhost/`    | `front:5173` |
| `http://api.localhost/`      | `api:8787`   |
| `http://app.localhost/api/*` | `api:8787`   |
| `http://app.localhost/*`     | `front:5173` |

この対応表を **Caddyfile / Nginx.conf / Traefik labels** で書く、ってだけだよ😊

---

## 7) ミニ体験：入口1個で2アプリに振り分ける🎮🚪✨（超ミニ）

ここでは **Caddy を使って「リバプロの動き」だけ体験**します🍞
（Caddy の `reverse_proxy` が中へ転送する directive ってのを実感するやつ！([Caddy Web Server][2])）

### 📁 作るもの

* `compose.yml`
* `Caddyfile`

### ✅ compose.yml（2つの“ダミーアプリ”＋プロキシ）

```yaml
services:
  proxy:
    image: caddy:2
    ports:
      - "80:80"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
    depends_on:
      - app1
      - app2

  app1:
    image: hashicorp/http-echo:0.2.3
    command: ["-listen=:8080", "-text=Hello from app1 👋"]

  app2:
    image: hashicorp/http-echo:0.2.3
    command: ["-listen=:8080", "-text=Hello from app2 ✨"]
```

### ✅ Caddyfile（パスで振り分け：/app1 と /app2）

```caddyfile
:80 {
  handle_path /app1/* {
    reverse_proxy app1:8080
  }

  handle_path /app2/* {
    reverse_proxy app2:8080
  }

  respond "Try /app1 or /app2 🙂" 200
}
```

* `reverse_proxy` が「中の service へ渡す」役([Caddy Web Server][2])
* `handle_path` は **マッチしたパスの先頭を自動で strip してくれる** 便利機能（`/app1` を剥がして中へ渡せる）([Caddy Web Server][4])

### ▶ 起動

```bash
docker compose up -d
```

### 🌐 ブラウザで確認

* `http://localhost/` → “Try /app1 or /app2 🙂”
* `http://localhost/app1/` → “Hello from app1 👋”
* `http://localhost/app2/` → “Hello from app2 ✨”

### 🧠 ここで起きたこと（超重要）

ブラウザは **常に `localhost:80` にしか行ってない** のに、
中では **app1 / app2 に分岐** してる！🎉🚪➡️🏠🏠

これが「入口1個」思想の正体です😊✨

---

## 8) 初心者がつまずくポイント（先に予防注射💉😇）

* **404 が出る**：ルール（Host/Path）が合ってない可能性大🧩
* **502 が出る**：中のアプリが落ちてる／ポートが違う／名前（サービス名）が違う可能性大🧯
* **パスが二重になる**：`/app1` を剥がさず中へ渡してしまったパターン

  * Caddy なら `handle_path` が定番の対策になりやすいよ([Caddy Web Server][4])

---

## 9) AIに聞くと爆速になる “質問テンプレ” 🤖💨

そのままコピペで OK だよ👇（Copilot / Codex どっちでも）

* 「この要件を Caddyfile にして」

  * “`/app1` は app1:8080、`/app2` は app2:8080。`/app1` の prefix は剥がしたい。最小構成で”
* 「今の 404 の原因候補を3つ、優先度順に」

  * “Caddy が 404。`/app1/` は app1 に行くはず。compose の services は proxy/app1/app2。”
* 「502 の切り分け手順をチェックリスト化して」

  * “proxy→backend の疎通、ポート、コンテナ起動、ログ確認の順で”

Traefik の場合は「Docker provider はラベルから設定を読む」って前提が超大事なので、その前提も一緒に投げると当たりやすいよ🚦
（Traefik は Docker のラベルを監視して設定にする、って公式で説明されてる）([Traefik Labs Documentation][5])

---

## 10) ミニ課題（5〜10分）📝✨

1. さっきのデモに **/app3** を追加してみよう🎯

* `app3` を増やして、`Hello from app3 🌟` を返す
* ルールも追加して `http://localhost/app3/` で見えるようにする

2. 入口の `respond` メッセージを、**自分のプロジェクト名** に変えてみよう😄

できたら次章で「候補比較」→ その次で「Caddy最短ルート」へ行くと、めっちゃ気持ちよく進むよ〜🚀✨

[1]: https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/?utm_source=chatgpt.com "NGINX Reverse Proxy | NGINX Documentation"
[2]: https://caddyserver.com/docs/caddyfile/directives/reverse_proxy?utm_source=chatgpt.com "reverse_proxy (Caddyfile directive) — Caddy Documentation"
[3]: https://docs.gotosocial.org/en/latest/getting_started/reverse_proxy/caddy/?utm_source=chatgpt.com "Caddy 2 - GoToSocial Documentation"
[4]: https://caddyserver.com/docs/caddyfile/directives/handle_path?utm_source=chatgpt.com "handle_path (Caddyfile directive)"
[5]: https://doc.traefik.io/traefik/providers/docker/?utm_source=chatgpt.com "Traefik Docker Documentation"
