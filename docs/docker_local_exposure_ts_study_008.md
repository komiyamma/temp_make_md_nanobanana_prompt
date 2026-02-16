# 第08章：“とりあえず動く”用の命名ルールを決める📏✅

ここでやることは超シンプルです👇
**「人間にやさしいURL」を先に固定して、あとからプロジェクトが増えても崩れないようにする**こと🧠💕
（命名が決まると、リバースプロキシ設定も、チーム会話も、デバッグも一気に楽になります🚀）

---

## 8.1 命名ルールがないと何が起きる？😵‍💫

よくある地獄👇💥

* 「frontってどれ？ apiってどれ？ localhost:5173ってどのプロジェクト？」って毎回迷う🌀
* 似たようなアプリが増えると、**名前の衝突**で破綻する⚡
* Cookie / ログイン / CORS の問題が出たとき、**どのURLでアクセスしてるか**が曖昧で詰む🍪💣

だから先に「URLの住所ルール」を作ります🏠✨

---

## 8.2 まず決めるのはこの3点だけ🧩

命名って難しそうに見えるけど、決めるのはこの3つだけです👇

1. **プロジェクト名（project）**：例 `sengoku` / `shop`
2. **役割（role）**：例 `front` / `api` / `admin` / `docs`
3. **環境（env）**（必要なら）：例 `dev` / `stg`（最初は無しでOK🙆）

---

## 8.3 迷ったらコレ！おすすめ命名フォーマット2つ🍱

どっちか1つに統一すれば勝ちです✅

**A案：役割.プロジェクト.localhost（おすすめ）** 🥇

* 例：`front.sengoku.localhost` / `api.sengoku.localhost` / `admin.sengoku.localhost`
* いいところ：**「同じプロジェクトでまとまる」**ので見通しが良い👀✨

**B案：プロジェクト-役割.localhost（シンプル）** 🥈

* 例：`sengoku-front.localhost` / `sengoku-api.localhost`
* いいところ：**短くて直感的**🧠

> どっちもOKだけど、教材としては A案が「増えた時に整理しやすい」ので推しです😺✨

---

## 8.4 `.localhost` を使う理由（超大事）🏠💪

`.localhost` は「例として安全に使っていい予約済みドメイン」です。([RFCエディタ][1])
さらに `localhost` と **`.localhost`配下の名前**は「特別扱いして良い」ことが RFC で整理されています。([RFCエディタ][2])
IANA の「Special-Use Domain Names」レジストリにも載っています。([iana.org][3])

そして実務的に強いのがここ👇
**最新の常用ブラウザは `*.localhost` をループバック（127.0.0.1 / ::1）へ自動解決する**ので、`myapp.localhost` みたいな名前がすぐ使えます。([Microsoft Learn][4])

---

## 8.5 逆に避けたい名前（罠を踏まない）⚠️

**避けたい：`.local`**
`.local` は mDNS（Bonjourとか）向けに予約されていて、ネットワーク環境で名前解決がややこしくなりがちです😇([IETF Datatracker][5])
（実際に `.local` を避ける注意喚起もあります）([Appleサポート][6])

**避けたい：実在TLD（例：`.com` / `.dev` / `.jp` とか）**

* 会社・学校ネットワークのDNSと衝突したり、変な方向に解決されたりする事故が起きやすいです💥
* 「ローカル専用」のつもりが、外の世界と混ざるのが怖い😱

---

## 8.6 “とりあえず動く”命名ルール（このままコピペでOK）📏✨

ここからは実際のルールセットです。これを固定しましょう✅

**✅ ルール1：全部小文字**

* `Front` と `front` が混ざると人間が死にます🪦🙂

**✅ ルール2：区切りは `.` と `-` だけ（おすすめ）**

* 変な記号（`_` とか）は、ツールや証明書で詰まる原因になりがち🙃

**✅ ルール3：役割は固定語彙にする（増えても崩れない）**
おすすめ role 辞書📚

* `front`（UI）
* `api`（バックエンド）
* `admin`（管理）
* `docs`（Storybook/Docサイト）
* `auth`（認証系が独立するなら）
* `assets`（静的配信を分けるなら）

**✅ ルール4：プロジェクト名は“リポジトリ名と一致”が最強**

* 例：リポジトリが `sengoku` なら `*.sengoku.localhost` に統一🏷️✨
* 人間の会話もログもブレない👍

---

## 8.7 具体例（完成形のURL一覧）🧾🎯

A案（役割.プロジェクト.localhost）で例を作るとこう👇

* `front.sengoku.localhost`（画面）🖥️
* `api.sengoku.localhost`（API）🔌
* `admin.sengoku.localhost`（管理）🛠️
* `docs.sengoku.localhost`（ドキュメント）📘

さらにプロジェクトが増えてもこうやって並ぶだけ👇🌱

* `front.shop.localhost` / `api.shop.localhost`
* `front.blog.localhost` / `api.blog.localhost`

**“アプリが増えても住所体系が崩れない”**のが勝ちです🏆✨

---

## 8.8 ここ重要：URLの名前と、Docker内の名前は別世界🌐🐳

混乱しやすいポイントを先に潰します🧯

* ブラウザが見るのは：`front.sengoku.localhost` みたいな **URLのホスト名**
* コンテナ同士が見るのは：`api` / `db` みたいな **Composeのサービス名**（内部DNS）🧩

つまり👇
**外（人間向けの住所）＝ `.localhost` 命名ルール**
**内（コンテナ通信）＝ service名ルール**
で、二層に分けて考えるのが正解です✅

（Windowsでは Docker の Desktop が WSL 2 を使う構成が一般的で、ブラウザ側のURL整理が効いてきます。）([Docker Documentation][7])

---

## 8.9 よくあるミス集（先に踏み抜きポイント回収）😇🧯

* **ミス1：途中で命名パターンが混ざる**

  * `api.sengoku.localhost` と `sengoku-api.localhost` が同居 → 未来の自分が泣く😭
* **ミス2：`.local` を使って、Wi-Fi環境で挙動がブレる**

  * 予約用途が違うので避けるのが安全です⚠️([IETF Datatracker][5])
* **ミス3：CLIで `*.localhost` が解決しないのに混乱する**

  * ブラウザは自動解決しても、コマンドは環境差が出ることがあります（その時は hosts を足す or そのコマンドだけ `localhost` を使う等で回避）🛠️([Microsoft Learn][4])

---

## 8.10 AIに投げる例（コピペ用）🤖✨

GitHub Copilot や OpenAI Codex に投げるときの型です👇

**命名ルールを作らせるプロンプト**

```text
次のサービス構成で、ローカル開発用のURL命名ルールを「役割.プロジェクト.localhost」形式で提案して。
プロジェクト名は sengoku。
役割は front, api, admin, docs。
一覧にして、増えた時の拡張ルールも短く添えて。
```

**プロジェクトが複数ある前提のプロンプト**

```text
プロジェクトが sengoku / shop / blog の3つある。
各プロジェクトに front と api がある。
「役割.プロジェクト.localhost」で、衝突しないURL一覧を作って。
命名の禁止事項（大文字、_ など）も添えて。
```

---

## 8.11 ミニ課題（10分）⏱️🎮

**課題：2プロジェクト分の住所を作る🏠🏠**

* プロジェクト：`sengoku` と `shop`
* 役割：`front`, `api`, `admin`

✅ やること

1. A案でURL一覧を書く（6個）📝
2. 「途中で増えても崩れない理由」を1行で説明する🧠✨

🎯 できたら自己採点

* ルールが1種類に統一されてる？✅
* 小文字だけ？✅
* `.localhost` になってる？✅

---

この第8章が固まると、次の「Dockerネットワーク復習🌐🐳」からの理解がめちゃ伸びます📈✨
続けて第9章に入るなら、「この命名を“内部DNS（service名）”側にもどう反映するか」まで一緒に整えちゃおう😺🧩

[1]: https://www.rfc-editor.org/rfc/rfc2606.html?utm_source=chatgpt.com "RFC 2606: Reserved Top Level DNS Names"
[2]: https://www.rfc-editor.org/rfc/rfc6761.html?utm_source=chatgpt.com "RFC 6761: Special-Use Domain Names"
[3]: https://www.iana.org/assignments/special-use-domain-names?utm_source=chatgpt.com "Special-Use Domain Names"
[4]: https://learn.microsoft.com/ja-jp/aspnet/core/test/localhost-tld?view=aspnetcore-10.0&utm_source=chatgpt.com ".localhost トップレベル ドメインのサポート"
[5]: https://datatracker.ietf.org/doc/html/rfc6762?utm_source=chatgpt.com "RFC 6762 - Multicast DNS"
[6]: https://support.apple.com/en-us/101903?utm_source=chatgpt.com "Apple devices might not open your internal network's '.local ..."
[7]: https://docs.docker.com/desktop/features/wsl/?utm_source=chatgpt.com "Docker Desktop WSL 2 backend on Windows"
