# 第14章：アカウント設計：同一人物の“統合”（リンク）を理解する🧷

この章は、**「メールで登録した人が、Googleでも入ってきた」**みたいな“あるある衝突”を、ちゃんと **同一人物として統合**する回です🙂🔧
やらないと、**同じ人なのに uid が2つ**になって、Firestore/課金/権限がグチャる未来が見えます…😇🔥

---

## 0) この章でできるようになること🎯✨

* **リンク（連携）**って何かを説明できる🧠🧷
* 「既に別の方法で登録済み」系の衝突を、**ユーザーが迷わない導線**で回避できる🚦🙂
* マイページに **“連携済み一覧（providerData）”** を出して、連携/解除の基本操作ができる👤🔗
* さらに、説明文を **Firebase AI Logic（Gemini）**で“やさしく言い換え”できる🤖📝✨ ([Firebase][1])

---

## 1) まず理解：リンクってなに？🤔🧷

Firebase Auth は、ログインすると **1つのユーザー（= uid）** ができて、そこに

* `password`（メール/パスワード）🔑
* `google.com`（Googleログイン）🌈

みたいな **ログイン方法（プロバイダ）** を「追加で結びつける」ことができます。これが **リンク（link / account linking）** です🧷✨ ([Firebase][2])

---

## 2) 典型パターン：衝突ってどんな時に起きるの？💥😵

## パターンA：Googleでログインしようとしたら「別の方法で登録済み」😇

例：先にメール/パスワードで登録 → 後から同じメールでGoogleログイン
この時に出がちなのが **`auth/account-exists-with-different-credential`** です💣

👉 正攻法はこれ👇

1. まず **既存の方法でログイン**（メール/パスワード）
2. その後、**Googleの資格情報をリンク**🧷✨ ([Firebase][2])

## パターンB：メール登録しようとしたら「そのメールはもう使われてます」😇

例：先にGoogleログイン済み → 後からメール/パスワード登録しようとして衝突
この場合はまず **“ログイン”へ誘導**して、必要なら **パスワードを追加リンク**（後述）って感じが安定です🙂🧷 ([Firebase][2])

---

## 3) 今日作るUI（完成イメージ）🧱🖥️✨

マイページ（MyPage）に、こんなのを置きます👇

* ✅ 連携済み一覧：`password` / `google.com` を表示👀
* 🔗 連携ボタン：Google未連携なら「Googleを連携」🌈
* 🧨 衝突導線：Googleログインで衝突したら

  * 「このメールは別の方法で登録済みだよ🙂」
  * 「メールで続行」ボタン（→ログイン後にリンク）

---

## 4) 手を動かす①：連携済みプロバイダ一覧を出す👤📋✨

まず、ログイン中ユーザーの `providerData` から「何が連携されてるか」を出します🧠
Firebase公式でも、**providerData から providerId を取れる**よって書いてあります🙂 ([Firebase][2])

```ts
import type { User } from "firebase/auth";

export function getLinkedProviderIds(user: User): string[] {
  // providerData は「連携済みログイン方法の一覧」
  return user.providerData.map((p) => p.providerId).filter(Boolean);
}
```

表示例（React）👇

```tsx
const linked = user ? getLinkedProviderIds(user) : [];

return (
  <div>
    <h3>連携済みログイン方法</h3>
    <ul>
      {linked.includes("password") && <li>✅ メール/パスワード</li>}
      {linked.includes("google.com") && <li>✅ Google</li>}
      {!linked.length && <li>まだ未連携（たぶん匿名とか）</li>}
    </ul>
  </div>
);
```

---

## 5) 手を動かす②：ログイン中に「Googleを連携」ボタンを作る🌈🔗

これは一番シンプルなリンクです🙂
Firebase公式は **`linkWithPopup(auth.currentUser, provider)`** を案内してます💡 ([Firebase][2])

```ts
import { getAuth, linkWithPopup, GoogleAuthProvider } from "firebase/auth";

export async function linkGoogleToCurrentUser() {
  const auth = getAuth();
  const provider = new GoogleAuthProvider();

  if (!auth.currentUser) throw new Error("ログインしてないよ😇");

  await linkWithPopup(auth.currentUser, provider);
  // これで「同じ uid に google.com が追加」される🎉
}
```

## ⚠️ つまずき注意：Popupは“クリック直後”に呼ぶ🖱️🚫

`signInWithPopup` / `linkWithPopup` は、クリックから離れたタイミングで呼ぶと **ブラウザにブロックされがち**です😵
公式でも「ユーザー操作から直接呼んでね」的な注意があります🧠

---

## 6) 手を動かす③：衝突（account-exists〜）を“リンク導線”に変える🚦🧷✨

ここが本番🔥
Googleログインで衝突したとき、公式の流れはざっくりこう👇

1. Googleログインを試す
2. `auth/account-exists-with-different-credential` なら

   * `error.customData.email`（メール）と
   * `error.credential`（リンク用の資格情報）
     を保持する
3. 既存方法でログインしてもらう
4. `linkWithCredential(currentUser, pendingCred)` で統合🧷✨ ([Firebase][2])

## 6-1) 状態（pending）を持つ型を作る📦

```ts
import type { AuthCredential } from "firebase/auth";

export type PendingLink = {
  email: string;
  pendingCred: AuthCredential;
};
```

## 6-2) Googleログイン関数（衝突したら pending を返す）🌈💥

```ts
import { getAuth, GoogleAuthProvider, signInWithPopup } from "firebase/auth";
import type { PendingLink } from "./pendingLink";

export async function signInWithGoogleOrStartLinking(): Promise<PendingLink | null> {
  const auth = getAuth();
  const provider = new GoogleAuthProvider();

  try {
    await signInWithPopup(auth, provider);
    return null; // 普通にログイン成功🎉
  } catch (e: unknown) {
    const code = typeof e === "object" && e && "code" in e ? String((e as any).code) : "";

    if (code === "auth/account-exists-with-different-credential") {
      const email =
        (e as any).customData?.email ??
        (e as any).email ??
        "";

      const pendingCred = (e as any).credential as unknown;

      if (!email || !pendingCred) {
        throw new Error("衝突は検知したけど、リンク情報が取れなかった…😇");
      }

      return { email, pendingCred: pendingCred as any };
    }

    throw e; // それ以外は上に投げる
  }
}
```

> `customData.email` や `error.credential` を使う形は公式ドキュメント側で説明があります🙂

## 6-3) 「メールで続行」→ ログイン後にリンク🧷🔑✨

```ts
import { getAuth, signInWithEmailAndPassword, linkWithCredential } from "firebase/auth";
import type { PendingLink } from "./pendingLink";

export async function finishLinkingByEmailPassword(p: PendingLink, password: string) {
  const auth = getAuth();

  // ① まず既存方法でログイン
  await signInWithEmailAndPassword(auth, p.email, password);

  // ② そのユーザーに、さっきのGoogle資格情報をリンク
  if (!auth.currentUser) throw new Error("ログイン後なのに currentUser がいない😇");

  await linkWithCredential(auth.currentUser, p.pendingCred);

  // これで「同一人物に統合」🎉
}
```

---

## 7) ⚠️ ありがちな落とし穴まとめ（ここ超大事）🧨🧠

## 落とし穴A：`fetchSignInMethodsForEmail()` で判定しようとして詰む😵

昔のチュートリアルだと「そのメールがどの方法で登録されてるか調べる」みたいに `fetchSignInMethodsForEmail()` を使いがちなんだけど、**Email enumeration protection がONだと無効化される**（新しいプロジェクトは既定でON）って公式に書かれてます🧯 ([Firebase][3])

👉 だからこの章では、**「衝突したらユーザーに選ばせる（メールで続行）」**みたいな設計に寄せるのが安全🙂✅

## 落とし穴B：unlinkすると「次回ログインで別 uid になる」😱

Firebase公式は、**unlinkした後に同じプロバイダでログインすると“別ユーザー”が新規作成される**って明言してます💥 ([Firebase][2])
👉 解除ボタンを付けるなら、**「本当に外す？戻れないよ？」**の警告は必須🙂⚠️

## 落とし穴C：すでに別 uid に資格情報が紐づいてたらリンク失敗😇

`linkWithCredential` は、資格情報が別ユーザーに紐づいてると失敗して、**データ統合（マージ）を自分で設計しなきゃいけない**です🧠🔥 ([Firebase][2])
初心者のうちは、まず **“二重 uid を作らない運用”** を目標にするのが正解🙂✅

---

## 8) AIでUX強化：衝突メッセージをGeminiに“やさしく言い換え”させる🤖📝✨

たとえば衝突時に、固定文じゃなくて
「今の状況（エラーコード/次に押してほしいボタン）を、やさしい日本語にする」
みたいな用途が相性いいです🙂💕

Firebase AI Logic のWeb側は `firebase/ai` で使えます🧠 ([Firebase][1])
※ 2026-02-16 時点で、**`gemini-2.0-flash` / `gemini-2.0-flash-lite` は 2026-03-31 に提供終了予定**と書かれてるので、モデル名は新しめを使うのが安心です🧯 ([Firebase][1])

```ts
import { getAI, getGenerativeModel } from "firebase/ai";
import { getApp } from "firebase/app";

export async function aiExplainAccountLinking(email: string) {
  const ai = getAI(getApp());
  const model = getGenerativeModel(ai, { model: "gemini-2.5-flash-lite" });

  const prompt = `
ユーザー向けの短い説明文を作って。
状況: 「${email}」は別の方法で登録済み。今はメール/パスワードでログインしてからGoogleを連携してほしい。
トーン: やさしい、日本語、短め、絵文字少し。
`;

  const res = await model.generateContent(prompt);
  return res.response.text();
}
```

---

## 9) Antigravity / Gemini CLI の使いどころ🚀🔎

## Antigravity（エージェント）🚀

「衝突導線（pending保持→メールで続行→linkWithCredential）を実装して」みたいに、**まとまったタスクを丸投げ**しやすいタイプです🙂🧰 ([Google Codelabs][4])

## Gemini CLI🔎

ターミナルでリポジトリ全体を見ながら、
「未処理のAuthエラーコードを洗い出して」
「リンク導線の抜け（popupブロック、pending消失）をチェックして」
みたいな **レビュー/点検**が得意です🧠✨ ([Google Cloud Documentation][5])

---

## 10) ミニ課題🎒✨

1. マイページに「連携済み：メール/Google」を表示👤📋
2. Google未連携なら「Googleを連携」ボタンを出す🌈🔗
3. Googleログイン衝突時に、

   * 「メールで続行」フォーム（パスワード入力）を出す🔑
   * 成功したら `linkWithCredential` で統合🧷🎉
4. おまけ：説明文「AIに聞く」ボタン🤖📝

---

## 11) チェックリスト✅✅✅

* [ ] 同じメールで「メール→Google」でも別人（uid違い）にならない🙂
* [ ] `auth/account-exists-with-different-credential` が出ても、ユーザーが迷子にならない🚦
* [ ] `providerData` に `password` / `google.com` が反映される👀
* [ ] unlinkを入れるなら、**警告つき**になってる⚠️ ([Firebase][2])
* [ ] `fetchSignInMethodsForEmail()` に依存してない（依存してもフォールバックあり）🧯 ([Firebase][3])

---

次の章（第15章：Persistence）に行くと、ログイン維持の“クセ”が絡んでくるので、**第14章で「同一人物＝同一uid」**が固まってるとめちゃ楽になります🙂💪✨

[1]: https://firebase.google.com/docs/ai-logic/get-started "Get started with the Gemini API using the Firebase AI Logic SDKs  |  Firebase AI Logic"
[2]: https://firebase.google.com/docs/auth/web/account-linking "Link Multiple Auth Providers to an Account Using JavaScript  |  Firebase"
[3]: https://firebase.google.com/docs/auth/web/email-link-auth "Authenticate with Firebase Using Email Link in JavaScript"
[4]: https://codelabs.developers.google.com/getting-started-google-antigravity "Getting Started with Google Antigravity  |  Google Codelabs"
[5]: https://docs.cloud.google.com/gemini/docs/codeassist/gemini-cli?utm_source=chatgpt.com "Gemini CLI | Gemini for Google Cloud"
