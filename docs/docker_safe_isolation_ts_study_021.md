# 第21章：Compose secrets実践：秘密はファイルで渡す（/run/secrets）📄🔐

この章のゴールはシンプル！😄
**「パスワードやAPIキーを“環境変数に直書きしない”で、Composeのsecretsとして“ファイルで渡す”** を手で覚えます🧠✨
secretsは **コンテナ内で `/run/secrets/<secret_name>` の“読み取り専用ファイル”として見える** のが基本です📌 ([Docker Documentation][1])

---

## 1) まず“何が嬉しいの？”を一言で💡🫶

* 環境変数で秘密を渡すと、**意図せず露出しやすい**（デバッグログに出たり、追跡が難しかったり）😇💥
* secretsなら **「そのサービスにだけ見せる」** をComposeで明示できます✅
  （サービス単位で許可しない限りアクセスできない）([Docker Documentation][1])

---

## 2) Compose secretsの“基本ルール”3つ📚🔒

1. **top-level `secrets:` で“秘密の中身の作り方”を定義**

   * `file:`（ファイル内容をsecretに）
   * `environment:`（ホスト側の環境変数の値をsecretに）([Docker Documentation][2])
2. **各サービス側 `services.<name>.secrets:` で“この秘密を見せる”と明示**（ここが超重要）([Docker Documentation][3])
3. コンテナ内では **`/run/secrets/<secret_name>` の読み取り専用ファイル** 🧊📄 ([Docker Documentation][3])

---

## 3) ハンズオン：Node/TypeScriptが `/run/secrets` を読む🧑‍💻✨

### 3-1) こんな構成で作るよ📁

* `compose.yaml`
* `app/`（Node/TSアプリ）
* `secrets/`（秘密ファイル置き場：**Gitに入れない！**🙅‍♂️）

---

### 3-2) secretファイルを作る（PowerShell例）🪟🔑

※例としてDBパスワードを作るよ（中身はダミーでOK）🙂

```powershell
mkdir secrets -Force
## 改行が末尾に入ると困るケースがあるので -NoNewline 推奨
Set-Content -Path secrets\db_password.txt -Value "super-secret-password" -NoNewline
```

**Gitに絶対入れない**（ここ、事故ポイント！）😱🧯

```gitignore
## secrets置き場はまるごと除外
secrets/
## よくある秘密ファイルもついでに
.env
```

---

### 3-3) compose.yaml（最小形）🧩🔐

`myapp` だけが `db_password` を読める設定にします✅

```yaml
services:
  myapp:
    build: ./app
    secrets:
      - db_password
    environment:
      # 値そのものではなく「ファイルの場所」だけ渡す（安全寄り）👍
      DB_PASSWORD_FILE: /run/secrets/db_password

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

ポイント👇

* `secrets:`（トップ）で **中身の出どころ** を決める
* `services.myapp.secrets:` で **見せる相手** を決める
* アプリは `DB_PASSWORD_FILE` を見てそこから読む（値をENVに直置きしない）👍

---

### 3-4) TypeScript側：secretファイルを読む📖✨

例：`app/src/secret.ts`

```ts
import { readFile } from "node:fs/promises";

export async function readSecretFromFile(
  envKey: string,
  defaultPath: string,
): Promise<string> {
  const path = process.env[envKey] ?? defaultPath;

  // 末尾改行が混ざっても困らないよう trimEnd() が安定👍
  const value = (await readFile(path, "utf8")).trimEnd();

  if (!value) throw new Error(`Secret is empty: ${path}`);
  return value;
}
```

例：`app/src/index.ts`

```ts
import { readSecretFromFile } from "./secret.js";

async function main() {
  const dbPassword = await readSecretFromFile(
    "DB_PASSWORD_FILE",
    "/run/secrets/db_password",
  );

  // 🚫 絶対に console.log(dbPassword) しない（漏れる）😇💥
  console.log("✅ secret loaded (length only):", dbPassword.length);
}

main().catch((e) => {
  // ここも注意：例外に秘密が混ざらない形にする
  console.error("❌ failed to start:", e instanceof Error ? e.message : e);
  process.exit(1);
});
```

---

### 3-5) 起動＆確認コマンド🚀

```bash
docker compose up --build
```

コンテナ内に secret が来てるか“中身を出さずに”確認👀🔍
（例：ファイル一覧とパーミッションだけ見る）

```bash
docker compose exec myapp sh -lc "ls -l /run/secrets"
```

`db_password` が `/run/secrets` に見えてたら成功🎉 ([Docker Documentation][1])

---

## 4) ちょい応用：long syntaxでファイル名を変える🪄📄

「コンテナ内では `server.cert` って名前がいい」みたいな時に `target` を使います✅ ([Docker Documentation][3])

```yaml
services:
  myapp:
    build: ./app
    secrets:
      - source: db_password
        target: db-password.txt

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

---

## 5) 重要な落とし穴集😇🧨（ここで事故る）

* **`/run/secrets` は基本“読み取り専用”**：アプリが書き換えようとするとコケます🧊📄 ([Docker Documentation][3])
* **`uid/gid/mode` を指定しても、`file:` 由来のsecretだとDocker Composeでは効かない**（実装上、裏側がbind mountなので）🫠
  → つまり「権限を細かく変えたい」は別の作戦が必要です（次の章以降でカバーしやすい）([Docker Documentation][3])
* **改行問題**：secretファイル末尾の改行でログイン失敗…あるある😵
  → `trimEnd()` が保険🛟
* **ENVに“秘密そのもの”を入れない**：Docker公式も、ENV注入は露出しやすい点を注意しています⚠️ ([Docker Documentation][1])

---

## 6) AI拡張（Copilot/Codex）時代の“秘密の守り方”🤖🧱🔐

AIが悪いというより、**うっかり流れ**が一番怖いです😇💥

* **秘密ファイルはワークスペースから隔離**（最強）🚪

  * 例：`secrets/` をプロジェクト外に置く、など
* 少なくとも **`.gitignore` で秘密を追跡対象から外す**✅
* さらに **GitHub のCopilotには“content exclusion”という仕組み**があり、**除外したファイルは提案/チャットの文脈に使われない**方向で設計されています🧯 ([GitHub Docs][4])
* **OpenAI のCodexも、基本はワークスペース範囲＋承認ポリシー等の安全設計が説明されています**（とはいえ“見せない”が最強）🛡️ ([OpenAI Developers][5])

✅合言葉：「秘密は“AIに貼らない・ログに出さない・Gitに入れない”】【最重要】📛

---

## 7) ミニ演習（3つ）✍️🔥

1. **secretをローテーション**してみよう🔁

   * `secrets/db_password.txt` を書き換える
   * `docker compose up -d --build` or `docker compose restart`
   * アプリが新しい長さを読み直すのを確認（中身は出さない）✅
2. **`target` を使ってファイル名を変える**🪄

   * `/run/secrets/db-password.txt` にして読み取りパスを更新
3. **“ENV直書き”をわざとやって、危なさを体感**😈（検証用ダミーで！）

   * `environment: DB_PASSWORD=...` としてみて
   * 「どこに露出し得るか」を想像してみる（ログ/デバッグ/共有/スクショ）🫣

---

## 8) まとめ🎯✨

* Compose secretsは **「秘密を“ファイルとして渡す”」** 仕組み📄🔐 ([Docker Documentation][1])
* **サービス単位でアクセスを絞れる**のが強み✂️🛡️ ([Docker Documentation][3])
* 実運用の事故はだいたい **Git / ログ / コピペ / AIチャット** から起きるので、そこを先回りして塞ぐのが勝ち🏆😄

次の章（第22章）では、この secrets を **ログ・例外・デバッグで“漏らさない設計”** に落とし込んでいきます🧯🫣

[1]: https://docs.docker.com/compose/how-tos/use-secrets/ "Secrets in Compose | Docker Docs"
[2]: https://docs.docker.com/reference/compose-file/secrets/ "Secrets | Docker Docs"
[3]: https://docs.docker.com/reference/compose-file/services/ "Services | Docker Docs"
[4]: https://docs.github.com/en/copilot/concepts/context/content-exclusion?utm_source=chatgpt.com "Content exclusion for GitHub Copilot"
[5]: https://developers.openai.com/codex/security/?utm_source=chatgpt.com "Security"
