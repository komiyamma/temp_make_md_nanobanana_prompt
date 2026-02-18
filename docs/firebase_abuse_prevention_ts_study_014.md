# 第14章：CIでもApp Check（GitHub Actionsなど）🏗️🔒

CI（自動テスト）を回し始めると、App Check の“強制ON”が急に牙をむきます🧿💥
「ローカルは動くのに、CIだけ落ちる…😇」を、この章でスッキリ片付けます✌️

---

## まず結論：CIでは“Debug Provider + デバッグトークン”で通す🧪🧿

![CI vs App Check](./picture/firebase_abuse_prevention_ts_study_014_01_ci_failure.png)

CIのE2Eテストは **実機でも本番ブラウザでもない**ので、通常の reCAPTCHA 経由の App Check をそのまま通すのが難しい場面が出ます。
そこで公式が案内しているのが **Debug Provider（= デバッグトークンで正規扱いにする）** です。([Firebase][1])

---

## この章でやること（ゴール）🎯✨

* CIの中で **App Check 強制ONの環境でもテストが通る**ようにする🏃‍♂️💨
* デバッグトークンを **コードに直書きしない**で安全に運用する🔐
* ついでに「AI整形ボタン🤖」まで含めた **最低限のE2E** を1本作る🧪

---

## 読む📖：CIで詰まる“あるある”と、公式の推奨ルート🧠

## あるある①：強制ONにした瞬間、CIが全部 403/permission-denied 😇

App Check を “enforce（強制）” にすると、正規の証明がないリクエストが落ちやすくなります。
CIはまさに「証明がない側」になりがち。だから **CI用のデバッグトークン**が必要になります。([Firebase][1])

## あるある②：トークンをフロントに埋めたら漏れそうで怖い😱

怖いです。なので **Secrets（秘密情報）として管理**し、ログに出さない・成果物として外に出さない、が基本です。
公式も「CI用のトークンは秘密情報として扱う」ルートを示しています。([Firebase][1])

---

## 手を動かす🛠️：CIでApp Checkを通す手順（王道コース）👑

ここは **3点セット**です👇

1. Firebase Console に「CI用デバッグトークン」を登録
2. GitHub の Secrets に保存
3. CIのビルド/テスト時だけ、そのトークンをフロントに渡して Debug Provider を有効化

---

## 1) CI用デバッグトークンを用意して Console に登録🧿✅

公式の Debug Provider の流れ（＝デバッグトークンを登録して通す）に従います。([Firebase][1])

おすすめはこれ👇

* トークン名：`github-actions-e2e`（みたいに用途が一目でわかる）📝
* 文字列：ランダム長め（例：32バイト以上）🔐

> 💡ポイント：デバッグトークンは「これを持ってるクライアントは“デバッグ中の正規”扱い」という通行証🎫
> なので **漏れたら困る** ＝ **Secret扱い必須** です😤

---

## 2) GitHub Secrets に入れる🔐（絶対にリポジトリへコミットしない）

![GitHub Secrets](./picture/firebase_abuse_prevention_ts_study_014_02_secrets.png)

GitHubのリポジトリ設定から、Actions用の Secrets を作ります。([GitHub Docs][2])

* 例：Secret名 `APP_CHECK_DEBUG_TOKEN`
* 値：さっきのデバッグトークン

---

## 3) フロント側：CIだけ Debug Provider をONにする（重要：読み込み順）⚛️🧿

![Order of Operations](./picture/firebase_abuse_prevention_ts_study_014_03_dynamic_import.png)

公式が強調してる大事ポイント👇

* `self.FIREBASE_APPCHECK_DEBUG_TOKEN` を **App Check を読み込む前** にセットする([Firebase][1])

モダンなReact構成だと “import順” がややこしくなりがちなので、**安全なやり方（dynamic import）**でいきます✅

```ts
// src/lib/appCheck.ts
import { initializeApp } from "firebase/app";

// （例）Vite想定：CIでだけ渡す
const debugToken = import.meta.env.VITE_APP_CHECK_DEBUG_TOKEN;

// 先に Firebase App は作る
export const app = initializeApp({
  // your firebaseConfig
});

export async function initAppCheck() {
  // ✅ ここが超重要：App Check を import する前にセット
  if (debugToken) {
    (self as any).FIREBASE_APPCHECK_DEBUG_TOKEN = debugToken;
  }

  // ✅ dynamic import なら “読み込み前にセット” を守れる
  const { initializeAppCheck, ReCaptchaV3Provider } = await import("firebase/app-check");

  // CI中は Debug Provider が有効になる（debug token があるから）
  // CIじゃない時は reCAPTCHA v3 で普通に運用、の形にできる
  return initializeAppCheck(app, {
    provider: new ReCaptchaV3Provider(import.meta.env.VITE_RECAPTCHA_SITE_KEY),
    isTokenAutoRefreshEnabled: true,
  });
}
```

> 🧠なぜCIでも reCAPTCHA provider を書いてるの？
> Debug Provider は「デバッグトークンが入ってるとき、SDKがデバッグ扱いにできる」仕組みなので、**コードの形は保ったまま** CIだけ通す、がやりやすいです。([Firebase][1])

---

## 4) CIワークフロー：Node 24 LTSでビルド→プレビュー→E2E🧪

![CI Pipeline](./picture/firebase_abuse_prevention_ts_study_014_04_workflow.png)

2026年2月時点で Node 24 系が LTS で安定運用の対象になっています。([nodejs.org][3])
GitHub Actions では `actions/setup-node` がよく使われます。([GitHub][4])

ここでは E2E に Playwright を使う例にします（公式がCI手順を用意してて楽✨）。([playwright.dev][5])
プレビューサーバーは `vite preview`（デフォルト `http://localhost:4173`）がシンプルです。 ([vitejs][6])

```yaml
## .github/workflows/e2e.yml
name: e2e

on:
  pull_request:
  push:
    branches: [ main ]

jobs:
  e2e:
    runs-on: ubuntu-latest
    # forks の PR だと secrets が渡らないので、必要ならここで弾くのもアリ
    # if: github.event.pull_request.head.repo.fork == false

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 24

      - run: npm ci

      # ✅ CIでだけDebug Tokenを渡す（buildに混ぜる）
      - name: Build
        run: npm run build
        env:
          VITE_APP_CHECK_DEBUG_TOKEN: ${{ secrets.APP_CHECK_DEBUG_TOKEN }}

      # Playwright 推奨の入れ方（ブラウザ依存も入る）
      - name: Install Playwright browsers
        run: npx playwright install --with-deps

      - name: Start preview server
        run: npm run preview -- --host 127.0.0.1 --port 4173
        env:
          VITE_APP_CHECK_DEBUG_TOKEN: ${{ secrets.APP_CHECK_DEBUG_TOKEN }}

      - name: Run E2E
        run: npx playwright test
        env:
          BASE_URL: http://127.0.0.1:4173
```

> 🔥超重要：**Debug Token は「build と preview の両方」で渡す**ほうが事故りにくいです（ビルド時にJSへ埋め込まれる系の構成が多いので）💡

---

## 5) Playwright側：App Checkが効いてる最低限の1本を作る🧪🧿🤖

![Smoke Test](./picture/firebase_abuse_prevention_ts_study_014_05_e2e_scenario.png)

「AI整形ボタン」を押して、結果が画面に出たらOK、みたいな **超スモーク**にします🧯
（毎PRで重たいAI呼び出しを連打すると財布が燃えるので、後で抑える仕組みも入れます🔥）

```ts
// tests/smoke.spec.ts
import { test, expect } from "@playwright/test";

test("App Checkありで、AI整形まで動く", async ({ page }) => {
  const baseURL = process.env.BASE_URL!;
  await page.goto(baseURL);

  // 例：メモ入力→保存
  await page.getByPlaceholder("メモを入力").fill("この文章を短くして！");
  await page.getByRole("button", { name: "保存" }).click();

  // 例：AI整形ボタン
  await page.getByRole("button", { name: "AI整形" }).click();

  // 例：結果が表示されるのを待つ
  await expect(page.getByTestId("ai-result")).toBeVisible();
});
```

---

## AI（Firebase AI Logic）をCIでどう扱う？🤖💸

## おすすめ方針：PRでは“軽い確認”、重いのは夜間 or mainだけ🌙

![PR vs Nightly](./picture/firebase_abuse_prevention_ts_study_014_06_ai_strategy.png)

Firebase AI Logic にはレート制限（デフォルト 100 RPM/user など）があり、運用では守りと制御がセットで語られます。([itnext.io][7])
なのでCIは👇みたいにすると平和です🙂✨

* PR：AIのテストは **ダミー応答**に切り替える（環境変数で切替）🧩
* main：AIも含めたE2Eを回す✅
* nightly：さらに重いシナリオ（画像＋要約など）を回す🌙

---

## ミニ課題🎓🔥：「PRで動く最低限E2E」を1本完成させよう

1. App Check 強制ONの状態でもCIが落ちないようにする🧿
2. PRで `smoke.spec.ts` が必ず走るようにする🏃‍♀️
3. できたら「Debug Tokenなしだと失敗する」ネガティブテストも、手元で1回だけ確認👿（CIに入れるのは慎重に）

---

## チェック✅：ここまでできたら合格🎉

* Debug Token を **コードに直書きしてない**（Secrets管理できてる）🔐([GitHub Docs][2])
* CIで `self.FIREBASE_APPCHECK_DEBUG_TOKEN` を **App Check import より前**にセットできてる🧠([Firebase][1])
* E2Eが “App Checkあり” の状態で通る🧪
* （できれば）App Check メトリクスで CIアクセスが観測できる👀📈([Firebase][1])

---

## 落とし穴まとめ（ここだけ読んでも価値あるやつ）🕳️😇

![Security Leaks](./picture/firebase_abuse_prevention_ts_study_014_07_pitfalls.png)

* ✅ **Secretsがfork PRに渡らない** → forkからのPRではE2Eをスキップする設計が必要になりがち
* ✅ Debug Token を **成果物としてアップロード**すると漏れる可能性（Artifacts注意⚠️）
* ✅ ログに環境変数を出す `echo` は事故のもと💥
* ✅ “import順”が崩れると Debug Token が効かず、CIだけ落ちる（dynamic importが安全）([Firebase][1])
* ✅ AI呼び出しを毎PRで重く回すと、レート制限や費用で詰む（PRは軽量で）([itnext.io][7])

---

## AIエージェントで、この章の作業を爆速化🚀🤖

## Antigravity（Mission Control）で「章タスク」をそのままミッション化🧭

“計画→実装→Web調査→確認”をエージェントに流せる思想が紹介されています。([Google Codelabs][8])
例：ミッションに「e2e.ymlを作る」「debug token導線を安全に」などを並べる📋✨

## Gemini CLIで「CI漏れ/危険ポイント」をレビューさせる🔎

Gemini CLI はターミナル上のオープンソースAIエージェントとして紹介されていて、リサーチやタスク整理にも向きます。([Google Cloud][9])

```bash
gemini "このリポジトリでApp Checkのデバッグトークンが漏れうる場所を探して。ログ出力、Artifacts、ビルド成果物の扱いもチェックして。"
```

---

次の第15章は「通らない時のUX🙂🧯」なので、この章で“CIでちゃんと通る”状態を作れてると一気に気持ちよく進められます😆🔥

[1]: https://firebase.google.com/docs/app-check/web/debug-provider "Use App Check with the debug provider in web apps  |  Firebase App Check"
[2]: https://docs.github.com/en/actions/reference/encrypted-secrets "Using secrets in GitHub Actions - GitHub Docs"
[3]: https://nodejs.org/en/blog/release/v24.11.0?utm_source=chatgpt.com "Node.js 24.11.0 (LTS)"
[4]: https://github.com/actions/setup-node?utm_source=chatgpt.com "actions/setup-node"
[5]: https://playwright.dev/docs/ci-intro?utm_source=chatgpt.com "Setting up CI"
[6]: https://vite.dev/guide/static-deploy?utm_source=chatgpt.com "Deploying a Static Site"
[7]: https://itnext.io/choosing-the-right-ai-framework-for-flutter-firebase-ai-logic-vs-genkit-68888721efa7?utm_source=chatgpt.com "Choosing the Right AI Framework for Flutter: Firebase AI Logic ..."
[8]: https://codelabs.developers.google.com/getting-started-google-antigravity?utm_source=chatgpt.com "Getting Started with Google Antigravity"
[9]: https://cloud.google.com/blog/ja/topics/developers-practitioners/introducing-gemini-cli?utm_source=chatgpt.com "Gemini CLI : オープンソース AI エージェント"
