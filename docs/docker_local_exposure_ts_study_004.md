# 第04章：ルーティング超入門：URLのどこで振り分ける？🔍🍰

この章は「リバースプロキシで複数アプリを共存させる」ための**超・基礎体力**だよ💪✨
まずは “どこを見て振り分けるの？” をスッキリ理解しよう〜🧠💡

---

## この章でできるようになること✅🎉

* URLを見て「**ホスト名**（サブドメイン）と**パス**（`/api` みたいな部分）の違い」を説明できる😊
* ルーティング（振り分け）の設計で「**どっちを選ぶと幸せか**」判断できる🌱
* “振り分け表（ルート表）” を作って、次章以降の設定にそのまま持ち込める📋✨

---

## 1) まずURLを分解しよう🍰🔪

![URL Parts Dissection](./picture/docker_local_exposure_ts_study_004_01_url_parts.png)

例：
`https://app1.localhost/api/users?limit=10#debug`

ざっくり分けるとこう👇

* **scheme**：`https`（通信の種類）
* **host**：`app1.localhost`（宛先の名前＝サブドメイン/ドメイン）
* **path**：`/api/users`（中のどこに行く？）
* **query**：`?limit=10`（条件・オプション）
* **fragment**：`#debug`（ページ内ジャンプっぽいやつ）

この「scheme / host / path / query / fragment」みたいな構造はURI/URLの基本ルールとして定義されてるよ📘✨ ([IETF Datatracker][1])

---

## 2) サーバー（＝リバプロ）が見れる場所 / 見れない場所👀🚪

![Server Visibility & Fragment](./picture/docker_local_exposure_ts_study_004_02_server_visibility.png)

ここ超重要‼️

## ✅ サーバーが見れる

* **Host（ホスト名）**：`app1.localhost`
* **Path（パス）**：`/api/users`
* **Query（クエリ）**：`?limit=10`（見れるけど、振り分けに使うのは基本おすすめしない）

## ❌ サーバーが見れない

* **Fragment（`#debug` の部分）**
  `#` 以降は **ブラウザ側で処理されて、サーバーへ送られない** よ📌 ([MDN Web Docs][2])

つまり…
**「`#`で振り分け」は不可能** 🙅‍♂️💥（これはハマりやすい！）

---

## 3) “振り分けレバー”は基本2つ🎛️✨

![Routing Levers](./picture/docker_local_exposure_ts_study_004_03_routing_levers.png)

リバースプロキシが交通整理🚦するとき、主に見るのはこれ👇

## A. ホスト名で分ける（サブドメイン方式）🏷️🌈

![Host Routing Flow](./picture/docker_local_exposure_ts_study_004_04_host_routing.png)

例：

* `front.localhost` → フロント
* `api.localhost` → API
* `admin.localhost` → 管理画面

**イメージ図🗺️**

* ブラウザ →（同じ入口 80/443）→ リバプロ → Hostを見て振り分け

ポイント：`.localhost` 配下は “特別扱い” で、基本ループバック（自分のPC）に向く前提があるから、ローカル開発で使いやすい設計になってるよ🏠✨ ([IETF Datatracker][3])

---

## B. パスで分ける（Path方式）🧩🍜

![Path Routing Flow](./picture/docker_local_exposure_ts_study_004_05_path_routing.png)

例：

* `localhost/` → フロント
* `localhost/api` → API
* `localhost/admin` → 管理画面

**イメージ図🗺️**

* ブラウザ →（同じ入口 80/443）→ リバプロ → Pathを見て振り分け

---

## 4) どっちを選ぶと幸せ？判断軸🌱✨

![Decision Scale](./picture/docker_local_exposure_ts_study_004_06_decision_scale.png)

ここは「正解は1つ」じゃなくて、**事故りにくさ**で選ぶのがコツだよ😌🍀

## 🟢 ホスト名方式が向いてる時（おすすめ寄り）🏷️✨

* フロントとAPIと管理画面が **別アプリ感** 強い（将来増えそう）📈
* **本番に近い形**（サブドメイン運用）で練習したい🎯
* Cookie / 認証 / OAuth などが絡みそう（後で揉めやすい）🍪💣
* SPAの「`/admin` 配下」みたいな **ベースパス地獄**を避けたい😇

> ちなみにブラウザの“同一オリジン”は **scheme/host/port** が一致してるかで決まるよ🔐
> hostやportが変わると別オリジンになりやすく、CORSなどの話にも繋がる👀 ([MDN Web Docs][4])

---

## 🟡 パス方式が向いてる時（最短で見せたい）🍜⚡

* とにかく **1ドメインで全部見せたい**（体験を単純化）🧠
* アプリが2つくらいで、構造も単純（増える予定が薄い）🙂
* 「`/api` だけ別」みたいな **超ありがち構成**でまず成功体験が欲しい🎉

---

## 5) パス方式の“あるある罠”まとめ😇🧯

パス方式は気軽だけど、初心者が踏み抜きやすい地雷があるよ💥

## 😵 罠1：SPAが `/admin` 配下で動かない

* 画面は出たけど、JS/CSSが 404… 😭
* ルーターやアセットの参照パスが「`/`前提」だとズレる

## 😵 罠2：`/api` を中へ流したのに、API側が `/api` を想定してない

* リバプロが `/api/users` を渡したら、APIが `/users` を期待してて404…
* 「prefixを剥がす/剥がさない」問題が出てくる🧩

## 😵 罠3：WebSocket（HMRなど）が怪しくなる👻

* フロントの開発サーバー（HMR）がパス配下だと、経路が増えて詰まりやすい
  （これは “後の章” でちゃんと対策するよ🛠️）

---

## 6) ルーティング表（設計の芯）を作ろう📋✨

![Routing Table Artifact](./picture/docker_local_exposure_ts_study_004_07_routing_table.png)

設定を書く前に、まず **人間が読めるルート表** を作ると超強いよ💪😺
（これがあるとAIにも一発で伝わる！）

## 例：ホスト名方式のルート表🏷️

* `front.localhost` → `front`（フロントdevサーバ）
* `api.localhost` → `api`（APIサーバ）
* `admin.localhost` → `admin`（管理画面）

## 例：パス方式のルート表🍜

* `localhost/` → `front`
* `localhost/api` → `api`
* `localhost/admin` → `admin`

---

## 7) “実在する設定”の雰囲気をちょい見せ👀✨（まだ暗記しなくてOK）

たとえば Docker のガイドにある Traefik の例だと、
「HostとPathPrefixを組み合わせて振り分け」みたいに書けるよ👇 ([Docker Documentation][5])

```yaml
## こんな感じの“条件”で振り分けできる（雰囲気だけ）
rule: "Host(`localhost`) && PathPrefix(`/api`)"
```

また、Caddy みたいなリバプロでも「reverse_proxyで中へ流す」設計が基本だよ🚪➡️🏠 ([Caddy Web Server][6])

---

## 8) ミニ実験：HostとPathって本当に届いてる？🧪📨

超ミニで「届いてる情報」を目で確認しよう👀✨
（まだDockerなしでOK！）

## ① `request-dump.ts` を作る📝

```ts
import http from "node:http";

const server = http.createServer((req, res) => {
  const host = req.headers.host ?? "(no host)";
  const url = req.url ?? "(no url)";
  console.log(`HOST=${host}  URL=${url}`);

  res.statusCode = 200;
  res.setHeader("Content-Type", "text/plain; charset=utf-8");
  res.end(`HOST=${host}\nURL=${url}\n`);
});

server.listen(3000, () => {
  console.log("Listening on http://localhost:3000");
});
```

## ② ブラウザで開く🌐

* `http://localhost:3000/api/users?limit=10#debug`

見てほしいポイント👇

* ログに `URL=/api/users?limit=10` は出る
* でも `#debug` は出ない（fragmentは送られない）📌 ([MDN Web Docs][2])

---

## 9) AIに聞く例（コピペOK）🤖✨

GitHub の GitHub Copilot や OpenAI の Codex に投げる用の“型”を用意しとくね🧠📦

## ルート表を作らせるプロンプト📋

* 「フロント（SPA）、API、管理画面の3つがあります。ローカルで “入口1つ” にまとめたいです。**ホスト名方式とパス方式でルート表を2案**作って、**事故りやすい点**も箇条書きで教えて。」

## “どっちが幸せ？”判断をさせるプロンプト🌱

* 「将来OAuthログインを入れるかも。Cookieも使う予定。初心者が事故りにくいのはホスト名方式とパス方式どっち？理由を3つ。」

## パス方式の地雷チェック用プロンプト💣

* 「`/admin` 配下にSPAを置くとき、**ルーティング/アセット/リバプロ**の観点で起きる問題を列挙して。対策もセットで。」

---

## 10) ミニ課題（やってみよう）🎒✨

## 課題A：ルート表を書いてみる📋

次の3つを、**ホスト名方式**と**パス方式**でそれぞれルート表にしてみてね👇

* フロント
* API
* 管理画面

## 課題B：選定理由を1行で🌱

* 「なぜその方式にしたか」を **1行**で書く（短くてOK！）✍️

## 課題C：ハマりそうポイントを2つ挙げる🧯

* “未来の自分” のために「ここ危ない」を2個メモしよう😺

---

## まとめ🎯✨

* リバプロの振り分けは基本 **Host** か **Path** 🎛️
* `#`（fragment）は **サーバーに届かない** からルーティングに使えない🙅‍♂️ ([MDN Web Docs][2])
* 設定を書く前に **ルート表** を作ると、設計もAI活用も一気に楽になる📋🤖

---

次の章（05〜）で、ホスト名方式をやるときの「ローカルドメイン（名前解決）」や、`.localhost` を味方につける話に進むと、ここで作ったルート表がそのまま効いてくるよ〜🪟🏠✨

[1]: https://datatracker.ietf.org/doc/html/rfc3986?utm_source=chatgpt.com "RFC 3986 - Uniform Resource Identifier (URI): Generic ..."
[2]: https://developer.mozilla.org/en-US/docs/Web/URI/Reference/Fragment?utm_source=chatgpt.com "URI fragment - MDN Web Docs"
[3]: https://datatracker.ietf.org/doc/html/rfc6761?utm_source=chatgpt.com "RFC 6761 - Special-Use Domain Names"
[4]: https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Same-origin_policy?utm_source=chatgpt.com "Same-origin policy - Security - MDN Web Docs - Mozilla"
[5]: https://docs.docker.com/guides/traefik/?utm_source=chatgpt.com "HTTP routing with Traefik"
[6]: https://caddyserver.com/docs/caddyfile/directives/reverse_proxy?utm_source=chatgpt.com "reverse_proxy (Caddyfile directive) — Caddy Documentation"
