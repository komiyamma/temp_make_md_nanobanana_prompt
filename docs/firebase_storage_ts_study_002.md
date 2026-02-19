### 第2章：料金・クォータ事故を“先に”避ける💸🧯

この章は「あとで泣かないための保険回」だよ…！🥹
画像アップロードって、楽しいけど **燃える時は一瞬**（課金＆クォータ）🔥 なので、先に安全装置を付けようね🔧✨

---

## 1) まず知っておくべき “最新” 地雷ポイント🧨

![Blaze Plan Warning](./picture/firebase_storage_ts_study_002_01_blaze_warning.png)

### ✅ 2026年2月3日以降、Cloud Storage を使うなら Blaze が必須になった⚠️

**2026-02-03 から**、デフォルトバケット含め Cloud Storage リソースへアクセスを維持するには、プロジェクトが **Blaze（従量課金）** である必要があるよ。([Firebase][1])
さらに **2024-10-30 以降**、新しいデフォルトバケットの作成も Blaze が必要になってる。([Firebase][2])

### ✅ でも「Blazeにしたら即課金地獄」ではない🌱

ポイントはここ👇

* `*.appspot.com` の古いデフォルトバケットは、Blazeに上げても **“従来の無償枠レベル”が維持**される（一定量まで）([Firebase][2])
* ただし、超えた分は課金対象になるから **アラート必須**🔔([Firebase][2])

> この章のゴールは「Blazeが必要な時代の“安全運転”ができる」ことだよ🚗💨

---

## 2) 課金の正体を “3つだけ” 覚える🧠✨

![Three Cost Factors](./picture/firebase_storage_ts_study_002_02_cost_factors.png)

画像アップロード周りでお金が動くのは主にこれ👇

1. **保存量（ストレージ）**：画像を溜め込むほど増える📦
2. **ダウンロード（ネットワーク転送）**：外部に見せるほど増える🌐
3. **操作回数（オペレーション）**：アップロード/一覧取得/メタデータ更新などの回数📨

Cloud Storage は **Class A / Class B** みたいに「操作の種類」で単価が分かれてるよ（例：一覧取得や作成系が重め、取得系が軽め、みたいなイメージ）([Google Cloud][3])

---

## 3) 手を動かす：5分で付ける安全装置🔧🕔

### Step A：いまの状態を確認する（最優先）👀

Firebase コンソールで確認するよ👇

* **プロジェクトのプラン**：Spark / Blaze
* **Storage のバケット名**：

  * 古い：`PROJECT_ID.appspot.com`
  * 新しい：`PROJECT_ID.firebasestorage.app`（2024-10-30以降の新規デフォルトはこの形式）([Firebase][2])

ここで「え、2/3過ぎてるけど Spark のままかも…」ってなっても大丈夫。
まずは現状把握 → 次の Step B のアラート設定へ💨

---

### Step B：予算アラート（Budget alerts）を作る🔔💸

![Budget Alert Setup](./picture/firebase_storage_ts_study_002_03_budget_alert.png)

これが **最強の保険**。予算で“止まる”わけじゃないけど、**気づける**のが大事！([Google Cloud Documentation][4])

やること👇

1. **Google Cloud コンソール** → Billing（請求）へ
2. **Budgets & alerts**（予算とアラート）へ
3. 予算を作成して、例えばこう設定👇

* 月額：まずは小さく（例：1,000円 / 3,000円）💴
* 通知：50% / 90% / 100%（＋できれば予測通知も）📈
* 通知先：自分のメール✉️

公式手順の流れはこのドキュメントがベースだよ。([Google Cloud Documentation][4])

---

### Step C：Firebase 側で “増え方” を毎日見える化📊

![Monitoring Dashboard](./picture/firebase_storage_ts_study_002_04_monitoring.png)

Cloud Storage の使用状況は Firebase コンソールでも追えるよ📷

* Bytes stored（保存量）
* object count（ファイル数）
* bandwidth（転送量）
* download requests（DL回数）

更新頻度（ズレやすい所）も書かれてるので、「今日増えたのに反映されない！」って焦りにくくなる👍([Firebase][5])

---

### Step D：異常検知を “スパイクで” 取る（おすすめ）🚨

「急にDLが増えた」「DENYが急増してる」みたいな兆候は、Cloud Monitoring のアラートでも検知できるよ。
Rules の評価回数（ALLOW/DENY/ERROR）を監視できるのが便利！🛡️([Firebase][5])

---

## 4) よくある “課金事故” パターン集🔥（先に潰そう）

![Cost Accident Patterns](./picture/firebase_storage_ts_study_002_05_accident_patterns.png)

### 事故①：画像URLが拡散してダウンロード爆増🌐💥

* 例：Download URL をSNSに貼られて、外部から大量アクセス
* 対策：

  * そもそも読ませる範囲を設計（公開？本人だけ？）🧭
  * 後の章でやる **Rules / App Check** を必ず入れる🧿([Firebase][6])

### 事故②：アップロードが無制限で “誰でも投げ放題” 🗑️💣

* 対策：Rulesで **サイズ・contentType** 制限を最初から入れる（後の章で本格的にやるけど、この発想は今持っておく）🛡️([Firebase][7])

### 事故③：履歴やサムネを増やし続けて保存量がジワ増え📦🐢

* 対策：

  * 「原本は保持する？」「何世代残す？」を先に決める📜
  * “掃除のタイミング” を設計する🧹（後半の章でやるよ）

### 事故④：Functions/Extensions が暴走してループ⚙️🔁

* 例：アップロード→関数→別ファイル生成→それもトリガー…で無限
* 対策：トリガー対象のパスを分ける / ガード条件を入れる🚧
  （Storageイベントで関数を起動できるのは公式でも紹介されてるよ）([Firebase][8])

---

## 5) AIも絡める：燃えポイントを “AIに先に洗い出し” させる🤖🧯

### ✅ Antigravity / Gemini CLI から Firebase を触れる（MCP server）🧩

Firebase MCP server は **Antigravity や Gemini CLI** などの MCP クライアントと一緒に使えるよ。
「設定や調査をAIにやらせる」→「人間は判断だけ」みたいな流れが作りやすい👍([Firebase][9])

たとえば、こんな依頼が強い👇（そのままコピペOK）

```txt
Cloud Storage で課金が増えやすいポイントを、このアプリ構成（プロフィール画像アップロード）前提で列挙して。
「保存量」「転送量」「操作回数」で分類して、対策もセットで。
最後に、予算アラートと監視で最低限やるToDoをチェックリスト化して。
```

```txt
この Storage の設計（users/{uid}/profile/...）で、ありがちな事故を5つ挙げて。
Rules / App Check / キャッシュ / 履歴削除 / サムネ生成 の観点でレビューして。
```

### ✅ Firebase AI Logic を使うなら “AI利用のコスト” も忘れずに🧠💸

Firebase AI Logic は、使う Gemini API プロバイダや監視（Observability）側で費用が発生しうるよ。
「AI機能を入れたのに、どこが課金源？」って迷ったらまずここを見るのが早い👍([Firebase][10])

---

## 6) ミニ課題🎯（10分）

1. **「課金に効く操作」**を3つ書く✍️

   * 例：アップロード、ダウンロード、一覧取得…など
2. **Budget alerts を作る**🔔（50%/90%/100%）
3. Firebase コンソールで Storage の使用状況を開いて、
   **どの指標が“増えたらヤバい”か**を1行で言語化する📝

---

## 7) チェック✅（ここまでできたら勝ち！）

* 2026-02-03 以降に必要なこと（Blaze必須化）を説明できる([Firebase][2])
* 予算アラートの場所を迷わず開ける([Google Cloud Documentation][4])
* Storage の「保存量 / 転送量 / 操作回数」を意識して設計できる([Google Cloud][3])
* AIに「燃えポイントレビュー」を投げるテンプレを持った([Firebase][9])

---

次の第3章は、いよいよ **Reactで画像選択UI（プレビュー付き）** 🖼️✨
ここで“体験として楽しい”ゾーンに入るよ！進めてOK？😆🚀

[1]: https://firebase.google.com/docs/storage/faqs-storage-changes-announced-sept-2024?utm_source=chatgpt.com "FAQs about changes to Cloud Storage for Firebase pricing ..."
[2]: https://firebase.google.com/docs/storage/faqs-storage-changes-announced-sept-2024 "FAQs about changes to Cloud Storage for Firebase pricing and default buckets"
[3]: https://cloud.google.com/storage/pricing?utm_source=chatgpt.com "Cloud Storage pricing"
[4]: https://docs.cloud.google.com/billing/docs/how-to/budgets?utm_source=chatgpt.com "Create, edit, or delete budgets and budget alerts"
[5]: https://firebase.google.com/docs/storage/monitor-storage "Monitor Cloud Storage activity  |  Cloud Storage for Firebase"
[6]: https://firebase.google.com/docs/app-check?utm_source=chatgpt.com "Firebase App Check - Google"
[7]: https://firebase.google.com/docs/storage/security?utm_source=chatgpt.com "Understand Firebase Security Rules for Cloud Storage - Google"
[8]: https://firebase.google.com/docs/storage/extend-with-functions?utm_source=chatgpt.com "Extend Cloud Storage with Cloud Functions - Firebase - Google"
[9]: https://firebase.google.com/docs/ai-assistance/mcp-server?utm_source=chatgpt.com "Firebase MCP server | Develop with AI assistance - Google"
[10]: https://firebase.google.com/docs/ai-logic/pricing?utm_source=chatgpt.com "Understand pricing | Firebase AI Logic - Google"
