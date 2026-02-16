# 第18章：パス方式の設計ミニ練習：/app1 /app2 /api 🧪🧩

この章は「**同じドメインの中で、パスでアプリを同居させる**」練習回だよ〜😊
完成形はこんな感じ👇

* `http://dev.localhost/app1/` → アプリ1 🎮
* `http://dev.localhost/app2/` → アプリ2 🧩
* `http://dev.localhost/api/...` → API 🔌

`.localhost` 配下の名前は “ローカルのループバックに向く想定で使ってOK” という扱いになってるので、`dev.localhost` みたいな名前が作りやすいよ〜🏠✨ ([IETF Datatracker][1])

---

## 1) まずは設計のコア感覚：「入口は同じ、最初の1段で振り分け」🚪➡️🚥

イメージはこれ👇

```text
ブラウザ
  |
  |  dev.localhost:80
  v
リバースプロキシ（入口）
  |------ /app1 ---> (静的 or フロント1)
  |------ /app2 ---> (静的 or フロント2)
  `------ /api  ---> (APIサーバ)
```

ここで超重要なのが **「上流（中のアプリ）に渡すURLをどうするか」** 🤔

* 入口：`/api/hello`
* 中のAPIが期待：`/hello`

この “差” を埋めるのが **prefix を剥がす（strip prefix）** ってやつだよ🪄
Caddy だと `handle_path` が「パス一致＋prefix剥がし」を勝手にやってくれるので、パス方式の練習にめちゃ向く👍 ([Caddy Web Server][2])
（同じことは `uri strip_prefix` でもできるよ〜） ([Caddy Web Server][3])

---

## 2) 事故りにくい “パス方式ルール” 5つ 🧯✨

1. **先頭の区切りは必ず固定（`/api/` みたいに）**
   `api` と `api-v2` を混ぜるより、`/api/` `/api-v2/` で明確に🧠

2. **末尾スラッシュを揃える（`/app1/` 推奨）**
   `/app1` と `/app1/` が混ざると、相対パス参照で事故りがち😇

3. **“中のアプリは / で動く” が基本（入口で剥がす）**
   中で `/api` 前提を作ると、将来の構成変更で泣くこと多い😭

4. **静的ファイル / SPA / API を同じ扱いにしない**
   それぞれ “404の意味” が違うから、ルールを分けると超ラク🌱

5. **「誰が 404 を返すべきか」を決めておく**
   入口が返す？中が返す？ ここが曖昧だとデバッグ地獄👻

---

## 3) ハンズオン：Caddyで `/app1` `/app2` `/api` を作る 🚀🍞

今回は **app1/app2 は静的ファイル**、**api だけ TypeScript** にして、最短で “パス方式の設計感覚” を掴むよ〜😺✨
（フロントを Vite にする時の注意は後半でやる！）

### 3-1. フォルダ構成（これを作る）📁

```text
path-routing-lab/
  compose.yml
  Caddyfile
  apps/
    app1/
      index.html
    app2/
      index.html
  api/
    package.json
    tsconfig.json
    src/
      server.ts
    Dockerfile
```

### 3-2. `apps/app1/index.html` と `apps/app2/index.html` 🖼️

`apps/app1/index.html`

```html
<!doctype html>
<html>
  <head><meta charset="utf-8" /><title>app1</title></head>
  <body>
    <h1>App1 🎮</h1>
    <p><a href="/api/hello">API呼び出ししてみる🔌</a></p>
    <p><a href="/app2/">App2へ移動🧩</a></p>
  </body>
</html>
```

`apps/app2/index.html`

```html
<!doctype html>
<html>
  <head><meta charset="utf-8" /><title>app2</title></head>
  <body>
    <h1>App2 🧩</h1>
    <p><a href="/app1/">App1へ戻る🎮</a></p>
  </body>
</html>
```

### 3-3. API（TypeScript）を用意する 🔧🟦

`api/package.json`

```json
{
  "name": "api",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "tsx watch src/server.ts"
  },
  "dependencies": {
    "express": "^4.19.2"
  },
  "devDependencies": {
    "tsx": "^4.19.2",
    "typescript": "^5.0.0"
  }
}
```

`api/tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ES2022",
    "moduleResolution": "Bundler",
    "strict": true,
    "skipLibCheck": true
  }
}
```

`api/src/server.ts`

```ts
import express from "express";

const app = express();

app.get("/hello", (_req, res) => {
  res.json({ message: "Hello from API 😺🔌" });
});

app.get("/health", (_req, res) => {
  res.type("text").send("ok");
});

app.listen(3000, () => {
  console.log("API listening on :3000");
});
```

`api/Dockerfile`

```dockerfile
FROM node:lts-alpine
WORKDIR /app
COPY package.json tsconfig.json ./
RUN npm install
COPY src ./src
EXPOSE 3000
CMD ["npm", "run", "dev"]
```

### 3-4. Caddyfile（ここが本題💡）🧠

`Caddyfile`

```caddyfile
dev.localhost {

	# /app1 で来たら /app1/ に揃える（相対パス事故を減らす）
	redir /app1 /app1/ 308
	redir /app2 /app2/ 308
	redir /api  /api/  308

	# /api/* は API コンテナへ
	# handle_path は「/api/ を剥がして」中に流してくれるよ🪄
	handle_path /api/* {
		reverse_proxy api:3000
	}

	# /app1/* は静的ファイル（app1）
	handle_path /app1/* {
		root * /srv/app1
		file_server
	}

	# /app2/* は静的ファイル（app2）
	handle_path /app2/* {
		root * /srv/app2
		file_server
	}

	# トップに来たら案内
	handle / {
		respond "Open /app1/ or /app2/ 😊" 200
	}
}
```

`handle_path` は「一致したパスprefixを剥がしてから処理」するディレクティブだよ〜。だから `/api/hello` が中には `/hello` で届く👍 ([Caddy Web Server][2])
（同じことを手動でやるなら `uri strip_prefix` を使う感じ！） ([Caddy Web Server][3])

### 3-5. Compose 🐳🧩

`compose.yml`

```yaml
services:
  caddy:
    image: caddy:2
    ports:
      - "80:80"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - ./apps/app1:/srv/app1:ro
      - ./apps/app2:/srv/app2:ro
    depends_on:
      - api

  api:
    build: ./api
    expose:
      - "3000"
```

### 3-6. 起動＆確認 🎉

PowerShell で👇

```powershell
cd path-routing-lab
docker compose up --build
```

ブラウザで👇

* `http://dev.localhost/app1/`
* `http://dev.localhost/app2/`
* `http://dev.localhost/api/hello`

API は JSON が返ればOK😺🔌

---

## 4) よくある詰まりポイント集（パス方式あるある）😵‍💫🧯

### A. `/app1` を開いたら見た目が崩れる / 画像が404 😇

原因：**末尾スラッシュなし** で相対パスがズレた、が多い！
→ この章では `redir /app1 /app1/` を入れて予防してるよ✅

### B. APIが 404（でもコンテナは生きてる）👻

原因：**prefix剥がしがない** or **ルーティング順** が違う。
→ `handle_path /api/*` を使うと、かなり事故が減る👍 ([Caddy Web Server][2])

### C. 「SPA（React等）」を静的配信したら、直リンクで404 🧟‍♂️

SPAは「存在しないパスでも index.html を返して、ブラウザ側でルーティング」するからね。
Caddy には “SPAのよくある型” があって、`try_files {path} /index.html` を使うのが定番だよ〜📌 ([Caddy Web Server][4])
（この章の app1/app2 はただのHTMLなので、まだ不要！）

---

## 5) Vite/SPA を `/app1/` 配下で動かす時の注意（ここ大事🔥）⚡

パス方式はSPAで事故りやすいポイントが2つあるよ👇

### ① ビルド成果物の “基準パス” 問題 🧭

`/app1/` 配下で配るなら、フロント側も「自分は /app1/ に住んでる」と知ってないと、`/assets/...` みたいにルート参照しがち😇
→ Viteなら `base` を合わせるのが基本（例：`/app1/`）。
（ここはフレームワークごとに作法がある、って覚え方でOK👌）

### ② 開発中のHMR（WebSocket）問題 🧨

Vite は「リバプロが WebSocket をちゃんと中継できる前提」で動くよ〜。失敗すると “直でWSに繋ぎに行くフォールバック” をする挙動があるので、入口の作り次第で混乱しやすい😵‍💫 ([vitejs][5])
→ 対策は「入口がWSを通せるか」をまず疑う、でOK👍

（※この章は “設計練習” なので、Vite完全対応は第15章あたりの内容と合体させるのが一番きれい😉）

---

## 6) 参考：Traefikで同じことやるなら（考え方だけ）🚦🤖

Traefik でパス方式をやる時も、結局 **StripPrefix** がほぼ必須になるよ〜。公式にも `StripPrefix` middleware がある👍 ([doc.traefik.io][6])
あと Traefik v3 では `PathPrefix` の扱いに変更があるので、古い設定例コピペは要注意⚠️ ([doc.traefik.io][7])

この章の結論としては👇
**「パス方式＝prefix剥がしの設計が勝負」** 🥊✨

---

## 7) AIに聞くと爆速になるプロンプト例 🤖💨

* 「Caddyfileで `/app1` を必ず `/app1/` にリダイレクトして、`/api/*` だけ別コンテナに流したい。最小構成で書いて」
* 「`/app1/` 配下のSPAで、直リンク（/app1/settings）でも404にしないCaddy設定にしたい。`try_files` を使う例を出して」 ([Caddy Web Server][4])
* 「Vite をリバプロ配下でHMR動かす時の、WebSocket問題の切り分け手順を箇条書きで」 ([vitejs][5])

---

## 8) ミニ課題（15〜30分）✍️✨

1. **`/admin/` を追加**して、`apps/admin/index.html` を配信してみよう🧩
2. APIに **`GET /version`** を追加して、`/api/version` で返すようにしよう🔌
3. `dev.localhost/` に来たら、**`/app1/` に自動転送**するようにしてみよう🚀

できたら最後にチェック✅

* `/app1/` と `/app2/` は崩れず表示できる？
* `/api/hello` は **`/hello` として**APIに届いてる？（=prefix剥がし成功🎉）

---

必要なら次の章として、**「app1/app2 を “本物のViteアプリ” に置き換える版（base設定＋SPA fallback＋HMR注意点つき）」** も、この構成のまま一気に作れるよ〜😺🔥

[1]: https://datatracker.ietf.org/doc/html/rfc6761?utm_source=chatgpt.com "RFC 6761 - Special-Use Domain Names"
[2]: https://caddyserver.com/docs/caddyfile/directives/handle_path?utm_source=chatgpt.com "handle_path (Caddyfile directive)"
[3]: https://caddyserver.com/docs/caddyfile/directives/uri?utm_source=chatgpt.com "uri (Caddyfile directive) — Caddy Documentation"
[4]: https://caddyserver.com/docs/caddyfile/patterns?utm_source=chatgpt.com "file/patterns - Common Caddyfile Patterns"
[5]: https://vite.dev/config/server-options?utm_source=chatgpt.com "Server Options"
[6]: https://doc.traefik.io/traefik/middlewares/http/stripprefix/?utm_source=chatgpt.com "Traefik StripPrefix Documentation"
[7]: https://doc.traefik.io/traefik/migrate/v2-to-v3-details/?utm_source=chatgpt.com "Configuration Details for Migrating from Traefik v2 to v3"
