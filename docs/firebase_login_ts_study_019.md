# 第19章：強い認証の入口：MFA（多要素）の位置づけだけ触れる🧿

この章は「実装をガッツリ」じゃなくて、**“必要になる場面”を言語化して、設計に落とす**のがゴールだよ🙂
（ただし、**雰囲気が掴める最小のハンズオン**はやるよ〜🛠️）

---

## 0) この章のゴール🎯

* MFA（多要素認証）って何を守れるの？を説明できる🙂
* 「うちのアプリは **いつMFAが必要**？」が決められる🧠
* “重要操作だけMFA”みたいな **段階的（Step-up）** の発想が入る🚧
* Firebase側で **MFAを有効化する場所**を知っておく🔧
* できれば「MFA必須になる瞬間」のエラー（`multi-factor-auth-required`）を一回見ておく👀

---

## 1) そもそもMFAってなに？🧩

![MFA Concept

**Labels to Render**:
- Password: "Something you know 🧠"
- Phone: "Something you have 📱"
- Lock: "Access Granted 🔓"

**Visual Details**:
1. Core Concept: Combining two factors for security.
2. Metaphor: A door with two locks. One key (Password) and one keypad (Phone code).
3. Action: Unlocking both.
4. Layout: Split composition merging into one.](./picture/firebase_login_ts_study_019_01_mfa_concept.png)


**MFA（Multi-Factor Authentication）**は、ログイン時に
「パスワードだけ」じゃなくて **追加の確認（2段階）** を入れる仕組みだよ🔐✨

よくある現実😇👇

* パスワードは漏れる（使い回し・フィッシング・流出…）💥
* Googleログインでも“セッション乗っ取り”みたいな事故はゼロじゃない😵
* そこで「本人が持ってるもの（スマホ）」や「アプリのコード」で追加チェック🧿

---

## 2) FirebaseでのMFAの現実（Web編）🧠

## ✅ SMSのMFA（Web）は「Identity Platform へのアップグレード」が前提

Firebase公式のWeb向けMFAは、**Firebase Authentication with Identity Platform** にアップグレードして使う流れが明記されてるよ。([Firebase][1])
コンソールの **Authentication → Sign-in method → Advanced** あたりで **SMS Multi-factor Authentication** を有効化する感じ👍([Firebase][1])

> 開発中は **テスト用電話番号**を登録しておくのが強く推奨（スロットリング回避）って書かれてるよ📵💦([Firebase][1])

## ✅ TOTP（認証アプリの6桁コード）も“Webに追加”できる

Web向けに **TOTP MFA を追加する公式ページ**があるよ（QRを読み取って認証アプリでコード生成するやつ）📱🔢([Firebase][2])
プロジェクト側でTOTPを有効にするには **Admin SDK か project config のREST**で設定する流れになってる。([Firebase][2])
さらに、**Admin Node SDK v11.6.0+ が必要**って条件も明記されてるよ🧷([Firebase][2])

---

## 3) MFAは「全員必須」にする？「必要な人だけ」にする？🤔

![MFA Patterns

**Labels to Render**:
- A: "All Users (Heavy) 🧱"
- B: "Optional (Light) 🍃"
- C: "Step-up (Balanced) ⚖️"

**Visual Details**:
1. Core Concept: Three strategies for implementing MFA.
2. Metaphor: A: A heavy fortress wall. B: An open gate with a sign. C: A light gate that turns into a heavy wall only when needed.
3. Action: Comparison.
4. Layout: Three panels.](./picture/firebase_login_ts_study_019_02_mfa_patterns.png)


Firebase公式でも、MFAの“入れ方パターン”が整理されてるよ👇([Firebase][1])

## パターンA：全員必須（強いけど重い）💪🧱

* 管理画面・金融・医療など、最初からガチガチに守る必要がある場合向け🏦🩺
* UXは重くなりやすい（離脱も増えやすい）😵‍💫

## パターンB：登録時に「スキップ可」で勧誘（バランス型）🌈

* まずは使ってもらい、後からMFAを付けてもらう🙌
* “後回しにされる”リスクはある🥲

## パターンC：重要操作だけMFA（Step-up認証）🚧✨ ← 初学者におすすめ

![Step-up Authentication Flow

**Labels to Render**:
- Login: "Standard (Easy) 🙂"
- Action: "Critical (Stop!) 🛑"
- MFA: "Verify (SMS) 📱"
- Result: "Allowed ✅"

**Visual Details**:
1. Core Concept: MFA is only required for sensitive actions.
2. Metaphor: A user walking freely until they reach a vault. To open the vault, they need a special key (MFA).
3. Action: Stopping and verifying.
4. Layout: Linear flow.](./picture/firebase_login_ts_study_019_03_step_up_flow.png)


* 普段ログインは軽く
* **「お金」「権限」「個人情報」「破壊操作」** の直前だけMFA要求🔥
* UXと安全のバランスが良い🙂

---

## 4) まず決めること（設計ワーク）📝🧠

ここが一番大事！✨
あなたのアプリで「MFAを要求すべき操作」をリスト化しよう👇

## “MFAが欲しい操作”テンプレ✅

![Critical Actions Checklist

**Labels to Render**:
- Item 1: "Change Password 🔑"
- Item 2: "Payment 💳"
- Item 3: "Delete Data 🗑️"
- Item 4: "API Key 🗝️"

**Visual Details**:
1. Core Concept: Identifying actions that need protection.
2. Metaphor: A clipboard with a checklist of high-risk items, marked with red flags.
3. Action: Listing.
4. Layout: List view with icons.](./picture/firebase_login_ts_study_019_04_critical_actions.png)


* 🔐 **パスワード変更**
* 📧 **メールアドレス変更**
* 💳 **決済 / 返金 / プラン変更**
* 👑 **権限変更（admin付与・削除）**
* 🗑️ **データ削除（復元できない）**
* 📦 **個人データのエクスポート（CSVダウンロード等）**
* 🔑 **APIキー発行 / 再生成**
* 🧾 **請求情報の閲覧（住所・カード末尾など）**

## ルール例（そのまま使ってOK）🙂

* ログイン直後：MFAなしでOK
* 上の重要操作を押した瞬間：**Step-up（MFA要求）**
* 直近5分以内にStep-up済みなら：もう一回は要求しない（UX配慮）⏱️

---

## 5) “UI導線”の作り方（実装前に絵を描く）🎨🧭

![Security Settings UI

**Labels to Render**:
- Section: "Two-Factor Auth"
- Status: "Not Enabled ⚠️"
- Button: "Setup MFA 🛡️"
- Note: "Recommended"

**Visual Details**:
1. Core Concept: The user interface for enabling MFA.
2. Metaphor: A clean settings panel wireframe.
3. Action: User about to click 'Setup'.
4. Layout: UI Mockup.](./picture/firebase_login_ts_study_019_05_security_settings_ui.png)


最低限これだけ決めると、後の実装が超ラクになるよ🙂

* 「セキュリティ設定」ページを作る🔐

  * **MFA未設定 → “おすすめです” + 設定ボタン**
  * **MFA設定済み → “解除” は慎重に（Step-up必須に）**
* 重要操作を押したら

  * 「この操作は大事なので追加確認します🧿」モーダル
  * MFAフローへ誘導

---

## 6) 手を動かす（最小）🛠️✨

## 6-1) コンソール側：MFAをONにする🔧

* Authentication → Sign-in method → Advanced → **SMS Multi-factor Authentication を有効化**
* **テスト用電話番号**も入れておく（開発が安定する）📞🧪([Firebase][1])

## 6-2) ローカルでMFAを“安全に試す”ならエミュレータが強い🧯

FirebaseのCodelabでは、**Auth EmulatorがMFAをサポート**していて、ログインすると **MFAコードがターミナルに出る**って説明されてるよ（開発を自己完結にできる）🧪🖥️([Firebase][3])

---

## 7) 手を動かす（最小コード）🧩 TypeScriptで“MFA必須エラー”を受け止める

![MFA Error Handling Logic

**Labels to Render**:
- Error: "multi-factor-auth-required"
- Catch: "getMultiFactorResolver"
- Action: "Show Modal"

**Visual Details**:
1. Core Concept: Catching the specific error to trigger the MFA flow.
2. Metaphor: A sorting machine. Normal errors go to the bin. The MFA error triggers a special alarm and opens a new gate (Modal).
3. Action: Routing.
4. Layout: Flowchart.](./picture/firebase_login_ts_study_019_06_error_logic.png)


この章では「MFAの本実装」までは踏み込まず、
**“MFAが必要になったら専用UIに切り替える”入口**だけ作るよ🚪✨

## 例：重要操作（例：メール変更）の前に「追加確認が必要かも」を受ける

```ts
import { getMultiFactorResolver } from "firebase/auth";
import type { Auth } from "firebase/auth";

export async function runSensitiveAction(auth: Auth) {
  try {
    // ここに「重要操作の前の再認証」や「重要操作そのもの」を置くイメージ
    // 例: reauthenticateWithCredential(...) とか、メール変更処理とか
  } catch (e: any) {
    // MFAが必要なときに来る代表エラー
    if (e?.code === "auth/multi-factor-auth-required") {
      const resolver = getMultiFactorResolver(auth, e);

      // resolver.hints に「どの2段階を使えるか」が入る（SMS/TOTPなど）
      // → ここで “MFA入力モーダル” を開く、という設計にする
      return {
        needMfa: true,
        resolver,
      };
    }

    // その他は普通に投げる
    throw e;
  }
}
```

ポイント🙂👇

* **「MFAは別画面/別モーダル」**に逃がすと実装が綺麗になる✨
* この章では `resolver` を受け取って「UIを開く」だけでOK🙆‍♂️
* 次の段階で、SMS/TOTPそれぞれのフローを埋めていく感じ！

---

## 8) ミニ課題🎯：「セキュリティ設定ページ」を作る🔐🧿

作るもの👇

* `/settings/security` 的なページ🧭
* 表示だけでOK（本実装は後回しでもOK）🙆‍♂️

  * ✅ 「MFA：未設定 / 設定済み」を表示
  * 🔘 「MFAを設定する」ボタン（今は“準備中”でもOK）
  * 🚨 「MFAを解除する」ボタン（押したら“重要操作なので追加確認します”と出す）

## 🔥AIを絡める（Firebase AI Logic / Gemini）

![AI Explanation Assistant

**Labels to Render**:
- User: "Why MFA?"
- AI: "To protect your money! 💸"
- Tone: "Friendly & Clear"

**Visual Details**:
1. Core Concept: AI generating user-friendly explanations.
2. Metaphor: A robot assistant holding a sign that translates "Security Protocol" to "Safety First".
3. Action: Explaining.
4. Layout: Interaction.](./picture/firebase_login_ts_study_019_07_ai_assist.png)


「なんでMFAが必要なの？」をユーザーに優しく説明する文章、毎回手で書くのしんどいよね🥲
そこで、**説明文だけGeminiに生成させる**のが気持ちいい✨

* 例：「決済・個人情報の変更は追加確認が必要な理由」を、短く/丁寧に/怖がらせずに…みたいに生成💬🤖
  （AI Logic自体の呼び出し詳細はAI章で本格的にやる想定で、この章では“使いどころの発想”を掴めればOK🙂）

---

## 9) チェック問題✅（3分でOK）

1. MFAを入れる目的を一言で言うと？🔐
2. あなたのアプリで「重要操作」3つ挙げると？📝
3. “全員必須” と “重要操作だけ” の違い（メリット/デメリット）を言える？⚖️
4. `auth/multi-factor-auth-required` が出たら、UIはどう切り替える？🧭

---

## 10) つまずきがちな所😵‍💫（先回りメモ）

* SMSが届かない / 遅い📵
  → 開発中は **テスト用電話番号**登録が推奨（スロットリング回避）([Firebase][1])
* ローカル検証が面倒🌀
  → **Auth Emulator + MFA** の流れがCodelabで案内されてる（コードがターミナルに出る）([Firebase][3])
* TOTPをやりたいけど、どこでON？🤔
  → Web向けTOTP追加ページ＆プロジェクト側の有効化手順が公式にある([Firebase][2])

---

## 11) Antigravity / Gemini CLI に投げると爆速になる依頼例🚀🤖

* Antigravity（エージェント型IDE）で「設計の叩き台」を作らせる🧠🧱([Google Codelabs][4])

  * 「このアプリ（認証あり）の重要操作を想定して、MFAを要求すべき一覧を作って」
  * 「Step-up認証の画面遷移図をMermaidで出して」🗺️

* Gemini CLI（ターミナルのAIエージェント）で「プロジェクト点検」🔎([Google for Developers][5])

  * 「重要操作っぽい関数を列挙して、MFAを噛ませるべき箇所を指摘して」
  * 「エラー表示の文言を、ユーザーが次に何をすれば良いか分かる日本語に整えて」🙂

---

## この章のまとめ🎉

* MFAは「ログインの強化」だけじゃなく、**重要操作の前にだけ要求する（Step-up）**のが強力🚧✨
* WebのSMS MFAは **Identity Platform前提**で、コンソールで有効化＆テスト番号が推奨📞([Firebase][1])
* TOTPもWebで扱える流れが公式にある（プロジェクト側で有効化が必要）🔢([Firebase][2])
* 実装は次段階でOK。今は **“いつ必要か”を決めて、UI導線を作る**だけで勝ち🙂🏆

---

次の章（第20章）はミニ課題の総仕上げだね✅🚪
もし「Step-upで、具体的にどの操作からMFAを噛ませるのが気持ちいいか」も一緒に決めたいなら、あなたのアプリの想定（例：管理画面/投稿/課金あり等）に合わせて“重要操作リスト”をカスタムして提案するよ🙂✨

[1]: https://firebase.google.com/docs/auth/web/multi-factor?utm_source=chatgpt.com "Enabling multi-factor authentication - Firebase - Google"
[2]: https://firebase.google.com/docs/auth/web/totp-mfa?utm_source=chatgpt.com "Add TOTP multi-factor authentication to your web app - Firebase"
[3]: https://firebase.google.com/codelabs/auth-mfa-blocking-functions?hl=ja&utm_source=chatgpt.com "高度な認証機能 - Firebase - Google"
[4]: https://codelabs.developers.google.com/getting-started-google-antigravity?utm_source=chatgpt.com "Getting Started with Google Antigravity"
[5]: https://developers.google.com/gemini-code-assist/docs/gemini-cli?utm_source=chatgpt.com "Gemini CLI | Gemini Code Assist"
