### 第13章：古い画像の掃除（削除タイミングの設計）🧹🗑️✨

この章は「古いプロフィール画像、どう消すのが安全？」を“事故らない設計”で作れるようになる回だよ〜🙂📷
結論から言うと、**おすすめは「猶予期間つき削除（＝いったん削除予定にして、あとで自動で掃除）」**です👍🔥

---

## 0) この章のゴール🎯

* 履歴一覧に **削除ボタン** をつける🧾🗑️
* **使用中（現在の画像）は削除できない** ようにする🛡️
* 「即削除」か「猶予期間つき」か、**自分のアプリに合う方を選べる**🤔✨
* うっかり削除しても詰みにくい（復旧ルートを残す）🚑

---

## 1) なぜ「削除」は事故りやすいの？😱

プロフィール画像って、だいたいこういう流れで参照されるよね👇

* UIは「現在の画像（photoPath）」を見て表示👀
* 履歴（profileImages）からサムネや一覧を作る🗂️

ここで雑に削除すると…

* **現在画像を消しちゃって、アイコン真っ白**😇
* **URLは残ってるのにファイルがない**（または逆）で整合性が崩壊🧨
* 端末が複数あると「片方で削除→片方がまだ参照」で混乱📱💥

さらに、Cloud Storage 側は削除しても **soft delete により “だいたい7日復元できる”**（デフォルトで有効）って挙動があるので、挙動理解も大事！([Firebase][1])
※「復元できるから安心！」ではなく、「だからこそ削除運用をちゃんと設計しよう」って話ね🙂

---

## 2) 削除ポリシー3択（どれが正解？）🤔🧩

### A. すぐ消す（即削除）⚡

* ✅ 実装が一番ラク
* ❌ 誤削除が怖い／整合性が崩れやすい
* 向いてる：**個人アプリ・学習用・履歴が薄い**ケース🙂

### B. 猶予期間つき（おすすめ）⏳🌟

* ✅ 誤操作に強い（「取り消し」できる）
* ✅ 自動掃除に繋げやすい（運用がラク）
* ❌ 実装は少し増える
* 向いてる：**“現実アプリ感”を出したい**ならだいたいコレ😎

### C. 手動削除（ユーザーが選んで掃除）🧑‍💻🗑️

* ✅ コントロールしやすい
* ❌ 放置されがち（ゴミが溜まる）
* 向いてる：画像を複数持てるSNS風、など📸

---

## 3) まず「削除できる状態」をFirestoreに持たせよう🧠🗃️

この章は **「Storageのファイル削除」だけじゃなく、Firestore側の状態設計が主役**だよ💪

おすすめデータ案👇（すでに前章までの流れを踏襲）

* `users/{uid}`

  * `photoPath`（現在の画像のパス）⭐
  * `updatedAt`
* `users/{uid}/profileImages/{imageId}`（履歴）

  * `path`
  * `status` : `"active" | "archived" | "pending_delete" | "deleted"`
  * `createdAt`
  * `deleteAfter`（猶予期限：Timestamp）← 猶予方式で使う⏳

ポイントはこれ👇

* **現在の画像は `users/{uid}.photoPath` が真実**（履歴より強い）🧱
* 履歴は「一覧・戻す・削除予定」を表現するための台帳📒✨

---

## 4) 手を動かす①：履歴UIに「削除」を付ける🖼️🗑️

### ステップ🪜

1. 履歴を `createdAt desc` で並べる🧾
2. `path === users.photoPath` の行は

   * 「使用中」バッジ🏷️
   * **削除ボタンを無効化**🚫
3. 削除は **確認ダイアログ** を必ず挟む✅（事故防止）

---

## 5) 手を動かす②：即削除（シンプル版）⚡🧹

Web SDK なら、削除は `deleteObject()` でOK👌
（削除やアップロードなどは、基本的に認証＋ルールで守るやつだよ〜🔐🛡️。デフォルトのルールだと認証が必要、という前提も押さえてね）([Firebase][1])

#### 例：いま選んだ履歴アイテムを削除する（安全チェック付き）👇

```ts
import { getFirestore, doc, getDoc, updateDoc, serverTimestamp } from "firebase/firestore";
import { getStorage, ref, deleteObject } from "firebase/storage";

type DeleteResult = { ok: true } | { ok: false; reason: string };

export async function deleteHistoryImageNow(uid: string, imageId: string): Promise<DeleteResult> {
  const db = getFirestore();
  const storage = getStorage();

  const userRef = doc(db, "users", uid);
  const imgRef  = doc(db, "users", uid, "profileImages", imageId);

  // 1) まず「使用中じゃない」を確認（最重要）
  const [userSnap, imgSnap] = await Promise.all([getDoc(userRef), getDoc(imgRef)]);
  if (!userSnap.exists() || !imgSnap.exists()) return { ok: false, reason: "データが見つからないよ🥲" };

  const currentPath = userSnap.data().photoPath as string | undefined;
  const path = imgSnap.data().path as string;

  if (!path) return { ok: false, reason: "pathが空だよ🥲" };
  if (currentPath && path === currentPath) {
    return { ok: false, reason: "これは使用中の画像だから削除できないよ🛡️" };
  }

  // 2) Storageのファイル削除
  await deleteObject(ref(storage, path)); // ここが失敗することもある（権限/存在など）

  // 3) Firestore側も「deleted」に
  await updateDoc(imgRef, {
    status: "deleted",
    deletedAt: serverTimestamp(),
  });

  return { ok: true };
}
```

### よくある失敗🥺（ここ大事）

* **権限エラー**：Rulesで「本人だけwrite」ができてない（または未ログイン）
* **存在しない**：すでに別端末で消してた（→ UI側は「消えてた🙂」でOK）
* **削除したのに容量減らない？**：soft delete の影響があり得る([Firebase][1])

---

## 6) 手を動かす③：猶予期間つき削除（おすすめ）⏳🌟

即削除はラクだけど、**“現実アプリ感”** は猶予つきが強い😎✨
やることはシンプルで、

1. まず `pending_delete` にして、`deleteAfter` を入れる📝
2. UIで「削除予定」表示＋「取り消し」ボタンを出す↩️
3. バックエンドが期限を見て、まとめて削除🧹

### 6-1) まず「削除予定にする」だけ（クライアント）🗓️

```ts
import { getFirestore, doc, getDoc, updateDoc, Timestamp, serverTimestamp } from "firebase/firestore";

export async function markImagePendingDelete(uid: string, imageId: string, days: number) {
  const db = getFirestore();

  const userRef = doc(db, "users", uid);
  const imgRef  = doc(db, "users", uid, "profileImages", imageId);

  const [userSnap, imgSnap] = await Promise.all([getDoc(userRef), getDoc(imgRef)]);
  const currentPath = userSnap.data()?.photoPath as string | undefined;
  const path = imgSnap.data()?.path as string | undefined;

  if (!path) throw new Error("pathが無いよ");

  if (currentPath && path === currentPath) {
    throw new Error("使用中の画像は削除予定にできないよ🛡️");
  }

  const deleteAfter = Timestamp.fromDate(new Date(Date.now() + days * 24 * 60 * 60 * 1000));

  await updateDoc(imgRef, {
    status: "pending_delete",
    deleteAfter,
    deleteRequestedAt: serverTimestamp(),
  });
}
```

### 6-2) 「取り消し」も簡単🙂↩️

```ts
import { getFirestore, doc, updateDoc, deleteField, serverTimestamp } from "firebase/firestore";

export async function cancelPendingDelete(uid: string, imageId: string) {
  const db = getFirestore();
  const imgRef  = doc(db, "users", uid, "profileImages", imageId);

  await updateDoc(imgRef, {
    status: "archived",
    deleteAfter: deleteField(),
    deleteCancelledAt: serverTimestamp(),
  });
}
```

---

## 7) 自動掃除（期限が来たら消す）🧹🤖

ここからが「現実アプリ感」ゾーン🔥
期限が来た `pending_delete` を毎日まとめて掃除するのが定番！

Cloud Functions なら **スケジュール実行（`onSchedule`）** が使えるよ。
ドキュメント上も `firebase-functions/v2/scheduler` の `onSchedule` を推してて、Cloud Scheduler が裏で動く仕組み📅([Firebase][2])
（Cloud Scheduler はジョブ課金の説明もあるよ）([Firebase][2])

### 7-1) Functionsのランタイム（2026時点の感覚）🧠

* Cloud Functions for Firebase は Node.js の対応ランタイムが明記されてる（例：Node 20/22）。([Google Cloud Documentation][3])
* Python の対応（例：3.10 / 3.11）も同ページにあるよ。([Google Cloud Documentation][3])
* さらに別ルートとして Cloud Run Functions のランタイム表（.NET / Python など）もある。([Google Cloud Documentation][3])

> この章はまず **TypeScript（Node）で掃除**が一番スムーズ🙂👍
> .NET/Python は「別の実行環境でやりたい」時の選択肢、って距離感でOK！

### 7-2) 期限切れを消す（スケジュール関数：概念コード）🧹

※ここは “考え方” を掴む用。実務ではログ・リトライ・同時実行制御も足すと強い💪
（管理者環境で Cloud Storage を触る時は Admin SDK のストレージ API を使う流れになるよ）([Firebase][4])

```ts
// functions/src/cleanup.ts
import { onSchedule } from "firebase-functions/v2/scheduler";
import { logger } from "firebase-functions";
import * as admin from "firebase-admin";

admin.initializeApp();

export const cleanupOldProfileImages = onSchedule("every day 03:00", async () => {
  const db = admin.firestore();
  const bucket = admin.storage().bucket(); // default bucket

  const now = admin.firestore.Timestamp.now();

  // 期限切れの pending_delete を探す（collectionGroupでもOK）
  const snap = await db
    .collectionGroup("profileImages")
    .where("status", "==", "pending_delete")
    .where("deleteAfter", "<=", now)
    .limit(200)
    .get();

  logger.info(`cleanup targets: ${snap.size}`);

  for (const docSnap of snap.docs) {
    const data = docSnap.data();
    const path = data.path as string | undefined;
    if (!path) continue;

    try {
      // Storage削除
      await bucket.file(path).delete({ ignoreNotFound: true });

      // Firestore更新
      await docSnap.ref.update({
        status: "deleted",
        deletedAt: admin.firestore.FieldValue.serverTimestamp(),
      });
    } catch (e) {
      logger.error(`failed delete: ${path}`, e);
      // ここで retryCount を増やす等もアリ
    }
  }
});
```

---

## 8) さらに安全にする小ワザ集🧠🛡️✨

### ✅ 「削除の真実」は photoPath だけにする

* 履歴を消しても、**現在画像が残ってれば表示は守られる**🙂

### ✅ 「削除予定」は見た目で分かるようにする

* “あと3日で削除” みたいな表示があるだけで安心感アップ📅✨

### ✅ Firestore TTL は「履歴ドキュメント掃除」に便利

TTL は「指定した期限フィールドでドキュメントを自動削除」してくれる（期限から24時間以内に削除されがち、という目安も書かれてる）([Firebase][5])
ただし注意！

* TTL で消えるのは **Firestoreのドキュメント**。
* **Storageのファイルは別途消す必要がある**（なので上のスケジュール掃除が効く）🧹

---

## 9) AIを絡めると“現実アプリ感”が一気に増える🤖✨

ここは「削除そのもの」より「削除の判断材料」をAIで整えるイメージ👍

* 履歴一覧に **AI生成の短い説明（alt）** を添える📝🤖
  → “似た写真が多すぎてどれ消すか分からん！”を減らせる😆
* “ほぼ同じ画像” を AI でまとめて提案（重複整理）🧠
* 「この削除ポリシー、穴ない？」を AI にレビューさせる🕵️‍♂️✨

  * 例：`photoPath` を消す可能性がないか
  * 例：複数端末同時操作でも壊れないか
* Google のAIやエージェント環境を使うなら、**「削除フロー図」「失敗時の分岐」**を作らせると爆速だよ🚀🧭

---

## 10) ミニ課題🧩🏁

1. 履歴UIで「使用中」バッジ＋削除無効化を実装🏷️🚫
2. 「削除」押下で確認ダイアログを必ず出す✅
3. 方式を選ぶ：

   * 即削除 か、猶予期間つき どっちかを動かす🔥
4. できれば「削除取り消し」まで入れる↩️✨

---

## 11) チェック✅✅✅

* [ ] 使用中画像は削除できない🛡️
* [ ] 削除前に確認が出る✅
* [ ] 削除後、Firestoreの状態も一貫してる🧠
* [ ] 失敗（権限/存在なし）でもアプリが固まらない🙂
* [ ] （猶予方式なら）取り消しできる↩️✨

---

## おまけ：地味に重要なお知らせ📣

Cloud Storage のデフォルトバケットとプラン要件は、**2026-02-03** の話が絡むので、学習プロジェクトでも一応意識してね（該当する場合）([Firebase][6])

---

次は、この第13章の流れのまま **「削除UI（履歴リスト）をReactで1画面ぶん」** ちゃんと作る形の教材（コンポーネント例）にしてもいい？🙂📄✨

[1]: https://firebase.google.com/docs/storage/web/delete-files?utm_source=chatgpt.com "Delete files with Cloud Storage on Web - Firebase"
[2]: https://firebase.google.com/docs/functions/schedule-functions "Schedule functions  |  Cloud Functions for Firebase"
[3]: https://docs.cloud.google.com/functions/docs/runtime-support "Runtime support  |  Cloud Run functions  |  Google Cloud Documentation"
[4]: https://firebase.google.com/docs/storage/admin/start?utm_source=chatgpt.com "Introduction to the Admin Cloud Storage API - Firebase"
[5]: https://firebase.google.com/docs/firestore/ttl?utm_source=chatgpt.com "Manage data retention with TTL policies | Firestore - Firebase"
[6]: https://firebase.google.com/docs/storage/faqs-storage-changes-announced-sept-2024?utm_source=chatgpt.com "FAQs about Cloud Storage for Firebase changes announced ..."
