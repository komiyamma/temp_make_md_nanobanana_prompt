# 第16章：Storageで画像アップロードUIを作る 📷☁️✨

この章で作るのは「プロフィール画像アップロード」機能です🙂
**選ぶ → プレビュー → アップロード（進捗バー） → 反映**まで、管理画面っぽく気持ちよく仕上げます💪✨

---

## 1) まず“仕組み”を超ざっくり理解する 🧠💡

![Firestore vs Storage](./picture/firebase_frontend_foundation_ts_study_016_01_firestore_vs_storage.png)

* **Firestore**：文章・数値みたいな「データ」を保存する場所🗃️
* **Storage（Cloud Storage for Firebase）**：画像・動画みたいな「ファイル」を置く場所📦
* 画像をStorageへアップしたら、**その画像URL（download URL）をFirestoreに保存**して、UIで表示するのが定番です📌

アップロードは**進捗表示が命**🔥
`uploadBytesResumable` で「何%進んだ？」を取れます。公式も “進捗・一時停止・再開・キャンセル” をこのAPIで案内しています✅ ([Firebase][1])

---

## 2) コンソール側の準備 🛠️（最短ルート）

![Upload Process Flow](./picture/firebase_frontend_foundation_ts_study_016_02_upload_flow.png)

## Storageを有効化する ☁️

Firebase Consoleで Storage を有効化して、バケット（保存場所）を作ります📦
StorageはFirebaseが管理する Cloud Storage バケットを使います。 ([Firebase][1])

## ルール（超重要）🔐⚠️

「とりあえず全部OK」は事故りやすいので、**画像アップロードに必要な範囲だけ許可**します🙂
公式ドキュメントに、`request.auth`（ログイン判定）や `request.resource.size` / `contentType`（画像だけ許可・サイズ制限）の例が載っています。 ([Firebase][2])

---

## 3) パス設計：どこに置く？📁✨

![Storage Path Strategy](./picture/firebase_frontend_foundation_ts_study_016_03_path_strategy.png)

おすすめはこのどちらか👇

* **固定ファイル名**：`users/{uid}/avatar.jpg`

  * いつも同じ場所に上書き👍
  * ただし**キャッシュ**で古い画像が残りやすい（対策が必要）🌀
* **毎回ファイル名を変える**：`users/{uid}/avatar/{timestamp}.jpg`

  * キャッシュ問題が起きにくい✨
  * ただし古い画像の掃除（削除）が必要になる🧹

この章は「固定ファイル名＋キャッシュ対策」で進めます（簡単で実務でも多い）🙂

---

## 4) Storageルール例 🔐（“自分だけアップできる”）

![Storage Security Rules](./picture/firebase_frontend_foundation_ts_study_016_04_rules_logic.png)

まずは「ログインしてる本人が、自分の場所にだけアップできる」ルール例👇
（※ここはアプリ方針で変えてOK。最低限の考え方が大事🙂）

```rules
service firebase.storage {
  match /b/{bucket}/o {

    // プロフィール画像
    match /users/{uid}/avatar.jpg {

      // 読み取り：ログインユーザーならOK（チーム内アプリ向け）
      allow read: if request.auth != null;

      // 書き込み：本人だけ + 画像だけ + 5MBまで
      allow write: if request.auth != null
                   && request.auth.uid == uid
                   && request.resource.size < 5 * 1024 * 1024
                   && request.resource.contentType.matches('image/.*');
    }
  }
}
```

`request.auth` / `size` / `contentType` の基本は公式の説明＆例そのままです✅ ([Firebase][2])

---

## 5) 実装：アップロード“サービス関数”を作る 🔧✨

![Upload Task State Machine](./picture/firebase_frontend_foundation_ts_study_016_05_upload_state.png)

UI（React）から直接Firebase Storageを叩くとコードが散りやすいので、先に **services** を作ります📦

## `src/services/avatarStorage.ts`

```ts
import { getStorage, ref, uploadBytesResumable, getDownloadURL } from "firebase/storage";

export type UploadState = "idle" | "uploading" | "paused" | "done" | "error";

export type UploadAvatarResult = {
  downloadURL: string;
  fullPath: string;
};

export function uploadUserAvatar(params: {
  uid: string;
  file: File;
  onProgress?: (percent: number) => void;
  onState?: (state: UploadState) => void;
}) {
  const { uid, file, onProgress, onState } = params;

  const storage = getStorage();
  const avatarRef = ref(storage, `users/${uid}/avatar.jpg`);

  // 任意：contentType をメタデータで明示（画像扱いが安定しやすい）
  const metadata = { contentType: file.type };

  const task = uploadBytesResumable(avatarRef, file, metadata);

  onState?.("uploading");

  const done = new Promise<UploadAvatarResult>((resolve, reject) => {
    task.on(
      "state_changed",
      (snap) => {
        const percent =
          snap.totalBytes > 0 ? (snap.bytesTransferred / snap.totalBytes) * 100 : 0;

        onProgress?.(Math.round(percent));

        if (snap.state === "paused") onState?.("paused");
        if (snap.state === "running") onState?.("uploading");
      },
      (err) => {
        onState?.("error");
        reject(err);
      },
      async () => {
        const downloadURL = await getDownloadURL(task.snapshot.ref);
        onState?.("done");
        resolve({ downloadURL, fullPath: task.snapshot.ref.fullPath });
      }
    );
  });

  return {
    task,
    done,
    pause: () => task.pause(),
    resume: () => task.resume(),
    cancel: () => task.cancel(),
  };
}
```

* `uploadBytesResumable` と `state_changed` で進捗が取れます📶
* `pause()` `resume()` `cancel()` も公式が案内している操作です🧊▶️⛔ ([Firebase][1])

---

## 6) 実装：Reactコンポーネント（プレビュー＋進捗バー）🖼️📊

![Avatar Uploader UI](./picture/firebase_frontend_foundation_ts_study_016_06_ui_mock.png)

## `src/components/AvatarUploader.tsx`

```tsx
import { useEffect, useMemo, useState } from "react";
import type { UploadState } from "../services/avatarStorage";
import { uploadUserAvatar } from "../services/avatarStorage";

type Props = {
  uid: string;
  currentAvatarUrl?: string | null;
  onUploaded?: (downloadURL: string) => void;
};

export function AvatarUploader(props: Props) {
  const { uid, currentAvatarUrl, onUploaded } = props;

  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const [state, setState] = useState<UploadState>("idle");
  const [progress, setProgress] = useState<number>(0);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const [controller, setController] = useState<ReturnType<typeof uploadUserAvatar> | null>(null);

  const shownAvatarUrl = useMemo(() => {
    // キャッシュ対策：固定ファイル名で上書きする場合はクエリで更新を促すのがラク
    if (!currentAvatarUrl) return null;
    return `${currentAvatarUrl}${currentAvatarUrl.includes("?") ? "&" : "?"}v=${Date.now()}`;
  }, [currentAvatarUrl]);

  useEffect(() => {
    if (!file) return;

    const url = URL.createObjectURL(file);
    setPreviewUrl(url);

    return () => URL.revokeObjectURL(url);
  }, [file]);

  const startUpload = async () => {
    if (!file) return;

    setErrorMsg(null);
    setProgress(0);

    const c = uploadUserAvatar({
      uid,
      file,
      onProgress: setProgress,
      onState: setState,
    });
    setController(c);

    try {
      const res = await c.done;
      onUploaded?.(res.downloadURL);
      setFile(null);
      setPreviewUrl(null);
    } catch (e: any) {
      // ここは“人間向け”に言い換えるのが大事🙂
      setErrorMsg(e?.message ?? "アップロードに失敗しました。もう一度試してね🙏");
    }
  };

  const disabled = state === "uploading";

  return (
    <div className="rounded-2xl border p-4 shadow-sm space-y-3">
      <div className="flex items-center gap-4">
        <div className="h-16 w-16 overflow-hidden rounded-full border bg-gray-50">
          {previewUrl ? (
            <img src={previewUrl} className="h-full w-full object-cover" alt="preview" />
          ) : shownAvatarUrl ? (
            <img src={shownAvatarUrl} className="h-full w-full object-cover" alt="avatar" />
          ) : (
            <div className="h-full w-full grid place-items-center text-sm text-gray-400">
              No Image
            </div>
          )}
        </div>

        <div className="flex-1 space-y-2">
          <input
            type="file"
            accept="image/*"
            disabled={disabled}
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />

          <div className="flex gap-2">
            <button
              className="rounded-xl bg-black px-3 py-2 text-white disabled:opacity-40"
              disabled={!file || disabled}
              onClick={startUpload}
            >
              アップロード🚀
            </button>

            <button
              className="rounded-xl border px-3 py-2 disabled:opacity-40"
              disabled={!controller}
              onClick={() => controller?.pause()}
            >
              一時停止🧊
            </button>

            <button
              className="rounded-xl border px-3 py-2 disabled:opacity-40"
              disabled={!controller}
              onClick={() => controller?.resume()}
            >
              再開▶️
            </button>

            <button
              className="rounded-xl border px-3 py-2 disabled:opacity-40"
              disabled={!controller}
              onClick={() => controller?.cancel()}
            >
              キャンセル⛔
            </button>
          </div>
        </div>
      </div>

      {/* 進捗バー */}
      <div className="space-y-1">
        <div className="text-sm text-gray-600">
          状態：{state} / {progress}%
        </div>
        <div className="h-2 w-full rounded-full bg-gray-100 overflow-hidden">
          <div className="h-full bg-black" style={{ width: `${progress}%` }} />
        </div>
      </div>

      {errorMsg && (
        <div className="rounded-xl bg-red-50 p-3 text-sm text-red-700">
          {errorMsg}
        </div>
      )}
    </div>
  );
}
```

ポイント💡

* `accept="image/*"` で画像だけ選ばせる🖼️
* `URL.createObjectURL` で爆速プレビュー✨（使い終わったら `revokeObjectURL` で後片付け🧹）
* 固定ファイル名で上書きするなら `?v=...` を付けて更新されやすくする（お手軽）🌀

---

## 7) App Checkを入れると“安心感”が一気に上がる 🛡️✨

Storageは**ルールが第一防衛線**だけど、さらに
「正規のアプリからのアクセスっぽい？」を判定する **App Check** を重ねると強いです💪

Webだと **reCAPTCHA Enterprise** を使う手順が公式にあります（しかもスコア型で基本“見えない”）。 ([Firebase][3])
ローカル開発は **debug provider** が便利で、デバッグトークンをConsoleに登録して使えます。 ([Firebase][4])

---

## 8) AIを絡める：ファイル名＆代替テキストをAIに決めさせる 🤖📝✨

![AI Metadata Generation](./picture/firebase_frontend_foundation_ts_study_016_07_ai_metadata.png)

「AIで画像そのものを解析」は次章以降でも良いけど、
この章でも **“実務で効く”AI** を入れられます👇

* ファイル名が `IMG_1234.png` のまま問題…😵
* 代替テキスト（alt）が空のまま問題…😵

→ **Firebase AI Logic** で、**ファイル名案・alt案**を生成してから保存✨
WebのSDKは `firebase/ai` で `getAI` / `getGenerativeModel` を使います。 ([Firebase][5])

```ts
import { initializeApp } from "firebase/app";
import { getAI, getGenerativeModel, GoogleAIBackend } from "firebase/ai";

const app = initializeApp({ /* ... */ });

// Gemini Developer API をバックエンドとして使う初期化例
const ai = getAI(app, { backend: new GoogleAIBackend() });

// 例：軽量モデルを選ぶ（用途に合わせてOK）
const model = getGenerativeModel(ai, { model: "gemini-2.5-flash" });

export async function suggestAvatarMeta(input: {
  displayName: string;
  contentType: string;
}) {
  const prompt = `
あなたはWebアプリのUIライターです。
ユーザー名: ${input.displayName}
画像タイプ: ${input.contentType}

次を日本語で短く提案して:
1) プロフィール画像のaltテキスト（10〜20文字）
2) storage用のファイル名（英小文字/数字/ハイフンのみ、拡張子なし）
`;

  // ※ 実際の呼び出しはSDKの生成APIに合わせて実装（この章では“使いどころ”が主役🙂）
  // const result = await model.generateContent(prompt);
  // return result... をパースして返す
}
```

さらに「モデルの世代交代」も地味に大事📌
Firebase AI Logicのドキュメント内で、**一部の Gemini 2.0 世代モデルが 2026-03-31 に廃止予定**で、代替として **Gemini 2.5 系（例：gemini-2.5-flash-lite など）**が案内されています。 ([Firebase][5])

---

## 9) Antigravity / Gemini CLIで“開発そのもの”も加速する 🛸💻✨

ここは実装よりも「使い方の型」を作るのが勝ちです🙂

* **Antigravity**：エージェントを管理して、調査→設計→実装→テスト叩き台まで進めるIDE的な動きができます（公式Codelabあり） ([Google Codelabs][6])
* **Gemini CLI**：VS Codeのエージェントモードと繋がっていたり、Cloud Shellで使えたりする流れが公式ドキュメントにあります ([Google Cloud Documentation][7])
* **Firestore×MCP**：Gemini CLI + MCP Toolbox でFirestoreに繋ぐ話も公式にあります（“Firebaseをシームレスに扱える可能性”の現実ラインとして有望） ([Google Cloud Documentation][8])

この章でのおすすめ“AI指示文”例👇

* 「AvatarUploaderを、状態（loading/error/data）を崩さずに分割して」🧩
* 「Storageルールを、本人のみ書き込み＋画像制限＋サイズ制限で提案して」🔐
* 「アップロード失敗パターンを想定して、ユーザー向けエラーメッセージ案を10個」📝

---

## 10) ミニ課題 🎯✨

次のうち1つやればOK（おすすめ順）👇

1. **画像の“軽量化”を入れる**🗜️

   * 例：長辺を 512px に縮小してJPEGで保存してからアップロード（通信量が激減）📉✨
2. **ドラッグ＆ドロップ対応**🧲
3. **削除ボタン**🧹（今の画像を消してデフォルトに戻す）

---

## 11) チェック✅（できたら勝ち🎉）

* 画像を選ぶと、**即プレビュー**が出る🖼️
* アップロード中に **進捗%** が動く📊
* **一時停止/再開/キャンセル**が動く🧊▶️⛔ ([Firebase][1])
* 失敗したとき、ユーザーに **意味が伝わる**メッセージが出る🙏
* ルールで「本人だけアップ可」「画像だけ」「サイズ制限」が入ってる🔐 ([Firebase][2])

---

## つまずきポイント集 🧯😵‍💫

* `storage/unauthorized`：**Storageルール**か、ログイン状態が原因になりがち🔐
  → `request.auth != null` が通ってるか見る ([Firebase][2])
* 画像が更新されない：**キャッシュ**🌀
  → 固定ファイル名なら `?v=timestamp` を付ける（この章のやり方）
* 本番で守りを固めたい：**App Check** を入れる🛡️
  → Webは reCAPTCHA Enterprise / 開発は debug provider が公式手順あり ([Firebase][3])

---

次（第17章）は、このアップロード後に **Functions を呼んで「サムネ生成」「NSFW判定」「AIで説明文生成」**みたいな“サーバー側の強化”に進めます⚙️🤖✨

[1]: https://firebase.google.com/docs/storage/web/upload-files "Upload files with Cloud Storage on Web  |  Cloud Storage for Firebase"
[2]: https://firebase.google.com/docs/storage/security "Understand Firebase Security Rules for Cloud Storage  |  Cloud Storage for Firebase"
[3]: https://firebase.google.com/docs/app-check/web/recaptcha-enterprise-provider "Get started using App Check with reCAPTCHA Enterprise in web apps  |  Firebase App Check"
[4]: https://firebase.google.com/docs/app-check/web/debug-provider "Use App Check with the debug provider in web apps  |  Firebase App Check"
[5]: https://firebase.google.com/docs/ai-logic/get-started "Get started with the Gemini API using the Firebase AI Logic SDKs  |  Firebase AI Logic"
[6]: https://codelabs.developers.google.com/getting-started-google-antigravity?utm_source=chatgpt.com "Getting Started with Google Antigravity"
[7]: https://docs.cloud.google.com/gemini/docs/codeassist/gemini-cli?utm_source=chatgpt.com "Gemini CLI | Gemini for Google Cloud"
[8]: https://docs.cloud.google.com/firestore/native/docs/connect-ide-using-mcp-toolbox?utm_source=chatgpt.com "Use Firestore with MCP, Gemini CLI, and other agents"
