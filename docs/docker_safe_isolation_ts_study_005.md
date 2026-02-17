# 第05章：最初に捨てる危険カード：privileged／docker.sock／秘密直書き🗑️⚠️

この章は「**うっかり1行で被害半径が爆増するやつ**」を先に回収する回です😇💥  
結論：この3つが出てきたら、**“便利の代償がデカすぎる”サイン**だと思ってください。

---

## この章でできるようになること🎯✨

- 👀 **危険カード3兄弟**を「見つけて」「危険度を説明できて」「代替に置換できる」
- 🧯 “とりあえず動いた”の事故（秘密漏れ・ホスト破壊・踏み台）を減らす
- 🧩 例外が必要なときも、**隔離して安全に使う**判断ができる

> なぜここまで強く言うの？  
> **Dockerデーモンを触れる人＝強い権限を持つ人**になりやすいからです。Docker公式も「Dockerデーモンを操作できるのは信頼できるユーザーだけにしよう」と明記しています。:contentReference[oaicite:0]{index=0}

---

## 0. まず“危険カード3兄弟”を覚える🃏⚠️

![Three Dangerous Cards](./picture/docker_safe_isolation_ts_study_005_01_three_dangerous_cards.png)

- 🟥 `privileged: true`（または `docker run --privileged`）
- 🟥 `- /var/run/docker.sock:/var/run/docker.sock`（Docker APIソケット共有）
- 🟥 秘密を直書き（Composeの`environment:`、Dockerfile、コード、ログ、AIへの貼り付け…）

この3つは、だいたい **「ホスト級のことができちゃう」か「秘密が漏れる」**に直結します。:contentReference[oaicite:1]{index=1}

---

## 1) 危険カード①：`privileged` は“全開放スイッチ”🔓💪

![Privileged Switch](./picture/docker_safe_isolation_ts_study_005_02_privileged_switch.png)

## 何が起きるの？😱
`--privileged` は、コンテナに強い権限を与えて制限を大幅にゆるめます（全部許可に近づく感じ）:contentReference[oaicite:2]{index=2}  
しかも **Docker Desktop（企業向けの強化機能）では「privilegedでも隔離を強める」方向の対策が入る**くらい、元々の`privileged`は危険寄りの存在です。:contentReference[oaicite:3]{index=3}

## ありがちな“使いどころミス”あるある😂
- 「権限エラー出た！とりあえず `privileged: true` だ！」  
  → ✅動く / ❌安全じゃない  
- 「USBデバイス触りたい」  
  → `devices:` で“そのデバイスだけ”渡せることが多い（後述）

---

## 代替案（優先度順）🥇🥈🥉

## 🥇A. まず“全部禁止”→必要な分だけ足す（capabilities方式）🧤✂️

![Cap Drop and Add](./picture/docker_safe_isolation_ts_study_005_03_cap_drop_add.png)

Composeには `cap_drop` / `cap_add` があって、できることを絞れます。:contentReference[oaicite:4]{index=4}  
**安全側の定番**はこれ👇

````yaml
services:
  api:
    build: .
    ports:
      - "3000:3000"

    # ✅ rootで動かさない（別章でも再登場する大事ポイント）
    user: "node"

    # ✅ まず固く
    read_only: true
    tmpfs:
      - /tmp

    # ✅ まず全部落として、必要が出たら1個ずつ足す
    cap_drop:
      - ALL
    # cap_add:
    #   - NET_BIND_SERVICE  # 例：80番ポートを使う時など

    security_opt:
      - no-new-privileges:true

    # ❌ これは捨てる
    # privileged: true
`````

`read_only` / `tmpfs` / `security_opt` みたいな“固めるオプション”はComposeでも使えます。([Docker Documentation][1])

## 🥈B. デバイスが目的なら `devices:` で限定する🎛️🔌

「全部開放」ではなく「必要な機器だけ」へ。
※ Windows＋Docker Desktopだと“Linux VM側に見えるデバイス”の話になるので、要件次第で挙動が変わります（ここは“全部開放で殴る”が最悪手、というのだけ覚えてOK）🙂🪟

## 🥉C. どうしても`privileged`が必要なときの最終防衛線🧱🧯

* ✅ **そのコンテナを“隔離専用”にする**（他のサービスと混ぜない）
* ✅ 永続ボリュームや重要フォルダを渡さない
* ✅ ネットワークも閉じ気味に（必要最小限の到達だけ）
* ✅ “使う瞬間だけ起動”して消す（常駐させない）

---

## 2) 危険カード②：`docker.sock` は“ほぼホスト権限”🐙🔥

![Docker Sock Control](./picture/docker_safe_isolation_ts_study_005_04_docker_sock_danger.png)

## 何が起きるの？😱

`/var/run/docker.sock` は **Docker CLIがデーモンに指示を出す入口**です。
ここをコンテナに渡す＝**コンテナからDockerデーモンを操作できる**＝かなり強い権限になりやすいです。([Docker Documentation][2])

Docker公式は、デーモンの攻撃面として「ホストのディレクトリを制限なしに共有できる」ことを挙げていて、だからこそ **“信頼できるユーザーだけがデーモンを操作すべき”**としています。([Docker Documentation][2])

## “よく見るヤバい1行”🧨

```yaml
services:
  tool:
    image: docker:cli
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock # ❌
```

---

## 代替案（優先度順）🥇🥈🥉

## 🥇A. 「dockerコマンドはホストで打つ」🖥️✅

![Host Side Command](./picture/docker_safe_isolation_ts_study_005_05_host_command.png)

VS Codeのターミナルはホスト側です。
**“dockerをコンテナから叩く”発想を捨てる**だけで事故が激減します🙂✨

## 🥈B. どうしても別エンジンに繋ぎたいなら「Docker context + SSH」🔐🚀

Docker公式は、デーモンソケットを守る方法として **SSHやTLS**を案内し、`docker context` の例も載せています。([Docker Documentation][3])
つまり「ソケットを雑に共有」より「正規の接続方法で管理」が基本です。

## 🥉C. “ビルドだけ”が目的なら buildx の分離（docker-container driver）🏗️🧊

Docker Desktopの隔離強化（ECI）の制限/推奨の中でも、ビルド用途で **`docker-container` build driver を推奨**する記述があります。([Docker Documentation][4])
（「docker.sockマウントで殴る」より“ビルドの仕組みを分ける”方向へ）

---

## それでも `docker.sock` が必要なケース（例：Testcontainers等）🧪

会社の管理下で **Enhanced Container Isolation（ECI）** を使うと、**デフォルトで docker.sock のマウントがブロック**されます。([Docker Documentation][5])
例外（許可）を作れるけど、それは「信頼できるイメージ」に限定する思想です。([Docker Documentation][5])

---

## 3) 危険カード③：秘密直書き（Compose / Dockerfile / ログ / AI貼り付け）🫣📄🔑

## 何が起きるの？😱

![Plaintext Secret Leak](./picture/docker_safe_isolation_ts_study_005_06_secret_leak.png)

Docker公式は「秘密はDockerfileやソースに平文で置くな」「環境変数で注入すると露出リスクがある（ログに出たり追跡が難しい）」と明記しています。([Docker Documentation][6])

ありがちな漏れポイント👇

* `compose.yaml` の `environment:` にAPIキー直書き
* `.env` をうっかりコミット
* Dockerfileの `ARG SECRET=...`（イメージ履歴に残る系の事故）
* デバッグで `console.log(process.env)` しちゃう
* AI拡張に “設定ファイル丸ごと” 投げる（後の章で深掘りするやつ🤖⚠️）

---

## 代替案（優先度順）🥇🥈🥉

## 🥇A. 実行時は Compose secrets（/run/secrets）📄🔐

![Compose Secrets Delivery](./picture/docker_safe_isolation_ts_study_005_07_compose_secrets.png)

Compose secrets は **`/run/secrets/<secret_name>` にファイルとしてマウント**され、サービスごとにアクセス付与できます。([Docker Documentation][6])

例：`jwt_secret` をファイルで渡す✅

```yaml
services:
  api:
    build: .
    secrets:
      - jwt_secret
    environment:
      JWT_SECRET_FILE: /run/secrets/jwt_secret

secrets:
  jwt_secret:
    file: ./.secrets/jwt_secret.txt
```

## 🥈B. ビルド時は Build secrets（BuildKit）🏗️🤫

Docker公式はビルド中に秘密を使う場合、Dockerfileの `RUN --mount=type=secret` を案内しています。([Docker Documentation][7])

## 🥉C. 「環境変数で渡す」のは“最終手段”に寄せる🧨

どうしても環境変数で渡すなら：

* ✅ **ログに出さない**
* ✅ “最小範囲”のプロセスだけが読めるようにする
* ✅ **漏れた前提でローテーション**（後章でやります🔁）

---

## TypeScript側：秘密は“ファイル優先”で読む🙂📦

```ts
import fs from "node:fs/promises";

async function readSecret(filePath: string, envKey: string) {
  try {
    return (await fs.readFile(filePath, "utf8")).trim();
  } catch {
    const v = process.env[envKey];
    if (!v) throw new Error(`Missing secret: ${envKey} (or ${filePath})`);
    return v;
  }
}

// 例：Compose secrets なら /run/secrets/...
const jwtSecret = await readSecret("/run/secrets/jwt_secret", "JWT_SECRET");

// ❌ これをログに出さない！
console.log("JWT secret loaded"); // ✅ こういうログだけにする
```

---

## 演習（VS Codeでやる）🧪🛠️✨

## 演習1：危険カードを“検索で発見”🔎⚡

PowerShell（リポジトリ直下）で👇

```powershell
rg -n "privileged:\s*true|/var/run/docker\.sock|docker\.sock|AWS_|GITHUB_TOKEN|NPM_TOKEN|API_KEY|SECRET|PASSWORD" .
```

見つかったら、まずこう分類👇

* 🟥 今すぐ削る（`privileged` / `docker.sock` / 直書き秘密）
* 🟨 置換する（env注入→secrets、権限→capabilities）
* 🟩 OK（非機密の設定値、ローカルだけのメモ等）

---

## 演習2：`privileged` を “cap_drop ALL” に置換✂️🧤

1. `privileged: true` をコメントアウト
2. `cap_drop: [ALL]` を入れて起動
3. 動かないなら **エラーメッセージを見て「必要な権限」を特定**
4. `cap_add` を“1個ずつ”足す（雑に戻さない🙂）

> Composeの `cap_add/cap_drop` や `read_only` などの項目は公式リファレンスにあります。([Docker Documentation][1])

---

## 演習3：秘密直書きを Compose secrets に移す🔑➡️📄

1. `.secrets/` フォルダを作る
2. `.gitignore` に `.secrets/` を追加
3. `compose.yaml` の直書きを削って `secrets:` に移す
4. TypeScript側は `/run/secrets/...` を読む

---

## “最新の現実”メモ：Docker Desktop/隔離機能も油断禁物🧠🧷

最近のDocker Desktopのセキュリティ情報として、たとえば

* **Docker Desktop 4.44.3**で、設定されたDockerサブネット経由でEngine APIに到達し得る問題（CVE-2025-9074）が修正された、というアナウンスがあります（ECIでも軽減されない旨の記載もあり）。([Docker ドキュメント][8])
* また、ECIのdocker.sock制限に関する不具合（CVE-2025-10657）が修正された、というアナウンスも出ています。([Docker Documentation][9])

👉 だからこそ、この章の3兄弟（特にdocker.sock）は「設計で避ける」が強いです😄🛡️

---

## 章末チェックリスト✅📝

* [ ] `privileged: true` を使ってない（使うなら“隔離専用”＋理由メモあり）
* [ ] `docker.sock` をマウントしてない（必要なら例外ルールと隔離がある）
* [ ] 秘密は **Compose secrets / Build secrets** に寄せた（直書きゼロ）
* [ ] ログに秘密を出してない（`console.log(env)` とかしてない）
* [ ] “困ったら危険カード”の癖を捨てた😇🗑️

---

次の章に進む前に、もし手元の `compose.yaml`（該当部分だけでOK）を貼ってくれたら、**この3兄弟が混ざってないか一緒に監査**して、代替案まで具体的に提案しますよ😄🔍✨

（会社環境でECIが使える/使えない、みたいな条件があっても、ちゃんと分岐して安全に作れます💪）



[1]: https://docs.docker.com/reference/compose-file/services/ "Services | Docker Docs"
[2]: https://docs.docker.com/engine/security/ "Security | Docker Docs"
[3]: https://docs.docker.com/engine/security/protect-access/ "Protect the Docker daemon socket | Docker Docs"
[4]: https://docs.docker.com/enterprise/security/hardened-desktop/enhanced-container-isolation/limitations/?utm_source=chatgpt.com "Enhanced Container Isolation limitations"
[5]: https://docs.docker.com/enterprise/security/hardened-desktop/enhanced-container-isolation/config/?utm_source=chatgpt.com "Configure Docker socket exceptions and advanced settings"
[6]: https://docs.docker.com/compose/how-tos/use-secrets/ "Secrets in Compose | Docker Docs"
[7]: https://docs.docker.com/build/building/secrets/?utm_source=chatgpt.com "Build secrets"
[8]: https://docs.docker.jp/engine/reference/run.html?utm_source=chatgpt.com "Docker run リファレンス — Docker-docs-ja 24.0 ドキュメント"
[9]: https://docs.docker.com/security/security-announcements/?utm_source=chatgpt.com "Docker security announcements"
