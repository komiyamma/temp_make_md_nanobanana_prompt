# 第11章：USERでroot回避：Nodeアプリを“普通ユーザー”で走らせる🙂👟

この章はひとことで言うと、**「コンテナの中でも “rootで動かさない” をデフォルトにしよう」**です😄
やることはシンプルなのに、事故った時の被害がかなり減ります🛡️✨

---

## まず結論：最低限これだけやる😊✅

* Dockerfileの最後のほうで **`USER nodejs`**（非root）にする
* **アプリが書き込むフォルダだけ**、そのユーザーに書けるようにしておく📁✍️
* `COPY --chown=...` を使って「コピーしたファイルの所有者」も揃える📦👤

これが “安全デフォルト” の第一歩です🚶‍♂️🔒
（Docker公式のビルド・ベストプラクティスでも、権限が要らないなら `USER` で非rootにしようと明記されています）([Docker Documentation][1])

---

## なぜrootが怖いの？😇💣（超ざっくり）

Dockerコンテナは「隔離されてるから安全！」と思いがちですが、**rootで動かす**と次の問題が起きやすいです👇

* アプリの脆弱性（RCEとか）で侵入された時、**コンテナ内で何でもできる権限**を渡しがち😱
* もし「マウント」「設定ミス」「別の脆弱性」が重なると、**被害がホスト側に波及**するルートが増えます🔥
* とくに「書き込みできる場所」が広いほど、改ざん・設置・破壊がラクになります🧨

Docker公式も「コンテナはデフォルトroot（UID 0）で動くから、非rootにしよう」「UID/GID指定も有効」と説明しています([Docker][2])

---

## 図でイメージ：root回避は“被害半径”を縮める🗺️✂️

```
[攻撃者がアプリを乗っ取った…] 😈
        |
        v
(コンテナ内プロセスの権限で) できることが決まる

rootで実行： できること多い😱  → 事故がデカくなりがち
一般ユーザー：できること少なめ🙂 → 事故を小さくしやすい
```

---

## 実践1：まず「今rootで動いてる」を確認しよう👀🔍

コンテナに入って、これを打ちます👇

```bash
docker compose exec app sh -lc "id && whoami"
```

* `uid=0(root)` と出たら、**rootで実行中**です😇💥
* `uid=1001(nodejs)` みたいに出たら、**非rootで実行中**です🙂✅

---

## 実践2：Node + TypeScriptの “非rootデフォルト” Dockerfile（鉄板構成）🧱✨

Docker公式のNodeガイド（最近更新）でも、**専用ユーザーを作って `USER` で切り替える**例が載っています([Docker Documentation][3])
ここでは「超よく使う形」にギュッとまとめます✂️😄

## 例：最小構成（まずは理解用）📦

```dockerfile
FROM node:24-alpine

WORKDIR /app

## 非rootユーザーを作る（例：uid=1001）
RUN addgroup -g 1001 -S nodejs \
  && adduser  -S nodejs -u 1001 -G nodejs \
  && chown -R nodejs:nodejs /app

## 依存ファイル → 先にコピー（キャッシュが効く）
COPY package*.json ./

## 依存インストール（ここはrootのままでもOK）
RUN npm ci

## アプリ本体をコピー（所有者も揃える）
COPY --chown=nodejs:nodejs . .

## ここが主役：非rootで実行！
USER nodejs

EXPOSE 3000
CMD ["npm", "run", "dev"]
```

ポイントは3つだけ🙂👇

1. **`/app` を `nodejs` が書ける**ようにしてる（`chown`）📁
2. `COPY --chown=...` で、**コピー後の所有者ズレ**を防ぐ📦
3. 最後に `USER nodejs` で、**実行時は非root**👟

---

## 実践3：本番寄り（マルチステージ）で “最後だけ非root” を徹底🏗️🔒

本番は「ビルドは重い・実行は軽い」に分けたいので、こうなりがちです😊
（Docker公式Nodeガイドでも、ステージごとにユーザー作成→ `USER` 切り替え例があります）([Docker Documentation][3])

## 例：productionステージで確実に非root化🧰

```dockerfile
## =========================
## build stage
## =========================
FROM node:24-alpine AS build
WORKDIR /app

COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

## =========================
## runtime stage
## =========================
FROM node:24-alpine AS runtime
WORKDIR /app

## 非rootユーザー作成
RUN addgroup -g 1001 -S nodejs \
  && adduser  -S nodejs -u 1001 -G nodejs \
  && chown -R nodejs:nodejs /app

## 実行に必要なものだけコピー（所有者も揃える）
COPY --from=build --chown=nodejs:nodejs /app/dist ./dist
COPY --from=build --chown=nodejs:nodejs /app/package*.json ./
COPY --from=build --chown=nodejs:nodejs /app/node_modules ./node_modules

## 実行は非root！
USER nodejs

EXPOSE 3000
CMD ["node", "dist/server.js"]
```

---

## 実践4：Compose側で user を上書きできる（でも“保険”扱い）🧯

Composeには `user:` があって、**「コンテナの実行ユーザーを上書き」**できます。
ただし **基本はイメージ（Dockerfileの `USER`）で安全デフォルトにしておく**のが王道です🙂

Docker公式Composeリファレンスでも「`user` は実行ユーザーを上書き。デフォルトはイメージ（Dockerfile `USER`）で、未指定ならroot」と説明されています([Docker Documentation][4])

## 例：開発だけ user を固定したい場合

```yaml
services:
  app:
    build: .
    user: "1001:1001"
```

---

## よくある詰まりポイント集（ここが一番大事）🧨🛠️

## 1) `EACCES: permission denied` が出る😵

だいたいこれ👇

* `/app` や `node_modules` や `.cache` に書こうとしてるのに、所有者がrootのまま
* `COPY . .` のせいで、ファイルがroot所有になってる

対策🙂✅

* `COPY --chown=nodejs:nodejs ...` を使う
* `RUN chown -R nodejs:nodejs /app` を「最後に一回」入れる（雑に解決しやすい）
* それでもダメなら「どこに書こうとしてるか」をログで特定して、書き込み場所を絞る（次章でガッツリやる）📁🔍

---

## 2) `npm` がキャッシュ書けなくて死ぬ😇

非rootだと、`npm` が触りたい場所に権限がなくてコケることがあります。

対策の方向性🙂

* キャッシュや一時ファイルは **`/tmp`** など “書いていい場所” に寄せる
* もしくは、必要なディレクトリだけ `nodejs` が書けるように作っておく

（書き込み場所の設計は次章の主役です🧺🗂️）

---

## 3) 80番ポートで待ち受けしたい（でも非rootだと無理）🤔

Linuxでは **1024未満のポートは基本rootが必要**になりがちです。

でも安心🙂

* コンテナ内は **3000** で待ち受け
* 外側で `-p 80:3000` みたいにマッピングすればOK（入口だけ80）🚪✨
* もしくはリバースプロキシを前に置く（第26章〜で出るやつ）🕸️

---

## 4) 「じゃあ `chmod -R 777` で良くない？」😇💥

それは最後の最後！
777は「誰でも何でも書ける」になって、**root回避の意味が薄れます**🥲

* “書ける場所” を最小にする
* それ以外は読めるだけに近づける

この方向が、隔離ロードマップの思想に合ってます🙂🔒

---

## AI拡張（GitHub Copilot / OpenAI Codex）を使う時の「レビュー観点」🤖🧠✅

AIにDockerfileを書かせると、**`USER` が抜ける**ことが結構あります😂
なので、生成物を見たらここだけは必ずチェック！👀

* `USER nodejs` が **最終ステージ（実行ステージ）にある？**
* ユーザー作成（`adduser`/`useradd`）がある？
* `/app` の所有者が揃ってる？（`chown` or `COPY --chown`）
* 変な “万能権限” を付けてない？（777、`sudo`導入、など）
* ついでに：秘密をDockerfileに直書きしてない？（次のSecrets章で本格的にやるやつ）🔑💥

---

## 章末ミニ演習🎓✨（15分でできる）

## 演習A：root→非rootの差を体験する🙂↔️😱

1. `whoami` / `id` を確認
2. `/root/test.txt` に書こうとして失敗するのを確認（非rootだと当然）
3. `/app/tmp.txt` に書けるように `/app` の権限を整える
4. 最終的に「アプリが必要な場所だけ書ける」状態にする✅

## 演習B：事故の芽を潰す（Dockerfileレビューごっこ）🕵️‍♂️🔎

AIに「Node+TSのDockerfile作って」と頼む → その出力を見て

* `USER` がないなら追加
* `COPY --chown` がないなら追加
* `chmod 777` があったら削除
  …まで直せたら勝ち🏆😄

---

## まとめ🎉

* **rootで動かさない**だけで、被害半径がかなり縮む🙂✂️
* やることは `USER` と **書き込み場所の整理**が中心📁
* Composeの `user:` は便利だけど、まずは **Dockerfileで安全デフォルト**が王道🧱
* AI時代は「`USER` が入ってるか」をレビューの最優先項目にしよう🤖✅

次章（第12章）は、この章で出てきた **“書き込み場所どこにする問題”** を、初心者でも迷わない形に設計していきます🧺🗂️✨

[1]: https://docs.docker.com/build/building/best-practices/?utm_source=chatgpt.com "Building best practices"
[2]: https://www.docker.com/blog/understanding-the-docker-user-instruction/?utm_source=chatgpt.com "Understanding the Docker USER Instruction"
[3]: https://docs.docker.com/guides/nodejs/containerize/ "Containerize | Docker Docs"
[4]: https://docs.docker.com/reference/compose-file/services/ "Services | Docker Docs"
