# 第17章：Cookieとセッションの地雷を避ける🍪💣

この章は「リバースプロキシで複数アプリを同居させた瞬間に、ログインが飛ぶ／戻る／消える😇」を**先に潰す**回だよ〜🛠️✨
結論から言うと、事故はだいたい **SameSite / Secure / Domain / Path / “HTTPSだと思われてない”** あたりで起きます🍪🔍
（ここを押さえると、18章の「パス方式」や19章の「サブドメイン方式」がめちゃ安定する👍）

---

## 0) まず “何が起きてる世界” なの？🗺️

イメージはこれ👇（入口＝リバプロ、奥＝複数アプリ）

```text
ブラウザ
  │  https://front.localhost  ← 入口1個（リバプロ）
  ▼
[ Reverse Proxy ]
  │            │
  ▼            ▼
Front App     API App
(3000)        (4000)
```

* Cookieは、サーバが `Set-Cookie` というレスポンスヘッダで「ブラウザに保存してね🍪」って渡すやつ
* ブラウザは条件が合うと、次回リクエストで `Cookie:` ヘッダとして送り返す📨
* でも、条件（属性）が1個でもズレると **保存されない／送られない** が発生する😇 ([MDN Web Docs][1])

---

## 1) 今日のゴール🎯✨

## ✅ ゴール

* ローカルでも「ログイン維持」が安定する🍪🔒
* 複数アプリ同居でも「別アプリのCookieが邪魔しない」🧹
* OAuthや別ドメイン連携で「突然死しない」🚑

---

## 2) Cookie属性の “超ざっくり地図” 🧭🍪

![Cookie Attributes Shield](./picture/docker_local_exposure_ts_study_017_01_cookie_attributes.png)

Cookieの事故率が高い属性はこの4つ👇（まずここだけ覚えればOK）

## 🍪 SameSite（送り先の制限）

* `Strict`：超ガード堅い🛡️（同一サイト以外には基本送らない）
* `Lax`：バランス型⚖️（リンク遷移など一部は送る）
* `None`：制限しない（＝クロスサイトでも送る）
  ただし **`SameSite=None` は `Secure` も必須**（雑に付けると弾かれる）([MDN Web Docs][2])

## 🔒 Secure（HTTPSの時だけ送る）

* `Secure` 付きCookieは **HTTPS通信でしか送られない**
* 逆に言うと、入口がHTTPSでも、アプリが「HTTPだと思ってる」と事故る（後でやる）😇

## 🌐 Domain（どのホストに効かせるか）

* **付けない**：そのホスト限定（ホスト限定＝安全寄り）
* `Domain=...`：サブドメイン含めて広げられる（便利だけど事故りやすい）

> “SameSiteの「site」って何？” は、ざっくり **登録可能ドメイン単位**（例：`www.web.dev` は `web.dev`）みたいな考え方だよ〜🧠 ([web.dev][3])

## 🧩 Path（どのURLパスに効かせるか）

* `Path=/`：全部に送る
* `Path=/app1`：`/app1` 以下だけに送る
  パス方式（/app1 /app2）をやると、ここが超重要🔥

---

## 3) “地雷あるある” 7連発💣💥（まずここ読むのが最短）

## 地雷①：SameSite=None なのに Secure 付いてない🍪❌

* ブラウザが「規約違反〜」って感じで弾くことがある
* 対策：`None` を使うなら **必ず `Secure`** ([MDN Web Docs][1])

## 地雷②：Secure 付けたのに、入口がHTTPのまま🔒❌

* Cookieは保存されても送られなかったり、そもそも保存されない挙動になる
* 対策：入口をHTTPSに寄せる or Secureを見直す（ローカルHTTPSの章で強くなるやつ💪）

## 地雷③：Domain を付けて “共有しすぎ” 🌐💥

![Domain Attribute Risk](./picture/docker_local_exposure_ts_study_017_02_domain_risk.png)

* 別アプリが同名Cookieを上書き→ログインが飛ぶ🌀
* 対策：基本は **Domainを付けずホスト限定**にするのが安全

さらに強い守りとして、`__Host-` プレフィックスが使える（条件：Secure + Path=/ + Domainなし）🛡️
「Domainなしを強制できる」ので事故りにくいよ👍 ([IETF Datatracker][4])

## 地雷④：Path=/ にして “全部のアプリに送ってる” 🧩💥

![Path Attribute Isolation](./picture/docker_local_exposure_ts_study_017_03_path_isolation.png)

* パス方式（/app1 /app2）で特に起きる
* 対策：パス方式なら **CookieもPathで分ける**（or Cookie名を絶対衝突させない）

## 地雷⑤：リバプロ越しで “HTTPSだと認識されてない” 😇

![HTTPS Misunderstanding](./picture/docker_local_exposure_ts_study_017_04_https_misunderstanding.png)

* 入口はHTTPSなのに、アプリ側が「HTTPだよね？」と思ってしまう
* 結果：Secure cookieの発行・検証・リダイレクトがズレてログインが死ぬ
* 対策：`X-Forwarded-Proto` / `X-Forwarded-Host` を信じる設定（アプリ側）を入れる
  リバプロ側は基本これらを渡すのが普通で、元ホストも伝える設計になってるよ📮 ([Caddy Web Server][5])

## 地雷⑥：別ドメイン連携（OAuth等）で SameSite が噛み合わない🔁

* “外部から戻ってくる” は **サイトをまたぐ**ので、SameSiteが原因でCookieが送られないことがある
* 対策：基本は `Lax` を中心に考える（必要時だけ None を検討）([MDN Web Docs][2])

## 地雷⑦：ブラウザの「サードパーティCookie制限」影響を食らう🍪🧊

* 近年ブラウザ側の制限が強め
* 特に “埋め込み（iframe）” や “別サイト文脈” は影響を受けやすい
* Chromeは方針が揺れたりもしてるので、「できるだけ同一サイトで完結」させる設計が強い💪 ([Reuters][6])

---

## 4) まず最初にやるデバッグ手順🕵️‍♂️🔍（ここが勝ち筋）

## ✅ 手順A：レスポンスに `Set-Cookie` が出てるか？

1. ブラウザDevTools → **Network**
2. ログインAPIなどのレスポンスを開く
3. **Response Headers** に `Set-Cookie` があるか確認🍪 ([MDN Web Docs][1])

## ✅ 手順B：Cookieが “保存” されてるか？

* DevTools → **Application** → Cookies
* ここに出てなければ「ブラウザに弾かれてる」可能性が高い😇

## ✅ 手順C：次のリクエストで “送られてる” か？

* Networkで次のAPIリクエストを見て、Request Headers に `Cookie:` が付いてるか📨
* 付いてないなら「SameSite / Secure / Domain / Path」が外れてる可能性が高い

---

## 5) パターン別 “安全レシピ” 🍳✨

![Subdomain vs Path Strategy](./picture/docker_local_exposure_ts_study_017_05_strategy_comparison.png)

## 🅰 サブドメイン方式（例：front.localhost / api.localhost）

**おすすめ：基本はホスト限定Cookie（Domainなし）**

* アプリごとに分離されるので、衝突しにくい🧼
* 「共通ログイン」が必要になった時だけ Domain共有を検討（上級編）

**推奨イメージ**

* `SameSite=Lax`
* `Secure`（入口HTTPS運用なら）
* `HttpOnly`（JSから触らせない）
* `Domain` は付けない（ホスト限定）

## 🅱 パス方式（例：example.localhost/app1 と /app2）

**おすすめ：Cookie名とPathで分離**

* `app1_session` は `Path=/app1`
* `app2_session` は `Path=/app2`
  こうしておくと「別アプリに送られない」ので事故りにくい🧯

---

## 6) 実装ミニ例（TypeScript / Node）🧪🍪

## 例1：安全寄りの “ログインCookie” を発行する（概念）

```ts
// 例：ログイン成功時にセッショントークンをCookieへ
const token = "signed-session-token"; // 本物は署名・暗号化などする

res.setHeader("Set-Cookie", [
  [
    `__Host-session=${encodeURIComponent(token)}`,
    "Path=/",
    "HttpOnly",
    "Secure",
    "SameSite=Lax",
    "Max-Age=604800", // 7日
  ].join("; ")
]);
```

ポイント🍪✨

* `__Host-` を使うと「Domainなし」が前提になって守りが堅い🛡️（条件が満たせないなら無理に使わなくてOK）([IETF Datatracker][4])
* `SameSite=Lax` は “使い勝手と防御のバランス枠” になりやすい ([MDN Web Docs][2])
* `Set-Cookie` はヘッダで、複数Cookieは複数行（配列など）で渡すのが基本 ([MDN Web Docs][1])

## 例2：パス方式で “アプリごとに分離” する

```ts
res.setHeader("Set-Cookie", [
  "app1_session=aaa; Path=/app1; HttpOnly; Secure; SameSite=Lax; Max-Age=3600",
  "app2_session=bbb; Path=/app2; HttpOnly; Secure; SameSite=Lax; Max-Age=3600",
]);
```

---

## 7) リバースプロキシ側で意識すること🚪➡️🏠

## ✅ “元のHost” と “元のスキーム（http/https）” を上流に伝える

多くのリバプロは `X-Forwarded-Host` などを付けてくれるけど、上流がHTTPS向け挙動（Secure cookie等）をするには、**「プロキシの後ろだよ」設定**が必要なことがあるよ〜😇
Caddyの場合も、上流へヘッダを渡しつつ、必要ならHostを上書きする設定がある（HTTPS上流の時など） ([Caddy Web Server][5])

※ここはフレームワーク別に設定名が変わるので、**次の「AIに聞く例」**を使うのが最速👍🤖

---

## 8) よくあるミス → 直し方（即効薬）💊✨

* ✅ **Cookieが保存されない**

  * `SameSite=None` なのに `Secure` 無し → `Secure` 付ける ([MDN Web Docs][1])
  * `Secure` なのにHTTPアクセス → 入口HTTPSへ
* ✅ **保存されたのに送られない**

  * `Path` がズレてる → 想定URLに合わせる
  * `Domain` を広げすぎ/間違い → いったんDomain消してホスト限定に戻す
* ✅ **別アプリと干渉してログインが飛ぶ**

  * Cookie名が衝突 → `app1_session` / `app2_session` みたいに分ける
  * `Path=/` で全部に送ってる → パス方式なら `Path=/app1` 等に分離

---

## 9) ミニ課題🎓🧩（15分で強くなる）

## 課題1：Cookieの“どこがズレてるか”当てゲーム🔍

1. ログインAPIのレスポンスで `Set-Cookie` を見る
2. ApplicationでCookie保存を確認
3. 次のAPIで `Cookie:` が送られてるか確認
4. 送られてなければ **SameSite / Secure / Domain / Path のどれが原因か**を一言でメモ✍️

## 課題2：2アプリ共存で “衝突ゼロ” にする🍪🧹

* app1 と app2 を用意して、Cookie名をわざと同じにして衝突させる😈
* 次に **Cookie名 + Path** で分離して、衝突が消えるのを確認🎉

---

## 10) AIに聞く例🤖💬（そのままコピペOK）

## 🧠 プロキシ配下でSecure cookieが効かない

```text
Node(TypeScript)のWebアプリをリバースプロキシ配下で動かしています。
入口はHTTPS、上流はHTTPです。Secure cookieが発行/送信されません。
使っているフレームワークは（Express/Fastify/Next.js等）です。
必要な “trust proxy” や forwarded headers の設定を最小構成で教えてください。
```

## 🍪 パス方式でCookieを安全に分けたい

```text
/app1 と /app2 を同一ドメインで共存させます。
ログインCookieを衝突させたくありません。
Cookie名、Path、SameSite、Secure の推奨セットを
「ローカル開発」と「本番」で分けて提案してください。
```

## 🧯 OAuthでログインが戻った瞬間に外れる

```text
OAuthログイン後のリダイレクトでセッションが消えます。
SameSite属性の観点で原因候補と、Lax/Noneの切り替え判断基準を
“CSRF対策”も含めて説明してください。
```

---

## まとめ🍪✨

* Cookie事故は **SameSite / Secure / Domain / Path** のどれかが多い
* 複数アプリ同居は「共有しすぎ」が最大の敵：まず **ホスト限定 or Path分離**🧹
* 入口HTTPS＋プロキシ配下は「上流がHTTPSだと理解してない問題」が出るので、ヘッダとアプリ設定がカギ🔑 ([Caddy Web Server][5])

---

次の第18章（パス方式の設計ミニ練習）では、今日の知識を使って「/app1 /app2 /api でCookie衝突ゼロ設計」を実際に組み立てるよ〜🧩🚀

[1]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie?utm_source=chatgpt.com "Set-Cookie header - HTTP - MDN Web Docs"
[2]: https://developer.mozilla.org/ja/docs/Web/HTTP/Guides/Cookies?utm_source=chatgpt.com "HTTP Cookie の使用 - MDN Web Docs"
[3]: https://web.dev/articles/samesite-cookies-explained?utm_source=chatgpt.com "SameSite cookies explained | Articles"
[4]: https://datatracker.ietf.org/doc/draft-ietf-httpbis-rfc6265bis/22/?utm_source=chatgpt.com "draft-ietf-httpbis-rfc6265bis-22 - Cookies: HTTP State ..."
[5]: https://caddyserver.com/docs/caddyfile/directives/reverse_proxy?utm_source=chatgpt.com "reverse_proxy (Caddyfile directive) — Caddy Documentation"
[6]: https://www.reuters.com/sustainability/boards-policy-regulation/google-opts-out-standalone-prompt-third-party-cookies-2025-04-22/?utm_source=chatgpt.com "Google opts out of standalone prompt for third-party cookies"
