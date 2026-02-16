# 第06章：.localhostの最強さを知る💪🏠

この章はひとことで言うと、**「ローカル用の“名前”を、いちばん安全＆ラクに整える方法」**を体に入れる回だよ〜🏠✨
ここが固まると、後の「入口1個（80/443）＋中で振り分け」🚪➡️🏘️ がめちゃ気持ちよく進むよ😆💨

---

## 1) .localhostって何者？👀🔍

`.localhost` は、**ローカル開発で使うために“特別扱い”される予約ドメイン**だよ🧠✨
RFCでは **「localhost. と、その配下（`.localhost` にぶら下がる名前全部）」**が特別で、

* `app1.localhost` みたいな名前でもOK
* **IPv4/IPv6の問い合わせはループバック（自分のPC）に解決されると考えてよい**
* **名前解決の仕組みは、localhost系を“特別扱い”してループバックを返すべき**

…という整理になってるよ📜✨ ([RFC エディタ][1])

---

## 2) .localhostが「最強」な理由 3つ💪✨

## 理由A：hosts編集なしで “それっぽいURL” が作れる🪄📝

`front.localhost` / `api.localhost` / `admin.localhost` …みたいに、**プロっぽいURL**がすぐ使えるよ😎✨
（hostsファイル編集を挟まないから、ミスも減る🙏）

## 理由B：うっかり外のDNSに飛びにくい🧯🌍

「実在するドメイン」と違って、**ローカル専用として扱われる前提**があるから、
“うっかり本物のインターネット側に問い合わせちゃった”事故を避けやすいよ🛡️ ([RFC エディタ][1])

## 理由C：ブラウザが “開発に都合のいい安全判定” をしてくれることが多い🔐✨

最近のWeb機能は「安全なコンテキスト（secure context）」が必要なものが増えがち😵‍💫
そこで嬉しいのが、ブラウザ側の仕様で **`http://localhost` や `http://*.localhost` を “潜在的に信頼できる” 扱いにできる**点！🚀
（ユーザーエージェントが localhost をループバックに解決するルールに従うことが条件、という整理） ([W3C][2])
MDN側でも、`http://localhost` / `http://*.localhost` が開発に便利な「trustworthy origin」扱いになり得る、と説明されてるよ🧠✨ ([MDN Web Docs][3])

---

## 3) まず体感しよう：名前解決チェック🪟🧪

## 実験1：PowerShellで「どこに解決されてる？」を見る👀

PowerShellでこれ👇（そのままコピペでOK）✨

```powershell
Resolve-DnsName localhost
Resolve-DnsName app1.localhost
Resolve-DnsName api.localhost
```

ポイント👇

* `127.0.0.1`（IPv4）や `::1`（IPv6）が出たら勝ち🎉
* `::1` が出るのは正常だよ（IPv6ループバック）🙂✨

## 実験2：pingでもOK（ざっくり確認）🏓

```powershell
ping app1.localhost
```

---

## 4) 5分で「.localhostにアクセスできた！」を作る🐳🚀

ここでは **Dockerで“80番にHello”を出して、`http://○○.localhost` で開ける**ところまで一気に行くよ🎉
（まだリバプロは使わない、超ミニ成功体験！）

## 手順A：とりあえず1個出す📦✨

```powershell
docker run --rm -p 80:80 traefik/whoami
```

## 手順B：ブラウザで開く🌐

* `http://localhost/`
* `http://app1.localhost/`
* `http://api.localhost/`

どれでも同じ画面が出たらOK！🎉
（まだ振り分けてないからね😆）

## うまくいかない時の“最速チェック”⚡

* **80番が他のアプリに取られてる**可能性が高いよ🧨
  代わりに 8080 で試す👇

  ```powershell
  docker run --rm -p 8080:80 traefik/whoami
  ```

  その場合は `http://app1.localhost:8080/` で開いてね🧩

---

## 5) 設計が超入門でも分かる「効き目」🧠✨

`.localhost` を使うと、頭の中がこう整理されるよ👇

* **入口の見た目（URL）**：`front.localhost` / `api.localhost` …👀
* **中身の実体（コンテナ/サービス）**：`front` / `api` …🐳
* **入口は将来“1個”にできる**：リバースプロキシが受けて中へ振る🚪➡️🏠

つまり、先に **URL設計だけ先回りで整う** のが強いのよ〜😆✨

---

## 6) よくある落とし穴と回避ワザ🕳️🛟

## 落とし穴A：ポート80が埋まってる😇🔒

Windowsだと、IISとか別の常駐ソフトが掴んでることがあるよ💦
チェック👇

```powershell
Get-NetTCPConnection -LocalPort 80 -State Listen
```

埋まってたら、いったん 8080 で進めてもOK🙆‍♂️（後で直せる！）

---

## 落とし穴B：`::1`（IPv6）に行ってアプリが反応しない🌀

たまに「IPv6では待ち受けてない」アプリがあるよ🥲
対策はシンプル👇

* まずは `http://127.0.0.1` で試す（切り分け）🧪
* もしくはアプリ側を IPv6 でも待ち受ける設定にする（後ででOK）🙂

---

## 落とし穴C：Cookieをサブドメイン間で共有しようとして沼る🍪🫠

結論：**最初は “Domain属性を付けない（host-only cookie）” が正義**✅✨
MDNでも、Domainを省略したCookieは「発行したホストだけに送られる」って整理だよ📘 ([MDN Web Docs][4])

そして重要ポイント👇

* `Domain=localhost` みたいな **“ドメインCookie”は制限されやすい**（特に「レジストリ管理ドメインじゃない」扱い）という説明があるよ🧠 ([Google Groups][5])
* なので入門のうちは **Cookie共有が必要な設計にしない**のが安全🛟

  * 例：まずは `api.localhost` にログイン、フロントは `api.localhost` 経由で通信（同一オリジン寄せ）🧹✨
  * これ、後の章でやる「入口でまとめてCORS減らす」に直結するよ🔥

---

## 落とし穴D：Windows更新で localhost が変になることがある🪟⚠️

2025年の更新で、HTTP.sys を使うIIS系が **`http://localhost/` を含む接続で不具合**になるケースが案内されてたよ（ERR_CONNECTION_RESETなど）🧯
この問題は **後続アップデート（KB）で対処**という流れになってるので、まずは Windows Update → 再起動 が最優先になるよ🔄✨ ([マイクロソフトサポート][6])

---

## 7) ミニ課題 3つ🎯✨

## 課題1：3つの名前を解決してみよう🧪

* `front.localhost`
* `api.localhost`
* `admin.localhost`

PowerShellの `Resolve-DnsName` で、`127.0.0.1` / `::1` が返るのを確認✅

## 課題2：Dockerで `http://api.localhost/` を開けるようにしよう🐳

さっきの `traefik/whoami` を使ってOK！
「開けた！」のスクショ撮っておくと、後で詰まった時に超助かるよ📸✨

## 課題3：命名ルールの“たたき台”をメモ📝

例👇

* `front.localhost`（UI）
* `api.localhost`（REST/GraphQL）
* `admin.localhost`（管理画面）

この3つだけでも、今後の章がスムーズになるよ〜🚀✨

---

## 8) AIに投げると爆速になる質問テンプレ🤖⚡

そのまま貼れるやつ置いとくね👇（Copilot/Codex向け）✨

```text
いま Windows + Docker でローカル開発してる。
front.localhost / api.localhost / admin.localhost を使って整理したい。
まずは「.localhost がループバックに解決される前提」で、
名前解決チェックの手順と、よくある失敗（80番競合、IPv6(::1)、Cookie Domain）を
初心者向けに短く整理して。
```

```text
http://app1.localhost が開けない。原因の切り分け手順を
「名前解決」「ポート競合」「コンテナ起動」「待ち受けアドレス」「ブラウザキャッシュ」
の順でチェックリスト化して。
```

```text
ローカルで Cookie を使う。Domain属性を付けるべきか迷ってる。
localhost / *.localhost で起きがちな制限を踏まえて、
最初に安全な設計（host-only cookie中心）で進める方針を提案して。
```

---

次の章（第7章）に行くと、**「サブドメイン運用のコツ」**で、`.localhost` をプロジェクト増殖に耐える形へ育てていくよ🌱✨
この第6章のゴールは「.localhost最高！が体感で分かった！」まででOK〜😆🏠💪

[1]: https://www.rfc-editor.org/rfc/rfc6761.html "RFC 6761: Special-Use Domain Names"
[2]: https://www.w3.org/TR/secure-contexts/ "Secure Contexts"
[3]: https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Secure_Contexts "Secure contexts - Security | MDN"
[4]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies?utm_source=chatgpt.com "Using HTTP cookies - MDN Web Docs - Mozilla"
[5]: https://groups.google.com/a/chromium.org/g/chromium-bugs/c/4HFLDhvvXsc?utm_source=chatgpt.com "Issue 56211 in chromium: chrome.cookies fails for ..."
[6]: https://support.microsoft.com/en-gb/topic/october-14-2025-kb5066835-os-builds-26200-6899-and-26100-6899-1db237d8-9f3b-4218-9515-3e0a32729685 "October 14, 2025—KB5066835 (OS Builds 26200.6899 and 26100.6899)  - Microsoft Support"
