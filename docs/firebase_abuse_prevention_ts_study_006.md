# 第06章：Enterprise版に差し替える（移行できる設計にする）🔁🏢

この章は「**reCAPTCHA v3 → reCAPTCHA Enterprise** へ、いつでも切り替えられる作り」にする回です💪✨
ポイントはシンプルで、**App Check の “provider を差し替え可能な部品” にする**だけです🧩

---

## 1) まず理解：Enterprise って何が “移行向き” なの？🧠

## ✅ reCAPTCHA v3 から Enterprise に寄せる流れが公式のおすすめ

Firebase の Web 向け App Check（reCAPTCHA v3）ページでは、**新規の統合は Enterprise を強く推奨**し、既存 v3 も **Enterprise へのアップグレード推奨**が明記されています。([Firebase][1])

## ✅ Enterprise は「スコアで怪しさを判断する」系（Webは invisible key が前提）

Enterprise では **スコアベース**で判定する設計で、Web では **score-based site key（invisible）**が推奨されています。([Firebase][2])

## 💸 料金と “トークン更新＝コスト” の感覚も大事

Enterprise は **月 10,000 assessments まで無料**で、それを超えると課金が発生します。さらに **App Check のトークン更新でも assessment が発生**するので、「更新頻度＝コスト」の感覚が必要です。([Firebase][2])
（だからこそ、**切り替えできる設計**にして “必要になったら Enterprise をON” が現実的 👍）

---

## 2) 今日のゴール（できたら勝ち🏁）🎯

* `initializeAppCheck()` を **1ファイルに封印**する📦
* provider を **Factory（生成関数）**にする🧰
* **v3 / Enterprise をスイッチ1つで切替**できるようにする🎛️
* ついでに **自前API（/api/ai-format など）へ App Check トークンを付けて呼ぶ**動作確認までやる🧪

---

## 3) “差し替えできる設計”の鉄則3つ 🧷

1. **App Check 初期化は1箇所だけ**（あちこちで `initializeAppCheck()` しない）
2. provider を作る処理は **関数に閉じ込める**（あとで差し替えやすい）
3. **キー（site key）を参照する場所を1箇所にする**（散らばると地獄😇）

---

## 4) Console 側：Enterprise のキーを作る（ざっくり）🛠️

Enterprise の導入は、Firebase のドキュメントに沿って進めるのが安全です。([Firebase][2])
（ここは画面操作が多いので、**“作業の意味” だけ**押さえます👀）

* reCAPTCHA Enterprise で **Web の score-based key（invisible）**を作る（ドメイン許可を忘れずに）([Firebase][2])
* Firebase Console の App Check で **Enterprise provider を選び、site key を登録**する([Firebase][2])
* しきい値（スコア）を調整する時の注意：
  Billing を設定していないと、選べるスコアが限定される場合があります（例：0.1/0.3/0.7/0.9 のみ等）。([Firebase][2])

---

## 5) 実装：provider を “差し替え部品” にする（React / TypeScript）⚛️🧿

ここからが本番🔥
構成はこんな感じがラクです👇

* `src/firebase/app.ts`（Firebase 初期化）
* `src/firebase/appCheck.ts`（App Check 初期化＝ここに封印）
* `src/main.tsx`（起動時に一回だけ呼ぶ）

## 5-1) App Check 初期化を1ファイルに封印する📦

```ts
// src/firebase/appCheck.ts
import type { FirebaseApp } from "firebase/app";
import {
  initializeAppCheck,
  ReCaptchaV3Provider,
  ReCaptchaEnterpriseProvider,
  setTokenAutoRefreshEnabled,
  type AppCheck,
} from "firebase/app-check";

export type AppCheckProviderKind = "v3" | "enterprise";

/**
 * provider を差し替え可能にする Factory 🧰
 */
function createProvider(kind: AppCheckProviderKind, siteKey: string) {
  if (kind === "enterprise") {
    return new ReCaptchaEnterpriseProvider(siteKey);
  }
  return new ReCaptchaV3Provider(siteKey);
}

/**
 * App Check 初期化（アプリ全体で1回だけ呼ぶ想定）🧿
 */
export function initAppCheck(app: FirebaseApp, args: {
  kind: AppCheckProviderKind;
  siteKey: string;
}): AppCheck {
  const provider = createProvider(args.kind, args.siteKey);

  // ✅重要：自動更新はデフォルトOFFなので、明示的にONにする
  // （initializeAppCheck の isTokenAutoRefreshEnabled でもOK）
  const appCheck = initializeAppCheck(app, {
    provider,
    isTokenAutoRefreshEnabled: true,
  });

  // 念のため二重にON（どちらかでOK）
  setTokenAutoRefreshEnabled(appCheck, true);

  return appCheck;
}
```

🔎 **自動更新がデフォルトOFF**なのは、Enterprise の公式ページでもハッキリ注意されています。([Firebase][3])
ここを忘れると「最初だけ動くけど、しばらくして死ぬ」みたいな事故が起きがちです😇

---

## 6) 切替スイッチの作り方（おすすめ順）🎛️

「v3/Enterprise どっちを使う？」の決め方は、代表的に3つあります👇
（どれも “第6章の目的＝差し替え可能” を満たします✨）

## A. いちばん堅い：ビルド時の環境変数で切替（おすすめ）🧱

* **メリット**：実装が簡単・事故が少ない
* **デメリット**：切替には再ビルドが必要

例（Vite想定）：

```ts
// src/firebase/providerConfig.ts
import type { AppCheckProviderKind } from "./appCheck";

export function getAppCheckProviderKind(): AppCheckProviderKind {
  return (import.meta.env.VITE_APP_CHECK_PROVIDER as AppCheckProviderKind) ?? "v3";
}
export function getAppCheckSiteKey(kind: AppCheckProviderKind): string {
  if (kind === "enterprise") return import.meta.env.VITE_RECAPTCHA_ENTERPRISE_SITE_KEY;
  return import.meta.env.VITE_RECAPTCHA_V3_SITE_KEY;
}
```

## B. そこそこ柔らかい：Hosting の静的JSONで切替（再ビルド不要）🪶

* `public/appcheck-config.json` を置く
* 起動時に fetch して provider 種別と site key を決める
* **Firebase を触る前に読める**ので、切替の自由度が高いです🧠

## C. Remote Config で切替（強いけど設計が必要）🧩

Remote Config は便利だけど、**「いつ・どこで読み込むか」**の設計が必要です。
おすすめの使い方はこれ👇

* provider 種別は **A or B で確定**（起動の超早い段階で決まる）
* Remote Config は **しきい値方針・UXメッセージ・AIボタンのレート制限**など “運用調整向き” に使う🎚️

---

## 7) 手を動かす：Enterprise に差し替えて動作確認する🧪✨

「差し替えたつもりだけど本当に効いてる？」を確かめるには、**自前APIに App Check トークンを付けて呼ぶ**のが手っ取り早いです👍
（公式も `getToken(appCheck, false)` → `X-Firebase-AppCheck` ヘッダーで送る例を出しています）([Firebase][4])

## 7-1) トークン付きで自前APIを叩くコード例🧾

```ts
// src/lib/callMyApi.ts
import type { AppCheck } from "firebase/app-check";
import { getToken } from "firebase/app-check";

export async function callAiFormatApi(appCheck: AppCheck, text: string) {
  const { token } = await getToken(appCheck, /* forceRefresh= */ false);

  const res = await fetch("/api/ai-format", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Firebase-AppCheck": token,
    },
    body: JSON.stringify({ text }),
  });

  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}
```

この方式は後々、**Functions / Cloud Run / 自前Express**にもそのままつながります🧱✨
（第18章の “カスタムバックエンド検証” の伏線にもなるやつ😎）

---

## 8) つまずきポイント（ここだけ注意⚠️）😵‍💫

* **`isTokenAutoRefreshEnabled: true` を忘れる** → 時限爆弾💣（公式が明確に注意）([Firebase][3])
* **スコアのしきい値を上げすぎる** → 正常ユーザーが弾かれて UX 崩壊🙂‍↕️
* **課金の感覚がないまま Enterprise を全開放** → 更新・利用増でコスト増の可能性💸([Firebase][2])

---

## 9) AI活用：移行の“事故ポイント”を先に潰す🤖🛡️

## 🛰️ Googleの「Antigravity」でやると速い🚀

Antigravity の “Mission Control 的な進め方” は、公式 Codelabs でも紹介されています。([Google Codelabs][5])
おすすめミッション例👇

* ✅「App Check 初期化を 1 ファイルへ集約」
* ✅「provider を factory 化」
* ✅「v3/Enterprise 切替スイッチ導入」
* ✅「自前APIへのトークン送信の動作確認」

## 🧰 Google Cloudの「Gemini CLI」でコード監査🔎

Gemini CLI は “ターミナルで動くオープンソースのAIエージェント” として Codelabs/公式ブログでも扱われています。([Google Codelabs][6])

投げると強い指示（例）👇

* 「`initializeAppCheck` が複数回呼ばれてないか探して」
* 「Firestore/Storage 呼び出しが App Check 初期化より先に走ってないか見て」
* 「切替スイッチ（env/json）を安全に実装する差分案を出して」

---

## ミニ課題（10〜15分）📝🔥

1. `AppCheckProviderKind` を `"v3" | "enterprise"` で作る✅
2. `createProvider()` を実装して、**差し替えが1行で済む**ようにする🎛️
3. `/api/ai-format` に `X-Firebase-AppCheck` を付けて呼ぶ（成功/失敗の分岐を確認）🧪
4. 「しきい値上げすぎのUX事故」を1つ想像して、対策文を1行で書く🙂

---

## チェック✅（ここが言えたらOK🎉）

* provider は **“差し替え可能な部品”**になってる🧩
* `initializeAppCheck()` は **1箇所に封印**できた📦
* 自動更新を **明示的にON**にしてる🔁([Firebase][3])
* `getToken()` → `X-Firebase-AppCheck` で **自前APIに渡せる**🧾([Firebase][4])

---

次の第7章は、この章で作った “差し替え可能な設計” を武器にして、**いきなり強制せずメトリクス監視から入る**流れに進めます👀📈
（ここから一気に “守りが運用になる” 感が出て楽しいです😆🔥）

[1]: https://firebase.google.com/docs/app-check/web/recaptcha-provider "Get started using App Check with reCAPTCHA v3 in web apps  |  Firebase App Check"
[2]: https://firebase.google.com/docs/app-check/web/recaptcha-enterprise-provider "Get started using App Check with reCAPTCHA Enterprise in web apps  |  Firebase App Check"
[3]: https://firebase.google.com/docs/app-check/web/recaptcha-enterprise-provider?utm_source=chatgpt.com "Get started using App Check with reCAPTCHA Enterprise in ..."
[4]: https://firebase.google.com/docs/app-check/web/custom-resource?utm_source=chatgpt.com "Protect custom backend resources with App Check in web apps"
[5]: https://codelabs.developers.google.com/getting-started-google-antigravity "Getting Started with Google Antigravity  |  Google Codelabs"
[6]: https://codelabs.developers.google.com/gemini-cli-hands-on?utm_source=chatgpt.com "Hands-on with Gemini CLI"
