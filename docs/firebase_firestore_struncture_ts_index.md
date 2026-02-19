# Firestore設計：サブコレ・正規化・インデックス最適化：アウトライン20章

ゴールは「どんな形で保存すべき？」を**自分で判断できる**状態にすることです💪✨（サブコレ/正規化/インデックス/集計/型安全CRUDまで）

---

## このカテゴリで作る成果物（最終ゴール）🎯

**「日報 / 記事 / コメント」3階層**を題材にして、次を完成させます👇📝

* Firestoreの**データ構造（コレクション設計）**
* よく使う画面（一覧/詳細/コメント欄）を想定した**クエリ設計**🔎
* **インデックス**を“意図して”作れる状態🛠️（遅い→なぜ？→どう直す？）
* **集計**（いいね数/コメント数/ランキング）を安全に運用できる形🥇
* TypeScriptで**型安全CRUD（DTO/Converter）**を整備🧱（withConverter）
* AI（Firebase AI Logic / Genkit / Antigravity / Gemini CLI）で**設計レビューと実装を加速**🤖⚡
  ※AI機能はApp Checkやレート制限も絡むので、設計で“事故りにくい形”に寄せます💡 ([Firebase][1])

---

## 20章アウトライン（読む→手を動かす→ミニ課題→チェック）📚✨

![Course Map](./picture/firebase_firestore_struncture_ts_index_01_course_map.png)

### 第1章：Firestore設計って何を決めるの？（最短で地図を作る）🗺️

* 読む：設計で決めるのは「画面に必要な取り出し方」から逆算😄
* 手を動かす：日報/記事/コメントの**画面一覧**を紙に書く📝
* ミニ課題：**“必要なクエリ”を10個**書き出す（例：記事一覧/自分の投稿/最新コメント…）
* チェック：クエリが決まると保存形が決まる感覚が出たらOK✅

---

### 第2章：エンティティ分解（User / Report / Post / Comment）🧩

![Entity Relations](./picture/firebase_firestore_struncture_ts_index_02_entity_relation.png)

* 読む：「どの単位がドキュメント？」を決める
* 手を動かす：各エンティティの必須フィールドを列挙
* ミニ課題：**“編集される頻度”**を各フィールドにメモ（後で非正規化判断に使う）
* チェック：頻繁に更新される物が1つのドキュメントに集まりすぎてない？👀

---

### 第3章：ID設計（自動ID vs 意味のあるID）🆔

* 読む：IDは“検索”じゃなく“参照”を強くする道具
* 手を動かす：`users/{uid}` にする？別IDにする？を決める
* ミニ課題：**URLに載せるID/載せないID**を分ける
* チェック：推測されるIDにしない（事故防止）✅

---

### 第4章：サブコレクションの使いどころ（親子関係に強い）🧩

![Subcollection vs Top-Level](./picture/firebase_firestore_struncture_ts_index_03_subcollection.png)

* 読む：サブコレは「親にぶら下がる大量データ」に強い💪
* 手を動かす：`posts/{postId}/comments/{commentId}` を作る案を考える
* ミニ課題：**コメントはサブコレ？トップレベル？**両案を作る
* チェック：同じID名のサブコレなら**コレクショングループクエリ**も使えるのを覚える✅ ([Firebase][2])

---

### 第5章：サブコレの落とし穴（削除・移動・集計）💥

* 読む：サブコレは**まとめて消しにくい**（運用で詰まりがち）😇 ([Google Cloud Documentation][3])
* 手を動かす：削除方針（論理削除/TTL/手動クリーンアップ）を選ぶ
* ミニ課題：「記事削除時にコメントもどう扱う？」を決める
* チェック：削除＝データ設計の一部、になってればOK✅

---

### 第6章：正規化 vs 非正規化（Firestore流の割り切り）⚖️

![Normalization Scale](./picture/firebase_firestore_struncture_ts_index_04_normalization.png)

* 読む：Firestoreは“JOINしない前提”で考えるのがコツ😄
* 手を動かす：記事に表示したい「投稿者名/アイコン」をどう持つか考える
* ミニ課題：**“表示に必要な情報は複製OK”**のラインを決める
* チェック：更新頻度が低い物は複製しやすい、が腹落ち✅

---

### 第7章：参照の持ち方（id文字列 vs DocumentReference）🔗

* 読む：参照は「読みやすさ」「移植しやすさ」「型」に影響
* 手を動かす：`authorId: string` / `authorRef` どちらにするか決める
* ミニ課題：参照先が消えた時の表示（“退会ユーザー”）を決める
* チェック：参照切れ時に落ちないUI設計になってる✅

---

### 第8章：一覧に強い設計（“並べ替え”から逆算）📜

* 読む：一覧画面は `orderBy + limit` を前提にすると楽✨
* 手を動かす：記事一覧のソートキー（`createdAt` など）を決める
* ミニ課題：**“同点が出たときの並び”**（第2キー）も決める
* チェック：安定ソートの発想が出たらOK✅

---

### 第9章：ホットスポットと書き込み衝突（地味に重要）🔥

* 読む：1ドキュメントに書き込み集中すると詰まることがある😵
* 手を動かす：コメント数やいいね数を「直書き」する危険を理解
* ミニ課題：“集中しそうな更新”を3つ挙げ、対策メモ
* チェック：アクセス増を想像して「1点集中を避ける」意識が出たらOK✅ ([Firebase][4])

---

### 第10章：集計の全体像（いつ計算する？いつ保存する？）🧮

![Aggregation Methods](./picture/firebase_firestore_struncture_ts_index_06_aggregation.png)

* 読む：集計は「その場で数える」or「保存しておく」の二択
* 手を動かす：コメント数/いいね数/ランキングを分類する
* ミニ課題：「リアルタイム性が必要？」を各集計に付ける
* チェック：集計ごとに方針が違ってOK、が理解できたら✅

---

### 第11章：Aggregation Queries（Count / Sum / Avg）で“その場集計”📊

* 読む：Firestoreは集計クエリも用意されてる（使い所を知る）✨ ([Google Cloud][5])
* 手を動かす：一覧画面で「件数だけ知りたい」ケースを想定
* ミニ課題：「件数表示」を集計クエリでやる案を設計
* チェック：集計の“読みコスト”の感覚が出たらOK✅

---

### 第12章：分散カウンタ（シャーディング）で“書き込み集計”を守る🧱

* 読む：頻繁更新カウンタは**分散カウンタ**が定番🥇 ([Firebase][6])
* 手を動かす：いいね数を「shards」方式で持つ案を作る
* ミニ課題：shard数の決め方（最初は少なく→増やす）をメモ
* チェック：高頻度更新＝分散の発想が出ればOK✅

---

### 第13章：ランキング設計（Top Nを気持ちよく出す）🥇

* 読む：ランキングは「並べ替えできるスコア」を持つのが基本
* 手を動かす：`score` / `likesCount` / `hotScore` などを設計
* ミニ課題：日次/週次ランキングの保存場所を決める
* チェック：ランキングは“別コレクション化”してOKと思えたら✅

---

### 第14章：インデックスの超基本（何が速くなる？何が増える？）🧭

![Index Mechanism](./picture/firebase_firestore_struncture_ts_index_05_index_mech.png)

* 読む：Firestoreはインデックスが命！複合インデックスも理解🛠️ ([Firebase][7])
* 手を動かす：自分のクエリ10個に「必要そうなインデックス」を印をつける
* ミニ課題：配列系（`array-contains`）を使う場所を洗い出す
* チェック：**配列フィールドは複合インデックスで制約がある**のを覚えたらOK✅ ([Firebase][7])

---

### 第15章：インデックス実践（エラー→作成→改善の流れ）🔧

* 読む：“遅い/失敗”はコンソールのインデックス画面で直していく
* 手を動かす：わざと `where + orderBy` を組み合わせて「必要インデックス」を体験
* ミニ課題：インデックス作成の判断フローを1枚にまとめる
* チェック：エラー文を見て落ち着けるようになったらOK✅

---

### 第16章：`orderBy` の罠（存在しないフィールドは落ちる）🕳️

* 読む：`orderBy()` はそのフィールドが無いドキュメントを結果から外す⚠️ ([Firebase][8])
* 手を動かす：`createdAt` を必ず入れる設計にする
* ミニ課題：必須フィールドを「作成時に自動で埋める」方針を決める
* チェック：検索の安定性＝設計で作る、が理解できたら✅

---

### 第17章：複数範囲クエリと制約（2026の重要ポイント）📏

* 読む：複数フィールドの範囲/不等号も使えるが、制限がある🧠 ([Firebase][9])
* 手を動かす：「検索フィルタUI」を想定して、許される組み合わせを整理
* ミニ課題：やりたい検索が無理なら“検索用フィールド”を作る案を考える
* チェック：「クエリが無理なら保存形を変える」が出たらOK✅

---

### 第18章：ページング設計（無限スクロールの作法）📜

* 読む：ページングは `limit + cursor(startAfter等)` の安定運用が大事
* 手を動かす：一覧クエリの「次ページ条件」を設計
* ミニ課題：並び順が変わるとページングが壊れる例を想像して対策
* チェック：**ソートキーは必須**、が腹落ちしたら✅

---

### 第19章：TypeScriptで“型安全CRUD”（DTO/Converter/ガード）🧱✨

* 読む：Firestoreの型は“Converterで守る”のが王道💪（`withConverter`） ([Firebase][10])
* 手を動かす：`PostDTO / CommentDTO` を作り、読み書きにConverterを挟む
* ミニ課題：**「Firestoreに保存する形」と「UIで使う形」**を分ける（DTOを作る）
* チェック：`doc.data()` に型が付いて気持ちよくなったら勝ち✅

---

### 第20章：整合性を“サーバー側”で守る（Functions / Cloud Run / AI）⚙️🤖

* 読む：集計や整合性は、クライアント任せにしないのが安全😇
* 手を動かす：

  * Node.jsのFunctions（2nd gen）で「コメント追加→コメント数更新」を設計
  * 本日時点で **Node.js 22 / 20** が選べる（Firebase Functionsのランタイム） ([Firebase][11])
  * Pythonも **python311 / python310** のランタイム指定が可能（同ページ） ([Firebase][11])
  * .NETは「Firebase Functions」ではなく、必要なら **Cloud Run functions** 側（.NETも対象）という整理にする ([Google Cloud Documentation][12])
* ミニ課題：AI生成結果をFirestoreに保存する「監査ログ」設計

  * 例：`aiLogs` に `{ model, promptHash, createdAt, userId, action }` など
  * Firebase AI LogicはクライアントSDK＋App Check＋レート制限などの考え方がある ([Firebase][1])
* チェック：クライアント改ざんでも“壊れにくい設計”になったらOK✅

---

## AIで設計が爆速になる「使い方テンプレ」🤖⚡（Antigravity / Gemini CLI）

![AI Design Assistant](./picture/firebase_firestore_struncture_ts_index_07_ai_assistant.png)

* Antigravityは“エージェントが計画→実行→検証”まで回す思想の開発環境（Mission Control的な使い方） ([Google Codelabs][13])
* Gemini CLIはターミナルで動くAIエージェント（ReActで作業を進める） ([Google for Developers][14])

### すぐ使える依頼例（コピペ用）📎

1. **スキーマ案を2〜3パターン出して比較**

   * 「記事/コメント/ユーザーをFirestoreで設計。サブコレ案とトップレベル案を比較して、想定クエリと必要インデックスも列挙して」

2. **インデックスの抜けを洗う**

   * 「このクエリ一覧に必要な複合インデックスを推定して、運用で困るポイントも教えて」

3. **DTO/Converter雛形を自動生成**

   * 「PostDTO/CommentDTOの型、FirestoreDataConverter(withConverter)の雛形、validation方針を生成して」

4. **集計方針の安全レビュー**

   * 「いいね数/コメント数/ランキングを、衝突・改ざん・コスト観点でレビューして」

5. **AIログ設計レビュー（AI Logic連携）**

   * 「AIの出力をFirestoreに保存したい。個人情報・トークン・コスト・監査の観点で最小構成を提案して」 ([Firebase][1])

---

## “2026の最新ポイント”として押さえておくメモ🆕

* Firebase Web SDKは **v12.8.0（2026-01-14）** までリリースノート上で確認でき、Node要件なども更新され続けています ([Firebase][15])
* Firestoreのドキュメントサイズは **最大1 MiB**（設計で地味に効く） ([Firebase][16])
* Firebase AI Logicはモデル更新が速く、例えば **Gemini 2.0 Flash系のretire日（2026-03-31）** のように“期限付き情報”が出ます（設計でモデル名/バージョン保存が役立つ） ([Firebase][1])
* Admin SDKの前提として、Pythonは **3.10+推奨（3.9はdeprecated）**、.NETは **.NET 8+推奨（6/7はdeprecated）** の情報が公式に明記されています ([Firebase][17])

---

[1]: https://firebase.google.com/docs/ai-logic "Gemini API using Firebase AI Logic  |  Firebase AI Logic"
[2]: https://firebase.google.com/docs/firestore/data-model "Cloud Firestore Data model  |  Firebase"
[3]: https://docs.cloud.google.com/firestore/native/docs/concepts/structure-data?utm_source=chatgpt.com "Structure data | Firestore in Native mode"
[4]: https://firebase.google.com/docs/firestore/understand-reads-writes-scale?utm_source=chatgpt.com "Understand reads and writes at scale | Firestore - Firebase"
[5]: https://cloud.google.com/blog/products/databases/aggregate-with-sum-and-avg-in-firestore?utm_source=chatgpt.com "Aggregate with SUM and AVG in Firestore"
[6]: https://firebase.google.com/docs/firestore/solutions/counters "Distributed counters  |  Firestore  |  Firebase"
[7]: https://firebase.google.com/docs/firestore/query-data/index-overview?utm_source=chatgpt.com "Index types in Cloud Firestore - Firebase - Google"
[8]: https://firebase.google.com/docs/firestore/query-data/order-limit-data?utm_source=chatgpt.com "Order and limit data with Cloud Firestore - Firebase - Google"
[9]: https://firebase.google.com/docs/firestore/query-data/multiple-range-fields?utm_source=chatgpt.com "Query with range and inequality filters on multiple fields ..."
[10]: https://firebase.google.com/docs/reference/js/v8/firebase.firestore.FirestoreDataConverter?utm_source=chatgpt.com "FirestoreDataConverter | Firebase JavaScript API reference"
[11]: https://firebase.google.com/docs/functions/manage-functions "Manage functions  |  Cloud Functions for Firebase"
[12]: https://docs.cloud.google.com/run/docs/runtimes/function-runtimes?hl=ja "Cloud Run functions ランタイム  |  Google Cloud Documentation"
[13]: https://codelabs.developers.google.com/getting-started-google-antigravity?utm_source=chatgpt.com "Getting Started with Google Antigravity"
[14]: https://developers.google.com/gemini-code-assist/docs/gemini-cli?utm_source=chatgpt.com "Gemini CLI | Gemini Code Assist"
[15]: https://firebase.google.com/support/release-notes/js "Firebase JavaScript SDK Release Notes"
[16]: https://firebase.google.com/docs/firestore/enterprise/quotas-native-mode?utm_source=chatgpt.com "Native mode: Quotas and Limits | Firestore - Firebase - Google"
[17]: https://firebase.google.com/docs/admin/setup "Add the Firebase Admin SDK to your server"
