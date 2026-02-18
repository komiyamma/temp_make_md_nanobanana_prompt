# 第6章：認証チェックの基本（ログインしてない人を入れない）🔐✨

今日やることは超シンプルです🙂
**「ログインしてない人は、Firestoreを1文字も読めない・書けない」** を Rules で実現します🚪🛡️
（2026-02-16 時点の公式ドキュメント前提で整理しています）([Firebase][1])

---

## 6-0. まず“脳内モデル”を1枚で🧠🗺️

* アプリ（Reactなど）から Firestore にアクセスするとき、**最終的に判定するのは Firestore Security Rules** です🛡️
* Rules では「このアクセスはログイン済み？」を **request.auth** で見ます👀

  * ログイン済み → request.auth が **nullじゃない**
  * 未ログイン → request.auth が **null** 🙅‍♀️
    ([Firebase][2])

⚠️ 大事：**サーバー用ライブラリ（Admin SDK / Server client libraries）は Rules をバイパス**します（別の守り＝IAM等の世界）🧯
「サーバーで呼ぶから安全」は別の話なので、ここで混ぜないのがコツです🙂([Firebase][3])

---

## 6-1. ルールの最小形：ログイン必須チェック✅🔐

Rulesの“ログイン必須”は、まずこれだけ覚えればOKです👇

* **条件：request.auth != null**

この章は「ログインしてない人を入れない」がゴールなので、まずはコレクション単位でロックします🔒

---

## 6-2. 手を動かす：privateNotes を“ログイン必須”にする🧑‍💻🧯

例として、こういうコレクションを作ったことにします👇

* privateNotes/{noteId}

そしてルールをこうします👇（※この章は“まず入口を閉める”版）

```js
rules_version = '2';

service cloud.firestore {
  match /databases/{database}/documents {

    // ✅ まずは「ここだけ」ログイン必須にする
    match /privateNotes/{noteId} {
      allow read, write: if request.auth != null;
    }

    // ✅ それ以外は何も書かなければ「全部拒否」になる（デフォルト拒否）
  }
}
```

ポイント🙂✨

* Rules は **allow が1個も成立しなければ拒否** です（つまり “書かない＝拒否” が基本で安全）([Firebase][4])
* いきなり全体に「ログインしてたら全部OK」は危険なので、**まずは1コレクションで体験**します🧯

---

## 6-3. 動作確認：未ログインはエラー、ログインは成功👍😱➡️😄

ここでは「認証の状態に応じて UI を分ける」＋「未ログイン時は Firestore が弾く」を体験します✨

### ① React側：ログイン状態で画面を切り替える（最小）🪟✨

やりたいことはこれ👇

* 未ログイン → 「ログインしてね🙂」ボタンを出す
* ログイン済み → privateNotes を読んだり書いたりできる

```ts
import { useEffect, useState } from "react";
import { initializeApp } from "firebase/app";
import {
  getAuth,
  onAuthStateChanged,
  signInWithPopup,
  GoogleAuthProvider,
  signOut,
  User,
} from "firebase/auth";
import {
  getFirestore,
  collection,
  addDoc,
  getDocs,
  serverTimestamp,
} from "firebase/firestore";

// ここはあなたのFirebase設定に置き換え
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_AUTH_DOMAIN",
  projectId: "YOUR_PROJECT_ID",
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

export default function PrivateNotesDemo() {
  const [user, setUser] = useState<User | null>(null);
  const [ready, setReady] = useState(false);
  const [log, setLog] = useState<string>("");

  useEffect(() => {
    // ✅ 認証状態が確定するまで待つ（ここ大事！）
    const unsub = onAuthStateChanged(auth, (u) => {
      setUser(u);
      setReady(true);
    });
    return () => unsub();
  }, []);

  const login = async () => {
    const provider = new GoogleAuthProvider();
    await signInWithPopup(auth, provider);
  };

  const logout = async () => {
    await signOut(auth);
  };

  const writeNote = async () => {
    try {
      await addDoc(collection(db, "privateNotes"), {
        text: "Hello private note!",
        createdAt: serverTimestamp(),
      });
      setLog("✅ 書き込み成功！");
    } catch (e: any) {
      setLog("❌ 書き込み失敗: " + (e?.message ?? String(e)));
    }
  };

  const readNotes = async () => {
    try {
      const snap = await getDocs(collection(db, "privateNotes"));
      setLog(`✅ 読み取り成功！件数=${snap.size}`);
    } catch (e: any) {
      setLog("❌ 読み取り失敗: " + (e?.message ?? String(e)));
    }
  };

  if (!ready) return <div>認証状態を確認中…⏳</div>;

  return (
    <div style={{ padding: 16 }}>
      <h2>privateNotes（ログイン必須）🔐</h2>

      {!user ? (
        <>
          <p>未ログインです🙈 まずログインしてね！</p>
          <button onClick={login}>Googleでログイン🔑</button>
        </>
      ) : (
        <>
          <p>ログイン中：{user.uid} ✅</p>
          <button onClick={logout}>ログアウト🚪</button>

          <div style={{ marginTop: 12 }}>
            <button onClick={writeNote}>書く✍️</button>{" "}
            <button onClick={readNotes}>読む📖</button>
          </div>
        </>
      )}

      <p style={{ marginTop: 12 }}>ログ：{log}</p>
    </div>
  );
}
```

### ② 期待する挙動（ここが“勝ち筋”🎯）

* **未ログインで読む/書く** → “Missing or insufficient permissions” 系のエラーになる😱（Rulesが守ってる証拠）
* **ログインして読む/書く** → 成功する😄

この「未ログインで弾ける」をまず体験すると、あとが爆速で理解できます🚀

---

## 6-4. 未ログイン時のUXを1行で決めよう🙂📝

Rulesで弾いても、ユーザー体験はあなたが作れます✨
おすすめはこの3つのどれか👇

1. **ログイン促し型**：「ログインすると使えるよ🙂」🔑
2. **一部だけ公開型**：公開記事は見せる、個人データはログイン必須🔐
3. **完全クローズ型**：ログインしないと何も見せない🙈

この章のミニ課題では **1)** でいきましょう👍

---

## 6-5. つまずきポイント集（先に潰す）💥🧯

**(A) “ログインしてるのに弾かれる”**
→ 多くは「認証状態が確定する前に Firestore を読みにいってる」パターンです😵
onAuthStateChanged で ready を作って、確定してから読むのが安全です⏳✅

**(B) Consoleで直したのに、CLIでデプロイしたら戻った**
→ Firebase CLI は、ローカルの rules を **Console上の既存ルールに上書き**します🧯
チーム運用ほどここで事故りやすいので注意！([Firebase][5])

**(C) “サーバーでAdmin SDK使えばRulesいらない？”**
→ Admin/Server は Rules を通らないので、**クライアントからの入口は Rules が本体**です🚪🛡️([Firebase][3])

---

## 6-6. AIで爆速にする（でも最後は人間が鍵を締める🔑👀）🤖✨

2026-02-16 時点だと、Rules周りは AI 支援がかなり整ってきています🔥
特に **Gemini CLI（Firebase拡張）** の “Security Rules” 向け機能は、**コードを解析してスキーマやアクセスパターンを推測し、最小権限のRules案＋テスト案を作る**方向で案内されています。([Firebase][6])

**使い方イメージ（そのままコピってAIに投げてOK）👇**

* 「privateNotes はログイン必須。将来 ownerUid で本人限定にしたい。今はまず未ログイン拒否だけ入れたい。Rules案と、未ログイン/ログインのテスト観点を出して」
* 「allow read, write を広範囲に書いてしまう事故を避けたい。安全な構造（matchの分け方）で提案して」([Firebase][3])

さらに **Antigravity + Firebase MCP** を使うと、Antigravity 側に Firebase MCP サーバーを追加して、プロジェクトの文脈を見ながら相談しやすい流れが紹介されています🧠🧰([The Firebase Blog][7])

⚠️ ただし：生成AIは間違えます。**本番反映前に必ずレビュー**が公式にも明記されています👀🧯([Firebase][8])

---

## 6-7. ミニ課題🎯✨

**課題：privateNotes を「未ログインは0件」「ログインは読める/書ける」にする**

1. Rules を入れる（この章のコード）🔐
2. React でログインUIを作る🔑
3. 未ログインで readNotes / writeNote を叩いて、エラーを確認😱
4. ログインして同じ操作をして、成功を確認😄

**おまけ（余裕あれば）**

* エラー文をそのまま出さずに「ログインが必要です🙂」に置き換える✨

---

## 6-8. チェック✅✅✅

* 未ログインで Firestore を読もうとすると弾かれる（=Rulesが効いてる）🛡️
* ログインすると読める/書ける😄
* 認証状態が確定するまで UI を待てている⏳
* Rules を “広範囲にゆるく” 書いてない🧯([Firebase][4])

---

## 6-9. 次章への“気持ちいい接続”🔗✨

この章は「入口を閉める」でした🔐
次はもっと気持ちよくなります👇

* **uidごとに自分のデータだけ見える**（王道の users/{uid} へ）👤📁

ちなみに、後半で **Custom Claims（管理者ロール）を付与**するときはサーバー側（Functions等）で Admin SDK を使う流れになります。
そのときの“いまどき目安”はこんな感じです👇（2026-02-16 時点）

* Cloud Functions：Node.js **20 / 22** がフルサポート、18は2025初頭にdeprecated扱い([Firebase][9])
* Admin SDK（.NET）：**.NET 8 以上推奨**（6/7はdeprecated）([Firebase][10])
* Admin SDK（Python）：**Python 3.10 以上推奨**（3.9はdeprecated）([Firebase][11])

---

次の章（第7章）に行くと、**「ログインしてる人の中でも、本人だけ」**に絞るので、さらに安全になりますよ〜🙂🔐✨

[1]: https://firebase.google.com/docs/firestore/security/get-started?utm_source=chatgpt.com "Get started with Cloud Firestore Security Rules - Firebase"
[2]: https://firebase.google.com/docs/firestore/security/rules-conditions?utm_source=chatgpt.com "Writing conditions for Cloud Firestore Security Rules - Firebase"
[3]: https://firebase.google.com/docs/firestore/security/rules-structure?utm_source=chatgpt.com "Structuring Cloud Firestore Security Rules - Firebase - Google"
[4]: https://firebase.google.com/docs/rules/rules-behavior?utm_source=chatgpt.com "How Security Rules work - Firebase - Google"
[5]: https://firebase.google.com/docs/rules/manage-deploy?utm_source=chatgpt.com "Manage and deploy Firebase Security Rules - Google"
[6]: https://firebase.google.com/docs/ai-assistance/prompt-catalog/write-security-rules?utm_source=chatgpt.com "AI Prompt: Write Firebase Security Rules"
[7]: https://firebase.blog/posts/2025/11/firebase-mcp-and-antigravity/?utm_source=chatgpt.com "Antigravity and Firebase MCP accelerate app development"
[8]: https://firebase.google.com/docs/ai-assistance/prompt-catalog?hl=ja&utm_source=chatgpt.com "Firebase の AI プロンプト カタログ | Develop with AI assistance"
[9]: https://firebase.google.com/docs/functions/get-started?utm_source=chatgpt.com "Get started: write, test, and deploy your first functions - Firebase"
[10]: https://firebase.google.com/support/release-notes/admin/dotnet?utm_source=chatgpt.com "Firebase Admin .NET SDK Release Notes"
[11]: https://firebase.google.com/support/release-notes/admin/python?utm_source=chatgpt.com "Firebase Admin Python SDK Release Notes - Google"
