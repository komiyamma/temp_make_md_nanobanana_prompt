# 第8章：一覧に強い設計（“並べ替え”から逆算）📜✨

この章は「記事一覧（フィード）」みたいな**“並べて見せる画面”**を、あとで詰まない形で設計する回だよ〜！😄
Firestoreは「JOINしない」ぶん、**一覧の出し方（orderBy/limit）で、保存する形がだいたい決まる**のがポイント🔥

---

## 1) 一覧設計の結論：まず“並べ方”を決める 🧠➡️📜

一覧画面って、結局これ👇のセットでできてるよね？

* どれを出す？（絞り込み：where）🔎
* どう並べる？（並び替え：orderBy）🧷
* 何件だけ？（limit）🍱
* 次のページは？（cursor：startAfter / startAt）📄➡️📄

Firestore公式でも、一覧は **orderBy + limit** を基本にして組み立てる流れが示されてるよ。([Firebase][1])

---

## 2) まず決める「記事一覧」の仕様（例）📰✨

題材の「記事（posts）」で、よくある一覧を3つ作ると超実践的👇

1. **新着順フィード**：最新の記事を上に 📅⬇️
2. **自分の投稿一覧**：自分のだけ見たい 🙋‍♂️
3. **人気順**：いいね多い順 ❤️⬇️

この3つを満たすように、フィールドを逆算しよう💡

---

## 3) ソートキー設計の鉄板ルール 🧱🔑

## ルールA：一覧で並べたいフィールドは「必ず全ドキュメントに入れる」✅

Firestoreの注意点として、**orderBy に使ったフィールドが存在しないドキュメントは、結果から外れる**んだ😱
（つまり、createdAt が無い記事は一覧に出てこない）([Firebase][1])

なので posts には最低これを“必須”にするのが安定👇

* createdAt（作成日時）🕒
* updatedAt（更新日時）🔁（必要なら）

## ルールB：一覧は “同点” が怖い（安定ソートが必要）⚠️

createdAt だけで並べると、**同じ時刻**が出ることがある（特に短時間に連続投稿した時）😵‍💫
このとき「ページング（次のページ）」が**重複したり、抜けたり**しやすい。

Firestore公式のカーソル説明でも、**カーソルに使うフィールド値が同じだと期待した挙動にならないことがある**って明言されてるよ。([Firebase][2])

👉 対策は2択！

* 対策①：**DocumentSnapshot をカーソルに使う**（一番ラク）📸
* 対策②：**第二ソートキー**を用意する（例：createdAt + postId）🧷🧷

---

## 4) ページング設計の基本（この章の最重要）📜➡️📜✨

Firestoreの推奨パターンはこれ👇

* まず limit で1ページ
* 次ページは startAfter（or startAt）で続き
* カーソルは **DocumentSnapshot** を渡せる（値を手で並べなくていい）([Firebase][2])

## ✅おすすめ：Snapshotカーソル方式（簡単で事故りにくい）📸

ポイントはこれだけ👇

* 「最後に表示したドキュメント（lastDoc）」を覚える
* 次の取得は startAfter(lastDoc)

---

## 5) 手を動かす：Reactで“新着順一覧＋もっと読む”を作る ⚛️🔥

ここでは posts を「新着順」で20件ずつ表示して、ボタンで追加読み込みするよ👍

## まず想定する posts のフィールド例 🧩

* title（文字）
* body（文字）
* createdAt（Timestamp）🕒
* authorId（文字）🙋‍♂️
* likesCount（数）❤️（人気順で使う）

## コード例（Firestore v9+ のモジュラーAPI）🧱

```ts
import { useEffect, useState } from "react";
import {
  collection,
  getDocs,
  limit,
  orderBy,
  query,
  startAfter,
  QueryDocumentSnapshot,
  DocumentData,
} from "firebase/firestore";
import { db } from "./firebase"; // 自分の初期化済みFirestore

type Post = {
  title: string;
  body: string;
  createdAt: any; // Timestamp（型は後でConverterでキレイにする）
  authorId: string;
  likesCount?: number;
};

export function PostsList() {
  const [posts, setPosts] = useState<(Post & { id: string })[]>([]);
  const [lastDoc, setLastDoc] = useState<QueryDocumentSnapshot<DocumentData> | null>(null);
  const [loading, setLoading] = useState(false);

  async function loadFirstPage() {
    setLoading(true);
    try {
      const q = query(
        collection(db, "posts"),
        orderBy("createdAt", "desc"),
        limit(20)
      );

      const snap = await getDocs(q);

      const items = snap.docs.map((d) => ({ id: d.id, ...(d.data() as Post) }));
      setPosts(items);
      setLastDoc(snap.docs.length ? snap.docs[snap.docs.length - 1] : null);
    } finally {
      setLoading(false);
    }
  }

  async function loadMore() {
    if (!lastDoc) return;

    setLoading(true);
    try {
      const q = query(
        collection(db, "posts"),
        orderBy("createdAt", "desc"),
        startAfter(lastDoc),
        limit(20)
      );

      const snap = await getDocs(q);

      const items = snap.docs.map((d) => ({ id: d.id, ...(d.data() as Post) }));
      setPosts((prev) => [...prev, ...items]);
      setLastDoc(snap.docs.length ? snap.docs[snap.docs.length - 1] : lastDoc);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadFirstPage();
  }, []);

  return (
    <div>
      <h2>新着記事</h2>

      {posts.map((p) => (
        <div key={p.id} style={{ padding: 12, borderBottom: "1px solid #ddd" }}>
          <div style={{ fontWeight: 700 }}>{p.title}</div>
          <div style={{ opacity: 0.8 }}>{p.body}</div>
        </div>
      ))}

      <button onClick={loadMore} disabled={loading || !lastDoc}>
        {loading ? "読み込み中…" : lastDoc ? "もっと読む" : "これ以上ありません"}
      </button>
    </div>
  );
}
```

🎉 これで「並び順がブレにくい一覧＋ページング」ができる！
カーソルの考え方はFirestore公式の “query cursors” の説明と同じ流れだよ。([Firebase][2])

---

## 6) よくある事故パターン（先に踏んでおく）💥😇

## 事故1：createdAt を入れ忘れて “消える記事” が出る 👻

orderBy に使うフィールドが無いと、結果から外れることがある⚠️([Firebase][1])
✅ 対策：作成時に必ず createdAt を入れる（必須フィールド化）

## 事故2：ページングが重複／抜ける 📄💫

同じ createdAt が続くと、カーソルが曖昧になりやすい⚠️([Firebase][2])
✅ 対策：Snapshotカーソル or 第二キー

---

## 7) ミニ課題 🎯（“一覧設計”を自分のものにする）

## 課題A：自分の投稿一覧を作る 🙋‍♂️🗂️

* 絞り込み：authorId が自分
* 並び：createdAt desc
* limit 20 / startAfter

（where + orderBy を組み合わせると、プロジェクトによってはインデックスが必要になることがあるよ。インデックスは後の章でがっつりやる🛠️）

## 課題B：人気順タブを作る ❤️🥇

* 並び：likesCount desc
* 同点対策：createdAt desc を第二キーにする（またはSnapshotカーソル）

---

## 8) AIで“一覧設計”を爆速にする 🤖⚡（Antigravity / Gemini CLI）

## 使える根拠（最新）

* Firebaseの **MCPサーバー**は、Antigravity や Gemini CLI などのMCPクライアントで使える（Firestore操作やRules理解なども支援）って公式に書かれてるよ。([Firebase][3])
* Firestoreは **Gemini CLI向けの専用拡張**も推していて、拡張がMCPサーバーを内包してセットアップを楽にする方針が明記されてる。([Google Cloud Documentation][4])
* Gemini CLIのFirebase拡張は、MCPサーバー設定やFirebase向けプロンプトを提供することが説明されてる。([Firebase][5])
* Antigravity自体も、エージェントが計画→実行→検証までやる“agentic開発”として説明されてる。([Google Codelabs][6])

## コピペで効く依頼文（一覧設計編）📎✨

* 「posts の一覧画面（新着/自分/人気）を作りたい。必要フィールド案、クエリ（where/orderBy/limit/startAfter）案、同点対策まで3案で比較して」
* 「createdAt が同時刻になるケースでページングが壊れない設計にして。Snapshotカーソル方式と第二キー方式のメリデメを出して」
* 「このクエリで将来インデックス地獄になりそうな箇所を先に指摘して」

---

## 9) Firebase AI Logic を絡めるなら：ログ一覧も“同じ設計”で作る 🧠📝🤖

AI機能を入れると「生成履歴」「監査ログ」「レビュー履歴」みたいな**ログ一覧**がすぐ欲しくなるよね👀
そのときも第8章の考え方がそのまま効く！

例：aiLogs コレクション

* createdAt（必須）🕒
* userId（絞り込み用）🙋‍♂️
* model（例：gemini-2.5-flash）🧠
* action（レビュー/要約/生成など）🏷️

特にモデル名は、モデルが退役することがあるので「ログに残す」価値が高いよ📌
Firebase AI Logicのドキュメントでも、モデルの退役（例：2026-03-31 退役の注意）や、移行の考え方が案内されてる。([Firebase][7])

---

## 10) チェック✅（理解できたら勝ち！）

* ✅ 一覧は「where / orderBy / limit / cursor」でできてる
* ✅ orderBy に使うフィールドは **全ドキュメントに必須**（無いと出ないことがある）([Firebase][1])
* ✅ 同点があるとページングが壊れやすい → **Snapshotカーソル or 第二キー**([Firebase][2])
* ✅ AIに「仕様→クエリ→フィールド→同点対策」までレビューさせると設計が一気に固まる🤖✨([Firebase][3])

---

次の章（第9章）は、この一覧が伸びた時に起きる **ホットスポット（書き込み衝突）🔥** に入るよ！
「いいね数」や「コメント数」をどう持つかが、ここから一気に面白くなる😆💥

[1]: https://firebase.google.com/docs/firestore/query-data/order-limit-data "Order and limit data with Cloud Firestore  |  Firebase"
[2]: https://firebase.google.com/docs/firestore/query-data/query-cursors "Paginate data with query cursors  |  Firestore  |  Firebase"
[3]: https://firebase.google.com/docs/ai-assistance/mcp-server "Firebase MCP server  |  Develop with AI assistance"
[4]: https://docs.cloud.google.com/firestore/native/docs/connect-ide-using-mcp-toolbox "Use Firestore with MCP, Gemini CLI, and other agents  |  Firestore in Native mode  |  Google Cloud Documentation"
[5]: https://firebase.google.com/docs/ai-assistance/gcli-extension "Firebase extension for the Gemini CLI  |  Develop with AI assistance"
[6]: https://codelabs.developers.google.com/getting-started-google-antigravity "Getting Started with Google Antigravity  |  Google Codelabs"
[7]: https://firebase.google.com/docs/ai-logic/get-started "Get started with the Gemini API using the Firebase AI Logic SDKs  |  Firebase AI Logic"
