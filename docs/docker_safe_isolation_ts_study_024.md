# 第24章：private repoや社内パッケージ：SSH/トークンを安全に使う🧷🔑

「社内ライブラリ（private repo）を `npm ci` で取ってきたい」「GitHub Packages / private npm レジストリから依存を入れたい」——この瞬間が、**秘密が漏れやすい最大の山場**です😵‍💫💥
ここを安全に越えるコツは一言でいうと👇

**✅ “ビルドに渡す。でもイメージに残さない”** 🔥

そのための主役が **BuildKit の SSH マウント / Secret マウント**です。([Docker Documentation][1])

---

## この章でできるようになること🎯✨

![Build Secret Concept](./picture/docker_safe_isolation_ts_study_024_01_pass_not_pack.png)

* private repo を **SSH鍵をイメージへコピーせず**にビルドできる🔐
* private npm レジストリのトークンを **レイヤ・ログ・履歴に残さず**に依存導入できる🫥
* 「どの認証を使うべき？」が選べるようになる（Deploy key / fine-grained PAT / CI用トークン）🧠
* AI拡張を使っていても、**秘密を巻き込まない手順**が作れる🤖🛡️

---

## 1) まず知っておく“事故り方”あるある😇💣

![Build Leak Accidents](./picture/docker_safe_isolation_ts_study_024_02_accident_patterns.png)

## 事故パターンA：Dockerfile にトークンを `ARG`/`ENV` で入れる

* `ARG NPM_TOKEN=...` とか `ENV` とかで渡すと、**ビルド履歴・キャッシュ・ログ**に残る可能性が出ます⚠️
* 「消したつもり」でも `docker history` などでバレることがあります🫣

## 事故パターンB：`.npmrc` や `~/.ssh` を `COPY` してしまう

* これはもう**漏れてください**って言ってるのに近いです😱
* さらに `.dockerignore` が甘いと、ビルドコンテキストに混入して事故率UP📦💥

## 事故パターンC：URLにトークン埋め込み（例：`https://TOKEN@...`）

* コマンド履歴・ログ・ツールの表示・AIへの貼り付けで漏れやすいです🧨

---

## 2) 正攻法マップ🗺️✨「これを使えば“残らない”】【本命】

![SSH vs Secret Mount](./picture/docker_safe_isolation_ts_study_024_03_auth_methods.png)

## 本命①：SSHエージェント転送（BuildKitの `RUN --mount=type=ssh`）🧑‍🚀🔐

* **秘密鍵ファイルをコンテナに入れない**
* “今このビルド中だけ” SSH を使えるようにする方式です。([Docker Documentation][2])

## 本命②：BuildKit secret（`RUN --mount=type=secret`）🤫🧪

* npmトークンや `.npmrc` を **そのRUN中だけ**見せる方式
* レイヤに残りにくい設計になっています。([Docker Documentation][1])

## Compose でもできる（`build.ssh`）🧩

* Compose 側でも “ビルド中に使うSSH” を指定できます。([Docker Documentation][3])

---

## 3) 認証の選び方（どれが一番安全？）🥇🔍

![Authentication Choice Guide](./picture/docker_safe_isolation_ts_study_024_04_auth_choice.png)

ここ、迷いがちなので “ざっくり優先順位” を置きます👇

## ✅ private repo を「読むだけ」なら：Deploy key（読み取り専用）🗝️📖

* リポジトリ単位で鍵を付けられて、**用途が限定**できるのが強い💪
* 「書き込み許可」は基本オフで運用するのが安心。([GitHub Docs][4])

## ✅ “人のトークン”を使うなら：fine-grained PAT（期限短め）⏳🔐

* GitHub は **classic PATより fine-grained を推奨**していて、リポジトリや権限を絞れます。([GitHub Docs][5])

## ✅ CI（GitHub Actions）なら：`GITHUB_TOKEN` を最小権限で🎛️🛡️

* 最小権限（例：`contents: read`）が基本、必要なときだけ増やすのが推奨です。([GitHub Docs][6])

## ✅ npm系（private packages）なら：CIは env + `.npmrc` が公式推奨🧾🔑

* npm公式は、CIでは **トークンを環境変数で持たせて `.npmrc` で使う**流れを説明しています。([npm ドキュメント][7])
* ただし **Dockerビルド中は BuildKit secret の方が安全設計に寄せやすい**です（後でやります）😎([Docker Documentation][1])

---

## 4) ハンズオン①：private repo を SSHで取ってきてビルドする🧪🐙

![SSH Mount Visualization](./picture/docker_safe_isolation_ts_study_024_05_ssh_mount.png)

> ゴール：`npm ci` が `git+ssh` 依存を含んでいても、**鍵をイメージに入れずに**ビルドできる✨

## (1) `.dockerignore` で「そもそも混入させない」🧹

まずは物理ガードです（超大事）🛡️

```gitignore
## secrets
.env
.npmrc
**/.npmrc
.ssh
**/.ssh

## node
node_modules
dist
```

## (2) Dockerfile（SSH が必要な RUN だけに `--mount=type=ssh`）🔐

例は Node の **Active LTS 系**（2026年2月時点だと v24 が Active LTS）を使う想定で書きます。([Node.js][8])

```dockerfile
## syntax=docker/dockerfile:1
FROM node:24-alpine AS deps
WORKDIR /app

## git + ssh クライアントだけ入れる
RUN apk add --no-cache git openssh-client

## 先に依存定義だけコピー（キャッシュ効かせる）
COPY package.json package-lock.json ./

## known_hosts を固定（対話プロンプト回避）
## ※安全のため本当は known_hosts を厳密に管理したいが、学習段階ではまず固定の考え方を掴む
RUN mkdir -p -m 700 /root/.ssh && \
    ssh-keyscan github.com >> /root/.ssh/known_hosts

## ここが肝：秘密鍵ファイルは入れず、SSHエージェントだけ借りる
RUN --mount=type=ssh npm ci

FROM node:24-alpine AS runner
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

CMD ["node", "src/index.js"]
```

* `# syntax=docker/dockerfile:1` は「最新の安定構文を使う」推奨の書き方です。([Docker Documentation][2])
* `RUN --mount=type=ssh` は Dockerfile の公式リファレンスにも載っています。([Docker Documentation][2])

## (3) ビルドコマンド（SSHエージェントを渡す）🚀

```bash
docker build --ssh default -t myapp:dev .
```

**ポイント**：この方式は「エージェントに入ってる鍵」を使うので、先に鍵をエージェントへ登録しておく必要があります🔑➡️🧠
（ここが詰まりポイントになりがち！後でまとめます）

---

## 5) ハンズオン②：private npm レジストリのトークンを“残さず”使う🧪🕵️‍♂️

![NPM Secret Mount](./picture/docker_safe_isolation_ts_study_024_06_npm_secret_mount.png)

> ゴール：`.npmrc` をイメージに残さず、トークンも残さずに `npm ci` する✨

## (A) BuildKit secret で `.npmrc` を “そのRUNだけ” 読ませる（おすすめ）🥇

BuildKit は **secret を渡して、Dockerfile 側で mount して使う**2段構えです。([Docker Documentation][1])

1. 手元に “ビルド専用 `.npmrc`” を用意（トークン直書きでもOKだが、扱い注意！）
   例（スコープやレジストリは自分の環境に合わせてね）👇

```ini
@my-scope:registry=https://registry.npmjs.org/
//registry.npmjs.org/:_authToken=REPLACE_ME
always-auth=true
```

2. ビルド時に secret として渡す👇

```bash
docker build --secret id=npmrc,src=.npmrc.build -t myapp:dev .
```

3. Dockerfile 側は、`npm ci` の行だけ secret mount する👇

```dockerfile
## syntax=docker/dockerfile:1
FROM node:24-alpine AS deps
WORKDIR /app

COPY package.json package-lock.json ./

RUN --mount=type=secret,id=npmrc,target=/root/.npmrc npm ci
```

* これで **`.npmrc` はその RUN でだけ見える**形に寄せられます🤫✨([Docker Documentation][1])

## (B) CI なら env + `.npmrc`（npm公式の基本パターン）🏭

npm公式は CI/CD で「トークンを環境変数に置き、プロジェクト `.npmrc` を使う」流れを説明しています。([npm ドキュメント][7])
また設定は `.npmrc` にトークンを置くのが一般的で、`npm login` で作るのが安全寄り、という注意もあります。([npm ドキュメント][9])

ただし **Dockerの “ビルド” 中に env を渡す**のはログやレイヤの観点で事故りやすいので、上の (A) を第一候補にするのが無難です😌🛡️

---

## 6) Compose でやる場合（`build.ssh`）🧩🐳

![Compose SSH Config](./picture/docker_safe_isolation_ts_study_024_07_compose_ssh.png)

Compose の build には `ssh` という指定ができます（例：default エージェントをマウント）🧷([docs.docker.jp][10])

```yaml
services:
  app:
    build:
      context: .
      ssh:
        - default
```

CLI でやるなら👇（こちらも `--ssh` が用意されています）([matsuand.github.io][11])

```bash
docker compose build --ssh default
```

---

## 7) AI拡張がいる世界の“秘密の守り方”🤖🧱⚠️

AIが便利なほど、うっかりが増えます😇
ここだけはルール化しちゃうのがおすすめ👇

* **秘密っぽい文字列をAIに貼らない**（ログもそのまま貼らない）🙅‍♂️
* エラー貼るときは **トークン/URL/Authorization/`.npmrc` 部分を黒塗り**🖍️
* 「AIが提案した `COPY ~/.ssh`」みたいな案は、**即却下できる判断基準**を持つ（＝この章の内容）🛡️✨

---

## 8) よくある詰まりポイント集（ここで沼る）🪤🧯

## ❌ `Permission denied (publickey)` が出る😵

だいたいこれ👇

* `ssh-agent` に鍵が入ってない（`ssh-add` してない）
* そもそも依存取得が SSH じゃなく HTTPS になってる（`git+https` など）
* known_hosts 周りで止まっている（対話が発生して build が落ちる）

## ❌ Compose の `ssh:` が効かない / “unsupported option” っぽい🤔

* 古い `docker-compose`（Python版）系だと対応してないことがあります
* 今は `docker compose`（Compose v2）側の機能として扱うのが安全寄りです（この章の例はそっち想定）📌

---

## 9) 仕上げ：5分セルフ監査✅🔍（漏れてない？）

* `docker history --no-trunc myapp:dev` を見て、**トークンや鍵の痕跡が無い**✅
* リポジトリ内を検索して、トークンっぽい文字列が混入してない✅
* `.dockerignore` に `.npmrc` / `.ssh` / `.env` が入ってる✅
* 使ってるトークンは

  * **期限あり**
  * **権限しぼり**（fine-grained PAT / read-only deploy key）
  * **用途ラベルあり**（どの用途か分かる）✅ ([GitHub Docs][4])

---

## まとめ🎉

この章の結論はシンプルです👇😄

* private repo → **SSH agent forwarding（`--mount=type=ssh`）が第一候補**🔐([Docker Documentation][2])
* private packages → **BuildKit secret で `.npmrc` を “その瞬間だけ”**🤫([Docker Documentation][1])
* トークンは **最小権限・期限短め・用途固定**（fine-grained / deploy key / CIトークン）🛡️([GitHub Docs][5])

次の第25章（ローテーション＆失効）で、ここで作った仕組みに「漏れた前提の復旧力」を足して完成度を上げられます🚑🔁✨

[1]: https://docs.docker.com/build/building/secrets/?utm_source=chatgpt.com "Build secrets"
[2]: https://docs.docker.com/reference/dockerfile/?utm_source=chatgpt.com "Dockerfile reference | Docker Docs"
[3]: https://docs.docker.com/reference/compose-file/build/?utm_source=chatgpt.com "Compose Build Specification"
[4]: https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys?utm_source=chatgpt.com "Managing deploy keys"
[5]: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens?utm_source=chatgpt.com "Managing your personal access tokens"
[6]: https://docs.github.com/en/actions/reference/security/secure-use?utm_source=chatgpt.com "Secure use reference - GitHub Docs"
[7]: https://docs.npmjs.com/using-private-packages-in-a-ci-cd-workflow/?utm_source=chatgpt.com "Using private packages in a CI/CD workflow"
[8]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[9]: https://docs.npmjs.com/cli/v9/using-npm/config/?utm_source=chatgpt.com "config | npm Docs"
[10]: https://docs.docker.jp/compose/compose-file/build.html?utm_source=chatgpt.com "Compose ファイル構築リファレンス - Docker ドキュメント"
[11]: https://matsuand.github.io/docs.docker.jp.onthefly/engine/reference/commandline/compose_build/?utm_source=chatgpt.com "docker compose build | Docker ドキュメント"
