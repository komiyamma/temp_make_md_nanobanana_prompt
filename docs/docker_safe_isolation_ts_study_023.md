# 第23章：ビルド時の秘密：BuildKit secretsで“レイヤに残さない”🏗️🤫

ビルドって、ざっくり言うと「手順（RUN/COPY…）のたびに“履歴とレイヤ”が積み上がる」世界です📚🧅
なので、秘密（トークンや鍵）を雑に置くと **あとから掘り返せる形で残りがち** 😱

この章のゴールはこれ👇

* ビルドに必要な秘密を、**ビルド中だけ** 使う（完成イメージに残さない）✨
* 「やりがち漏えいパターン」を避ける🧨
* Compose や CI（GitHub Actions）でも同じ発想で運用できるようにする🛡️

---

## 1) まず“何がダメか”を体感しよう🙅‍♂️💥

![Layer Persistence vs Secret Mount](./picture/docker_safe_isolation_ts_study_023_01_layer_vs_mount.png)

**ダメな考え方**：Dockerfile に秘密を置く／コマンドに埋める

* ファイルを COPY すると、そのファイルがレイヤに入る📦
* ARG/ENV に入れて、それを RUN で使うと、履歴やキャッシュに痕跡が残りやすい🕵️‍♂️

「秘密は“ビルド中だけ見える一時マウント”にする」が正解です✅
この“一時マウント”が **BuildKit の secret mount** です。
BuildKit では、秘密をビルドコンテナに **その RUN の間だけ** 一時的に置けます（2ステップ：コマンドで渡す→Dockerfile 側で使う）📌([Docker Documentation][1])

---

## 2) BuildKit secrets の基本ルール（超重要）🔑📏

![BuildKit Secret Rules](./picture/docker_safe_isolation_ts_study_023_02_three_rules.png)

**ルールA：秘密は RUN の中でだけ使う**

* Dockerfile では RUN に「mount=type=secret」を付けて使います。([Docker Documentation][1])

**ルールB：秘密は“ファイル”か“環境変数”として渡せる**

* 元データは「ファイル」でも「環境変数」でもOK。([Docker Documentation][1])
* ビルド中のコンテナ内では、既定で「/run/secrets/＜id＞」に見えます。([Docker Documentation][1])

**ルールC：秘密をログに出さない**

* うっかり表示（cat / echo / set -x）すると、その瞬間に漏れます🫣🧯

---

## 3) ハンズオン①：.npmrc（トークン）を“ビルド中だけ”使って npm install する📦🤫

「プライベートパッケージ取得」って、個人開発でも一番漏れやすいポイントです😵
ここを BuildKit secrets で安全にします✨

### 手順 1：秘密ファイルをリポジトリ外扱いにする🗂️🙈

プロジェクト直下に `.secrets` を作って、そこに `.npmrc` を置く想定にします。

* `.secrets/.npmrc`（例：中身はトークンを含むので絶対コミットしない）

`.dockerignore` にも追加しておくと安心です🧯

```text
.secrets
```

### 手順 2：Dockerfile（秘密を一時マウントして npm ci）🧪

![Npmrc Secret Mount](./picture/docker_safe_isolation_ts_study_023_03_npmrc_mount.png)

ポイントは「npm ci を実行する RUN にだけ secret を付ける」です💡

```Dockerfile
## syntax=docker/dockerfile:1

## 1) 依存取得 + ビルド（dev依存も必要になりがち）
FROM node:24-alpine AS build
WORKDIR /app

COPY package*.json ./

## 秘密はこのRUNの間だけ /root/.npmrc として見せる（レイヤに残さない）
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc \
    npm ci

COPY . .
RUN npm run build

## 2) 本番用依存だけ（必要ならここでも秘密を“このRUNだけ”渡す）
FROM node:24-alpine AS prod-deps
WORKDIR /app
COPY package*.json ./
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc \
    npm ci --omit=dev

## 3) 実行用イメージ（秘密は一切不要）
FROM node:24-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production

COPY --from=prod-deps /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
COPY package.json ./

USER node
CMD ["node", "dist/index.js"]
```

* 「RUN の間だけ秘密が見える」仕組みが 핵です🔑([Docker Documentation][1])
* Node の現行 LTS 系は v24 が Active LTS 扱いなので、ベースに置くと無難です🧠（例として node:24 を使用）([nodejs.org][2])

### 手順 3：PowerShell でビルド（秘密を渡す）🪟⚡

![CLI Secret Command](./picture/docker_safe_isolation_ts_study_023_04_cli_secret_flow.png)

```powershell
docker build --secret id=npmrc,src=.secrets\.npmrc -t myapp:secure .
```

ここでやっている「秘密をビルドに渡す」操作が公式の基本形です📌([Docker Documentation][1])

### 手順 4：漏れてないかチェック（“完成品にない”を確認）🔍✅

```powershell
## /run/secrets が実行時に存在しない（=ビルド時限定だった）
docker run --rm myapp:secure sh -lc "ls -la /run/secrets || true"

## .npmrc が入ってない（念のため）
docker run --rm myapp:secure sh -lc "find / -maxdepth 4 -name .npmrc 2>/dev/null || true"
```

---

## 4) ハンズオン②：環境変数から secret を渡す（ファイルを作りたくない時）🌱🤫

![Environment Variable Secret](./picture/docker_safe_isolation_ts_study_023_05_env_secret.png)

BuildKit は secret の“元”を環境変数にもできます。([Docker Documentation][1])
例：API_TOKEN を secret として渡す（ビルド中は /run/secrets/API_TOKEN に見える）🧪

```powershell
$env:API_TOKEN = "********"
docker build --secret id=API_TOKEN -t myapp:envsecret .
```

Dockerfile 側は、必要な RUN にだけ付けます👇
（※表示しない！ログに出さない！🫣）

```Dockerfile
RUN --mount=type=secret,id=API_TOKEN \
    node -e "require('fs').readFileSync('/run/secrets/API_TOKEN'); console.log('ok')"
```

* 「環境変数→secret」の例も公式に載っています。([Docker Documentation][1])
* Dockerfile 側では `target`（ファイルの置き場変更）や `env`（環境変数として渡す）もできます。([Docker Documentation][1])

---

## 5) Compose から “ビルド用 secret” を渡す（チーム運用しやすい）🐳🧩

![Compose Build Secrets](./picture/docker_safe_isolation_ts_study_023_06_compose_build.png)

Compose には **build.secrets** という「このサービスのビルドにだけ秘密を許可する」仕組みがあります。([Docker Documentation][3])
短い書き方ならこんな感じ👇

```yaml
services:
  app:
    build:
      context: .
      secrets:
        - npmrc

secrets:
  npmrc:
    file: ./.secrets/.npmrc
```

* build.secrets は「サービスのビルド単位で、秘密のアクセス権を付ける」発想です🔐([Docker Documentation][3])
* Dockerfile では `RUN --mount=type=secret,id=npmrc,...` を使えばOKです。([Docker Documentation][3])

さらに「渡し忘れたら失敗してほしい」場合は `required=true` も使えます（Compose の例にも出てきます）🧨🧯([Docker Documentation][3])

---

## 6) CI（GitHub Actions）での secrets：仕組みは同じ🧪🤖

CI でも「ビルド中だけ secret を渡す」が基本です。
Docker の GitHub Actions 向けドキュメントでは、workflow から `secrets` 入力で BuildKit secret mount を渡す例が示されています。([Docker Documentation][4])

（ここで大事なのは「CI の secret を Dockerfile に埋めない」こと！🚫）

---

## 7) よくある落とし穴（ここ踏む人多い）🕳️😵‍💫

![Build Secret Pitfalls](./picture/docker_safe_isolation_ts_study_023_07_pitfalls.png)

* **秘密を COPY しちゃう** → レイヤに入って終わり📦💀
* **RUN の中で秘密をファイルに書き出して残す** → “残る”ので意味が薄い🧨
* **ログに出す（cat / echo / set -x）** → その場で漏れます🫣
* **必要ない RUN にまで secret を付ける** → 被害半径が広がる🗺️💥
* **AI が提案した「ARG で入れよう」を採用** → 便利そうに見えて危険なことが多い⚠️🤖
  👉 “secret mount で RUN の間だけ”に戻そう、が正解です✅([Docker Documentation][1])

---

## 8) 仕上げ：第23章チェックリスト✅🧾✨

* [ ] 秘密は Dockerfile に書いてない（COPY/ARG/ENV で焼き込んでない）🚫
* [ ] 秘密を使うのは「その RUN だけ」（mount=type=secret）🧪([Docker Documentation][1])
* [ ] ログに出してない（デバッグでも出さない）🫣
* [ ] `.secrets` は gitignore + dockerignore 済み🙈
* [ ] できれば `required=true` で渡し忘れを事故にしない🧯([Docker Documentation][3])
* [ ] 完成イメージ内に秘密が無いことを `find` 等で確認した🔍✅

---

次の章（第24章）が「private repo や社内パッケージ（SSH/トークン）」なので、
この第23章で作った“secret を一時マウントする型”がそのまま効いてきますよ〜！😄🔑✨

[1]: https://docs.docker.com/build/building/secrets/ "Secrets | Docker Docs"
[2]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[3]: https://docs.docker.com/reference/compose-file/build/ "Compose Build Specification | Docker Docs"
[4]: https://docs.docker.com/build/ci/github-actions/secrets/ "Build secrets | Docker Docs"
