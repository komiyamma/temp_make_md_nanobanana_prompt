### 第6章：進捗バー付きアップロード（途中経過が見える）📶✨

この章は「アップロードできた！」の次に来る、**“現実アプリ感”が一気に増えるポイント**だよ〜😎
ファイルが大きいときほど、進捗が見えないと不安になるので、ここでちゃんと作り込もう！💪

---

## この章でできるようになること🎯

* アップロード中の **進捗% を表示**できる📊
* **一時停止 / 再開 / キャンセル**ができる⏸️▶️🛑
* 失敗したときに、ユーザーが迷わない **エラーメッセージ**が出せる🙂

---

## まず理解パート🧠（何が起きてる？）

### `uploadBytesResumable` は「途中経過が取れるアップロード」📦

Storage のアップロードを “進捗付き” にしたいなら、基本はこれです👇
`uploadBytesResumable(...)` が返す **UploadTask** に対して、進捗や状態を監視します。([Firebase][1])

### 進捗は `state_changed` で取る📡

UploadTask には `on('state_changed', ...)` があって、状態が変わるたびに呼ばれます。
そのときの `snapshot.bytesTransferred / snapshot.totalBytes` で **進捗%** が出せます。([Firebase][1])

### 状態（paused / running）も取れる⏸️🏃

`snapshot.state` で `"paused"` と `"running"` が取れるので、UIの表示切り替えができます。([Firebase][1])

### 一時停止・再開・キャンセルは UploadTask のメソッド💡

* `pause()`
* `resume()`
* `cancel()`

これで操作できます。キャンセルは **アップロードが失敗扱いになって**、エラーコードとして `storage/canceled` が返るのが正常です（“失敗”じゃなくて“キャンセル”として扱うのがコツ）🛟([Firebase][1])

---

## 手を動かすパート🛠️（React + TypeScript）

ここでは「プロフィール画像アップロード」を想定して、**進捗バー＋操作ボタン**まで一気に作るよ〜📷✨

### 1) 実装方針（迷子防止マップ🗺️）

* `UploadTask` は React の state に入れない（レンダリングと相性悪い）
  → `useRef` に置くのが安全🙆‍♂️
* `uploadTask.on(...)` の監視は **解除（unsubscribe）**できる
  → コンポーネント破棄時に解除して事故防止🧯
* 2回目のアップロード開始時は、前のアップロードがあればキャンセル（または無効化）して整合性を守る🧼

---

## サンプル：進捗・停止・再開・キャンセル付きコンポーネント🧩

* `<progress>` を使うので、UIは超シンプルでOK👌
* 実務ではここに Tailwind で見た目を整える感じで🙌

```tsx
import React, { useEffect, useMemo, useRef, useState } from "react";
import { getStorage, ref, uploadBytesResumable, getDownloadURL, UploadTask } from "firebase/storage";

// 進捗表示用の状態
type UploadUiState =
  | { phase: "idle" }
  | { phase: "running"; progress: number }
  | { phase: "paused"; progress: number }
  | { phase: "done"; progress: 100; url: string; path: string }
  | { phase: "error"; progress: number; message: string };

export function ProfileImageUploader({ uid }: { uid: string }) {
  const storage = useMemo(() => getStorage(), []);
  const taskRef = useRef<UploadTask | null>(null);
  const unsubRef = useRef<null | (() => void)>(null);

  const [ui, setUi] = useState<UploadUiState>({ phase: "idle" });
  const [selected, setSelected] = useState<File | null>(null);

  // コンポーネント破棄時：監視解除＋タスク停止（安全第一🧯）
  useEffect(() => {
    return () => {
      unsubRef.current?.();
      unsubRef.current = null;
      taskRef.current?.cancel();
      taskRef.current = null;
    };
  }, []);

  const canPause = ui.phase === "running";
  const canResume = ui.phase === "paused";
  const canCancel = ui.phase === "running" || ui.phase === "paused";

  function resetToIdle() {
    setUi({ phase: "idle" });
    setSelected(null);
  }

  async function startUpload(file: File) {
    // 前の監視があれば解除
    unsubRef.current?.();
    unsubRef.current = null;

    // 前のタスクが残ってたら止める（多重事故防止）
    taskRef.current?.cancel();
    taskRef.current = null;

    // 置き場所（パス）は Chapter4/5 の設計に従う想定
    const fileId = crypto.randomUUID();
    const path = `users/${uid}/profile/${fileId}`;
    const fileRef = ref(storage, path);

    // 進捗付きアップロード開始
    const task = uploadBytesResumable(fileRef, file, { contentType: file.type });
    taskRef.current = task;

    // 初期状態
    setUi({ phase: "running", progress: 0 });

    // 監視（state_changed）
    unsubRef.current = task.on(
      "state_changed",
      (snapshot) => {
        const progress =
          snapshot.totalBytes > 0
            ? Math.round((snapshot.bytesTransferred / snapshot.totalBytes) * 100)
            : 0;

        // paused / running をUIへ反映
        if (snapshot.state === "paused") {
          setUi({ phase: "paused", progress });
        } else {
          setUi({ phase: "running", progress });
        }
      },
      (error: any) => {
        // キャンセルは「正常系の中断」扱いにするのがコツ🙂
        if (error?.code === "storage/canceled") {
          resetToIdle();
          return;
        }

        const progress =
          ui.phase === "running" || ui.phase === "paused" ? ui.progress : 0;

        // ここでは代表的なものだけメッセージ化（Chapter7/Rulesで改善していく）
        const message =
          error?.code === "storage/unauthorized"
            ? "アップロード権限がありません（ログイン状態やRulesを確認してね）🔐"
            : "アップロードに失敗しました。通信状況やファイル形式を確認してね🧯";

        setUi({ phase: "error", progress, message });
      },
      async () => {
        // 完了！URL取得してUI反映
        const url = await getDownloadURL(task.snapshot.ref);
        setUi({ phase: "done", progress: 100, url, path });

        // 監視解除（完了したら解除してOK）
        unsubRef.current?.();
        unsubRef.current = null;
        taskRef.current = null;
      }
    );
  }

  function pause() {
    taskRef.current?.pause();
  }
  function resume() {
    taskRef.current?.resume();
  }
  function cancel() {
    taskRef.current?.cancel();
    // cancel後は error observer で storage/canceled が来て resetToIdle() になる
  }

  return (
    <div style={{ display: "grid", gap: 12, maxWidth: 520 }}>
      <div>
        <input
          type="file"
          accept="image/*"
          onChange={(e) => {
            const f = e.target.files?.[0] ?? null;
            setSelected(f);
          }}
        />
      </div>

      <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
        <button
          onClick={() => selected && startUpload(selected)}
          disabled={!selected || ui.phase === "running" || ui.phase === "paused"}
        >
          アップロード開始⬆️
        </button>

        <button onClick={pause} disabled={!canPause}>
          一時停止⏸️
        </button>

        <button onClick={resume} disabled={!canResume}>
          再開▶️
        </button>

        <button onClick={cancel} disabled={!canCancel}>
          キャンセル🛑
        </button>
      </div>

      <div>
        {/* 進捗バー */}
        {"running" === ui.phase || "paused" === ui.phase ? (
          <>
            <progress value={ui.progress} max={100} style={{ width: "100%" }} />
            <div style={{ marginTop: 6 }}>
              {ui.phase === "running" ? "アップロード中…" : "一時停止中…"}{" "}
              {ui.progress}%
            </div>
          </>
        ) : null}

        {/* エラー */}
        {ui.phase === "error" ? (
          <div style={{ marginTop: 8 }}>
            <progress value={ui.progress} max={100} style={{ width: "100%" }} />
            <div style={{ marginTop: 6 }}>{ui.message}</div>
            <button style={{ marginTop: 8 }} onClick={resetToIdle}>
              やり直す🔁
            </button>
          </div>
        ) : null}

        {/* 完了 */}
        {ui.phase === "done" ? (
          <div style={{ marginTop: 8 }}>
            <div>完了！🎉</div>
            <img
              src={ui.url}
              alt="profile"
              style={{ width: 120, height: 120, borderRadius: "50%", objectFit: "cover", marginTop: 8 }}
            />
            <div style={{ marginTop: 8, fontSize: 12 }}>
              保存パス: <span>{ui.path}</span>
            </div>
            <button style={{ marginTop: 8 }} onClick={resetToIdle}>
              もう一度やる📷
            </button>
          </div>
        ) : null}
      </div>
    </div>
  );
}
```

この実装は、公式ドキュメントの **進捗計算（bytesTransferred / totalBytes）**、状態（paused/running）、`pause/resume/cancel` の動きに沿っています。([Firebase][1])

---

## ミニ課題🧩（10〜15分）🔥

1. 進捗表示を **%だけじゃなく「KB/MB」表示**も追加してみよう📏
   （例：`(bytesTransferred/1024/1024).toFixed(1)` みたいな感じ）
2. `paused` のときは「再開▶️」だけ押せるようにして、ボタンの **有効/無効**を整理しよう🎛️
3. `storage/canceled` を「エラー表示しない」ようにして、キャンセル体験を気持ちよくしよう🙂

---

## チェック✅（できた？）

* アップロード中に進捗%が増えていく📈
* 一時停止すると止まる⏸️（状態表示も変わる）
* 再開すると続きから進む▶️
* キャンセルすると `storage/canceled` 扱いでスッと戻る🛑
* 完了したら `getDownloadURL()` で画像が表示される🖼️([Firebase][1])

---

## 🤖 AIで“さらに実務っぽく”する小ワザ（この章の範囲でできるやつ）

### 1) Antigravity / Gemini CLI で「UI文言」を一瞬で整える🧠💬

アップロード中の文言って、地味に悩むよね😂
そこで AI に「気持ちいい文言案」を出させるのが速い！

しかも **Firebase MCP server** は Antigravity や Gemini CLI などの MCP クライアントと一緒に使えるので、Firebase周りの理解も加速できます🚀([Firebase][2])

例：AIに投げるお題👇

* 「進捗0〜100%で、ユーザーが不安にならないメッセージ案を10個」
* 「キャンセル時は“失敗”に見えない文言にして」
* 「アップロード中のボタン文言、短くて分かりやすくして」

### 2) FirebaseのAI（Firebase AI Logic）と自然につなぐ🌈

Firebase AI Logic は **Gemini / Imagen をアプリから扱える**仕組みで、App Check などと組み合わせた “乱用対策” も考慮されています。([Firebase][3])
この章では実装はしないけど、次のどこかでこういう“現実アプリ感”が出せるよ👇

* アップロード完了後に、Gemini に「画像の短い説明（altテキスト）」を作らせる📝🤖
* 「プロフィール画像として適切？」を軽く判定して注意を出す🧯

---

## 次章へのつながり🔜

第6章で **“途中経過が見える”** までできたので、次は **アップ前に弾く（ファイル形式・サイズなど）** をやると、一気に事故が減るよ〜🚦✨

[1]: https://firebase.google.com/docs/storage/web/upload-files "Upload files with Cloud Storage on Web  |  Cloud Storage for Firebase"
[2]: https://firebase.google.com/docs/ai-assistance/mcp-server "Firebase MCP server  |  Develop with AI assistance"
[3]: https://firebase.google.com/docs/ai-logic "Gemini API using Firebase AI Logic  |  Firebase AI Logic"
