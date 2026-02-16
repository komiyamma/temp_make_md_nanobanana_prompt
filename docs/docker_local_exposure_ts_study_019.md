# 第19章：サブドメイン方式の設計ミニ練習：app1.localhost など🏷️🎯

この章は「設計の練習」がメインだよ〜🧠✨
手を動かしつつ、「どう決めると後でラクか？」を体に覚えさせる回です💪🐳

---

## 1) 目的🎯✨

* 複数アプリを **サブドメインで分ける設計** を作れるようになる🌈
  例：`front.localhost` / `api.localhost` / `admin.localhost`
* 入口（リバプロ）は 1つ、でもURLはスッキリを実現する🚪➡️🏠
* “本番に近い” 感覚（Hostでルーティング）を掴む🧩

---

## 2) 図でイメージ🗺️✨

「ブラウザが見てるのは Host（ドメイン名）で、リバプロがそれで振り分ける」って絵です🎨

```text
          ブラウザ🌐
     ┌────────────────┐
     │ front.localhost │
     │  api.localhost  │
     │ admin.localhost │
     └───────┬────────┘
             │ 80/443（入口は1個）🚪
     ┌───────▼────────┐
     │ Reverse Proxy   │  Caddy / Traefik 🍞🚦
     └───┬────┬───┬───┘
         │    │   │
   ┌─────▼┐ ┌─▼──┐┌─────▼┐
   │front │ │api  ││admin │
   │:5173 │ │:3000││:5174 │
   └──────┘ └────┘└──────┘
（外にポートを出すのは基本リバプロだけ、がキレイ✨）
```

---

## 3) サブドメイン方式が「強い」場面💪🔥

* **本番でありがちな構成に近い**（Hostベースのルーティング）
* SPA / API / 管理画面を「別アプリ」として分けやすい🧱
* Cookie・OAuth みたいな “ドメインが大事” な要素を、ローカルでも再現しやすい🍪🔐（※後述）

---

## 4) 名前の決め方（設計ミニ練習）📏✅

まず **3つだけ**決めると迷子になりにくいよ🙂✨

### 4-1. 公開URLの命名（人間が見て分かる名前）🏷️

* `front.localhost`：フロント
* `api.localhost`：API
* `admin.localhost`：管理画面

コツ👇

* “役割名” をそのまま使う（`app1`より強い）💡
* 後で増えても破綻しない（`front2`地獄を避ける）😇

### 4-2. 内部サービス名（Composeのサービス名）🐳

* `front` / `api` / `admin` みたいに短く
  Compose内部ではサービス名が名前解決に使えるので、ここは簡潔が正義🧠✨

### 4-3. 入口は誰？（外に出すのはどれ？）🚪

基本ルール：**外に公開するのはリバプロだけ**
（front/api/admin は “内部” に隠す）🫥✨
これができると、ポート競合が激減するよ🎉

---

## 5) `.localhost` の扱い（超重要）🏠🧠

`.localhost` は “特別扱いされる名前” 側のカテゴリで、IANAの「Special-Use Domain Names」では **サブドメインも含めて** special-use の対象だよ、って明記されてるよ📌([iana.org][3])
背景として `localhost` は special-use ドメイン名として RFC 6761 に紐づいてるよ📚([RFCエディタ][4])

なので実務では、`front.localhost` みたいな形が「ローカル用途の定番」になりやすいです👍

---

## 6) 手順（最小で動かす）🛠️🚀

ここからは「CaddyでHost振り分け」→「Traefikでラベル振り分け」の2本立てにするね🍞🚦
（どっちも “Hostでルーティング” は同じ！）

---

## 6-A) Caddyでサブドメイン振り分け🍞✨

## A-1. `compose.yaml` の例（雰囲気つかむ用）🐳

* 外に出すのは `proxy` のみ
* 他は `expose`（内部向け）だけにする

```yaml
services:
  proxy:
    image: caddy:2
    ports:
      - "80:80"
      # HTTPSは次の章でOK（必要なら443も）
      # - "443:443"
    volumes:
      - ./caddy/Caddyfile:/etc/caddy/Caddyfile
    depends_on:
      - front
      - api
      - admin

  front:
    build: ./front
    expose:
      - "5173"

  api:
    build: ./api
    expose:
      - "3000"

  admin:
    build: ./admin
    expose:
      - "5174"
```

## A-2. `Caddyfile`（Hostで振り分け）🎯

Caddyの `reverse_proxy` は公式で案内されてる基本ディレクティブだよ📘([Caddy Web Server][5])

```caddyfile
front.localhost {
  reverse_proxy front:5173
}

api.localhost {
  reverse_proxy api:3000
}

admin.localhost {
  reverse_proxy admin:5174
}
```

## A-3. 起動して確認✅

* `http://front.localhost`
* `http://api.localhost`
* `http://admin.localhost`

---

## 6-B) Traefikでサブドメイン振り分け🚦🤖

Traefikは「ラベルでルーティングを作れる」のが売りで、Docker連携も公式ドキュメントでこう書かれてるよ📌([doc.traefik.io][6])
最近だと Docker公式ガイドでも、URL（host/path）でルーティングする流れが分かりやすくまとまってるよ🧭([Docker Documentation][7])

## B-1. ざっくり構成（例）🧩

```yaml
services:
  traefik:
    image: traefik:v3.0
    command:
      - --providers.docker=true
      - --entrypoints.web.address=:80
    ports:
      - "80:80"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro

  front:
    build: ./front
    labels:
      - traefik.http.routers.front.rule=Host(`front.localhost`)
      - traefik.http.services.front.loadbalancer.server.port=5173

  api:
    build: ./api
    labels:
      - traefik.http.routers.api.rule=Host(`api.localhost`)
      - traefik.http.services.api.loadbalancer.server.port=3000

  admin:
    build: ./admin
    labels:
      - traefik.http.routers.admin.rule=Host(`admin.localhost`)
      - traefik.http.services.admin.loadbalancer.server.port=5174
```

ポイント👉

* Traefikは「どのポートにつなぐか」をラベルで指定できるよ（公式例にもある）📌([doc.traefik.io][6])

---

## 7) よくあるミス集（ここが実戦力）📕🧯

### 7-1. ブラウザで開くと404😵‍💫

* Host名が一致してない（例：`front.localhost` を `localhost` で開いてる）
* ルールは “Hostが一致” しないと発火しないよ⚠️

対策✅

* まず `http://front.localhost` のように **Hostを正しく**打つ
* 迷ったら「今のHost名」を画面のURLバーで確認👀

### 7-2. 502 Bad Gateway👻

* 中のサービスが落ちてる/ポート違い
  Traefikは「間違ったポートにつないでる」と502になりがちなので、公式もポート指定ラベルを推してるよ📌([doc.traefik.io][6])

対策✅

* サービスが実際にそのポートで待ってるか確認
* `front` が 5173、`api` が 3000、みたいに “内部ポート” を揃える🧠

### 7-3. ViteのHMRが効かない（更新されない）🌀

Viteは「リバプロの前に置くなら WebSocket をプロキシできる前提」って公式で注意してるよ📌([vitejs][8])

対策✅

* リバプロ側がWebSocketを通せる設定にする
* それでもダメなら `server.hmr` 系を調整（Vite公式の案内がある）📌([vitejs][8])
  （※HMRまわりは “ここだけ沼” になりがちなので、困ったらログと設定を一緒にAIへ投げるのが正解🤖✨）

---

## 8) Cookie / OAuthが絡むときの「うれしさ」🍪🔐✨

サブドメイン方式が効くのは、こういう“ドメイン前提”の世界🌍

* Cookieは `Set-Cookie` ヘッダーで属性（Domain/SameSite/Secureなど）を指定できる📌([MDNウェブドキュメント][9])
* SameSite は “どこまで同一サイト扱いか” に関係して、挙動に影響するよ🍪🧠([web.dev][10])

ここで大事なのは「ローカルでも、本番っぽいURL構造でテストできる」こと👍
（パス方式だけだと、OAuthのredirectやCookieの範囲で “本番と違う” が起きがち😇）

---

## 9) AIに聞く例（コピペで使える）🤖🪄

### 9-1. Caddyfileを作らせる🍞

* 「`front.localhost`→`front:5173`、`api.localhost`→`api:3000`、`admin.localhost`→`admin:5174` で振り分けるCaddyfileを書いて。ついでにトラブル時のログの見方も1行で。」

### 9-2. Traefikラベルを作らせる🚦

* 「Traefik v3 + Docker Composeで、Hostルールで `front/api/admin` を振り分けたい。必要なlabelsを各サービスに付けたcompose例を出して。」

### 9-3. HMRが死んだ時の相談🌀

* 「Viteをリバプロ越し（Hostで振り分け）で開いてる。HMRが効かない。Vite側の `server.hmr` 設定候補と、リバプロ側でWebSocketを通す観点のチェックリストを作って。」

（Vite側の “リバプロ越しWebSocket前提” は公式にも書いてあるよ📌([vitejs][8])）

---

## 10) ミニ課題（設計→実装→確認）🎒✨

### 課題A：命名ルールを完成させる📛

* `front/api/admin` 以外に、今後増えそうなものを2つ想像して名前を決める
  例：`docs.localhost` / `worker.localhost` 📚⚙️

### 課題B：入口だけを公開にする🚪

* Composeで `ports:` を持つのが `proxy`（または `traefik`）だけになってるか確認✅
  （これができると “ポート地獄” が消える🎉）

### 課題C：動作確認のチェックリスト✅

* 3つのURLが開ける
* `api.localhost` はAPIのレスポンスが返る
* front/admin はそれぞれ別アプリの画面になる
* （Viteなら）HMRが動く or どこで死んでるか説明できる🕵️

---

## まとめ🎓✨

* サブドメイン方式は「本番に近い形」で複数アプリを整理できる最強パターン🏷️
* `.localhost` は special-use 扱いで、サブドメインも含めて扱われる前提がある📌([iana.org][3])
* つまずきはだいたい **Host一致 / 502 / WebSocket(HMR)** の3つ。ここを潰せば勝ち🏆
  Viteはリバプロ越しWebSocket前提の注意があるので、そこは要チェック📌([vitejs][8])

次の章に進むなら、ここで作った `front/api/admin` を **ラベルだけで増やせる方向（Traefik）** に寄せると、気持ちよく自動化ルートに入れるよ🚦🤖✨

[1]: https://chatgpt.com/c/698d4fea-d74c-83a5-94e3-6dac64d6dc92 "リバプロ比較と選択ガイド"
[2]: https://chatgpt.com/c/698d4d16-a03c-83a6-8591-bc05037ce9ef "リバースプロキシ入門"
[3]: https://www.iana.org/assignments/special-use-domain-names?utm_source=chatgpt.com "Special-Use Domain Names"
[4]: https://www.rfc-editor.org/rfc/rfc6761.html?utm_source=chatgpt.com "RFC 6761: Special-Use Domain Names"
[5]: https://caddyserver.com/docs/caddyfile/directives/reverse_proxy?utm_source=chatgpt.com "reverse_proxy (Caddyfile directive) — Caddy Documentation"
[6]: https://doc.traefik.io/traefik/reference/routing-configuration/other-providers/docker/ "Traefik Docker Routing Documentation - Traefik"
[7]: https://docs.docker.com/guides/traefik/?utm_source=chatgpt.com "HTTP routing with Traefik"
[8]: https://vite.dev/config/server-options "Server Options | Vite"
[9]: https://developer.mozilla.org/ja/docs/Web/HTTP/Reference/Headers/Set-Cookie?utm_source=chatgpt.com "Set-Cookie ヘッダー - HTTP - MDN Web Docs"
[10]: https://web.dev/articles/samesite-cookies-explained?utm_source=chatgpt.com "SameSite cookies explained | Articles"
