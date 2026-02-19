# 第14章：インデックスの超基本（何が速くなる？何が増える？）🧭🛠️

## この章のゴール🎯

* クエリ（`where / orderBy / limit`）を見るだけで、**「単一フィールドで足りる？複合が要る？」**がざっくり判断できる👀✨
* インデックスが増えると何が起きるか（**速さ・書き込み・コスト**）をイメージできる💰🧱
* **配列（`array-contains`）まわりの“地雷”**を先に踏んで安全になる💣➡️✅

---

## 1) Firestoreは「全部インデックスで動く」📚➡️🚀

Firestoreは、基本的に**どのクエリもインデックスを使って高速化**する設計です。だから、**クエリの速さは「DBの総件数」より「結果セットのサイズ」に依存しやすい**、という思想になってます。([Firebase][1])

そして超大事ポイント👇
インデックスは「そのフィールドを持つドキュメント」しか載らないことがあるんです。
**複合インデックスの場合、指定した全フィールドに値が入ってないドキュメントは、インデックスに載らない＝そのクエリでは絶対に出てこない**、という挙動になります😇([Firebase][1])

> だから「`createdAt` 入れてない記事が一覧に出ない😱」みたいな事故が起きます（第16章で深掘りするやつ）。

---

## 2) インデックスは2種類だけ覚えればOK✅

![Index Types](./picture/firebase_firestore_struncture_ts_study_014_01_index_types.png)

## A. 単一フィールドインデックス（Single-field）🧱

* Firestoreは基本、**各フィールドに対して単一フィールドインデックスを自動で作る**よ（ascending/descending など）([Firebase][1])
* 配列フィールドには `array-contains` 用の単一フィールドインデックスも自動で作られる（概念として）([Firebase][1])
* 例：

  * `where('authorId','==', uid)`
  * `orderBy('createdAt','desc')`
    みたいな“単発”は、単一フィールドで済むことが多い👍

さらに、節約テクとして👇
「このフィールド、検索に使わないしデカい…」みたいなのは、**単一フィールドの自動インデックス対象から外す（exemption/fieldOverrides）**もできるよ。
ただし、**単一フィールドで外しても、複合インデックス側では索引できる**点がポイント😉([Firebase][1])

## B. 複合インデックス（Composite）🧩

* `where` と `orderBy` を組み合わせたり、複数条件で絞り込むと、**複合インデックスが必要**になりがち。([Firebase][1])
* 複合インデックスは自動作成されない（組み合わせが多すぎるから）。足りないときはエラーとリンクで教えてくれる。([Firebase][1])
* **重要：複合インデックスには「配列フィールドは最大1つ」制約がある**⚠️([Firebase][1])

---

## 3) 何が速くなる？何が増える？（ここが設計の勘どころ）⚖️💰

![Performance vs Cost](./picture/firebase_firestore_struncture_ts_study_014_02_cost_balance.png)

## 速くなる🚀

* インデックスで目的の範囲を“目次から引く”ので速い📚([Firebase][1])

## 増える（＝コスト/負荷が上がる）📈

* **ストレージ**：保存するデータには、**メタデータや自動インデックス/複合インデックスのオーバーヘッド**が乗る([Firebase][2])
* **書き込み負荷**：ドキュメントを1回書くと、関連するインデックスの更新も必要になる（＝書き込みが重くなる方向）([Google Cloud Documentation][3])
* **読み課金のクセ**：クエリは「返したドキュメントの読み」だけじゃなく、条件次第で**インデックスエントリの読み**も課金対象になりうる（Query Explainで確認できる）([Firebase][4])

> 雑に言うと：
> ✅ インデックスは“読む”を楽にする
> ⚠️ その代わり“書く”と“保存容量”にツケが回りがち

---

## 4) “あなたのクエリ10個”にインデックス印をつける方法✍️🔎

第1章で書いた「必要なクエリ10個」を見ながら、これをやってください👇

## ステップ①：クエリを3行で分解🧩

![Query Decomposition](./picture/firebase_firestore_struncture_ts_study_014_03_query_decomposition.png)

各クエリをこう書き換える✍️

* フィルタ：`where` は何？（等号？範囲？配列？）
* 並び：`orderBy` は何？
* 件数：`limit` は？（これはインデックス要否に直結しないけど設計に大事）

## ステップ②：ざっくり判定ルール（最初はこれでOK）✅

![Index Decision Flow](./picture/firebase_firestore_struncture_ts_study_014_07_decision_flow.png)

* `where` 1個だけ（等号） → 単一フィールドでいけることが多い
* `orderBy` だけ → 単一フィールドでいけることが多い
* `where` + `orderBy`（別フィールド） → 複合が要りやすい
* `where` が複数（特に + `orderBy`） → 複合が要りやすい
* `array-contains` を使う → 複合にするとき**配列フィールドは1つだけ**⚠️([Firebase][1])

---

## 5) 配列系（`array-contains`）の“ありがち事故”💥➡️✅

![Array Trap](./picture/firebase_firestore_struncture_ts_study_014_04_array_trap.png)

## 事故①：`array-contains` は同じORグループで1つだけ😇

Firestoreは、OR条件（`or` / `in` / `array-contains-any` など）を含むとき、
**1つのORグループ内で `array-contains` は最大1つ**、さらに **`array-contains` と `array-contains-any` は同じグループで混ぜられない** です⚠️([Firebase][5])

## 事故②：複合インデックス側も「配列フィールドは最大1つ」🧨

つまり、例えば「タグANDタグAND…」みたいな世界は、**素直にやると詰みやすい**です。
→ 対策は第17章以降でやる「検索用フィールド」や「検索用コレクション」寄せが現実的になります🧠✨

---

## 6) コレクション vs コレクショングループ（サブコレ絡みの注意）🧩

![Collection Group Query](./picture/firebase_firestore_struncture_ts_study_014_05_collection_group.png)

サブコレを使っていると、**collection group query**（全親をまたいで `comments` を検索）を使う場面が出ますよね。

ここで注意：
単一フィールドインデックスは、**コレクショングループスコープはデフォで維持されない**（＝必要なら設定が絡む）という前提があります。([Firebase][1])

この章の段階では、まずは
「**サブコレを横断するクエリは、インデックス設計が一段むずい**」
だけ覚えればOKです😄（実践は第15章で体験する！）

---

## 7) 手を動かす（TypeScript）🖐️🔥

ここでは「日報/記事/コメント」題材っぽいクエリ例を3つだけ書いて、**“どれが複合くさそう？”**を感じます。

## 例1：記事一覧（新着順）📰

```ts
import { collection, getDocs, limit, orderBy, query } from "firebase/firestore";
import { db } from "./firebase";

export async function listLatestPosts() {
  const ref = collection(db, "posts");
  const q = query(ref, orderBy("createdAt", "desc"), limit(20));
  return getDocs(q);
}
```

* これは単一フィールド（`createdAt`）で済むことが多い👍
* ただし `orderBy()` は **そのフィールドが存在するドキュメントしか結果に入らない**点に注意！([Firebase][6])

## 例2：自分の記事一覧（自分で絞って新着順）🙋‍♂️📰

```ts
import { collection, getDocs, limit, orderBy, query, where } from "firebase/firestore";
import { db } from "./firebase";

export async function listMyPosts(uid: string) {
  const ref = collection(db, "posts");
  const q = query(
    ref,
    where("authorId", "==", uid),
    orderBy("createdAt", "desc"),
    limit(20)
  );
  return getDocs(q);
}
```

* `where(authorId==)` + `orderBy(createdAt)`
  → **複合インデックスが必要になりやすい**タイプ💡（第15章でわざとエラー出すと超わかる）

## 例3：タグで絞って新着順（配列）🏷️📰

```ts
import { collection, getDocs, limit, orderBy, query, where } from "firebase/firestore";
import { db } from "./firebase";

export async function listPostsByTag(tag: string) {
  const ref = collection(db, "posts");
  const q = query(
    ref,
    where("tags", "array-contains", tag),
    orderBy("createdAt", "desc"),
    limit(20)
  );
  return getDocs(q);
}
```

* 配列系が絡むと、**複合インデックスの“配列1つ制限”**が効いてくる可能性がある⚠️([Firebase][1])

---

## 8) ミニ課題🧪✨（第15章への仕込み）

あなたの「クエリ10個」に、次のマークを付けてください👇

* ✅（単一で行けそう）：`where` 1個だけ / `orderBy` だけ
* 🧩（複合くさそう）：`where` + `orderBy`（別フィールド） / 条件複数
* 🏷️（配列注意）：`array-contains` / `array-contains-any` が入る
* 🧨（設計変更候補）：タグAND、検索UIが欲張りすぎ、みたいなやつ

最後に、🧩と🏷️のクエリだけ抜き出して
「**どのフィールドの組み合わせが必要？**」を1行メモしておく📝

---

## 9) AIで“インデックス抜け”を最短レビュー🤖⚡

![AI Index Review](./picture/firebase_firestore_struncture_ts_study_014_06_ai_review.png)

ここ、AIがめちゃくちゃ刺さります👇（設計の見落とし検知が得意）

## Geminiに投げるテンプレ（コピペ）📎

* **インデックス推定**

  * 「このクエリ一覧（10個）を見て、単一/複合の必要性を分類して。複合は `collectionGroup` と `fields(order/arrayConfig)` の形で候補も出して」
* **配列地雷チェック**

  * 「`array-contains` / `array-contains-any` を含むクエリの制約（同じORグループ、複合の配列1つ制限）に違反しそうなものを指摘して」([Firebase][5])
* **コスト観点の確認**

  * 「このクエリはインデックスエントリ読み課金が発生しそう？Query Explainで見たい観点も教えて」([Firebase][4])

---

## 10) チェック✅（自分で答えられたら勝ち）

* インデックスが増えると、主に何が増える？（2つ）💰🧱
  → **ストレージのオーバーヘッド**、**書き込み側の負荷/コスト**（＋条件次第でインデックスエントリ読み課金も）([Firebase][2])
* `where(authorId==)` + `orderBy(createdAt)` が複合になりやすい理由は？🧩
  → **複数フィールドを並べ替え/絞り込みで同時に使うから**（単一だけじゃ足りないことがある）([Firebase][1])
* 複合インデックスで配列は最大いくつ？🏷️
  → **1つ**([Firebase][1])

---

次の第15章では、今マークした🧩のクエリをわざと実行して、**「エラー文→リンク→インデックス作成→改善」**を“儀式”として体に入れます🔧😄
この第14章ができてると、エラーにビビらなくなります👍

[1]: https://firebase.google.com/docs/firestore/query-data/index-overview "Index types in Cloud Firestore  |  Firebase"
[2]: https://firebase.google.com/docs/firestore/pricing?utm_source=chatgpt.com "Understand Cloud Firestore billing | Firebase - Google"
[3]: https://docs.cloud.google.com/firestore/native/docs/understand-reads-writes-scale?utm_source=chatgpt.com "Understand reads and writes at scale | Firestore in Native ..."
[4]: https://firebase.google.com/docs/firestore/pricing "Understand Cloud Firestore billing  |  Firebase"
[5]: https://firebase.google.com/docs/firestore/query-data/queries "Perform simple and compound queries in Cloud Firestore  |  Firebase"
[6]: https://firebase.google.com/docs/firestore/query-data/order-limit-data?utm_source=chatgpt.com "Order and limit data with Cloud Firestore - Firebase - Google"