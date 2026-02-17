# 第03章：“公開の整理”の3大パターンを知る🧠🔀

この章は「**ローカルで複数アプリを共存させるとき、URLをどう切る？**」がテーマだよ〜😊
結論から言うと、公開の整理はこの3つに集約されます👇✨

* **① ポートで分ける**（`localhost:3000` / `localhost:5173` みたいに）
* **② パスで分ける**（`localhost/app1` / `localhost/app2` みたいに）
* **③ サブドメインで分ける**（`app1.localhost` / `api.localhost` みたいに）

---

## 0) まず“URLの部品”だけ超ざっくり理解しよ🧩✨

![URL Anatomy](./picture/docker_local_exposure_ts_study_003_01_url_anatomy.png)

URLって「住所」なんだけど、分解するとこう👇

```text
http://app1.localhost:8080/api/users?page=1
     └──ホスト名──┘ └ポート┘└─パス─┘ └ クエリ ┘
```

* **ホスト名**：どの“家（アプリの入口）”に行く？🏠
* **ポート**：その家の“玄関番号”どれ？🚪（同じ家でも玄関が複数ある感じ）
* **パス**：家の中の“部屋”どこ？🧭

この章は、**ホスト名 / ポート / パス**のどれを使って「アプリAとBを分けるか」って話だよ😺

---

## 1) ① ポートで分ける（いちばん簡単😆）🔌

![Port Splitting Pattern](./picture/docker_local_exposure_ts_study_003_02_port_split.png)

## イメージ図🗺️

```text
ブラウザ
  ├─ http://localhost:3000  → app1
  └─ http://localhost:5173  → app2
```

## いいところ👍✨

* すぐできる！リバプロ不要！🚀
* アプリ側の設定が少ない（“自分は / で動く”でOK）🙂

## つらいところ😵‍💫

* アプリが増えるほど **URLが地獄**（3000/3001/3002…）🌀
* **ポート衝突**が起きがち（別プロジェクトも3000使ってた等）💥
* フロントとAPIが別ポートだと **CORS**が出やすい（後で詳しく）😇

---

## 1分ハンズオン：同じTypeScriptアプリを2つ起動して“ポートで分ける”🧪🐳

![Hands-on Compose Setup](./picture/docker_local_exposure_ts_study_003_03_compose_setup.png)

## フォルダ構成📁

```text
chapter03-port/
  docker-compose.yml
  app/
    package.json
    tsconfig.json
    src/server.ts
    Dockerfile
```

## app/src/server.ts（超ミニWebサーバ）🌱

```ts
import http from "node:http";

const appName = process.env.APP_NAME ?? "app";
const port = Number(process.env.PORT ?? "3000");

const server = http.createServer((req, res) => {
  res.setHeader("Content-Type", "text/plain; charset=utf-8");
  res.end(`Hello from ${appName} 👋\npath=${req.url}\n`);
});

server.listen(port, () => {
  console.log(`[${appName}] listening on ${port}`);
});
```

## app/package.json 🧩

```json
{
  "name": "chapter03-port-app",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "node --watch dist/server.js",
    "build": "tsc -p tsconfig.json"
  },
  "devDependencies": {
    "typescript": "^5.9.0"
  }
}
```

> TypeScriptの安定最新版は 5.9 系として案内されてるよ（2026-02-12時点）😊 ([typescriptlang.org][1])
> さらに今日、TypeScript 6.0 Beta も発表された流れ（追い風🌪️） ([Microsoft for Developers][2])

## app/tsconfig.json 🛠️

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ES2022",
    "outDir": "dist",
    "strict": true
  },
  "include": ["src"]
}
```

## app/Dockerfile 🐳

```dockerfile
FROM node:24-alpine AS build
WORKDIR /app
COPY package.json tsconfig.json ./
RUN npm i
COPY src ./src
RUN npm run build

FROM node:24-alpine
WORKDIR /app
COPY --from=build /app/dist ./dist
ENV PORT=3000
EXPOSE 3000
CMD ["node", "dist/server.js"]
```

> Node は v24 が Active LTS（安定枠）で、v25 が Current（新機能枠）という整理（最終更新 2026-02-09）。 ([Node.js][3])

## docker-compose.yml（同じビルドを2サービスで使う）🧠✨

```yaml
services:
  app1:
    build: ./app
    environment:
      APP_NAME: app1
      PORT: 3000
    ports:
      - "3000:3000"

  app2:
    build: ./app
    environment:
      APP_NAME: app2
      PORT: 3000
    ports:
      - "5173:3000"
```

## 起動🚀

```bash
docker compose up --build
```

ブラウザで👇

* `http://localhost:3000` → app1
* `http://localhost:5173` → app2

✅ これが「ポートで分ける」だよ〜！

---

## 2) ② パスで分ける（“入口1個＋中で振り分け”🚪➡️🏠）🍰

![Path Splitting Pattern](./picture/docker_local_exposure_ts_study_003_04_path_split.png)

## イメージ図🗺️

```text
ブラウザ
  └─ http://localhost/
        ├─ /app1  → app1
        └─ /app2  → app2
```

これをやるには、だいたい **リバースプロキシ**が必要になるよ（入口係🚥）
まだ本格的には後の章だけど、感覚だけ先に持つと超ラク😊

## いいところ👍✨

* URLが**スッキリ**（入口が1個）✨
* `/api` を同一ドメイン配下に置けると **CORS減りがち**🧹（後でやるよ）

## つらいところ😵‍💫（ここ大事⚠️）

* アプリ側が「自分は `/app1` 配下で動く」前提になってないと事故りやすい

  * SPAの**ルーティング**
  * 静的ファイルの**相対パス**
* リバプロで「`/app1` を付けたまま渡す？外して渡す？」問題が出る🤯

## 例：Caddyだと“パスの先頭を外して渡す”がやりやすい🍞

![Path Stripping Mechanism](./picture/docker_local_exposure_ts_study_003_05_path_strip.png)

`handle_path` は “マッチしたパスを strip してくれる” 仕組みとして用意されてるよ。 ([Caddy Web Server][4])

```text
http://localhost/app1/hello
  ↓（/app1 を外して）
app1 コンテナには /hello で届く
```

---

## 3) ③ サブドメインで分ける（本番っぽくて強い💪）🏷️

![Subdomain Splitting Pattern](./picture/docker_local_exposure_ts_study_003_06_subdomain_split.png)

## イメージ図🗺️

```text
ブラウザ
  ├─ http://app1.localhost  → app1
  ├─ http://app2.localhost  → app2
  └─ http://api.localhost   → api
```

## いいところ👍✨

* **本番の構成に近い**（ホスト名で分かれるのは現場あるある）🎯
* 多くのWebアプリが「自分は `/` で動く」前提なので、**パス方式より事故りにくい**🙂
* CookieやOAuthなど“ドメインっぽい話”をする時に整理しやすい🍪

## つらいところ😵‍💫

* “名前解決（どのIPに向く？）”が絡む（次の章でやるやつ）🧠
* ローカルHTTPSや証明書の話と相性が強い（後半でやる🔒）

でもね、ここで朗報🎉
`.localhost` はローカル用途として扱われる流れが強く、`*.localhost` をローカルへ向ける挙動が一般的に期待できる（仕様・実装の背景あり）。 ([RFC エディタ][5])
DockerのTraefikガイドでも `nginx.localhost` の例で “そのままブラウザで開ける” 前提で説明されてるよ。 ([Docker Documentation][6])

---

## 4) 3パターン比較まとめ（迷ったらここを見る😺）📌

![Pattern Comparison](./picture/docker_local_exposure_ts_study_003_07_comparison.png)

| パターン   | URL例             | 難易度 | 向いてる       | つらいポイント        |
| ------ | ---------------- | --: | ---------- | -------------- |
| ポート    | `localhost:3000` |   ★ | とにかく今すぐ動かす | ポート増殖・衝突・CORS  |
| パス     | `localhost/app1` | ★★★ | 入口1個に統一したい | “/app1配下”対応が必要 |
| サブドメイン | `app1.localhost` |  ★★ | 本番っぽくしたい   | 名前解決/HTTPSが絡む  |

---

## 5) ざっくり判断のコツ（設計超入門向け）🧭✨

* **今日だけ動けばOK**：まず **ポート方式**で勝つ🏆😆
* **複数アプリが当たり前になる**：**サブドメイン方式**が安定しやすい🏷️
* **/api を同一ドメインに寄せたい**：**パス方式**が候補（ただしアプリ側が対応必要）🍰

「あとで変えればいいや〜」は、だいたい後で泣くので😂
この章で “自分のチーム（未来の自分）に優しいURL” を選ぶ意識を持つのが勝ちだよ✅✨

---

## 6) よくあるミス辞典😇🧯（第3章ver）

* **ポート方式**

  * 「3000が既に使われてた」→ まず衝突を疑う💥
* **パス方式**

  * 「画面は出るけどリンク遷移で404」→ SPAのベースパス未対応👻
  * 「/app1 を付けたら502」→ リバプロが“どこに流すか”間違い🚑
* **サブドメイン方式**

  * 「app1.localhost が開かない」→ 名前解決/ブラウザ/OSの挙動確認（次章で丁寧に）🪟🔍

---

## 7) AIに聞くと爆速になる質問テンプレ🤖✨

コピペして、プロジェクト名だけ変えると超便利だよ👇😺

* ポート方式

  * 「docker composeで同じDockerfileから app1/app2 を起動して、ホスト側のポートを 3000 と 5173 に分けたい。最小構成のcomposeを書いて」
* パス方式

  * 「`/app1` と `/app2` を入口1つで振り分けたい。Caddyで `handle_path` を使ったCaddyfile例と、composeへの組み込み例を作って」 ([Caddy Web Server][4])
* サブドメイン方式

  * 「`app1.localhost` と `api.localhost` をリバプロで振り分けたい。Traefikのラベル例でcomposeを書いて」 ([Docker Documentation][6])

---

## 8) ミニ課題（10〜20分）🎒✨

## 課題A：ポート方式を“3アプリ”に増やす🔌➕

* app3 を追加して `http://localhost:8787` で開けるようにしてみよう😺
* ヒント：composeでサービス増やして、`ports` だけ変える！

## 課題B：あなたの開発スタイルだと、どれを採用する？✍️

次の質問に1行ずつ答えてみてね👇

* アプリは今後いくつ増えそう？📈
* OAuthやCookieログイン、扱いそう？🍪
* “本番っぽさ”どれくらい必要？🎯

この回答が、そのまま次の章（ルーティング／ローカルドメイン）で効いてくるよ〜🧠✨

---

必要なら、次の返答で「**第3章の続きとして**」
✅ パス方式 / サブドメイン方式を **“最小のCaddy or Traefik構成で実際に動かす”**ところまで、コピペ教材として仕上げちゃうよ🚀😺

[1]: https://www.typescriptlang.org/download/?utm_source=chatgpt.com "How to set up TypeScript"
[2]: https://devblogs.microsoft.com/typescript/announcing-typescript-6-0-beta/?utm_source=chatgpt.com "Announcing TypeScript 6.0 Beta"
[3]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[4]: https://caddyserver.com/docs/caddyfile/directives/handle_path?utm_source=chatgpt.com "handle_path (Caddyfile directive)"
[5]: https://www.rfc-editor.org/rfc/rfc6761.html "RFC 6761: Special-Use Domain Names"
[6]: https://docs.docker.com/guides/traefik/?utm_source=chatgpt.com "HTTP routing with Traefik"
