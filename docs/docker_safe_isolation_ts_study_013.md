# 第13章：read-only root filesystem：基本は読めるだけ📖🔒

この章では、「コンテナの中の“基本の床”は書き込み禁止にしよう！」という強力な守り方をマスターします 💪
一言でいうと **“改ざん・永続化・事故の被害半径” を小さくする** ための定番テクです 🧯

---

## 1) まず超ざっくり理解しよう🧠💡

![Root FS Layers](./picture/docker_safe_isolation_ts_study_013_01_layers.png)

## ✅ root filesystem ってどこ？

コンテナには大きく2種類の“置き場所”があります。

* **root filesystem（ルートFS）**：イメージに入ってるOSやアプリの本体（`/` 配下ぜんぶ）
* **マウント（volume / bind / tmpfs）**：あとから“ここだけ別の置き場所”として差し込む領域

イメージの上に「書き込み用の薄い層」が乗っていて、通常はそこに色々書けます。
でも **read-only にすると、その“書き込み層”を封鎖**します 🔒

---

## 2) 何が嬉しいの？（効き方をイメージ）🛡️😈➡️😇

![Read-Only Protection](./picture/docker_safe_isolation_ts_study_013_02_protection.png)

## ✅ よくある事故の被害を減らす

* 攻撃者やマルウェアが **勝手にバイナリや設定を書き換えにくい** 🧨➡️🧊
* アプリやAI拡張の“うっかり操作”で **OS側のファイルを壊しにくい** 🧯
* “一度書かれた改ざんファイルが残り続ける” を減らせる（永続化の阻止）🧹

もちろん **volume に書ける場所は書ける** ので、
「どこをvolumeにするか」もセットで設計します✍️

---

## 3) どうやって有効化するの？（Docker / Compose）⚙️✨

![Compose Read-Only Config](./picture/docker_safe_isolation_ts_study_013_03_compose_syntax.png)

## A. docker run の場合

`--read-only` を付けると、root filesystem が読み取り専用になります。([Docker Documentation][1])

* **重要ポイント**：書けるのは **指定したvolume等だけ**になります。([Docker Documentation][1])

## B. Compose の場合（おすすめ）

Compose ではサービスに `read_only: true` を書くだけです。
これは「サービスコンテナを read-only filesystem で作る」設定です。([Docker Documentation][2])

さらに、**一時書き込み用**に `tmpfs` を付けられます（メモリ上の一時領域）🧊
Compose の `tmpfs` は `<path>` や `<path>:<options>` 形式で書けます。([Docker Documentation][2])

`tmpfs` 自体の思想は「永続化したくない一時データ向け」で、セキュリティ面でも有用です。([Docker Documentation][3])
（※Docker的には Linux の tmpfs 機能に紐づきます。([Docker Documentation][3])）

---

## 4) “ありがちに詰まる”ポイント先読み👀💥

![Write Pitfalls](./picture/docker_safe_isolation_ts_study_013_04_pitfall_map.png)

read-only を有効化すると、こういうエラーに出会います👇

* `EROFS: read-only file system`（そこ書けないよ！）
* `EACCES: permission denied`（権限がないよ！）

原因はだいたいこれ👇

1. **アプリが /tmp 以外に一時ファイルを書こうとしてる**
2. **ログを /var/log などに吐こうとしてる**
3. **キャッシュを /root や /home/node 直下に作ろうとしてる**
4. **起動時スクリプトが /etc を書き換えるタイプのイメージ**（意外とある）😇💣

対策は超シンプルで、設計の基本はこれです👇

> 🧩「書いていい場所を“専用のマウント”として用意し、それ以外は書けない」

---

## 5) ハンズオン：TypeScript + Node を read-only 化して動かす🎮🧪

ここでは **“本体は不変（read-only）”** にして、
**書く場所は `/data`（永続）と `/tmp`（一時）だけ**にします ✨

## ステップ0：Node のバージョン感（2026年2月時点）🧭

2026-02 時点で **Node v24 が Active LTS**、v25 は Current です。([nodejs.org][4])
本番寄りの例では LTS（v24系）を使うのが無難、という前提で進めます🙂

---

## ステップ1：最小アプリ（/data に書く & /tmp を使う）🗂️🧊

![Hands-on Architecture](./picture/docker_safe_isolation_ts_study_013_05_handson_arch.png)

```ts
// src/index.ts
import express from "express";
import fs from "node:fs/promises";
import path from "node:path";
import os from "node:os";

const app = express();
app.use(express.json());

const DATA_DIR = process.env.DATA_DIR ?? "/data";

app.get("/health", (_req, res) => res.json({ ok: true }));

app.post("/memo", async (req, res) => {
  const text = String(req.body?.text ?? "");
  await fs.mkdir(DATA_DIR, { recursive: true });

  // 永続保存（ここだけ書いてOKにする）
  const file = path.join(DATA_DIR, "memo.txt");
  await fs.writeFile(file, text + "\n", { flag: "a" });

  // 一時ファイル（tmpfsでOKにする）
  const tmpFile = path.join(os.tmpdir(), `memo-${Date.now()}.tmp`);
  await fs.writeFile(tmpFile, "temp");
  await fs.unlink(tmpFile);

  res.json({ saved: true, file });
});

app.listen(3000, () => console.log("listening on :3000"));
```

---

## ステップ2：Dockerfile（ビルドは別ステージ、実行は軽く）🏗️➡️🚀

```dockerfile
## Dockerfile
FROM node:24-slim AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY tsconfig.json ./
COPY src ./src
RUN npm run build

FROM node:24-slim AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY package*.json ./
RUN npm ci --omit=dev
COPY --from=build /app/dist ./dist

## 実行ユーザーはイメージ側の慣習に合わせてもOK（ここでは省略）
CMD ["node", "dist/index.js"]
```

---

## ステップ3：Compose（ここが本題！read_only + tmpfs + data volume）🧩🔒

```yaml
## compose.yaml
services:
  api:
    build: .
    ports:
      - "3000:3000"

    # ✅ ルートFSを読み取り専用にする
    read_only: true

    # ✅ 一時書き込み場所（/tmp）を tmpfs で用意
    # options には mode/uid/gid などが使える
    tmpfs:
      - /tmp:mode=1777

    # ✅ 永続書き込み場所（/data）だけを volume として許可
    volumes:
      - type: volume
        source: api-data
        target: /data

volumes:
  api-data:
```

* `read_only` はサービスを read-only filesystem で作る設定です。([Docker Documentation][2])
* `tmpfs` は一時ファイル用の“メモリ上の領域”をマウントできます。([Docker Documentation][2])
* `tmpfs mounts` は「永続化したくない一時データ向け」という説明が公式にあります。([Docker Documentation][3])

---

## ステップ4：起動して確認✅🎉

1. `docker compose up --build`
2. 別ターミナルで

   * `curl http://localhost:3000/health`
   * `curl -X POST http://localhost:3000/memo -H "Content-Type: application/json" -d "{\"text\":\"hello\"}"`

---

## 6) わざと壊して学ぶ（超おすすめ）😈➡️🧠

## 課題A：/app に書こうとして落ちるのを体験💥

![EROFS Error](./picture/docker_safe_isolation_ts_study_013_06_erofs_error.png)

さっきのコードにこれを追加👇

```ts
await fs.writeFile("/app/try.txt", "nope");
```

→ `read_only: true` なので高確率で `EROFS` になります。
**“アプリ本体の場所に書く設計”が即バレる**のが気持ちいいポイントです😆🔒

---

## 課題B：/tmp を tmpfs で用意しないとどうなる？🧊❌

Composeから `tmpfs:` を消すと、環境によっては `/tmp` に書けなくて死ぬケースが出ます。
（イメージやアプリの挙動で差が出るので、体験しておくと強い💪）

---

## 7) 実務での“設計テンプレ”（最短で強くなるやつ）📦✨

![3-Part Design Template](./picture/docker_safe_isolation_ts_study_013_07_design_template.png)

## 🥇鉄板の分け方

* **読めるだけ（root filesystem）**：OS、ライブラリ、アプリ本体（不変）
* **一時だけ（tmpfs）**：`/tmp`（必要なら `/run` やアプリ専用tmp）
* **永続だけ（volume）**：`/data`（アップロード、DBファイル、永続ログなど）

## 🧷「volume自体も read-only」にできる（必要なとき）

Composeのマウント定義には `read_only` フラグがあります。([Docker Documentation][2])
たとえば設定ファイルは bind mount で `read_only: true` にして固める…みたいな運用ができます🙂

---

## 8) よくある詰まりどころQ&A🧯😵

## Q1. 「ログを /var/log に書けなくて落ちる」😭

A. まずは **ログの出し先を stdout/stderr に寄せる**のが王道です（Docker的にも運用しやすい）。
どうしてもファイルが必要なら **`/var/log/app` だけ tmpfs or volume** にします🧩

---

## Q2. 「キャッシュをホームディレクトリに作ろうとして死ぬ」😇

A. 対策は2つ：

* キャッシュを切る（プロダクションで不要なら最高）
* キャッシュ用のディレクトリだけ volume/tmpfs で渡す（例：`/cache`）

---

## Q3. 「Windows だと tmpfs ってどうなるの？」🪟🤔

A. コンテナが Linux で動いている限り（Docker Desktop + Linuxコンテナ運用）、**tmpfs の考え方でOK**です。
公式の tmpfs 説明は Linux カーネル機能に紐づく、と書かれています。([Docker Documentation][3])
（つまり“中身はLinux側の仕組み”だと思って扱えば迷いにくい👍）

---

## 9) 章末チェックリスト✅🔍（5分セルフ監査）

* [ ] `read_only: true` を付けた
* [ ] 書き込みが必要な場所は **/data などに集約**した
* [ ] 一時ファイル用に **/tmp を tmpfs** にした
* [ ] 「本体（/app や /etc）に書く」挙動がない
* [ ] “書ける場所”が増えると被害半径も増える、と意識できてる🧠🧯

---

## 10) まとめ🎁✨

read-only root filesystem は、**設定1個で世界が変わるレベルの強化**です 🔒🔥
でも本当のコツは「書ける場所を設計で“狭く決める”」こと👇

> 📌「書くならここ」以外は、**そもそも書けない**ようにする

次の章（capabilities）に行くと、さらに「できること」自体も削れて、守りが一段上がりますよ〜😄🧤✂️

[1]: https://docs.docker.com/reference/cli/docker/container/run/ "docker container run | Docker Docs"
[2]: https://docs.docker.com/reference/compose-file/services/ "Services | Docker Docs"
[3]: https://docs.docker.com/engine/storage/tmpfs/ "tmpfs mounts | Docker Docs"
[4]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
