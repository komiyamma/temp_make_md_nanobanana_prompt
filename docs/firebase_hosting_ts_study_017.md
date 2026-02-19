# 第17章：`apphosting.yaml` で環境変数・VPCなどを扱う🧩

## この章のゴール🏁

* App Hosting の設定を **apphosting.yaml にまとめて管理**できる✨ ([Firebase][1])
* 環境変数を「ビルド時だけ」「実行時だけ」みたいに **渡す範囲をコントロール**できる🔐 ([Firebase][1])
* APIキーなどの秘密は **Cloud Secret Manager を参照**して安全に扱える🗝️ ([Firebase][1])
* DBや社内APIなど“非公開ネットワーク”に繋ぎたい時、**VPC接続を apphosting.yaml で設定**できる🌉 ([Firebase][1])
* staging / production みたいな **複数環境をファイル分け**して運用できる🏗️ ([Firebase][2])

---

## 1) apphosting.yaml って何者？📄🤔

![apphosting.yaml Anatomy](./picture/firebase_hosting_ts_study_017_01_anatomy.png)

App Hosting は、同じリポジトリでも「環境変数」「CPU/メモリ」「同時処理数」などを変えたい場面が多いです💡
その設定の中心になるのが **apphosting.yaml** です。ここにランタイム設定（Cloud Run 側の設定）や環境変数、シークレット参照、VPC接続まで書けます。 ([Firebase][1])

まず雛形を作るにはこれ👇（プロジェクトのルートで実行）

```powershell
firebase init apphosting
```

これで apphosting.yaml のスターターが作られます。 ([Firebase][1])

---

## 2) まずは“普通の環境変数”を入れてみよう🌱🧪

たとえば「ストレージのバケット名」みたいに、公開しても問題ない（or 影響が小さい）値は value でOKです✅

```yaml
## apphosting.yaml
env:
  - variable: STORAGE_BUCKET
    value: mybucket.firebasestorage.app
```

この形式は公式に載ってます。 ([Firebase][1])

## ここで超大事ポイント⚠️

* 変数名は **大文字A-Z とアンダースコア**が基本（ルールあり）
* **予約語（内部用のキー）**もあるので、変な名前を付けない
  この注意は公式にもあります。 ([Firebase][1])

---

## 3) “ビルド時”と“実行時”を分ける✂️🧠

![Variable Availability](./picture/firebase_hosting_ts_study_017_02_availability.png)

App Hosting では、環境変数を **どこで使えるか** を availability で制御できます✨

* BUILD：ビルド中（例：Next.js の build が読む）
* RUNTIME：デプロイ後の実行中（例：サーバー処理が読む）
* 何も書かないと、基本は両方に渡る（デフォルト） ([Firebase][1])

例：両方で使えるようにする👇

```yaml
env:
  - variable: API_BASE_URL
    value: https://api.example.com
    availability:
      - BUILD
      - RUNTIME
```

「ビルドでだけ必要」な値（例えばビルド設定の切り替え）なら BUILD のみにする、みたいな使い分けができます👌 ([Firebase][1])

---

## 4) ブラウザに出していい？ NEXT_PUBLIC_ の考え方🌍🕵️‍♀️

![Public vs Secret Variables](./picture/firebase_hosting_ts_study_017_03_public_vs_secret.png)

Next.js 系だと、NEXT_PUBLIC_ が付く変数は「ブラウザ側に出る」扱いになります。
App Hosting でも同様に NEXT_PUBLIC_ を使えます。 ([Firebase][1])

✅ 出していい例：公開しても困らない設定（例：画像CDNの公開URL）
❌ 出しちゃダメ例：APIキー、秘密鍵、課金に直結するトークン、管理者用URL…🧨

---

## 5) 秘密は Cloud Secret Manager 参照にする🗝️🔐

![Secret Manager Reference](./picture/firebase_hosting_ts_study_017_04_secret_ref.png)

APIキーなど **漏れたら終わる** ものは、apphosting.yaml にベタ書きしません🙅‍♂️
代わりに Cloud Secret Manager のシークレットを参照します。これが公式推奨ルートです。 ([Firebase][1])

## apphosting.yaml 側（secret 参照）

```yaml
env:
  - variable: THIRD_PARTY_API_KEY
    secret: myApiKeySecret
```

さらに「特定バージョンに固定」もできます（例：@5）👇 ([Firebase][1])

```yaml
env:
  - variable: PINNED_API_KEY
    secret: myApiKeySecret@5
```

## シークレット作成（CLI）🧰

公式では、Firebase CLI からシークレットを作れて、権限付与や apphosting.yaml への追加も誘導してくれます。 ([Firebase][1])

```powershell
firebase apphosting:secrets:set myApiKeySecret
```

「コンソールで作った場合」は、あとから grantaccess で権限を付ける流れになります。 ([Firebase][1])

```powershell
firebase apphosting:secrets:grantaccess myApiKeySecret --emails your-team@example.com
```

---

## 6) 環境（staging / production）でファイルを分ける🏗️🧩

![Configuration Overrides](./picture/firebase_hosting_ts_study_017_05_file_priority.png)

App Hosting は、環境名に応じて **apphosting.ENVIRONMENT_NAME.yaml** を優先して読みます。
例：apphosting.production.yaml / apphosting.staging.yaml ✨ ([The Firebase Blog][3])

## おすすめ運用（安全）🛟

* apphosting.yaml：**どの環境でも安全なデフォルトだけ**（危険な値は置かない） ([Firebase][2])
* apphosting.staging.yaml：検証用の設定
* apphosting.production.yaml：本番用の設定（minInstances を上げる等）

例（雰囲気）👇

```yaml
## apphosting.yaml（安全なデフォルトだけ）
runConfig:
  minInstances: 0
env:
  - variable: APP_ENV
    value: default
```

```yaml
## apphosting.staging.yaml
runConfig:
  minInstances: 0
env:
  - variable: APP_ENV
    value: staging
```

```yaml
## apphosting.production.yaml
runConfig:
  minInstances: 1
env:
  - variable: APP_ENV
    value: production
```

---

## 7) VPC接続：DBや社内APIに“内側”から繋ぐ🌉🛡️

![VPC Access](./picture/firebase_hosting_ts_study_017_06_vpc_tunnel.png)

「Cloud SQL みたいな非公開アクセスのDB」「社内サービス」「VPC内のキャッシュ」などに繋ぎたい場合、App Hosting のバックエンドを VPC に接続できます。 ([The Firebase Blog][4])

設定は runConfig の vpcAccess に書きます。

## パターンA：Direct VPC Egress（例：PRIVATE_RANGES_ONLY）🚄

```yaml
runConfig:
  vpcAccess:
    egress: PRIVATE_RANGES_ONLY
    networkInterfaces:
      - network: my-network-id
        subnetwork: my-subnetwork-id
```

公式の例そのままの形です。 ([Firebase][1])

## パターンB：Serverless Connector（例：ALL_TRAFFIC）🔌

```yaml
runConfig:
  vpcAccess:
    egress: ALL_TRAFFIC
    connector: connector-id
```

これも公式に載ってる形です。 ([Firebase][1])

💡「IDで書ける」ので、staging/prod で中身が違っても“同じapphosting.yaml運用”がしやすいよ、という話も公式ブログで説明されています。 ([The Firebase Blog][4])

---

## 8) ローカル検証：App Hosting Emulator で“設定の事故”を減らす🧯🧪

App Hosting Emulator を初期化すると **apphosting.emulator.yaml** が作れて、ローカルだけ値を上書きできます。 ([Firebase][5])

しかもここが良い👇

* emulator 用ファイルも **本番と同じスキーマ**
* 秘密は「本番でsecretなら、emulatorでもsecretとして扱え」みたいに、うっかり漏洩を抑える設計 ([Firebase][5])

---

## 9) AIを混ぜる：Antigravity / Gemini CLI で“設定作業”を短縮🤖⚡

![AI Config Generator](./picture/firebase_hosting_ts_study_017_07_ai_config.png)

## Firebase MCP server を使うと何が嬉しい？🧩

Firebase MCP server は、Antigravity や Gemini CLI などの MCP クライアントから Firebase 操作・調査をしやすくします。 ([Firebase][6])

## Gemini CLI（Firebase拡張）📦

Gemini CLI には Firebase 拡張があり、インストールすると MCP 周りもまとめてセットアップされます。 ([Firebase][6])

```powershell
gemini extensions install https://github.com/gemini-cli-extensions/firebase/
```

## Antigravity 側（MCPを追加）🧠

Antigravity から Firebase MCP を追加して、エージェントに「Firebase初期化して」「Hosting/App Hostingのデプロイ手順出して」みたいに頼めます。 ([The Firebase Blog][7])

## 使いどころ（第17章向け）🎯

* 「apphosting.yaml の雛形を、うちの構成（staging/prod、secret参照、VPC）で作って」
* 「NEXT_PUBLIC_ にするべきもの／ダメなものを仕分けして」
* 「BUILDだけにすべき変数ってどれ？」
* 「VPC接続の設定が、Direct/Connectorどっち向きか判断して」

“設定レビュー役”としてAIを置くと、事故が一気に減ります😌🧯

---

## 手を動かす✋🔥（ワーク）

## Step 1：apphosting.yaml を用意

```powershell
firebase init apphosting
```

([Firebase][1])

## Step 2：環境変数を3つ入れる（例）

* APP_ENV（staging/prodで変える）
* NEXT_PUBLIC_APP_NAME（表示用）
* THIRD_PARTY_API_KEY（secret参照）

## Step 3：secret を作って紐付け

```powershell
firebase apphosting:secrets:set myApiKeySecret
```

([Firebase][1])

## Step 4：staging / production のファイル分け

* apphosting.staging.yaml
* apphosting.production.yaml
  ([The Firebase Blog][3])

## Step 5（任意）：VPC を使うなら vpcAccess を追加

Direct か Connector かを選んで書く。 ([Firebase][1])

---

## ミニ課題📝✨

「本番と検証で値が違う環境変数」を3つ考えて、分類してみよう👇

1. ブラウザに出してOK（NEXT_PUBLIC_候補）🌍
2. サーバーだけでOK（RUNTIMEのみ候補）🖥️
3. シークレットにすべき（secret参照）🔐

---

## チェック✅🎉（できたら勝ち！）

* apphosting.yaml に env と runConfig を書けた🧩 ([Firebase][1])
* availability（BUILD/RUNTIME）を説明できる✂️ ([Firebase][1])
* secret 参照にして「ベタ書きしない」理由が言える🔐 ([Firebase][1])
* apphosting.production.yaml / staging.yaml の意義が説明できる🏗️ ([The Firebase Blog][3])
* VPC接続の2方式（Direct/Connector）を見て「どっちが合うか」判断できる🌉 ([Firebase][1])

---

## よくあるハマり🧯（先に潰す）

* 「NEXT_PUBLIC_ を付けたせいで秘密がブラウザに出た」😱 → 公開前に必ず仕分け！ ([Firebase][1])
* 「secret を作ったのに権限が足りない」🔒 → grantaccess で付与（チーム運用なら特に） ([Firebase][1])
* 「ローカルでだけ値を変えたい」🧪 → apphosting.emulator.yaml で上書き ([Firebase][5])
* 「VPCが必要なのに設定がない」🌉 → vpcAccess を runConfig に追加 ([Firebase][1])

---

次の第18章は「ロールアウト制御（勝手に出ないようにする）🧯」だね！
第17章の内容を “staging/prod 実例（変数名セット）” で固定して、テンプレとして完成させる版も作れるよ😆✨

[1]: https://firebase.google.com/docs/app-hosting/configure "Configure and manage App Hosting backends  |  Firebase App Hosting"
[2]: https://firebase.google.com/docs/app-hosting/multiple-environments "Deploy multiple environments from a codebase  |  Firebase App Hosting"
[3]: https://firebase.blog/posts/2024/09/app-hosting-environments/ "Firebase App Hosting: Environments & deployment settings"
[4]: https://firebase.blog/posts/2025/03/apphosting-march-update/ "App Hosting updates: rollbacks, SDK auto-configuration, and more"
[5]: https://firebase.google.com/docs/emulator-suite/use_app_hosting "Test web apps locally with the Firebase App Hosting Emulator  |  Firebase Local Emulator Suite"
[6]: https://firebase.google.com/docs/ai-assistance/mcp-server "Firebase MCP server  |  Develop with AI assistance"
[7]: https://firebase.blog/posts/2025/11/firebase-mcp-and-antigravity/ "Antigravity and Firebase MCP accelerate app development"
