# 第10章：Functionsを守る（CallableでenforceAppCheck）☎️🔒

この章は、「**管理者だけが使える処理**」とか「**課金に直結する処理**」を、**Cloud Functions（Callable）に寄せて**、さらに **App Check で“正規アプリからの呼び出しだけ”に絞る**ところまで一気にやります💪🧿
Callable は **Auth / FCM / App Check トークンが（あれば）自動で付く**ので、守りを固めやすいのが強みです✨ ([Firebase][1])

---

## 0) まずイメージを作ろう🧠🗺️

![Three Defense Layers](./picture/firebase_abuse_prevention_ts_study_010_01_defense_layers.png)

守りのレイヤーはこんな感じです👇

* **Auth**：誰が操作してる？（ログインしてる？管理者？）👤🔑
* **App Check**：その呼び出し元は“本物のあなたのアプリ”？🧿
* **Functions（Callable）**：上の2つが揃ったら「危険な処理」を実行する本丸🏯🔥

そして、この章の主役は **Callable + `enforceAppCheck`** です☎️
Firebase 公式でも、Callable に対して **App Check 強制を有効化する**流れが示されています。 ([Firebase][2])

---

## 1) “守るべき処理”を Callable に寄せるコツ🧲✨

![Moving Logic to Server](./picture/firebase_abuse_prevention_ts_study_010_02_migration.png)

「これ、クライアント（React）から直接やらせたら危ないやつだ…😱」っていう処理は、Callable 側へ引っ越し対象です🏃‍♂️💨

例👇（今回のミニアプリ：メモ＋画像＋AI整形📝📷🤖）

* 管理者だけができる「メモ削除（強制削除）」「通報の処理」🧹🧑‍💼
* 連打されると痛い「画像サムネ生成」「重い集計」「一括処理」📈🔥
* AI を使う「管理者向けの要約」「不適切判定」「レビュー整形」🤖🧾

  * AI は **App Check 推奨**＋**ユーザーごとのレート制限**があるので、コスト破産を避けやすいです💸🛟 ([Firebase][3])

---

## 2) バージョンだけ先に押さえる🔢（ここ大事！）

* Node の Functions は **Node.js 20 / 22 がフルサポート**で、**18 は 2025年初頭に非推奨**になっています。 ([Firebase][4])
* Python Functions も選べて、**Python 3.10〜3.13 をサポート（デフォルト 3.13）**です。 ([Firebase][4])

そして **App Check 強制（`enforceAppCheck`）を使うには**、Functions SDK を **新しめ（`firebase-functions >= 4.0.0`）**にしておくのが公式の手順です。 ([Firebase][2])

---

## 3) 実装（Node/TypeScript）：管理者用 Callable を1本作る🧑‍💼☎️

![Enforcement Gate](./picture/firebase_abuse_prevention_ts_study_010_03_enforcement_mechanism.png)

ここでは「管理者だけができる **メモ削除**」を例にします📝❌
やることはシンプル👇

1. Callable を作る
2. `enforceAppCheck: true` を付ける（ここが主役🧿）
3. Auth で「ログイン必須」
4. Firestore で「管理者か？」を確認
5. 削除する

> 公式の挙動：`enforceAppCheck: true` にすると **App Check トークンが missing / invalid のリクエストは拒否**され、`request.app`（App Check 情報）を使えるようになります。 ([Firebase][2])

## functions/src/index.ts（例）

```ts
import { onCall, HttpsError } from "firebase-functions/v2/https";
import { logger } from "firebase-functions";
import { initializeApp } from "firebase-admin/app";
import { getFirestore } from "firebase-admin/firestore";

initializeApp();
const db = getFirestore();

// ✅ 管理者がメモを削除する（危険なのでCallableに寄せる）
export const adminDeleteMemo = onCall(
  {
    enforceAppCheck: true, // 🧿 App Check 強制（missing/invalid を拒否）
    // region: "asia-northeast1", // 必要なら近いリージョンに（任意）
  },
  async (request) => {
    // 1) App Check 情報（強制ONなので基本は入る想定）
    logger.info("AppCheck appId", { appId: request.app?.appId });

    // 2) Auth（ログイン必須）
    if (!request.auth) {
      throw new HttpsError("unauthenticated", "ログインが必要です🙏");
    }

    const uid = request.auth.uid;

    // 3) 管理者判定（例：/admins/{uid} が存在するか）
    const adminDoc = await db.doc(`admins/${uid}`).get();
    if (!adminDoc.exists) {
      throw new HttpsError("permission-denied", "管理者のみ実行できます🙅‍♂️");
    }

    // 4) 入力チェック
    const memoId = request.data?.memoId as string | undefined;
    if (!memoId) {
      throw new HttpsError("invalid-argument", "memoId が必要です📝");
    }

    // 5) 削除実行（Admin SDK なので Rules を“読む必要はない”）
    await db.doc(`memos/${memoId}`).delete();

    return { ok: true };
  }
);
```

ポイントまとめ✨

* `enforceAppCheck: true` を付けるだけで、Callable 側で **App Check を強制**できます。 ([Firebase][2])
* Callable はクライアント SDK が **App Check トークン等を自動で付ける**ので、クライアント側でヘッダを手で付ける必要は基本ありません👍 ([Firebase][1])

---

## 4) React 側：呼び出すだけ（App Check は裏で勝手に付く）⚛️☎️

![Automatic Token Attachment](./picture/firebase_abuse_prevention_ts_study_010_04_client_auto_token.png)

```ts
import { getFunctions, httpsCallable } from "firebase/functions";

const functions = getFunctions();

export async function adminDeleteMemo(memoId: string) {
  const fn = httpsCallable(functions, "adminDeleteMemo");
  const res = await fn({ memoId });
  return res.data;
}
```

エラー時は、とにかくまず👇を表示できるようにしておくと最強です🧯

* `err.code`
* `err.message`

```ts
try {
  await adminDeleteMemo(memoId);
} catch (err: any) {
  console.error(err?.code, err?.message, err);
  // ここで「再読み込みしてね🙏」とか案内を出す
}
```

> App Check 強制後は「通らない呼び出しは拒否」が基本になるので、UIが無言で落ちない作りが超重要です🙂🧯 ([Firebase][2])

---

## 5) “AI整形”も Callable に寄せると強い🤖🧱

![AI Fortress](./picture/firebase_abuse_prevention_ts_study_010_05_ai_protection.png)

AI をクライアントから直接叩く設計もできますが、
**管理者だけが使うAI**や、**重いAI処理**は Callable に寄せると運用が楽になります💪

* App Check で “正規アプリ” だけに絞る🧿
* Auth と admin 判定で “管理者だけ” に絞る🧑‍💼
* さらに AI 側は **ユーザー単位レート制限（デフォルト 100 RPM/ユーザー）**があるので、安全弁になる🧯 ([Firebase][5])

---

## 6) 予告：もっと強くするなら「リプレイ対策」♻️🚫

![Anti-Replay Token](./picture/firebase_abuse_prevention_ts_study_010_06_replay_teaser.png)

「同じトークンを盗まれて使い回されたら困る😱」みたいな超重要APIは、**トークンを“使い捨て”にする**手があります。

* `consumeAppCheckToken: true`（ベータ）
* ただし **追加のネットワーク往復が増えて遅くなる**ので、本当に重要なCallableだけに絞るのが推奨です🐢⚠️
* さらに **Node.js の SDK のみ対応**です。 ([Firebase][2])

（ここは次章（第11章）でガッツリやるやつです🔥）

---

## 7) Antigravity / Gemini で、この章を“爆速”に終わらせる🚀🤖

![AI Developer Assist](./picture/firebase_abuse_prevention_ts_study_010_07_ai_assist.png)

Antigravity は「エージェントが計画してコード書いて、必要ならWeb調査もできる」系の開発プラットフォームです🛰️ ([Google Codelabs][6])
Firebase Studio でも Gemini をワークスペースに統合して、コード変更やコマンド実行まで流れでやれます（設定やルールファイルも用意できます）🧰🧠 ([Firebase][7])

使い方（例）👇

* 「`adminDeleteMemo` を `enforceAppCheck: true` で作って。Auth必須で、admins/{uid} で管理者判定。入力バリデーションも入れて」
* 「React側の呼び出しコードと、失敗時の UI 文言（3パターン）も作って」🙂
* 「危険な点（直叩きできる経路、権限漏れ、ログに個人情報が出る等）をチェックして」🔎🛡️

---

## 8) ミニ課題🧩🔥

次のうち **1つ**を「Callable + `enforceAppCheck`」で実装してみてください👇

* 🧑‍💼 管理者だけ：メモを「凍結（編集不可）」にする
* 🧹 管理者だけ：通報されたメモを「非公開」にする
* 🤖 管理者だけ：メモの要約を生成して `memos/{id}/summary` に保存する

---

## 9) チェック✅（ここまでできたら勝ち🎉）

* Callable に `enforceAppCheck: true` を付けると、**missing/invalid の App Check トークンは拒否**されるのを理解してる🧿 ([Firebase][2])
* React から呼ぶとき、Callable は **App Check トークン等を自動で付けてくれる**のを理解してる☎️ ([Firebase][1])
* 「App Check（正規アプリ）」＋「Auth（誰）」＋「admin判定（権限）」の3点セットで設計できた🛡️🧑‍💼
* Node の Functions は **20/22 が中心**、Python は **3.10〜3.13（デフォルト3.13）**という感覚がある🔢 ([Firebase][4])

---

次の章（第11章）は、この Callable をさらに硬くする **リプレイ（再生攻撃）対策**に行きます♻️🚫
「管理者機能」みたいな高価値APIほど、ここまでやる価値があります🔥

[1]: https://firebase.google.com/docs/functions/callable "Call functions from your app  |  Cloud Functions for Firebase"
[2]: https://firebase.google.com/docs/app-check/cloud-functions "Enable App Check enforcement for Cloud Functions  |  Firebase App Check"
[3]: https://firebase.google.com/docs/ai-logic/app-check?utm_source=chatgpt.com "Implement Firebase App Check to protect APIs from ... - Google"
[4]: https://firebase.google.com/docs/functions/get-started "Get started: write, test, and deploy your first functions  |  Cloud Functions for Firebase"
[5]: https://firebase.google.com/docs/ai-logic/quotas?utm_source=chatgpt.com "Rate limits and quotas | Firebase AI Logic - Google"
[6]: https://codelabs.developers.google.com/getting-started-google-antigravity?utm_source=chatgpt.com "Getting Started with Google Antigravity"
[7]: https://firebase.google.com/docs/studio/get-started-workspace?utm_source=chatgpt.com "About Firebase Studio workspaces - Google"
