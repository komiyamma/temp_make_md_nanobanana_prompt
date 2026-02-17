# 第07章：サブドメイン運用のコツ🌈📛

この章は「app1.localhost / app2.localhost みたいに、**アプリごとに“名前”を分けて運用する**」コツを身につける回だよ〜🐳✨
のちの「リバースプロキシでホスト名ルーティング」にそのまま繋がる、超重要パーツです💡🚪

---

## 1) サブドメイン運用って、何がうれしいの？😎🏷️

たとえばこう👇

* フロント：`front.localhost`
* API：`api.localhost`
* 管理画面：`admin.localhost`

こう分けると何が楽かというと…

## ✅ “脳内ルーティング”が簡単になる🧠✨

![_01_mental_routing](./picture/docker_local_exposure_ts_study_007_01_mental_routing.png)

`localhost:5173` とか `localhost:8787` って **数字で覚えるゲーム**になりがち😇
でも `api.localhost` なら、見ただけで役割がわかる！

## ✅ 本番に近い形に寄せやすい🏗️

本番ってだいたい `app.example.com` / `api.example.com` みたいな構造だよね。
ローカルも近づけると、移行がスムーズになるよ〜🚀

## ✅ Cookieや認証の“事故”を早めに発見できる🍪💥

サブドメインを分けると、**ブラウザ的には別オリジン**になりやすくて、CORSやCookieの挙動が本番に近くなる🙌
（このあと軽く触れるね👀）

---

## 2) `.localhost` の強さ（サブドメインが“勝手に”ループバックへ）💪🏠

![_02_wildcard_resolution](./picture/docker_local_exposure_ts_study_007_02_wildcard_resolution.png)

最近の主要ブラウザでは、`xxx.localhost` のような **localhost配下のサブドメイン**が、ループバック（127.0.0.1 / ::1）へ解決される挙動が一般的になってるよ〜🧲✨ ([GitHub][1])

ただし注意点もある👇

* **OSの名前解決（pingやcurl）では失敗することがある**（ブラウザだけ特別扱い、みたいなケース）👀
* **Safari系（WebKit）では localhost サブドメインがうまく動かない報告がある**🍎🧯 ([WebKit Bugzilla][2])
* そもそも `localhost` は “特別用途” として扱われうる（実装がいろいろ）🧩 ([IETF Datatracker][3])

そしてもう1つ大事👇
`localhost` やループバックは **安全なコンテキスト（secure context）として扱われることがある**ので、ローカル開発で“動く/動かない”の差にも関係するよ〜🔐 ([MDNウェブドキュメント][4])

---

## 3) ここで詰まりやすい2大ポイント：CORS と Cookie 🍪🧱

サブドメイン運用を始めると、ここが一気に現実味を帯びるよ😇

## 3-1) “同一オリジン”の判定：ざっくりこれだけ🧠

![_03_same_origin](./picture/docker_local_exposure_ts_study_007_03_same_origin.png)

ブラウザが「同じ場所？」を判断する材料は、基本これ👇

* スキーム（http/https）
* ホスト（ドメイン）
* ポート番号

だから例えば👇

* `http://front.localhost:5173` と `http://api.localhost:8787`
  → **ホストもポートも違う**＝だいたい別オリジン扱い → CORS が絡む可能性💣 ([MDNウェブドキュメント][5])

## 3-2) Cookieの“超ざっくり”注意点🍪

* Cookieは基本「**どのホストに送る？**」が超重要
* `SameSite=None` を使うなら、今は **Secure が必須**になってる（ブラウザ都合）🔒 ([MDNウェブドキュメント][6])
* ローカル開発では例外的挙動もあるので、「本番と同じ感覚に寄せたいならHTTPSも視野」って感じ👀 ([MDNウェブドキュメント][7])

## 3-3) CORSの“超ざっくり”注意点🌍

* 別オリジンへのアクセスを許可する仕組みが CORS
* 代表ヘッダ：`Access-Control-Allow-Origin` / `Access-Control-Allow-Credentials` など🧾 ([MDNウェブドキュメント][5])
* Cookie（資格情報）を跨がせるなら、`Allow-Credentials: true` が要ることが多い（でも設定ミスりやすい）🍪🧯 ([MDNウェブドキュメント][8])

この章では深追いしないけど、**「サブドメインを分けると、CORS/Cookieが話題に上がる」**だけ先に頭に置いとけばOK〜🙆‍♂️✨

---

## 4) ハンズオン：`front.localhost` と `api.localhost` を“今すぐ体験”する🚀🧪

![_04_handson_setup](./picture/docker_local_exposure_ts_study_007_04_handson_setup.png)

「おお、こういう感じか！」って掴むだけのミニ実験だよ🎮✨
（リバプロはまだ無し。**サブドメイン＋ポート**で雰囲気を掴む）

## 4-1) APIサーバーを立てる（超ミニ）🧱

空のフォルダでOK。`server.mjs` を作って👇

```js
import http from "node:http";

const server = http.createServer((req, res) => {
  if (req.url === "/health") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ ok: true }));
    return;
  }

  res.writeHead(200, { "Content-Type": "text/plain; charset=utf-8" });
  res.end("hello from api 👋");
});

// 0.0.0.0で待つ（ローカルでもDockerでも扱いやすい形）
server.listen(8787, "0.0.0.0", () => {
  console.log("API: http://api.localhost:8787/health");
});
```

起動👇

```powershell
node .\server.mjs
```

ブラウザで開く👇
`http://api.localhost:8787/health` ✅

---

## 4-2) フロント（Viteなど）を `front.localhost` で開く🌬️🖥️

すでにViteプロジェクトがある前提でOK🙌

```powershell
npm run dev -- --host 0.0.0.0 --port 5173
```

ブラウザで👇
`http://front.localhost:5173`

## もし Vite に怒られたら（Blocked request系）😇

![_05_vite_shield](./picture/docker_local_exposure_ts_study_007_05_vite_shield.png)

最近のViteは **devサーバーを守るために“許可ホスト制”**が入ってるよ🛡️
ただ `.localhost` 配下はデフォルト許可、という扱いも明記されてる（＝基本は通るはず）📘 ([vitejs][9])

それでも環境や構成で弾かれたら、`vite.config.ts` にこう足す👇

```ts
import { defineConfig } from "vite";

export default defineConfig({
  server: {
    allowedHosts: ["front.localhost", ".localhost"],
  },
  preview: {
    allowedHosts: ["front.localhost", ".localhost"],
  },
});
```

---

## 4-3) （任意）PowerShellの curl で叩きたいのに解決しない時🪟🧯

「ブラウザでは開けるのに、`curl http://api.localhost:8787` が死ぬ」みたいな時は、Windowsの hosts に足すと安定するよ🙌
（詳しい編集は第5章だけど、必要な行はこれ👇）

```txt
127.0.0.1 front.localhost api.localhost admin.localhost
::1       front.localhost api.localhost admin.localhost
```

---

## 5) サブドメイン運用の“命名”コツ（ここが設計っぽい所）📏✨

![_06_naming_convention](./picture/docker_local_exposure_ts_study_007_06_naming_convention.png)

## ✅ コツ1：役割が一撃でわかる名前にする🎯

おすすめ：**名詞は短く、役割は固定語彙で**

* `front.localhost`
* `api.localhost`
* `admin.localhost`

## ✅ コツ2：複数プロジェクト同居を見越すなら“接頭辞”を足す🧩

あとで地獄になりがちポイントなので先に潰す😇

* `p1-front.localhost` / `p1-api.localhost`
* `p2-front.localhost` / `p2-api.localhost`

「人間が読みやすい」が最強ルールだよ🧠💕

---

## 6) よくあるミスあるある📕🧯

* **① ブラウザOK、CLI（curl/ping）NG**
  → hostsに足せば安定しやすい（第5章と接続）🪛

* **② Viteに怒られる：Blocked request…**
  → `server.allowedHosts` で許可（`.localhost`はデフォルト許可のはず、でも例外はある）([vitejs][9])

* **③ fetch が CORS で落ちる**
  → 別オリジンだとCORS設定が必要になることがある（ヘッダ・preflight）🧱 ([MDNウェブドキュメント][5])

* **④ Cookieでログインが飛ぶ🍪💥**
  → SameSite / Secure の影響が出やすい。`SameSite=None` は `Secure` 必須などを思い出す🔒 ([MDNウェブドキュメント][6])

* **⑤ Safari/iOSで localhost サブドメインが怪しい**
  → WebKit側の事情で引っかかるケースがある🍎🧯 ([WebKit Bugzilla][2])

---

## 7) AIに投げる“ちょうどいい聞き方”🤖🪄

コピペでどうぞ👇（Copilot/Codex向けの頼み方の型）

* **命名ルール決め**

  * 「ローカルで front/api/admin をサブドメイン運用したい。複数プロジェクトが同居しても衝突しない命名規則を3案、メリデメ付きで提案して」

* **CORSの最小設定**

  * 「`front.localhost:5173` から `api.localhost:8787` を叩く。Cookieは使わない前提で、最小のCORS設定例（Node）を出して。危険な設定（`*`など）も注意書きして」

* **Cookie運用の方針相談（超重要）**

  * 「ローカルで front/api をサブドメイン分離したい。認証をCookieでやる場合の落とし穴（SameSite/Secure/Domain）を“初心者にもわかる言葉”で整理して。おすすめの回避策も」

---

## 8) ミニ課題（5〜10分）🎒✨

## 課題A：命名してみよう🏷️

次の3つの役割に名前を付けてみて👇
「フロント」「API」「管理画面」
→ さらに「プロジェクトが2つに増えた」版も作ってみる🧩

## 課題B：同一オリジン？別オリジン？🧠

次が「同一オリジンかどうか」を判定してみよう👇

* `http://front.localhost:5173` と `http://front.localhost:3000`
* `http://front.localhost:5173` と `http://api.localhost:8787`
* `https://front.localhost` と `http://front.localhost`

（答えは次章以降のCORS理解がめっちゃ楽になるよ〜🧠✨）

## 課題C：Viteの“ホスト制限”を体験する🛡️

`front.localhost` 以外のホスト名でも開こうとして、怒られたら `allowedHosts` で直してみよう（できたら勝ち🎉）([vitejs][10])

---

次の章（第8章）は、このサブドメイン運用を “破綻しない命名ルール” に落とし込んで、プロジェクトが増えても迷子にならない状態を作っていくよ〜🧱✨

[1]: https://github.com/nodejs/undici/issues/4391?utm_source=chatgpt.com "Add support for resolving wildcard subdomains *.localhost"
[2]: https://bugs.webkit.org/show_bug.cgi?id=160504&utm_source=chatgpt.com "160504 – Localhost subdomains don't work"
[3]: https://datatracker.ietf.org/doc/html/rfc6761?utm_source=chatgpt.com "RFC 6761 - Special-Use Domain Names"
[4]: https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Secure_Contexts?utm_source=chatgpt.com "Secure contexts - MDN Web Docs - Mozilla"
[5]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS?utm_source=chatgpt.com "Cross-Origin Resource Sharing (CORS) - MDN Web Docs"
[6]: https://developer.mozilla.org/ja/docs/Web/HTTP/Guides/Cookies?utm_source=chatgpt.com "HTTP Cookie の使用 - MDN Web Docs"
[7]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie?utm_source=chatgpt.com "Set-Cookie header - HTTP - MDN Web Docs"
[8]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Access-Control-Allow-Credentials?utm_source=chatgpt.com "Access-Control-Allow-Credentials header - HTTP | MDN"
[9]: https://ja.vite.dev/config/server-options?utm_source=chatgpt.com "サーバーオプション"
[10]: https://vite.dev/config/server-options?utm_source=chatgpt.com "Server Options"
