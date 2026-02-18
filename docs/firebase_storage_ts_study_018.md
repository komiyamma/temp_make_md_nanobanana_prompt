### 第18章：ローカルで安全に試す（エミュレーター＆切り替え）🧪🧯

この章はひとことで言うと「**本番を汚さずに、わざと失敗させて強くなる**」回です😎✨
Storage って、Rules・App Check・認証が絡むとバグりやすいので、**最初から“安全に壊せる場所”**を作っておくのが最強です💪🔥

---

#### この章でできるようになること 🎯

* ローカルで **Auth/Firestore/Storage** を動かして、課金・本番データ汚染を回避🏠✅ ([Firebase][1])
* React 側を **エミュレーター接続 / 本番接続** で切り替えできるようにする🔁🧩
* わざと「サイズ超過」「権限なし」「未ログイン」を起こして、**正しく弾ける**のを確認💥🛡️
* Antigravity / Gemini CLI で、Rules・テストケース・詰まり原因をAIに素早く整理させる🤖🚀 ([Firebase][2])

---

## 読む：エミュレーターが“最強の保険”な理由 🧠🛟

### 1) ローカル実行のメリットがでかすぎる 😭✨

* 本番データが汚れない（変な画像が残らない）🧼
* 失敗ケースを何回やっても安全（Rulesの穴あきテストもOK）🕳️🔍
* Storage/Firestore の読み書き回数でドキドキしなくていい💸🙅‍♂️
* エミュレーター UI で「今なにが起きてる？」が見える👀🧪 ([Firebase][1])

### 2) 注意：設定しないと“開きっぱなし”になることがある⚠️🚪

エミュレーターは便利だけど、**Rules や設定をちゃんと紐づけないと “open data security” 状態で動くことがある**ので注意です😱
（＝ローカルとはいえ、ルール検証としては最悪）([Firebase][1])

---

## 手を動かす：Windowsでエミュレーター起動→React切替→失敗テスト💻⚙️

### Step 0：必要なもの（最低ライン）✅

* Firebase CLI（エミュレーター操作に必須）
* Node.js（Firebase CLI の要件として **Node 16+**）([Firebase][1])
* Java（エミュレーター実行に **Java JDK 11+**）([Firebase][1])

---

### Step 1：エミュレーターを初期化＆起動 🔥

プロジェクト直下で👇（PowerShellでもOK）

```powershell
# 1回だけなら npx でもOK（グローバル汚さない派）
npx firebase-tools@latest --version

# グローバルで入れたいなら
npm i -g firebase-tools
firebase --version

# エミュレーター初期化（Auth / Firestore / Storage を選ぶのが定番）
firebase init emulators

# 起動
firebase emulators:start
```

起動すると、だいたいこのポートが使われます👇

* Emulator UI: **4000**
* Auth: **9099**
* Firestore: **8080**
* Storage: **9199** ([Firebase][1])

---

### Step 2：`firebase.json` の例（雰囲気）🧩

`firebase init emulators` が作る形に近い例です👇（細部はあなたの生成物が正）

```json
{
  "emulators": {
    "ui": { "enabled": true, "port": 4000 },
    "auth": { "port": 9099 },
    "firestore": { "port": 8080 },
    "storage": { "port": 9199 }
  },
  "firestore": { "rules": "firestore.rules" },
  "storage": { "rules": "storage.rules" }
}
```

ポイントはこれ👇

* **Rules ファイルをちゃんと紐づける**（じゃないと検証にならない）([Firebase][1])
* Firestore/Storage の両方を使うなら、両方エミュレートするのが楽ちん🧠✨

---

### Step 3：Storage Rules を“わざと厳しく”して失敗を作る🛡️💥

ここは「失敗ケースを起こす」ため、あえて上限を小さくします（例：200KB）📉

```txt
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /users/{uid}/profile/{fileId} {
      allow write: if request.auth != null
        && request.auth.uid == uid
        && request.resource.size < 200 * 1024
        && request.resource.contentType.matches('image/(jpeg|png)');
      allow read: if request.auth != null && request.auth.uid == uid;
    }
  }
}
```

`request.resource.size` と `request.resource.contentType` で制限できるのがキモです🧠🛡️ ([Firebase][3])

---

### Step 4：React 側を「本番 / エミュ」切り替えにする🔁✨

#### 4-1) `.env.local`（ローカルだけ有効）🧪

Vite想定の例です👇

```env
VITE_USE_EMULATORS=true
```

#### 4-2) `src/firebase.ts`（接続先を切り替える）🧩

**重要：`connect*Emulator()` は、使う前に1回だけ**呼ぶのがコツです（HMRで2回呼ぶと事故りがち😵‍💫）

```ts
import { initializeApp } from "firebase/app";
import { getAuth, connectAuthEmulator } from "firebase/auth";
import { getFirestore, connectFirestoreEmulator } from "firebase/firestore";
import { getStorage, connectStorageEmulator } from "firebase/storage";

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET
};

const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);
export const db = getFirestore(app);
export const storage = getStorage(app);

// ✅ 切り替えフラグ（localだけ true にする）
const USE_EMULATORS = import.meta.env.VITE_USE_EMULATORS === "true";

// ✅ HMR対策：二重接続を防ぐ
const g = globalThis as unknown as { __emuConnected?: boolean };

if (USE_EMULATORS && !g.__emuConnected) {
  connectAuthEmulator(auth, "http://127.0.0.1:9099");
  connectFirestoreEmulator(db, "127.0.0.1", 8080);
  connectStorageEmulator(storage, "127.0.0.1", 9199);
  g.__emuConnected = true;
}
```

* Storage エミュへの接続は `connectStorageEmulator(storage, host, port)` でOKです🧩
* Auth エミュも同様に `connectAuthEmulator` で接続します🔐 ([Firebase][4])
* さらに安全にするなら、**エミュ用の “demo project” を使う**のが推奨です（特にチーム学習や教材では強い）([Firebase][4])

---

### Step 5：アップロードして、成功→失敗を観察する👀📷

前章までの `uploadBytesResumable` / `getDownloadURL` がそのまま使えます。
この章のポイントは **「失敗のときに、ちゃんと失敗してくれるか？」** です😎🧯

#### 失敗を起こすネタ（おすすめ3つ）💥

1. **サイズ超過**：200KB超える画像を投げる → 弾かれる✅
2. **権限なし**：`users/他人uid/profile/...` に書こうとする → 弾かれる✅
3. **未ログイン**：ログアウトしてからアップロード → 弾かれる✅

弾かれたら、それは勝ち🎉（Rulesが仕事してる！）

---

### Step 6：App Check を入れてる場合のローカル対策🧿🧪

App Check を本番で強制してると、ローカルは“正規環境じゃない”扱いになりやすいです💦
Web では **Debug Provider** を使うのが定番です🧩（デバッグトークンで通す）

* Debug token は **秘密にする**（漏れると危険）
* コンソール側で token を許可リストに入れる必要あり
  …などの注意があります⚠️ ([Firebase][5])

（※ここは第17章の復習ポイントでもあります🔁）

---

### Step 7：ローカルデータを保存したい（import/export）📦💾

毎回まっさらにしたくないときは、エミュのデータを **import/export** できます🎒
起動オプションで扱えるので便利です✨ ([Firebase][1])

---

## AI活用：Antigravity / Gemini CLI で“検証の質”を上げる🤖🚀

### 1) Firebase MCP server を使うと何が嬉しい？🧩

Firebase MCP server は、Antigravity / Gemini CLI などのAIアシスタントからFirebase作業を進めるための土台で、**定番プロンプト集**も付いてきます📚✨ ([Firebase][2])

たとえば Gemini CLI だと、プロンプトが **スラッシュコマンド**で出てきます👇

* `/firebase:init`
* `/firebase:generate_security_rules`（Firestore/StorageのRules生成＆テスト） ([Firebase][2])

### 2) この章でAIにやらせると効くこと💡

* 「このStorage Rules、穴ない？最小権限？」🕵️‍♂️
* 「失敗ケースのテスト項目を10個出して」🧪
* 「エミュで出たエラー文、原因候補を3つに絞って」🧯
* 「HMRで connectEmulator が2回走る事故の回避案は？」😵‍💫

---

## Firebase AI Logic との付き合い方（ローカル編）🤖🧠

AI Logic はクラウド側のAIモデルを使うので、エミュだけで完結しにくいです。
だからローカルでは👇がラクです✨

* **`VITE_USE_EMULATORS=true` のときは AI 呼び出しをモック**（固定文を返す）
* 本番だけ AI Logic を使う（またはステージングで試す）🔁

あと地味に大事：AI Logic 側のモデルは入れ替わることがあるので、教材・実装では「今使ってるモデル名」を固定しつつ、**廃止予定に注意**です⚠️（例：一部モデルが 2026-03-31 で退役予定の案内あり）([Firebase][6])

---

## ミニ課題：わざと壊して、直して、勝つ🏁🔥

1. `VITE_USE_EMULATORS` で接続が切り替わるのを確認🔁✅
2. さっきの Rules を入れて、次の3つで弾かれるのを確認🧪

   * サイズ超過📦
   * 未ログイン🔐
   * 他人パス書き込み👤
3. AIに「追加で5個、失敗テスト案」を出してもらって実行💥🤖 ([Firebase][2])

---

## チェック：できたか確認✅✨

* エミュ起動できて Emulator UI が見える👀 ([Firebase][1])
* React が `connectStorageEmulator` に接続している🧩
* Rules の size / contentType 制限でちゃんと弾ける🛡️ ([Firebase][3])
* “失敗したときに失敗する”＝本番事故が減る🧯🎉

---

## 次章へのつなぎ（チラ見せ）👀➡️

Storage と Functions の両方のエミュを動かすと、**Storageイベント→Functions**の流れもローカルで試せます（ここが実務っぽくなって超楽しい😆⚙️）

---

必要なら次の返答で、この第18章の続きとして
**「失敗ケース別：出がちなエラー文と対処テンプレ（App Check含む）」**を、超実戦チート表みたいにまとめます🧯😎

[1]: https://firebase.google.com/docs/emulator-suite/install_and_configure "Install, configure and integrate Local Emulator Suite  |  Firebase Local Emulator Suite"
[2]: https://firebase.google.com/docs/ai-assistance/prompt-catalog "AI prompt catalog for Firebase  |  Develop with AI assistance"
[3]: https://firebase.google.com/docs/storage/security/rules-conditions "Use conditions in Firebase Cloud Storage Security Rules  |  Cloud Storage for Firebase"
[4]: https://firebase.google.com/docs/emulator-suite/connect_auth "Connect your app to the Authentication Emulator  |  Firebase Local Emulator Suite"
[5]: https://firebase.google.com/docs/app-check/web/debug-provider?utm_source=chatgpt.com "Use App Check with the debug provider in web apps - Firebase"
[6]: https://firebase.google.com/docs/ai-logic/ref-docs "Reference documentation for the Firebase AI Logic SDKs  |  Firebase AI Logic"
