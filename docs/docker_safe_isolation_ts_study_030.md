# 第30章：最終成果：安全デフォルト・テンプレ完成🎉📦 + 自己点検チェック✅

この章は **「次の新規PJで毎回コピペして使える、安全寄りテンプレ」を完成**させる回だよ〜！😄✨
ゴールは2つ👇

* **① 安全デフォルトのテンプレ一式（Compose / Dockerfile / 運用ルール）を完成**🎁
* **② 5分セルフ監査で、やらかし（秘密漏れ・踏み台・誤爆）を毎回潰す**🕔🔍✅

---

## 30.1 完成イメージ（“被害半径”が小さい構造）🗺️🔒

ざっくり、こういう形に固定します👇

* 公開するのは **入口（app）だけ**🚪
* DB/Redisは **内部ネットワークに閉じ込め**🍱
* 秘密は **env直書き禁止 → secretsでファイル注入**🔑
* ビルド時の秘密も **BuildKit secretsで一時注入**🏗️🤫
* AI拡張は **「見せていい範囲」をテンプレ側で作る**🤖🧱

（Docker Composeのsecretsは `/run/secrets/<secret_name>` に**ファイルとしてマウント**され、サービス単位で明示的に渡したものだけが見える設計だよ📄🔐）([Docker Documentation][1])

---

## 30.2 テンプレのフォルダ構成📁✨

こんな構成で固定しちゃうのがラクです👇

* `compose.yaml`（本命テンプレ）
* `Dockerfile`（本命テンプレ）
* `.dockerignore`（秘密やゴミをビルドに入れない）
* `.env.example`（秘密じゃない設定だけ）
* `secrets/`（ローカル専用。必ずgitignore対象）🔒
* `docs/SECURITY_CHECK.md`（5分監査チェック表📝）

---

## 30.3 安全デフォルトの `compose.yaml`（コピペして育てる🌱📦）

ポイントは **「公開・共有・権限・秘密・AI」** が最小になってること！✂️🔐🤖

```yaml
services:
  app:
    build:
      context: .
      secrets:
        - npm_token  # ビルド時だけ使う（例：private npm）
    ports:
      # 入口だけ公開。しかも localhost に縛る（LANへ撒かない）🧯
      - "127.0.0.1:3000:3000"
    environment:
      NODE_ENV: production
      DB_HOST: db
      DB_USER: app
      DB_NAME: appdb

      # 秘密は「値」じゃなく「ファイルの場所」を渡す📄🔐
      DB_PASSWORD_FILE: /run/secrets/db_password
      SESSION_KEY_FILE: /run/secrets/session_key

    secrets:
      - db_password
      - session_key

    depends_on:
      db:
        condition: service_healthy

    networks:
      - front
      - back

    # ===== 権限を削る（安全寄りの標準装備）🛡️ =====
    user: "node"                 # rootで動かさない🙂
    read_only: true              # ルートFSは基本読取専用📖
    tmpfs:
      - /tmp                     # 書ける場所はここに寄せる🧊
    security_opt:
      - no-new-privileges:true   # 途中で権限が増えない🧱
    cap_drop:
      - ALL                      # 権限は全部落としてスタート✂️
    init: true                   # ゾンビプロセス対策（地味に大事）🧹

    # 書き込みが必要な場所だけ「専用」にする✅
    volumes:
      - app_uploads:/app/uploads

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: app
      POSTGRES_DB: appdb
      # postgres公式イメージは *_FILE で secret ファイルを読める慣習があるよ🔐
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password
    networks:
      - back
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d appdb"]
      interval: 5s
      timeout: 3s
      retries: 20

  redis:
    image: redis:7-alpine
    networks:
      - back
    command: ["redis-server", "--appendonly", "yes"]
    volumes:
      - redisdata:/data

  # ===== AIや自動化で「コマンド実行させたい」時の避難所（任意）🤖🧯 =====
  tools:
    profiles: ["tools"]
    image: node:22-alpine
    working_dir: /work
    # リポジトリは「読取専用」で渡す（壊せない）📎🔒
    volumes:
      - ./:/work:ro
      - tools_tmp:/tmp
    read_only: true
    tmpfs:
      - /tmp
    network_mode: "none"         # 外に出られない（流出しにくい）🚫🌐
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    user: "node"
    command: ["node", "--version"]

secrets:
  db_password:
    file: ./secrets/db_password.txt
  session_key:
    file: ./secrets/session_key.txt

  # ビルド時だけ使うsecret：環境変数から注入（例）🏗️🤫
  npm_token:
    environment: NPM_TOKEN

networks:
  front: {}
  back:
    internal: true  # 外部と遮断したネットワークにできる🔒

volumes:
  pgdata: {}
  redisdata: {}
  app_uploads: {}
  tools_tmp: {}
```

* secretsが `/run/secrets/...` に**ファイルで入る**こと、env直入れより漏れにくい理由（ログに出たりしやすい等）は公式が明言してるよ📚([Docker Documentation][1])
* `internal: true` は **外部接続を遮断したネットワークを作れる**（=閉じ込めに使える）よ🔒([Docker Documentation][2])
* `build: secrets:` で **ビルド時だけ** secret を使う書き方も公式の例があるよ🏗️([Docker Documentation][1])

---

## 30.4 `Dockerfile`（BuildKit secretsで“ビルド中だけ見える”🏗️🤫）

BuildKitのsecret mountは「ビルド命令の間だけ一時的に見える」設計。private依存を取る時に便利！([Docker Documentation][3])

```dockerfile
## syntax=docker/dockerfile:1
FROM node:22-alpine AS deps
WORKDIR /app

## 依存関係だけ先にコピー（キャッシュ効かせる）⚡
COPY package*.json ./

## 例：private npm を使う場合だけ token を build secret で渡す
## secret は /run/secrets/<id> にデフォルトでマウントされる📄
## （ビルド命令の間だけ一時的に利用できる）:contentReference[oaicite:5]{index=5}
RUN --mount=type=secret,id=npm_token \
    sh -lc 'if [ -f /run/secrets/npm_token ]; then \
      echo "//registry.npmjs.org/:_authToken=$(cat /run/secrets/npm_token)" > .npmrc; \
    fi; \
    npm ci; \
    rm -f .npmrc'

COPY . .
RUN npm run build

FROM node:22-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production

## 実行に必要なものだけ持ってくる（小さく・安全に）📦
COPY --from=deps /app/dist ./dist
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/package*.json ./

USER node
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

---

## 30.5 TypeScript側：secretを読む“最小パターン”🔑📄

「DBパスワード文字列」じゃなくて、**“ファイルパス”を環境変数で受けて読む**のがコツ！🙂

```ts
import { readFile } from "node:fs/promises";

async function readSecret(pathEnv: string): Promise<string> {
  const p = process.env[pathEnv];
  if (!p) throw new Error(`Missing env: ${pathEnv}`);
  return (await readFile(p, "utf8")).trim();
}

export const secrets = {
  dbPassword: await readSecret("DB_PASSWORD_FILE"),
  sessionKey: await readSecret("SESSION_KEY_FILE"),
};
```

---

## 30.6 VS Codeでの作業手順（最短）🧑‍💻✨

1. `secrets/` を作って、以下2ファイルを作成✍️

* `secrets/db_password.txt`
* `secrets/session_key.txt`

2. `.dockerignore` と `.gitignore` を用意🧯

```gitignore
secrets/
.env
```

```dockerignore
secrets/
.env
node_modules
dist
.git
```

3. 起動（ターミナルで）🚀

```bash
docker compose up -d --build
```

4. 動作確認👀

```bash
docker compose ps
docker compose logs -f app
```

---

## 30.7 5分セルフ監査（毎回これだけ✅🕔）

チェックは **Yesが並んだら勝ち**🏆✨

## A. 権限（Privilege）🧤✂️

* [ ] `privileged: true` が無い
* [ ] `docker.sock` をマウントしてない
* [ ] `user: root` になってない（`USER`/`user:` がある）
* [ ] `cap_drop: [ALL]` + `no-new-privileges:true` が入ってる
* [ ] `read_only: true` になってる（書く場所は volume/tmpfs に分離）

## B. 共有（Share / Mount）📎🗂️

* [ ] bind mount（`.:/work` 等）を“必要最小限”にした
* [ ] できる場所は `:ro`（読取専用）にした
* [ ] 書き込みは「専用volume」だけ（`/app/uploads` 等）

## C. 公開（Expose）🚪🌐

* [ ] `ports:` は **入口の1つだけ**
* [ ] `127.0.0.1:` でローカルに縛ってる
* [ ] DB/Redisに `ports:` が無い
* [ ] 内部ネットワーク `internal: true` を使って閉じ込めてる([Docker Documentation][2])

## D. 秘密（Secrets）🔑🫣

* [ ] パスワード/APIキーを `environment:` に直書きしてない
* [ ] `/run/secrets/...` で受けてる（サービス単位で付与）([Docker Documentation][1])
* [ ] ビルド時の秘密も `build: secrets:` / BuildKit secret mount に寄せてる([Docker Documentation][1])
* [ ] `secrets/` はgitに入ってない（絶対）🚫

## E. AI（Prompt Injection / AI拡張）🤖⚠️

* [ ] AIに見せる範囲から `secrets/` を外してる（“見える場所”を減らす）
* [ ] 外部のIssue/PR/README等の文章は **“信用しない”**（混入指示があり得る）
* [ ] AIがコマンド実行する系は、できれば `tools` サービス（ネット無し・読取専用）でやる

  * 間接プロンプト注入で **トークン露出・機密ファイル露出・任意コード実行**に繋がり得る、という指摘があるよ🧨([The GitHub Blog][4])
  * “サンドボックス（例：Dockerコンテナ等）”を防御層にする話も出てる🧱([The GitHub Blog][4])

---

## 30.8 演習（テンプレを“自分のもの”にする💪😆）

## 演習1：DBが外から見えないのを確認🔍

* いまの構成だとDBは `ports:` なし＝外部から直アクセスしづらい👍
* わざと `db` に `ports: "5432:5432"` を追加して、**何が起きるか**を体験→すぐ戻す🧯

## 演習2：secretsが「必要なサービスだけ見える」を体験🔐

* `redis` に `db_password` を渡してない状態でOK
* 逆に渡しちゃうと「被害半径が増える」感覚を掴む🗺️

## 演習3：AI用避難所（tools）を使ってみる🤖🧯

* `tools` はネット無し＆読取専用なので、AIが提案したコマンドを“安全寄り”に試せる

```bash
docker compose --profile tools run --rm tools sh
```

---

## 30.9 よくある詰まりポイント（ここで沼る😵‍💫）

* **read_onlyにしたら落ちる**
  → アプリが書く場所（uploads, tmp, cache）を洗い出して、**volume/tmpfsに逃がす**✅
* **DB接続でパスワードが空っぽ**
  → `DB_PASSWORD_FILE` のパスが合ってるか、secretがappサービスに付与されてるか確認👀
* **private npmが取れない**
  → `NPM_TOKEN` が環境変数としてセットされてるか、`build: secrets:` が効いてるか確認🔍([Docker Documentation][1])

---

ここまでできたら、もう **新規PJはこのテンプレからしか始めない**でOK！🎉📦
次の章（もし作るなら）は、このテンプレを **「Next.js版」「API+Worker版」「DBなし版」**みたいに“派生テンプレ集”にしていくと最強だよ😆✨

[1]: https://docs.docker.com/compose/how-tos/use-secrets/ "Secrets in Compose | Docker Docs"
[2]: https://docs.docker.com/reference/compose-file/networks/ "Networks | Docker Docs"
[3]: https://docs.docker.com/build/building/secrets/ "Secrets | Docker Docs"
[4]: https://github.blog/security/vulnerability-research/safeguarding-vs-code-against-prompt-injections/ "Safeguarding VS Code against prompt injections - The GitHub Blog"
