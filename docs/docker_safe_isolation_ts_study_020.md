# 第20章：configs / env / files の整理術：どれに何を置く？🧰🧩

この章は「**設定と秘密とただの値**」をごちゃ混ぜにしないで、チームでも未来の自分でも迷わない“置き場所ルール”を作る回だよ〜😄✨
（ここが固まると、セキュリティも運用も一気にラクになる！）

---

## 0. まず結論：迷ったらこの3箱📦📦📦

![Three Boxes Classification](./picture/docker_safe_isolation_ts_study_020_01_three_boxes_classification.png)

設定っぽいものは、最終的にこの3種類に分類できるよ👇

1. **env（環境変数）**：

* 「文字列のスイッチ」向き（例：`NODE_ENV=production`、`LOG_LEVEL=debug`）
* **12-factorっぽい運用**に寄せたい時に強い💪

2. **configs（設定ファイルとして配る“非秘密”）**：

* 「ファイルとして渡したい設定」向き（例：`app-config.json`、`nginx.conf`）
* Composeでは **ファイルとしてコンテナにマウント**される（デフォルトの置き場所あり）📄
* コンテナ内のデフォルトマウント先は Linux なら `/<config-name>`（Windows コンテナなら `C:\<config-name>`）だよ。([Docker Documentation][1])

3. **files（普通のファイル）**：

* 画像・テンプレ・SQL・初期データ・ローカル専用設定など
* bind mount で共有することも多い（ただし共有範囲は最小で！）🧷

そして「秘密（secret）」は **この章では“別枠”扱い**にするのが正解✅
（次のSecrets章で本格的にやるやつ）

---

## 1. ありがちな事故：全部envに押し込んで爆発💥

![Env Explosion Mess](./picture/docker_safe_isolation_ts_study_020_02_env_explosion_mess.png)

envって便利だから、こうなりがち👇

* `.env` に **DBパスワード**も **APIキー**も **設定JSON**も詰め込む
* どれが「公開OK」で、どれが「漏れたら即死」かわからなくなる😇
* ログやエラーに env が混ざって漏れる、AI拡張に貼って漏れる…🫣

だから、この章は**“分ける”が主役**だよ🧠✨

---

## 2. envを正しく理解しよう（ここが超重要）🧪

## 2-1. `.env` は「Composeのための変数」になりがち🤹‍♂️

Composeは、Composeファイル内の `${VAR}` を埋める（**変数補間**）ために、複数ソースから変数を読み込むよ。優先順位もある。([Docker Documentation][2])
つまり `.env` を置くと「Composeが読む」用途でまず効いてくる。

## 2-2. コンテナに入るenvは別（`environment` と `env_file`）📦

![Env Precedence Ladder](./picture/docker_safe_isolation_ts_study_020_03_env_precedence_ladder.png)

コンテナへ渡すenvは、主にこの2つ👇

* `environment:` … Composeファイルに直書き（or 変数補間で差し込み）
* `env_file:` … ファイルからまとめて読み込んでコンテナへ

しかも **どれが勝つか（優先順位）**が明文化されてる！
ざっくり言うと「CLIで渡した `-e` が最強」で、その次に色々続くよ。([Docker Documentation][3])

> ✅ ここだけ覚えればOK
> **「最後に上書きしたいものほど“強い場所”に置く」**（CLI > environment > env_file）

---

## 3. configsって何がうれしいの？📄✨

![Config File Injection](./picture/docker_safe_isolation_ts_study_020_04_config_file_injection.png)

Composeの `configs` は、サービスの挙動を変える設定を**イメージ再ビルドなしで差し替え**たい時に便利。
しかも「ファイルとして」コンテナに入る。([Docker Documentation][1])

## 使いどころの目安🎯

* ✅ JSON/YAML/TOML みたいな設定ファイル
* ✅ nginx や caddy の conf
* ✅ 「環境変数にすると読みにくい」設定の塊
* ✅ “サービスごとに違う設定ファイル”を渡したい

逆に env が向くのは👇

* ✅ ON/OFF、URL、ポート、ログレベルみたいな「短い文字列」

---

## 4. “置き場所ルール”テンプレ（そのまま採用OK）📌

チームで揉めない、定番の分け方を置いとくね😄

## 4-1. リポジトリ構成（例）📁

![Ideal Repository Structure](./picture/docker_safe_isolation_ts_study_020_05_ideal_repo_structure.png)

* `compose.yaml`
* `.env` … **公開OKなデフォルト値**（例：ポート、機能フラグ）
* `.env.local` … **個人PCだけの値**（Git管理しない）
* `configs/` … **非秘密の設定ファイル置き場**
* `secrets/` … **秘密ファイル置き場（Git管理しない）**
* `src/` … アプリ本体
* `scripts/` … 運用補助（初期化など）

## 4-2. 仕分けの判定フロー（秒速で決まる）⚡

![Decision Flowchart](./picture/docker_safe_isolation_ts_study_020_06_decision_flowchart.png)

1. **漏れたらヤバい？**（パスワード/鍵/トークン）
   → **secret（ファイル）**へ（envに置かない）🔑

2. 漏れても致命傷じゃないが、**ファイル形式の方が読みやすい？**
   → **configs**（ファイルで渡す）📄

3. それ以外の「短い値」
   → **env**（ただしログに出ない設計に）🧪

---

## 5. 実践：Composeで “env + configs + files” を同居させる🛠️

ここからは、**よくあるNode/TS構成**を例に「こう書けば迷わない」を作るよ😄
（コードは雰囲気でOK！）

## 5-1. `compose.yaml` 例（configs + env_file + bind mount）🧩

```yaml
services:
  api:
    build: .
    ports:
      - "${APP_PORT:-3000}:3000"

    # ✅ 短い値は env へ
    environment:
      NODE_ENV: "development"
      LOG_LEVEL: "${LOG_LEVEL:-info}"

    # ✅ まとまった“非秘密の値”は env_file でもOK（ただし秘密は入れない）
    env_file:
      - ./.env

    # ✅ 非秘密の設定ファイルは configs へ（ファイルとして入る）
    configs:
      - source: app_config
        target: /app/config/app-config.json

    # ✅ 開発中だけ、ソースを bind mount（共有範囲は最小！）
    volumes:
      - ./src:/app/src:ro

configs:
  app_config:
    file: ./configs/app-config.dev.json
```

ポイント👇

* `configs` は「ファイルとして入れる」。デフォルトのマウント先もあるけど、`target` で揃えると読みやすいよ。([Docker Documentation][1])
* envの優先順位があるので「どこで上書きするか」は最初に決めちゃうのが楽！([Docker Documentation][3])
* Composeファイルの仕様は基本「Compose Specification」を見ればOK（これが今の推奨路線）。([Docker Documentation][4])

---

## 6. Node/TypeScript側の読み方（“漏れない”読み方）🧠🔒

## 6-1. まず原則：ログに出すな🫣

* `process.env` を丸ごと出力しない
* エラー時に設定オブジェクトを丸ごと投げない
* 「接続文字列」や「ヘッダ」も危険（トークン混ざりがち）⚠️

## 6-2. “設定の入口”を1か所にする（超大事）🚪

![Single Config Entry Point](./picture/docker_safe_isolation_ts_study_020_07_single_config_entry_point.png)

* env と config file をアプリのあちこちで読まない
* `config.ts` みたいな **1ファイル**に集約する

例（雰囲気）👇

```ts
import fs from "node:fs";

type AppConfig = {
  featureX: boolean;
  allowOrigins: string[];
};

function readJson(path: string): AppConfig {
  return JSON.parse(fs.readFileSync(path, "utf-8"));
}

const configPath = process.env.APP_CONFIG_PATH ?? "/app/config/app-config.json";
export const appConfig = readJson(configPath);

export const env = {
  nodeEnv: process.env.NODE_ENV ?? "development",
  logLevel: process.env.LOG_LEVEL ?? "info",
};
```

> ✅ これで「envは短い値」「configsは読みやすい塊」って役割分担がキレイになる✨

---

## 7. “秘密”をenvに入れない理由（この章でも触れる）🔑💥

「秘密はファイルで渡す」が安全寄り。理由は単純で👇

* envはログやクラッシュレポートに混ざりやすい
* ツールやAI拡張に“見えやすい”
* うっかり `printenv` で全部出る😇

Composeの secrets は、**コンテナ内で `/run/secrets/<name>` にファイルとしてマウント**されるよ。([Docker Documentation][5])
（この詳細は次章でがっつり！）

---

## 8. AI拡張時代の“置き場所ルール”追加🚧🤖

AI拡張は便利だけど、「見せていい範囲」を先に決めないと危ないやつ😵
特に **間接プロンプトインジェクション**（リポジトリ内の文章やコメントに仕込まれた指示でAIが暴走）みたいな話が現実にある。([The GitHub Blog][6])
Microsoftも間接インジェクション対策の考え方を整理してるよ。([Microsoft Developer][7])

## この章の結論としての対策（超現実的）✅

* **秘密はワークスペース直下に置かない**（AIが拾いやすい）🫥
* `secrets/` は `.gitignore` ＋ “AIに読ませない場所”に寄せる
* AIに貼るのは **`.env.example`** まで（本物は貼らない）🙅‍♂️
* 生成されたコマンド・設定変更は **必ず人間がレビュー**（自動実行しない）👀
* 「設定ファイル（configs）」は攻撃の混入地点になりうるので、**レビュー対象**にする（PRで見る）🔍

---

## 9. 演習（15〜25分）✍️🔥

## 演習A：15個を仕分けしよう📦

次を「env / configs / secrets / files」に分類してみて〜😄

* `LOG_LEVEL`
* `DB_HOST`
* `DB_PASSWORD`
* `JWT_SECRET`
* `featureFlags.json`
* `nginx.conf`
* `allowed-origins.json`
* `seed.sql`
* `google-oauth-client-secret.json`
* `READMEに書いたAPIキー（ダメ）` …とか😂

## 演習B：構成を作る🛠️

* `configs/app-config.dev.json` を作って `configs` で渡す
* `LOG_LEVEL` は env で渡す
* アプリは `APP_CONFIG_PATH` から config を読む

## 演習C：事故を体験（安全に）💥

* わざと `console.log(process.env)` を入れて「危なさ」を見て、すぐ消す😇
* 次に「ログに出さない config.ts 集約」に直す

---

## 10. 章末チェックリスト✅🕵️‍♂️

* [ ] 秘密（鍵/トークン/パスワード）が env / `.env` に入ってない
* [ ] `.env.example` があって、秘密が混ざってない
* [ ] “設定の入口”が1か所（`config.ts` など）
* [ ] configs は「ファイルの塊」、env は「短い値」に寄せた
* [ ] configs / 設定ファイルはPRでレビュー対象になってる
* [ ] AIに貼るのは example まで。本物は貼らない🙅‍♂️

---

次の第21章（Compose secrets実践）に進むと、ここで分けた「secrets箱」を**ちゃんと安全に運用する**ところまで一気に完成するよ〜🔐🚀

[1]: https://docs.docker.com/reference/compose-file/configs/?utm_source=chatgpt.com "Configs"
[2]: https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/?utm_source=chatgpt.com "Interpolation - Docker Compose"
[3]: https://docs.docker.com/compose/how-tos/environment-variables/envvars-precedence/?utm_source=chatgpt.com "Environment variables precedence in Docker Compose"
[4]: https://docs.docker.com/reference/compose-file/?utm_source=chatgpt.com "Compose file reference"
[5]: https://docs.docker.com/compose/how-tos/use-secrets/?utm_source=chatgpt.com "Secrets in Compose"
[6]: https://github.blog/security/vulnerability-research/safeguarding-vs-code-against-prompt-injections/?utm_source=chatgpt.com "Safeguarding VS Code against prompt injections"
[7]: https://developer.microsoft.com/blog/protecting-against-indirect-injection-attacks-mcp?utm_source=chatgpt.com "Protecting against indirect prompt injection attacks in MCP"
