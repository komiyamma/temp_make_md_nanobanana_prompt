これから「第20章」を、**Extensions（自動サムネ）＋Functions（整合性）＋AI（説明文/タグ/判定）**を“1本の実務フロー”として組み上げる形で、手順→コード→チェックまで一気に教材化します🔥📷🤖

---

### 第20章：Extensions/Functions/AIの“合体技”で実務っぽくする🔥

#### この章のゴール🎯

プロフィール画像アップロードに、次の“自動化3点セット”を合体させます💪✨

1. **サムネ自動生成**：アップロードしたら勝手に `128px / 512px` を作る🧩
2. **整合性の自動管理**：Firestoreの状態（processing/ready等）をFunctionsで更新⚙️
3. **AIで付加価値**：画像説明（alt）・検索タグ・簡易NG判定を追加🤖📝

---

## 0) 全体の流れ（設計図）🗺️

**①ユーザーが画像を選ぶ**（React）
→ **②AIで“説明/タグ/判定”を作る**（Firebase AI Logic）
→ **③Storageへアップロード**（Cloud Storage for Firebase）
→ **④サムネ自動生成**（Firebase Extensions の Resize Images）
→ **⑤FunctionsがFirestoreを更新**（Cloud Functions for Firebase）
→ **⑥UIはFirestoreの状態を見て表示切替**（readyになったらサムネ表示✅）

---

## 1) サムネはExtensionsで“勝手に作る”🧩🖼️

ここは実務でも鉄板です。自分で画像処理を書く前に、まず拡張でラクします😎

### 1-1. Resize Images拡張を入れる🧩

Resize Images拡張は、Cloud Storageへのアップロードをトリガーにして画像をリサイズしてくれます（中で画像処理を実行）。Blazeプランが必要です。([extensions.dev][1])
また、**バケット内の変更を広く拾う**ので、実運用では「リサイズ対象を分けたバケット/パス設計」が推奨されます。([extensions.dev][1])

#### 推奨パス設計📁

* オリジナル：`users/{uid}/profile/original/{imageId}`
* サムネ：`users/{uid}/profile/thumbs/{imageId}_128` / `{imageId}_512` など

> 拡張のパラメータで「どのパスを対象にするか」「出力先」を指定できます👍

### 1-2. “サムネ生成完了”を検知したい人へ📣

Resize Images拡張は、設定によって**完了イベントを飛ばす**（Eventarc経由）こともできます。([extensions.dev][1])
今回は初心者向けに、まずは「**サムネファイルが生成された**」ことをFunctions側で検知する形でいきます（次の章で発展可能）✨

---

## 2) FunctionsでFirestoreの“状態”を自動で揃える⚙️🧠

ここからが「現実アプリ感」のキモです🔥
**UIは“ファイルがあるか”じゃなくて、“状態がreadyか”で判断**すると壊れにくいです👍

### 2-1. Firestoreのドキュメント例🗃️

`users/{uid}/profileImages/{imageId}` を作る想定で、こんな感じにします👇

* `originalPath`: `users/.../original/...`
* `thumb128Path`: `users/.../thumbs/..._128`
* `thumb512Path`: `users/.../thumbs/..._512`
* `aiAlt`: 画像説明（短文）
* `aiTags`: タグ配列
* `aiReview`: `"ok" | "needs_review"`
* `status`: `"processing" | "ready" | "failed"`
* `updatedAt`: サーバー時刻

---

### 2-2. Storageにオリジナルが来たら「processing」にする📥➡️⚙️

ポイント：

* Storageイベントは重複配信されることがあるので、**同じimageIdに対して上書きOK**な設計にする🙂
* `users/{uid}/profile/original/` だけ拾うようにする🎯

```ts
// functions/src/index.ts
import { initializeApp } from "firebase-admin/app";
import { getFirestore, FieldValue } from "firebase-admin/firestore";
import { onObjectFinalized } from "firebase-functions/v2/storage";

initializeApp();

export const onProfileOriginalUploaded = onObjectFinalized(
  {
    region: "asia-northeast1",
  },
  async (event) => {
    const obj = event.data;
    const name = obj.name ?? "";
    // users/{uid}/profile/original/{imageId}
    const m = name.match(/^users\/([^/]+)\/profile\/original\/([^/]+)$/);
    if (!m) return;

    const uid = m[1];
    const imageId = m[2];

    const docRef = getFirestore()
      .collection("users")
      .doc(uid)
      .collection("profileImages")
      .doc(imageId);

    await docRef.set(
      {
        originalPath: name,
        thumb128Path: `users/${uid}/profile/thumbs/${imageId}_128`,
        thumb512Path: `users/${uid}/profile/thumbs/${imageId}_512`,
        status: "processing",
        updatedAt: FieldValue.serverTimestamp(),
      },
      { merge: true }
    );
  }
);
```

#### ランタイムの目安🧠（2026-02-18時点）

* Functions（Node）：Node.js **20 / 22** がサポート対象（18は非推奨扱い）([Firebase][2])
* Functions（Python）：Python **3.10〜3.13**（デフォルトは3.13）([extensions.dev][1])

---

### 2-3. サムネが生成されたら「ready」にする🖼️✅

Resize Images拡張が作るサムネは “別オブジェクト” としてStorageに出てきます。
だから `thumbs/` の `onObjectFinalized` を拾えばOKです👌

```ts
import { onObjectFinalized } from "firebase-functions/v2/storage";
import { getFirestore, FieldValue } from "firebase-admin/firestore";

export const onProfileThumbCreated = onObjectFinalized(
  { region: "asia-northeast1" },
  async (event) => {
    const obj = event.data;
    const name = obj.name ?? "";
    // users/{uid}/profile/thumbs/{imageId}_128 など
    const m = name.match(/^users\/([^/]+)\/profile\/thumbs\/([^/]+)$/);
    if (!m) return;

    const uid = m[1];
    const fileName = m[2];

    // 例: abc_128 → imageId=abc
    const idMatch = fileName.match(/^(.+?)_(128|512)$/);
    if (!idMatch) return;

    const imageId = idMatch[1];

    const docRef = getFirestore()
      .collection("users")
      .doc(uid)
      .collection("profileImages")
      .doc(imageId);

    // 128/512の両方が来たか…まで厳密にやるなら、fieldsでフラグ管理がおすすめ🙂
    await docRef.set(
      {
        status: "ready",
        updatedAt: FieldValue.serverTimestamp(),
      },
      { merge: true }
    );
  }
);
```

> 厳密にやるなら `thumb128Ready/thumb512Ready` を持って「両方trueでready」がおすすめです👍（UIがチラつかない✨）

---

## 3) AIで“説明文/タグ/簡易NG判定”を足す🤖📝

ここからが楽しいところ！
Gemini を **クライアントから呼べる形**にするのが Firebase AI Logic の強みのひとつです（Web SDKもあります）。([Firebase][3])

### 3-1. Web（React）でモデルを作る🧠

ドキュメントの通り、Webは `firebase/ai` から読み込みます👇([Firebase][3])

```ts
import { initializeApp } from "firebase/app";
import { getAI, getGenerativeModel, GoogleAIBackend } from "firebase/ai";

const firebaseApp = initializeApp({ /* ... */ });

const ai = getAI(firebaseApp, { backend: new GoogleAIBackend() });
const model = getGenerativeModel(ai, { model: "gemini-2.5-flash" });
```

> モデル名は**Remote Configで後から差し替え**できるようにするのが推奨です（本番運用で超助かる）🔁([Firebase][3])
> なおモデルの入れ替わりは起きるので、“固定しない設計”が安全です🙂

### 3-2. 画像を解析してテキストを出す📷➡️📝

Firebase AI Logicは、画像＋テキストのマルチモーダル入力で `generateContent()` ができます。([Firebase][4])

**やりたいこと（例）**👇

* 画像説明（alt）：「短い日本語で」
* 検索タグ：「5個」
* 簡易判定：「プロフィール画像として不適切っぽいならneeds_review」

イメージ（Webは `model.generateContent([prompt, ...imageParts])` 形式）です👇([Firebase][4])

```ts
// 擬似コード：imageParts の作り方は「analyze-images」ドキュメントのWeb例に沿って実装する🙌
const prompt = `
あなたは画像の内容を要約するアシスタントです。
次のJSONだけ返してください:
{
  "alt": "20文字以内の日本語",
  "tags": ["タグ1","タグ2","タグ3","タグ4","タグ5"],
  "review": "ok or needs_review"
}
`;

const result = await model.generateContent([prompt, ...imageParts]);
const text = result.response.text();
const json = JSON.parse(text);
```

> コツ：**「JSONだけ返せ」**を強く言うとパースが安定します🙂✨
> そしてパースに失敗したら `review="needs_review"` に倒すのが安全です🛡️

---

## 4) “クラウド側の別言語”を選ぶときの目安🧠🧰

「画像処理/AI処理をサーバー側に寄せたい」「.NETでやりたい」みたいなときは、Google Cloud Run functions が選択肢になります。

* Cloud Run functions（.NET）：**.NET 8**（.NET 10はPreview枠）([Google Cloud Documentation][5])
* Cloud Run functions（Node）：**Node.js 20/22/24** が並んでいます（サポート表で確認）([Google Cloud Documentation][5])

---

## 5) Antigravity / Gemini CLI / MCPで“調査→修正→検証”を短距離化🚀🧩

ここは作業速度が爆上がりします😇
Firebase MCP server は、AIクライアントからFirebase操作をつなぐための仕組みとして案内されています。([Firebase][6])
設定例として `npx firebase-tools@latest mcp` を使う流れがドキュメントにあります。([Firebase][6])

**おすすめの使い方（プロンプト例）💡**

* 「このStorageパス設計、漏れやすい穴ある？」🕵️‍♂️
* 「このFunctions、同じイベントが2回飛んでも壊れない？」🔁
* 「このFirestoreのstatus遷移、UIがチラつかない形にして」🎨

※さらにコンソール内のAI（Gemini in Firebase）でログや設定の詰まりを相談するのもアリです🧯（詰まりが“会話で”ほどける系）([Firebase][7])

---

## ミニ課題（最終）🏁🔥

次を全部そろえて、**「変更したら勝手に揃う」**状態にしてください✅

1. オリジナルアップロードで `status="processing"` になる
2. サムネ生成後に `status="ready"` になる
3. AIで `aiAlt / aiTags / aiReview` が入る
4. UIは `ready` のときだけサムネを表示（processing中はスピナー）⏳

---

## チェックリスト✅😎

* [ ] オリジナルとサムネのパスが“混ざってない”📁
* [ ] Firestoreの `status` がUIの表示切替に直結している🎛️
* [ ] 失敗時に `failed` / `needs_review` に倒せてる🛡️
* [ ] AI出力は「JSONだけ返せ」で安定してる📦
* [ ] モデル名は後で替えられる設計になってる（Remote Config）🔁([Firebase][3])

---

## よくある詰まり🧯（ここだけ押さえれば大体勝てる🙂）

* **サムネが作られない**：拡張の“対象パス”がズレてることが多い（originalの場所が違う）
* **readyが早すぎる**：128だけ来た時点でreadyにしてる（フラグ方式にする）
* **AIのJSONが壊れる**：返答に余計な文章が混じる→「JSON以外禁止」を強く書く＋失敗時フォールバック

---

必要なら次は、この第20章の「完成版」として
**React側（アップロード＋AI＋Firestore購読）まで、1つのコンポーネントにまとめたサンプル**も出します📦✨

[1]: https://extensions.dev/extensions/firebase/storage-resize-images "Resize Images | Firebase Extensions Hub"
[2]: https://firebase.google.com/docs/functions/get-started?utm_source=chatgpt.com "Get started: write, test, and deploy your first functions - Firebase"
[3]: https://firebase.google.com/docs/ai-logic/get-started "Get started with the Gemini API using the Firebase AI Logic SDKs  |  Firebase AI Logic"
[4]: https://firebase.google.com/docs/ai-logic/analyze-images?utm_source=chatgpt.com "Analyze image files using the Gemini API | Firebase AI Logic"
[5]: https://docs.cloud.google.com/functions/docs/runtime-support "Runtime support  |  Cloud Run functions  |  Google Cloud Documentation"
[6]: https://firebase.google.com/docs/ai-assistance/mcp-server "Firebase MCP server  |  Develop with AI assistance"
[7]: https://firebase.google.com/docs/studio/customize-workspace?utm_source=chatgpt.com "Customize your Firebase Studio workspace - Google"
