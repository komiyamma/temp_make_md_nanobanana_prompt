# 第15章：インデックス実践（エラー→作成→改善の流れ）🔧

この章は「インデックス怖い😵→インデックス便利😆」に変える回です✨
わざとエラーを起こして、**エラーを読んで→作って→速くする**を“手順として”体に入れます💪🔥

---

## 1) 読む：インデックスは「並べ替えのための名簿」📇✨

## ✅ まず大事な前提（超ざっくり）

* Firestore には **単一フィールドインデックス** と **複合インデックス** の2種類があるよ🧠
* **複合インデックスは自動では増えない**ので、必要になったら自分で作るのが基本👷‍♂️
  → その代わり、足りない時は Firestore が「このインデックス要るよ！」って**エラーで教えてくれる**😄 ([Firebase][1])

## ✅ エラーが出たら勝ち（チャンス）🎯

![Error Workflow](./picture/firebase_firestore_struncture_ts_study_015_01_error_workflow.png)

Firestore のドキュメントにある通り、**複合インデックスが足りない時はエラーに“作成リンク”が含まれる**ので、それを踏むのが最短ルートです🚀

* エラー内リンク → コンソールが開く
* すでにフィールドが自動で埋まってる
* **Create** を押すだけでOK ([Firebase][2])

> ちなみに：等価条件（`==`）で使うフィールドでも、コンソール上は **ASC/DESC を選ぶ必要がある**けど、等価条件の挙動には影響しません（落ち着いて選べばOK）😌 ([Firebase][2])

## ✅ 超重要注意：エミュレータだと“エラーが出ない”ことがある⚠️

![Emulator Warning](./picture/firebase_firestore_struncture_ts_study_015_03_emulator_warning.png)

Firestore エミュレータは **複合インデックスを追跡しない**ので、必要なインデックスがなくてもクエリが通っちゃうことがあります😇
だからこの章の「わざとエラー体験」は、**実際の Firestore（開発用プロジェクト）**でやるのが確実です✅ ([Google Cloud Documentation][3])

---

## 2) 手を動かす：わざとエラーを出して、リンクから作る💥➡️🛠️

ここでは「記事一覧」っぽいクエリで、**where + orderBy** を組み合わせてエラーを出します🔥

## ステップA：失敗するクエリを仕込む😈

例として `posts` コレクションに、こんなフィールドがある想定にします👇

* `authorId: string`
* `status: "public" | "private"`
* `createdAt: Timestamp`

React/TS（Web SDK）のクエリ例：

```ts
import { collection, query, where, orderBy, limit, getDocs } from "firebase/firestore";
import { db } from "./firebase"; // 既に作ってある想定

export async function loadMyPublicPosts(authorId: string) {
  const q = query(
    collection(db, "posts"),
    where("authorId", "==", authorId),
    where("status", "==", "public"),
    orderBy("createdAt", "desc"),
    limit(20)
  );

  const snap = await getDocs(q);
  return snap.docs.map(d => ({ id: d.id, ...d.data() }));
}
```

これを画面（例：マイ記事一覧）で呼び出すと……👇

## ステップB：「The query requires an index」が出たら大成功🎉

ブラウザのコンソールやエラー表示に、だいたいこんな感じの内容が出ます：

* “このクエリにはインデックスが必要です”
* “ここで作れます（Firebase console のリンク）”

Firestore公式ドキュメントでも、この流れ（エラー→リンク→作成）が推奨されています✅ ([Firebase][2])

## ステップC：リンクを開いて Create を押す🛠️✨

![Console UI](./picture/firebase_firestore_struncture_ts_study_015_02_console_ui.png)

1. エラー文の **Create index のリンク**を開く🔗
2. フィールドが自動で入ってるのを確認👀
3. **Create** を押す✅
4. Indexes 画面で **ビルド中のバー**が出るので待つ（データ量によって数分かかることも）⏳ ([Firebase][2])

## ステップD：もう一度同じ画面を開いて成功を確認✅😆

インデックスが有効になると、さっきのクエリが通って一覧が出ます🎊
これで「エラーが出ても直せる」状態に一段上がりました💪✨

---

## 3) 改善：インデックスを“運用できる形”にする📦✅

## ✅ ① コンソールで作ったら、ファイルにも反映する（チーム用）👥

![Indexes File](./picture/firebase_firestore_struncture_ts_study_015_04_indexes_file.png)

Firestore公式は、コンソールで編集したら **ローカルの indexes ファイルも更新してね**と言っています📌 ([Firebase][2])

やり方（代表ルート）👇

## 1) Firestore 設定ファイルを用意

```powershell
firebase init firestore
```

すると `firestore.indexes.json` が作られます（必要なインデックスをここで管理） ([Firebase][2])

## 2) 既存インデックスをエクスポートして差分を埋める

```powershell
firebase firestore:indexes
```

このコマンドでインデックス定義を出せます（コピペして `firestore.indexes.json` を揃える） ([Firebase][4])

## 3) デプロイ

![Deploy Flow](./picture/firebase_firestore_struncture_ts_study_015_05_deploy_flow.png)

```powershell
firebase deploy --only firestore
```

（Rules と indexes をまとめて反映できる） ([Firebase][2])

---

## 4) よくある落とし穴（ここで詰まる😇）🕳️

## 落とし穴①：配列系は「複合インデックスに入れられる配列は1つまで」🎒

`array-contains` など配列系は便利だけど、**複合インデックスでは配列フィールドは1つまで**という制約があります🧠 ([Firebase][1])

## 落とし穴②：インデックスが増えすぎる（上限や作成失敗）📈💥

![Index Building](./picture/firebase_firestore_struncture_ts_study_015_07_building_wait.png)

インデックスの作成が失敗するケースとして、**上限に当たる**などが挙げられています。困ったら「Index building errors」も確認ポイント👀 ([Firebase][5])

## 落とし穴③：エミュレータで通って本番で落ちる⚠️

もう一回！大事なので2回言うやつです🤣
エミュレータは複合インデックスを追跡しないので、本番（実Firestore）で初めて落ちることがあります✅ ([Google Cloud Documentation][3])

---

## 5) AIで“インデックス対応”を爆速にする🤖⚡（Antigravity / Gemini CLI / Firebase AI Logic）

![AI Assistance](./picture/firebase_firestore_struncture_ts_study_015_06_ai_assistance.png)

## ✅ Gemini CLI に「エラー文→必要インデックス→indexes.json化」をやらせる🧠💨

Gemini CLI はターミナルで動くAIエージェントで、ツールやMCPサーバと連携した ReAct ループで作業できます🚀 ([Google Cloud Documentation][6])

**コピペ依頼例**👇

* 「この Firestore エラー全文から、必要な複合インデックスを推定して `firestore.indexes.json` の追記案を出して」
* 「この `where/orderBy` の組み合わせを満たす最小インデックス集合に整理して（重複を削って）」

## ✅ Antigravity で「計画→調査→修正案→検証」を回す🛰️

Antigravity は “Mission Control” 的にエージェントを管理して、調査・実装・検証まで進める思想の開発環境です🧑‍✈️✨ ([Google Codelabs][7])

## ✅ Firebase AI Logic で「設計レビュー用AI」をアプリ内に置く🤖📎

Firebase AI Logic はアプリから Gemini API を呼べて、**レート制限（per-user）も調整可能**なので、開発者向けの「設計レビューボタン」みたいな形にもできます🔐 ([Firebase][8])

**例：AIに投げるネタ**

* 「この画面で使うクエリ一覧（10個）から、必要な複合インデックス候補を列挙して」
* 「インデックスが増えすぎないように、`createdAt` を軸にクエリを揃える設計に直して」

> ついでに：AI検索（ベクター系）をやると、インデックス作成が “コンソールではなくCLIコマンド” になるケースもあるよ、って公式に書かれてます（将来の伏線）🧩 ([Firebase][2])

---

## ミニ課題：インデックス作成の判断フローを1枚にまとめる📝✨

下のテンプレを、自分の言葉で“1枚メモ”にして完成🎯

* ① まずクエリを書く（画面から逆算）📺
* ② 実Firestoreで実行して、エラー出たらリンクを踏む🔗
* ③ コンソールで Create → ビルド完了を確認🛠️⏳
* ④ `firestore.indexes.json` に反映してコミット📦
* ⑤ `firebase deploy --only firestore` で揃える🚀
* ⑥ インデックス増えすぎたら、クエリの形を揃えて減らす✂️✨

---

## チェック✅（ここまでできたら勝ち🏆）

* エラーの「作成リンク」を見ても焦らない😌
* 1つインデックスを作って、クエリが通るのを確認できた😆
* コンソールで作ったインデックスを `firestore.indexes.json` に反映できた📦
* エミュレータに騙されない（実Firestoreで確認する意識がある）🧠 ([Google Cloud Documentation][3])

---

次の章（第16章）は **`orderBy` の罠（フィールド無しで落ちる/結果から消える）**で、また「設計で事故を防ぐ」方向に進めます😇🕳️

[1]: https://firebase.google.com/docs/firestore/query-data/index-overview?utm_source=chatgpt.com "Index types in Cloud Firestore - Firebase - Google"
[2]: https://firebase.google.com/docs/firestore/query-data/indexing "Manage indexes in Cloud Firestore  |  Firebase"
[3]: https://docs.cloud.google.com/firestore/native/docs/emulator "Use Firestore emulator locally  |  Firestore in Native mode  |  Google Cloud Documentation"
[4]: https://firebase.google.com/docs/reference/firestore/indexes "Cloud Firestore Index Definition Reference  |  Firebase"
[5]: https://firebase.google.com/docs/firestore/query-data/indexing?utm_source=chatgpt.com "Manage indexes in Cloud Firestore - Firebase - Google"
[6]: https://docs.cloud.google.com/gemini/docs/codeassist/gemini-cli?utm_source=chatgpt.com "Gemini CLI | Gemini for Google Cloud"
[7]: https://codelabs.developers.google.com/getting-started-google-antigravity?utm_source=chatgpt.com "Getting Started with Google Antigravity"
[8]: https://firebase.google.com/docs/ai-logic/get-started?utm_source=chatgpt.com "Get started with the Gemini API using the Firebase AI Logic ..."