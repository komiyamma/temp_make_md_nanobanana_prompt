# 第16章：APIを同じドメイン配下に寄せてCORSを減らす🧹✨

この章は「**CORSで時間が溶ける問題**」を、**入口（リバプロ）でまとめて解決**する回だよ〜😇🚪➡️🏠
結論から言うと、**ブラウザに“同一オリジン”だと思わせる**のが最強です💪

---

## 1) 今日のゴール🎯✨

* フロントが呼ぶURLを **`/api/...` みたいな相対パス**にする🧭
* 入口（Caddy / Traefik）が **`/api` をAPIコンテナへ転送**する🚚
* 結果：**CORS設定がほぼ不要**になって、余計な `OPTIONS` も減ることが多い🫶

---

## 2) そもそもCORSって何がつらいの？😵‍💫🍝

![CORS Nightmare](./picture/docker_local_exposure_ts_study_016_02_cors_nightmare.png)

### ✅ “同一オリジン”の定義（超重要）🧠

ブラウザ的には、オリジンが同じかどうかは **scheme/host/port のセット**で決まるよ。([MDN Web Docs][1])
つまり…

* `http://localhost:5173`（フロント）
* `http://localhost:8787`（API）

これ、**ポートが違うので別オリジン** → CORSの世界へようこそ🎉😭

### ✅ プリフライト（`OPTIONS`）が増える理由🧨

![Preflight OPTIONS Request](./picture/docker_local_exposure_ts_study_016_04_preflight_check.png)

CORSが絡むと、ブラウザは「いきなり送っていい？」って **事前確認（プリフライト）**を飛ばすことがあるよ。
このプリフライトは **`OPTIONS`** で、`Access-Control-Request-Method` などのヘッダーが付くやつ。([MDN Web Docs][2])

さらに、リクエストヘッダーが “安全リスト（safelisted）” 以外だとプリフライトになりやすい、みたいな細かい条件もある（ややこしいやつ）😇🌀([MDN Web Docs][3])

---

## 3) 解決のアイデア：同じドメイン（同じオリジン）に寄せる🏠✨

![Same Origin Solution](./picture/docker_local_exposure_ts_study_016_01_same_origin.png)

ポイントはこれ👇

* フロントのJSが叩く先を **`https://dev.localhost/api/...`** に統一
* APIは裏側で別コンテナでもOK（入口が転送してくれる）

### 図でイメージ📌

```text
ブラウザ
  |
  | https://dev.localhost/        → フロントへ
  | https://dev.localhost/api/... → APIへ
  v
[ リバースプロキシ（入口） ]
   |                  |
   v                  v
[ frontコンテナ ]   [ apiコンテナ ]
```

こうすると、ブラウザから見たアクセス先はずっと **同一オリジン（dev.localhost）** なので、CORSで悩みにくくなる✌️😆

---

## 4) 手順：Caddyで `/api` をAPIへ流す🚀🍞

### 4-1. Caddyfile（基本形：`/api` を剥がしてAPIへ）🧩

![API Path Stripping](./picture/docker_local_exposure_ts_study_016_03_api_strip.png)

Caddyには **`handle_path`** っていう「**パスプレフィックスを剥がして処理する**」便利機能があるよ。([Caddy Web Server][4])

```caddyfile
dev.localhost {

	# API: /api/* → apiコンテナへ（/api を剥がして渡す）
	handle_path /api/* {
		reverse_proxy api:8787
	}

	# フロント（例：Vite dev server）
	handle {
		reverse_proxy front:5173
	}
}
```

* `handle_path /api/*`：`/api` を剥がしてAPIへ転送してくれる🧼([Caddy Web Server][4])
* `reverse_proxy` は基本、Hostをそのまま渡しつつ `X-Forwarded-*` を良い感じに付けてくれる（自分でヘッダー盛り盛りにしなくてOK寄り）🙆‍♂️([Caddy Web Server][5])

### 4-2. フロント側のfetchを「相対パス」に直す🎯

![Relative Fetch](./picture/docker_local_exposure_ts_study_016_05_relative_fetch.png)

ここが気持ちいいポイント！✨

```ts
// ✅ 同一オリジンに寄せる（CORSの悩みが激減）
const res = await fetch("/api/todos");

// ❌ これだと別オリジンになりがち（CORS地獄）
const res2 = await fetch("http://localhost:8787/todos");
```

---

## 5) 手順：Traefikでやるなら（概念だけでもOK）🚦🤖

Traefikは「Dockerラベルでルーティング」が得意なやつ。([doc.traefik.io][6])
パスを剥がしたいときは **StripPrefix** ミドルウェアが定番だよ。([doc.traefik.io][7])

イメージ👇（細部は環境で変わるので“型”として見てね）

```yaml
labels:
  - traefik.http.routers.api.rule=Host(`dev.localhost`) && PathPrefix(`/api`)
  - traefik.http.middlewares.api-stripprefix.stripprefix.prefixes=/api
  - traefik.http.routers.api.middlewares=api-stripprefix
  - traefik.http.services.api.loadbalancer.server.port=8787
```

---

## 6) うまくいったか確認する方法🕵️‍♀️✅

### ✅ ブラウザDevToolsで見る（いちばん確実）🔍

* Networkタブで APIリクエストを見る
* **`OPTIONS` が消えた/減った** → めっちゃ勝ち（ケースによるけど）🫶([MDN Web Docs][2])
* Request URL が **`https://dev.localhost/api/...`** になってるか確認👀

### ✅ Caddyログを見る👂

* `dev.localhost` に来たログが出て
* `/api/...` が api 側に流れてたらOK👍

---

## 7) よくあるミス集（ここで詰まりやすい）🧯📕

### 🧨 ミス1：`/api` を剥がす/剥がさないのズレ

* `handle_path` は **剥がす** ([Caddy Web Server][4])
* API側が `/api/todos` を期待してる設計なら、剥がすと 404 になる😇

👉 対処：

* APIが `/todos` を期待：`handle_path /api/*`（剥がす）
* APIが `/api/todos` を期待：`handle /api/*`（剥がさない）にする手もある（章18で設計練習するやつ）

### 🧨 ミス2：フロントがまだ `http://localhost:8787` を叩いてる

入口でまとめても、コードが直ってなければCORS発生🤦‍♂️
👉 `fetch("/api/...")` に寄せる！

### 🧨 ミス3：502（Bad Gateway）

だいたいこれ👇

* APIが落ちてる / ポート違い / コンテナ名違い
* 同じネットワークにいない（Composeのネットワーク設計が原因）

---

## 8) ここ、ちょっとだけ注意🍪🧷（次章への伏線）

APIが同一オリジンになると、**Cookieが自然に飛ぶようになる**ので、ログイン系は楽になる反面、**CSRF対策**の話が気になってくる（これは次章でちゃんとやるよ）🍪💣

---

## 9) AIに頼むと爆速になる質問テンプレ🤖⚡

### ✅ Caddyfileを作らせる

* 「`dev.localhost` で `/api/*` は `api:8787`、それ以外は `front:5173` に流す **Caddyfile** を書いて。`/api` は剥がして」

### ✅ 404/502の切り分けを手伝わせる

* 「Caddyで `/api/*` を `api:8787` に流してるのに 502。原因候補を“確認コマンド付き”で優先順に出して」

### ✅ フロントのAPI呼び出しを置換

* 「`http://localhost:8787` を叩いてる箇所を、環境変数なしでも動く `fetch('/api/...')` に置き換える方針で修正案を出して」

---

## 10) ミニ課題🧪✨（15〜30分）

### 課題A：CORSを“消す”成功体験🎉

1. Caddyfile に `handle_path /api/* { reverse_proxy api:8787 }` を追加([Caddy Web Server][4])
2. フロントの `fetch` を `/api/...` に統一
3. DevToolsで **`OPTIONS` がどう変わったか**観察する([MDN Web Docs][2])

### 課題B：わざと壊して直す🧯

* `handle_path` を `handle` に変えて挙動の違いを見る（404になるなら理由を言語化✍️）

---

必要なら、この章の「完成形サンプル」として、**front(Vite) + api(Node) + caddy** の最小Compose一式も、コピペで動く形にまとめて出せるよ🐳📦✨

[1]: https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Same-origin_policy?utm_source=chatgpt.com "Same-origin policy - Security - MDN Web Docs - Mozilla"
[2]: https://developer.mozilla.org/en-US/docs/Glossary/Preflight_request?utm_source=chatgpt.com "Preflight request - Glossary - MDN Web Docs"
[3]: https://developer.mozilla.org/en-US/docs/Glossary/CORS-safelisted_request_header?utm_source=chatgpt.com "CORS-safelisted request header - Glossary - MDN Web Docs"
[4]: https://caddyserver.com/docs/caddyfile/directives/handle_path?utm_source=chatgpt.com "handle_path (Caddyfile directive)"
[5]: https://caddyserver.com/docs/caddyfile/directives/reverse_proxy?utm_source=chatgpt.com "reverse_proxy (Caddyfile directive) — Caddy Documentation"
[6]: https://doc.traefik.io/traefik/routing/providers/docker/?utm_source=chatgpt.com "Traefik Docker Routing Documentation"
[7]: https://doc.traefik.io/traefik/middlewares/http/stripprefix/?utm_source=chatgpt.com "Traefik StripPrefix Documentation"
