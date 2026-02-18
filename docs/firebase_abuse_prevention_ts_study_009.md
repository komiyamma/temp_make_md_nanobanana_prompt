# 第09章：Storageを守る（アップロードが狙われる😱）📷🛡️

この章は「プロフィール画像アップロード」を題材に、**Cloud Storage を “荒らされない設計” にする**回だよ〜💪✨
ポイントはこれ👇

* ✅ **Storage Rules**：誰が何できるか（認可）🧾
* ✅ **App Check**：正規アプリっぽいリクエストか（正規クライアント証明）🧿
* ✅ **UXと運用**：強制ONでユーザー体験が壊れないようにする🙂🧯

App Checkの強制は **Cloud Storage も対象**で、強制すると **未検証リクエストは拒否**されるよ。さらに反映に最大15分かかることがある点も大事！([Firebase][1])

---

## 0) まず「なぜStorageが狙われるの？」😱💸

![Storage Threats](./picture/firebase_abuse_prevention_ts_study_009_01_storage_threats.png)

Storageがやられると、被害が“わかりやすく高い”から狙われがち👇

* 📦 **巨大ファイル**を投げ込まれて保管料が増える
* 🔁 **連打アップロード**で帯域・オペが死ぬ
* 🌍 **直リンク拡散**でダウンロード転送量が増える
* 🧨 画像に見せた **危険なファイル**（拡張子偽装など）
* 🧑‍🎤 不適切画像を置かれて炎上…😇

なのでこの章では、**アップロード入口を固める**よ！🔒✨

---

## 1) 読む📖：守りのレイヤーを1枚絵で理解しよう🧠🗺️

![Storage Defense](./picture/firebase_abuse_prevention_ts_study_009_02_defense_layers.png)

イメージはこう👇

* 🧾 **Rules**：ユーザーの身元（ログイン）と権限で制御
* 🧿 **App Check**：そもそも“正規アプリから来てる？”を判定
* 🧰（必要なら）**バックエンド処理**：AI検査・サムネ・回数制限など

App Check のメトリクス画面では、**Verified / Unverified / Error / Rate limited** みたいに「今どんなリクエストが来てるか」が見えるので、**いきなり強制しないで観察**ができるよ👀📈（分類はコンソールで確認できる）([Firebase][2])

---

## 2) 手を動かす🛠️：プロフィール画像アップロードを作る📷⚛️

## 2-1) 依存関係（2026年2月時点の“今”）📦✨

Web/React 側は `firebase` パッケージを使うよ。最新版は `12.9.0` が出てる（2026-02-05時点）([npm][3])

## 2-2) React（TS）でアップロード + 進捗バー🚀

![Upload UI](./picture/firebase_abuse_prevention_ts_study_009_03_upload_ui.png)

`ProfileImageUploader.tsx` の例👇（**サイズ/タイプを先に弾く**のが超大事！）

```tsx
import React, { useMemo, useState } from "react";
import { getAuth } from "firebase/auth";
import {
  getStorage,
  ref,
  uploadBytesResumable,
  getDownloadURL,
} from "firebase/storage";
import { app } from "./firebaseApp"; // 既に初期化済みの前提（前章までで作ったやつ）

type UploadState =
  | { kind: "idle" }
  | { kind: "uploading"; progress: number }
  | { kind: "done"; url: string }
  | { kind: "error"; message: string };

const MAX_BYTES = 2 * 1024 * 1024; // 2MB（例）

export function ProfileImageUploader() {
  const [state, setState] = useState<UploadState>({ kind: "idle" });

  const auth = useMemo(() => getAuth(app), []);
  const storage = useMemo(() => getStorage(app), []);

  const onPickFile = async (file: File | null) => {
    if (!file) return;

    // ① 先に“雑にでも”弾く（ここで落とすほど安い）💰
    if (!file.type.startsWith("image/")) {
      setState({ kind: "error", message: "画像ファイルだけOKだよ🙂📷" });
      return;
    }
    if (file.size > MAX_BYTES) {
      setState({
        kind: "error",
        message: "ファイルが大きすぎるよ😵‍💫 2MB以下にしてね",
      });
      return;
    }

    const user = auth.currentUser;
    if (!user) {
      setState({ kind: "error", message: "ログインしてから試してね🙂🔑" });
      return;
    }

    // ② 保存パス：ユーザーごとに分離（超重要）🧱
    const ext = file.name.split(".").pop()?.toLowerCase() || "jpg";
    const safeExt = ["jpg", "jpeg", "png", "webp"].includes(ext) ? ext : "jpg";
    const fileName = `${crypto.randomUUID()}.${safeExt}`;
    const path = `users/${user.uid}/profile/${fileName}`;

    const storageRef = ref(storage, path);

    // ③ メタデータ：最低限いれておくと後が楽📎
    const metadata = {
      contentType: file.type,
      cacheControl: "public,max-age=3600", // 例：1時間（運用で調整）
    };

    setState({ kind: "uploading", progress: 0 });

    const task = uploadBytesResumable(storageRef, file, metadata);

    task.on(
      "state_changed",
      (snap) => {
        const progress = Math.round(
          (snap.bytesTransferred / snap.totalBytes) * 100
        );
        setState({ kind: "uploading", progress });
      },
      (err) => {
        // 強制ON後に App Check が無い/無効だとここで落ちることがあるよ🧿💥
        setState({
          kind: "error",
          message: `アップロード失敗😇：${err.code ?? "unknown"}`,
        });
      },
      async () => {
        const url = await getDownloadURL(task.snapshot.ref);
        setState({ kind: "done", url });
      }
    );
  };

  return (
    <div style={{ display: "grid", gap: 12, maxWidth: 420 }}>
      <div>
        <input
          type="file"
          accept="image/*"
          onChange={(e) => onPickFile(e.target.files?.[0] ?? null)}
        />
      </div>

      {state.kind === "uploading" && (
        <div>
          <div>アップロード中… {state.progress}% 🚀</div>
          <progress value={state.progress} max={100} />
        </div>
      )}

      {state.kind === "done" && (
        <div style={{ display: "grid", gap: 8 }}>
          <div>完了！🎉</div>
          <img src={state.url} alt="profile" width={180} />
          <small>※ URL は扱い注意（後で解説）🙂🔒</small>
        </div>
      )}

      {state.kind === "error" && (
        <div style={{ color: "crimson" }}>
          {state.message} <br />
          <small>困ったら「再読み込み」「少し待つ」「別ブラウザで試す」も👍</small>
        </div>
      )}
    </div>
  );
}
```

---

## 3) ここが本丸🧾：Storage Rules で “最低限の防波堤” を作る🛡️

![Rules Logic](./picture/firebase_abuse_prevention_ts_study_009_04_rules.png)

Rules は「誰が」「どのパスに」「何を」できるかを決めるよ🙂✨
画像アップロードは **サイズ制限**と **contentType制限**が基本セット！

```rules
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    // ユーザーのプロフィール画像だけ許可する例
    match /users/{uid}/profile/{fileName} {
      allow read: if request.auth != null && request.auth.uid == uid;

      allow write: if request.auth != null
        && request.auth.uid == uid
        && request.resource.size < 2 * 1024 * 1024
        && request.resource.contentType.matches('image/.*');
    }
  }
}
```

`request.resource.size` と `request.resource.contentType.matches()` みたいなチェックは、まさに公式の例でもよく出てくる “王道” 🧱([Firebase][4])

> ✅ **Rulesだけでも重要**だけど、**Rulesだけだと「正規アプリじゃないクライアント」も（認証さえできれば）叩けちゃう**
> → そこで App Check が効いてくる！🧿✨

---

## 4) App Check を Cloud Storage に効かせる🧿📦

![Storage Enforcement](./picture/firebase_abuse_prevention_ts_study_009_05_enforcement.png)

## 4-1) 先にメトリクスで観察👀📈

App Check コンソールのメトリクスで「Storage にどんなリクエストが来てるか」を見るよ。
ここで **Unverified が多い**のに強制ONすると、普通にユーザーが死ぬ可能性ある😇([Firebase][2])

## 4-2) 強制ON（Enforce）🚨

手順はめちゃシンプルで、

1. App Check 画面を開く
2. 対象プロダクト（Cloud Storage）のメトリクスを開く
3. **Enforce** を押す

…これだけ！
そして **強制ON後は未検証リクエストが拒否**される。反映まで最大15分かかることもあるよ⏳([Firebase][1])

---

## 5) ON/OFF で挙動差を観察する👀🧪（安全なやり方）

「攻撃っぽいこと」はしなくてOK🙆‍♂️
**App Check 初期化を“わざと外したビルド”**を一時的に作って、同じUIで試すのが安全で分かりやすいよ🙂

例：`src/services/appCheck.ts` を作って “切替” できる形にする（Vite想定）👇

```ts
import { initializeAppCheck, ReCaptchaV3Provider } from "firebase/app-check";
import type { FirebaseApp } from "firebase/app-check";

// Viteなら VITE_*** が import.meta.env で読める
const ENABLE_APP_CHECK = import.meta.env.VITE_ENABLE_APP_CHECK === "true";

export function initAppCheck(app: FirebaseApp) {
  if (!ENABLE_APP_CHECK) return;

  initializeAppCheck(app, {
    provider: new ReCaptchaV3Provider(import.meta.env.VITE_RECAPTCHA_V3_SITE_KEY),
    isTokenAutoRefreshEnabled: true,
  });
}
```

* `VITE_ENABLE_APP_CHECK=true` のとき：いつも通りアップロード成功😊
* `VITE_ENABLE_APP_CHECK=false` のとき：**強制ONならアップロードが失敗**しやすい（エラーUX確認できる）🧿💥

---

## 6) 事故りやすい落とし穴⚠️（ここだけは押さえて🙂）

## 落とし穴A：`getDownloadURL()` を “アクセス制御” だと思う😇

![Secure Download](./picture/firebase_abuse_prevention_ts_study_009_06_secure_download.png)

`getDownloadURL()` で出たURLは **シェアできちゃう**ので、扱いは「秘密のURL（ベアラートークンっぽい）」として慎重にね🙂🔒

もし「毎回ルールでガチ判定したい」なら、**SDKで直接ダウンロード**（例：`getBlob()` / `getBytes()`）の方が **細かい制御をしやすい**、という案内が公式にもあるよ。([Firebase][5])

（画像表示が目的なら `getBlob()` → `URL.createObjectURL()` で `<img>` に入れる作戦もアリ📷✨）

## 落とし穴B：サイズ制限を Rules だけに頼ってる

UIでも弾こう！
**UIで弾く→Rulesで弾く**の二段ロックが強い💪🧱（安い順に落とす💰）

## 落とし穴C：エラーUXが無言😇

強制ON後は失敗が増える可能性があるので、最低でも👇は用意しよ🙂

* 🔄 再読み込みボタン
* ⏳ “少し待って再試行”
* 🆘 サポート導線（問い合わせ）

---

## 7) 🔥AIも絡める：アップロード後に “AI整形” を足す🤖✨

この教材の題材は「メモ＋画像＋AI整形」だから、Storageの章でもAIをちょい足しするよ🙂

## 7-1) 画像アップロード後に「説明文（alt）」をAIに作らせる📝🤖

![AI Alt Text Generation](./picture/firebase_abuse_prevention_ts_study_009_07_ai_alt.png)

* ユーザーが入力したメモ（例：「長崎で撮った夕焼け」）を元に
* AIに「短くて良い alt テキスト」を作らせて Firestore に保存✨

Firebase AI Logic 側も **App Check が推奨**されていて、さらに **limited-use App Check tokens** を使う設定も用意されてる（より堅くしたいときに便利）([Firebase][6])

> 🧠 コツ：
> Storage（アップロード）も AI（呼び出し）も、どっちもコストが出る → **両方に App Check** を意識すると安心感が跳ね上がるよ🧿🤖

---

## 8) AIで実装を速くする🚀（Antigravity / Gemini CLI / Firebase CLI）

## 8-1) Antigravity に投げる “ミッション例” 🧑‍🚀🧩

* ✅ Storage Rules を「プロフィール画像専用」に整理
* ✅ 2MB上限＋画像MIMEのみ
* ✅ App Check 強制ON時のエラーUX追加
* ✅ テスト観点（ON/OFF、反映待ち15分）をチェックリスト化

## 8-2) Gemini CLI に投げる “レビュー依頼例” 🔎🤖

* 「このアップロード実装で、悪用されそうなポイントを3つ指摘して、修正案を出して」
* 「Rulesの穴（読み取り/書き込み/サイズ/MIME）を洗い出して」

## 8-3) Firebase CLI の “AI連携っぽい新機能” もチェック✅

Firebase CLI には **AIアシスタントがFirebaseリソースとやり取りするための `firebase experimental:mcp`** が追加された、というリリースノートがあるよ（実験機能）([Firebase][7])
「AntigravityやGeminiがFirebaseをシームレスに触る」方向は、ここが入口になりそうで熱い🔥

---

## 9) ミニ課題📝🔥（3つ考えて、1つ実装！）

## ミニ課題

「不正アップロード（巨大ファイル / 連打 / 変なファイル）」を想定して、対策案を3つ書こう✍️🙂
例👇

* 🧾 Rules：2MB制限＋画像MIMEのみ（もうやった！）
* ⏱️ UI：短時間の連打を抑制（ボタン連打ガード）
* 🧠 AI：アップロード後に不適切っぽい画像なら非公開にする（将来の発展）

**1つは実装**しよう💪✨（おすすめは「UIのサイズ/MIMEチェック強化」）

---

## 10) チェック✅（この章の合格ライン🏁）

* ✅ Storage Rules で「自分のパスだけ」「サイズ/MIME制限」ができた ([Firebase][4])
* ✅ App Check のメトリクスで Storage の状態を見れた ([Firebase][2])
* ✅ Cloud Storage を強制ONにして、未検証が弾かれるのを体感できた（反映待ち最大15分も理解）([Firebase][1])
* ✅ 失敗時UX（再試行/案内）が用意できた🙂🧯
* ✅ AI整形（alt文生成など）とセットで「守り＋コスト対策」の目線が持てた🧿🤖 ([Firebase][6])

---

次の第10章（Functions）に進むと、**「アップロード後の処理をCallableに寄せて、enforceAppCheckでガチガチに守る」**ができて一気に守りが完成してくるよ〜☎️🔒🔥

[1]: https://firebase.google.com/docs/app-check/enable-enforcement "Enable App Check enforcement  |  Firebase App Check"
[2]: https://firebase.google.com/docs/app-check/monitor-metrics "Monitor App Check request metrics  |  Firebase App Check"
[3]: https://www.npmjs.com/package/firebase?utm_source=chatgpt.com "firebase"
[4]: https://firebase.google.com/docs/storage/security/rules-conditions "Use conditions in Firebase Cloud Storage Security Rules  |  Cloud Storage for Firebase"
[5]: https://firebase.google.com/docs/storage/web/download-files "Download files with Cloud Storage on Web  |  Cloud Storage for Firebase"
[6]: https://firebase.google.com/docs/ai-logic/app-check "Implement Firebase App Check to protect APIs from unauthorized clients  |  Firebase AI Logic"
[7]: https://firebase.google.com/support/release-notes/cli "Firebase CLI Release Notes"
