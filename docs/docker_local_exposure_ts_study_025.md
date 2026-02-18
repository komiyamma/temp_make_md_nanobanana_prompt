# 第25章：ローカルHTTPSの必要性を知る

「え、ローカルって `http://localhost` でよくない？🤔」
……って思うの、めっちゃ普通です😆✨
でも最近は **“HTTPS（＝安全な通信）じゃないと使えない機能” が増えてきた**ので、ローカルでもHTTPSが必要になる場面がちょいちょい出ます。

この章では「いつ必要？」「何が困る？」「今やるべき？」をスッキリ判断できるようにします💡

---

## 25-1 「HTTPSが必要」って、実は2種類ある🧠🔎

ローカルHTTPSの話で混乱しがちなのがココ👇

* **A：ブラウザが“安全なコンテキスト”じゃないと許可しない機能**
  例：Service Worker / Passkeys / クリップボード など
  → これは **“Secure Context” かどうか**がポイントです。([MDN Web Docs][1])

* **B：外部サービスや設定が “URLの見た目（https:// かどうか）” を厳密に見るケース**
  例：OAuth / OIDC の `redirect_uri` が **https と http で別物扱い**になる、など
  → これは **文字列としてのURL一致**がポイントです。([OpenIDファウンデーション][2])

そして重要ポイント✨
`localhost` や `*.localhost` は、仕様上 “開発用として信頼できる扱い” になってます。([W3C][3])
だから **`http://localhost` でも動く機能がある**んだけど……
「本番（HTTPS）では壊れるのに、ローカルだと気づけない😇」が起きやすいんです。

![Two Types of HTTPS Requirements](./picture/docker_local_exposure_ts_study_025_https_needs.png)

---

## 25-2 HTTPSが欲しくなる代表シーン集📦✨（あるある順）

「自分に関係あるか」をここで見極めればOKです✅

![Scenes Requiring HTTPS](./picture/docker_local_exposure_ts_study_025_https_scenes.png)

### ① PWA / オフライン / プッシュ通知を触る📱⚡

Service Worker は **安全なコンテキストでしか動きません**（開発のために `http://localhost` を例外扱いする、とも明記されています）。([MDN Web Docs][4])
👉 つまり「ローカルでPWAっぽいことやりたい」なら、HTTPS側も視野に入ります。

### ② Passkeys（WebAuthn）・強いログイン🔑😎

WebAuthn は **Secure Context が前提**です。([MDN Web Docs][5])
👉 ローカルで “本番に近いログイン体験” を詰めたいなら HTTPS が現実的になります。

### ③ カメラ・マイク・画面共有🎥🎙️

`getUserMedia()` などは **Secure Context が前提**。([MDN Web Docs][6])
👉 「Web会議っぽい機能」や「撮影アップロード」などやるなら要注意！

### ④ クリップボード（コピー/ペースト）📋✨

Clipboard API も **Secure Context 前提**。([MDN Web Docs][7])
👉 “コピーボタン作ったのに動かない” が起きがち😇

### ⑤ Cookieまわり（特にログイン）🍪💣

* `SameSite=None` を使うなら **`Secure` が必須**（＝安全なコンテキストが必要）([MDN Web Docs][8])
* そもそも `Secure` なCookieは **http では基本セットできない**（ただし `localhost` は特別扱いがある、と明記あり）([MDN Web Docs][9])

👉 ここが超ややこしいポイントで、**ローカルの例外に甘えると本番でズレる**ことがあります😵‍💫

![The Localhost Exception Trap](./picture/docker_local_exposure_ts_study_025_localhost_trap.png)

### ⑥ 外部ログイン（OAuth/OIDC）🔁🔐

OIDC では `redirect_uri` が **登録値と完全一致（文字列一致）**が要求されます。([OpenIDファウンデーション][2])
つまり👇

* ローカル `http://...` で試して
* 本番 `https://...` にすると
  **“同じつもりでも別物”** でエラーになりがち😇([Microsoft Learn][10])

---

## 25-3 「ローカルは動くのに本番で死ぬ」典型パターン😇📛

### パターンA：HTTPSページからHTTPを呼んでしまう（Mixed Content）🚫

本番でHTTPSにした途端、画像・API・WebSocketがブロックされるやつです。
Mixed Content はブラウザがガッツリ防御します。([MDN Web Docs][11])

### パターンB：WebSocketが `ws://` のまま👻

ページが `https://` だと、WebSocketも基本 `wss://`（暗号化）側に寄せないと事故ります。
（これも “本番差分” の代表です⚠️）

### パターンC：Cookie属性が “ローカル例外” で通ってた🍪

`localhost` には例外があるので、ローカルで「動いてるじゃん！」が成立しやすい。([MDN Web Docs][9])
でも本番は例外なしで、突然ログインが飛びます😇

![Typical Production Failures](./picture/docker_local_exposure_ts_study_025_prod_failures.png)

---

## 25-4 今すぐHTTPSにするべき？判断チェック✅✨

当てはまったら「HTTPS導入、前倒しが吉」です👇

* ✅ PWA / Service Worker をやる（オフラインやプッシュ含む）([MDN Web Docs][4])
* ✅ Passkeys（WebAuthn）をやる([MDN Web Docs][5])
* ✅ カメラ/マイク/画面共有をやる([MDN Web Docs][6])
* ✅ クリップボードAPIを安定して使いたい([MDN Web Docs][7])
* ✅ Cookieや認証を本番に近い形で検証したい([MDN Web Docs][8])
* ✅ OAuth/OIDC の `redirect_uri` を扱う（URL一致の罠を踏みたくない）([OpenIDファウンデーション][2])

逆に👇

* 🔸 「フロント表示＋簡単APIだけ」「外部ログインもPWAも無し」
  → いったんHTTPで進めて、必要になったらHTTPSでもOK👌（ただし後で移行は確実に発生しがち😆）

![HTTPS Decision Checklist](./picture/docker_local_exposure_ts_study_025_decision_checklist.png)

---

## 25-5 5分でできる「必要性」セルフ診断🧪🔎

ブラウザのDevTools（F12）コンソールでこれ👇

```js
window.isSecureContext
```

* `true` → “Secure Context的にはOK” な可能性が高い✨([MDN Web Docs][1])
* `false` → その環境だと、Secure Context前提APIが止まりやすい😇

ついでに👇

```js
location.protocol
```

* `"https:"` なら URL的にもHTTPS
* `"http:"` なら URL的にはHTTP（外部サービスの一致判定で落ちる系の罠が残る）([OpenIDファウンデーション][2])

![DevTools Secure Context Check](./picture/docker_local_exposure_ts_study_025_secure_context_check.png)

---

## 25-6 “ローカルHTTPS” はどこでやるのが自然？🚪🔒

結論：**入口（リバースプロキシ）でHTTPS終端**するのがラクです😺✨

```txt
[Browser] -- https://app.localhost --> [Reverse Proxy] -- http --> [front]
                                   └-----------------------> [api]
```

* コンテナの中まで全部TLSにしなくてOK（入口で受けて、中はHTTPで十分なことが多い）👍
* “入口1個＋中に複数アプリ” の構成と相性バツグン💯

![Proxy HTTPS Termination](./picture/docker_local_exposure_ts_study_025_proxy_termination.png)

---

## 25-7 よくあるミス集📕🧯（先に潰すと勝てる）

* ❌ 「localhostで動いた＝本番も大丈夫」
  → `localhost` には例外が多いので油断しやすいです😇([MDN Web Docs][9])

* ❌ `SameSite=None` なのに `Secure` を付け忘れ🍪
  → ブラウザ側で弾かれる/挙動が変になる典型！([MDN Web Docs][8])

* ❌ 本番HTTPSにしたら突然リソースが死ぬ（Mixed Content）🚫
  → HTTP混入を疑う！([MDN Web Docs][11])

* ❌ OAuth/OIDC が http/https の違いでエラー🔁
  → `redirect_uri` は **完全一致**が基本。([OpenIDファウンデーション][2])

---

## 25-8 AIに聞くと爆速になる質問例🤖💬✨

* 「`window.isSecureContext` が false だった。原因候補を “優先度順” に10個出して、確認コマンドもセットで教えて」🕵️‍♂️
* 「ローカルHTTPSにするとき、リバースプロキシ終端にする設計のメリット/デメリットを、初心者向けに説明して」🧠
* 「Mixed Content を最短で見つけるチェックリスト作って。DevToolsで見る場所もセットで」🔍
* 「Cookieの `SameSite` と `Secure` で “ローカルでは動くのに本番で死ぬ” 例を3つ作って」🍪💣
* 「OIDCの `redirect_uri` 完全一致の意味を、例（httpとhttpsで別物）で分かりやすく説明して」🔁([OpenIDファウンデーション][2])

---

## 25-9 ミニ課題🎯✨（次に進む前の整理）

あなたの今のPJを想定して👇を埋めてみてください✍️

1. `window.isSecureContext` は **true/false どっち？** 🧪
2. 今後やりたい機能に、次が含まれる？（YES/NO）

   * PWA/Service Worker📱
   * Passkeys🔑
   * カメラ/マイク🎥
   * クリップボード📋
   * OAuth/OIDC🔁
3. YESが1個でもあったら：**ローカルHTTPS導入する価値アリ**✅✨
   （導入すると “本番差分の事故” がかなり減ります😆）

---

ここまでで「なぜローカルでもHTTPS欲しくなるのか」が腹落ちしたはずです😺🔐✨
次は、**実際にローカルHTTPSをラクに張る方法**へ進めばOKです🚀

[1]: https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Secure_Contexts?utm_source=chatgpt.com "Secure contexts - MDN Web Docs - Mozilla"
[2]: https://openid.net/specs/openid-connect-core-1_0.html?utm_source=chatgpt.com "OpenID Connect Core 1.0 incorporating errata set 2"
[3]: https://www.w3.org/TR/secure-contexts/?utm_source=chatgpt.com "Secure Contexts"
[4]: https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API?utm_source=chatgpt.com "Service Worker API - MDN Web Docs"
[5]: https://developer.mozilla.org/en-US/docs/Web/API/Web_Authentication_API?utm_source=chatgpt.com "Web Authentication API - MDN Web Docs - Mozilla"
[6]: https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia?utm_source=chatgpt.com "MediaDevices: getUserMedia() method - Web APIs | MDN"
[7]: https://developer.mozilla.org/en-US/docs/Web/API/Clipboard_API?utm_source=chatgpt.com "Clipboard API - MDN Web Docs"
[8]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies?utm_source=chatgpt.com "Using HTTP cookies - MDN Web Docs - Mozilla"
[9]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie?utm_source=chatgpt.com "Set-Cookie header - HTTP - MDN Web Docs"
[10]: https://learn.microsoft.com/en-us/entra/identity-platform/v2-protocols-oidc?utm_source=chatgpt.com "OpenID Connect (OIDC) on the Microsoft identity platform"
[11]: https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Mixed_content?utm_source=chatgpt.com "Mixed content - Security - MDN Web Docs - Mozilla"
