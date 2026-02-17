# 第03章：3原則：最小権限・最小共有・最小公開✂️🔐📤

この章は「**迷ったらこれに戻る**」ための“安全のコンパス”を作る回です🧭✨
Dockerを使うとき、設定の選択肢が多すぎて「え、結局どれが安全なの…？」となりがちですが、**3つの質問**に落とせばほぼ迷いません😄

---

## この章のゴール🎯

![Three Isolation Goals](./picture/docker_safe_isolation_ts_study_003_01_three_goals.png)

次の3つを、**自分の言葉で説明できて**、さらに **Compose/Dockerfileの設定に落とせる**ようになることです💪😊

1. **最小権限**：そのコンテナ（プロセス）に「できること」を最小にする👤✂️
2. **最小共有**：ホストや他サービスと「触れ合う範囲」を最小にする📁🧷
3. **最小公開**：ネットワーク的に「見える範囲」を最小にする🌐🚪

---

## まずは“3つの質問”に変換しよう🧠🔁

![Three Security Questions](./picture/docker_safe_isolation_ts_study_003_02_three_questions.png)

設定を見たら、全部この3つに翻訳します👇

## Q1. それ、何ができる権限を与えてる？（最小権限）🔐

* rootで動かしてない？😱
* `privileged` になってない？🛑
* 余計なcapabilityを持ってない？🧤

> 「最小権限」は、必要なことだけできるように権限を絞る考え方です。NISTの用語集でも“必要最小限の権限”として定義されています。([NIST Computer Security Resource Center][1])

---

## Q2. それ、何を共有してる？（最小共有）📦

* ホストのフォルダを丸ごと渡してない？🧨
* 書き込み可能（rw）になってない？✍️
* “最強危険カード”の `docker.sock` を渡してない？🐙🔥

---

## Q3. それ、誰に見せてる？（最小公開）📡

* `ports:` で外（ホスト/ネットワーク）に公開しすぎてない？🚨
* DBまで公開してない？（ありがち）🫣
* 公開するなら “localhost限定” できてる？🏠

> ポート公開は**デフォルトだと危険寄り**（外部から到達可能になり得る）で、`127.0.0.1` を付けると「ホストだけ」に限定できます。([Docker Documentation][2])

---

## 3原則の“超ざっくり暗記”📌😄

困ったらこれだけ思い出せばOKです👇

* **最小権限**：まず「普通ユーザー」で動かす🙂👟（rootにしない）
* **最小共有**：共有するなら「狭く」「できれば読み取り専用」📁🔒
* **最小公開**：公開するのは「入口だけ」「できればlocalhost限定」🚪🏠

そして最大のコツはこれ👇

## 「削って困ったら足す」✂️➡️➕

最初から盛らない！安全側から始める！✨

---

## 原則①：最小権限（できることを削る）👤✂️🔐

## 1) まず“rootで動かさない”🙂🚫

![Root vs Node User](./picture/docker_safe_isolation_ts_study_003_03_min_privilege_user.png)

コンテナは放っておくとroot（UID 0）で動きがちです。
公式のセキュリティ説明でも「非特権ユーザーで動かすと安全性が上がる」趣旨が書かれています。([Docker Documentation][3])

## 典型パターン✅

* Dockerfileで `USER node`（または専用ユーザー）にする
* もしくはComposeで `user:` を指定する（できる範囲でOK）

**例（Dockerfile）**

```dockerfile
## 例：Nodeイメージは node ユーザーが用意されていることが多い
FROM node:22-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
USER node
CMD ["node", "server.js"]
```

**例（compose.yaml）**

```yaml
services:
  api:
    image: my-api
    user: "node"   # もしくは "1000:1000" のようにUID:GIDでも
```

> Composeの `user` はサービスの属性として定義されています。([Docker Documentation][4])

---

## 2) “できること”を追加で削る：capabilities / no-new-privileges🧤🧯

![Capabilities Drop](./picture/docker_safe_isolation_ts_study_003_04_capabilities_drop.png)

「rootじゃないなら安心でしょ？」…**まだ半分**です😇
コンテナにはデフォルトで色々な“できること（capability）”が付くので、削ると攻撃面が減ります🎯
Docker公式も「デフォルトのcapabilitiesやmountの組み合わせはリスクになり得る」と説明しています。([Docker Documentation][3])

**例（まずは雰囲気だけ掴む）**

```yaml
services:
  api:
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true
```

> `cap_add`/（同ページ内に）capability関連の属性があり、`security_opt` もサービス属性として定義されています。([Docker Documentation][4])

※ここは環境やアプリによって「削りすぎて動かない」が起きるので、章のゴールは **“判断できるようになる”** ことです😊
（困ったら：削ったやつを“必要最小限で戻す”）

---

## 原則②：最小共有（触れられる範囲を削る）📦✂️🧷

## 1) 共有は“狭く・浅く”が正義📁🧠

ありがちな事故：

* プロジェクト直下を丸ごとマウント → `.env` や鍵ファイルまでコンテナが読める😱
* ホストの重要フォルダをうっかりマウント → 誤操作で破壊💥

まずはこの一言で判断できます👇
**「そのコンテナが触っていいデータだけ渡す」**📌

---

## 2) 共有するなら読み取り専用（ro）で“壊せない”にする🔒🧊

![Read-Only Mount](./picture/docker_safe_isolation_ts_study_003_05_readonly_mount.png)

コード共有などは **原則ro** が強いです💪
Composeの例でも、bind mountに `read_only: true` を付ける例が載っています。([Docker Documentation][4])

**例：コードはro、書き込みは専用フォルダだけrw**

```yaml
services:
  api:
    volumes:
      - type: bind
        source: .
        target: /app
        read_only: true
      - type: volume
        source: api-tmp
        target: /app/tmp
volumes:
  api-tmp:
```

---

## 3) “これ渡したら強すぎ”の代表：docker.sock🐙🔥

`/var/run/docker.sock` をコンテナに渡すと、Dockerを操作できてしまいがちで危険度が跳ね上がります📈
Dockerの強化機能（ECI）でも、**docker.sockのbind mountは「Docker Engineを制御できてしまう」のでデフォルトでブロックする**と明記されています。([Docker Documentation][5])

> 覚え方：「docker.sock＝だいたい最強権限」🧟‍♂️💥
> 必要になったら、この教材の後半で“隔離専用”の考え方で扱います🙂

---

## 原則③：最小公開（見える範囲を削る）🌐✂️🚪

## 1) `ports:` は“公開”、`expose:` は“内部向け”📌

![Ports vs Expose](./picture/docker_safe_isolation_ts_study_003_06_ports_vs_expose.png)

Composeでは次のイメージでOKです👇

* `ports:` → **ホスト側に公開する**（外から来れる入口になる）🚪
* `expose:` → **同じネットワーク内のサービス向け**（ホストには公開しない）🏠

Composeのサービス定義でも `expose` は「ホストにpublishすべきではない」「内部ポートのみ」と説明されています。([Docker Documentation][4])

---

## 2) 公開するなら“入口だけ”＆“localhost限定”🏠🔒

Web/APIだけ公開して、DBは公開しない（内部だけ）🍱✨
そして公開するなら、できれば `127.0.0.1` で縛るのが強いです💪
Docker公式のポート公開ページでも「公開はデフォルトで危険寄り」「localhost IPを付けるとホストだけ」と説明されています。([Docker Documentation][2])

**例：APIはlocalhost限定、DBは公開しない**

```yaml
services:
  api:
    ports:
      - "127.0.0.1:3000:3000"

  db:
    # ports: は書かない（＝ホストに公開しない）
    expose:
      - "5432"
```

---

## まとめ：3原則を“1分レビュー”にする✅⏱️🤖

![Security Review Checklist](./picture/docker_safe_isolation_ts_study_003_07_review_checklist.png)

AI拡張（コード提案）を使うと爆速で進む反面、**危険な設定も平気で混ざる**ことがあります😇💥
そこで、提案をコピペする前にこの“1分レビュー”を挟みます👇

## ✅ 1分レビュー（コピペ前に見るやつ）

* **最小権限**👤

  * `user:` ある？ rootで動いてない？
  * `privileged: true` になってない？（なってたら赤信号🚨）
  * capを雑に増やしてない？（`cap_add: ALL` とか🧨）

* **最小共有**📦

  * 共有フォルダ広すぎない？（`.:/app` とかは要注意）
  * roにできるところはro？
  * `docker.sock` 渡してない？（渡してたら理由を100回確認🐙🔥）

* **最小公開**🌐

  * `ports:` が増えてない？
  * DB/Redisまで公開してない？
  * 公開するなら `127.0.0.1` で縛れる？🏠

---

## ミニ演習🧪✨（“危険→安全”を体で覚える）

## 演習1：ポート公開の被害半径を縮める🚪➡️🏠

1. `ports: - "3000:3000"` で起動
2. 次に `ports: - "127.0.0.1:3000:3000"` に変更
3. どっちが“外に開く可能性が高い”か、理由を言えるようにする🗣️💡

   * ヒント：公式に「公開はデフォルトで危険寄り」「localhostを付けるとホストだけ」って書いてあります📚([Docker Documentation][2])

## 演習2：共有を“ro + 専用rw”に分ける📁🔒🧺

1. コード共有を `read_only: true` にする
2. ログや一時ファイルは `tmpfs` か named volume に逃がす
3. 「書き込みが必要な場所を限定できた？」を確認👀✅

---

## この章の“持ち帰りテンプレ”📦🎁

最後に、3原則を最初から入れた“素の型”を置いておきます😊
（次章以降で、ここに例外だけ足していく感じです✨）

```yaml
services:
  api:
    image: my-api
    user: "node"
    read_only: true
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    ports:
      - "127.0.0.1:3000:3000"
    volumes:
      - type: bind
        source: .
        target: /app
        read_only: true
      - type: volume
        source: api-tmp
        target: /app/tmp

  db:
    image: postgres:18
    # ports: は書かない（ホストに公開しない）
    expose:
      - "5432"
    volumes:
      - db-data:/var/lib/postgresql/data

volumes:
  api-tmp:
  db-data:
```

> `read_only` / `user` / `ports` / `expose` / `security_opt` などは、Composeサービス定義の属性として整理されています。([Docker Documentation][4])

---

次は第4章の「安全デフォルトの作り方（テンプレ→例外だけ追加）」で、この章の3原則を“毎回自動で効く仕組み”にしていきます📦✨
必要なら、この章のテンプレをあなたの教材用プロジェクト（Node + 何か）に合わせて、もう少し現実寄りに調整した版も作れます😄🔧

[1]: https://csrc.nist.gov/glossary/term/least_privilege?utm_source=chatgpt.com "least privilege - Glossary - NIST CSRC"
[2]: https://docs.docker.com/engine/network/port-publishing/?utm_source=chatgpt.com "Port publishing and mapping"
[3]: https://docs.docker.com/engine/security/?utm_source=chatgpt.com "Docker Engine security"
[4]: https://docs.docker.com/reference/compose-file/services/ "Services | Docker Docs"
[5]: https://docs.docker.com/enterprise/security/hardened-desktop/enhanced-container-isolation/?utm_source=chatgpt.com "Enhanced Container Isolation"
