# 第20章：総合演習：ON/OFFで挙動差を観察して、運用手順まで完成🏁👀

この最終章は、“守りを入れたらアプリが動かなくなった😇” を **わざと起こして**、ちゃんと復旧できるようになる回です💪🔥
最後に **運用手順書（チェックリスト）** まで作って、もう迷子にならない状態にします🧭✨

---

## この章のゴール🎯✨

* **App Check OFF / ON（強制）/ Debug** を切り替えて、挙動差を説明できる🙂
* **Firestore / Storage / Functions / AI Logic** の全部で、守りが効いているのを確認できる🛡️
* 事故らないための **運用手順書（10〜15項目）** が完成している🧾✅
* AI（Antigravity / Gemini CLI / Firebase Studio / Gemini in Firebase）を使って、実装・レビュー・運用文書づくりまで加速できる🚀🤖

---

## まず読む📚（超重要ポイントだけ）

## 1) “クライアントに入れただけ”では、基本まだ死なない🙂

Web で App Check を初期化すると、リクエストにトークンが付き始めます。でも **Firebase 側で enforcement（強制）をONにするまでは、基本「必須」にはならない** です。つまり、最初は「メトリクス観察」から入れるのが安全👌
（※ドキュメントにも「強制をONにするまで必須にならない」流れが明記されています）([Firebase][1])

## 2) 自動更新は “明示ON” が前提✅

Web の `initializeAppCheck` は、`isTokenAutoRefreshEnabled: true` を自分で入れるのが基本です。入れないと更新されません😇([Firebase][1])

## 3) ローカルは Debug Provider が命綱🧪

Debug token を Firebase Console に登録（safelist）しておくと、ローカルでも強制ON環境を通せます。
ただし **このトークンは超危険**（漏れたら守りが崩れる）ので、扱いはパスワード級に🔐([Firebase][2])

## 4) Functions は `enforceAppCheck` が直球の守り☎️

Callable Functions は `enforceAppCheck: true` で「トークン無い/無効なら拒否」にできます。さらに **リプレイ対策（beta）** として `consumeAppCheckToken: true` もあります（Node のみ）♻️🚫([Firebase][3])

## 5) AI Logic は “早めに App Check が強く推奨”🤖🧿

Firebase AI Logic は **App Check 連携で AI API を守るゲートウェイ**になっていて、enforcement をONにすると未検証は拒否されます。早期導入が強く推奨されています🛡️([Firebase][4])
さらに AI はコスト事故しやすいので、**per-user rate limit** も必ず見る！
デフォルトは **100 RPM** と高めなので、必要に応じて下げるの推奨です💸([Firebase][5])

---

## 手を動かす🛠️（“ON/OFFで壊す→直す”をやる）

## Step 0：切り替えスイッチを作る🎛️（これが最終章の核）

「本番」「ローカル」「わざとOFFで壊す」を **コード1箇所で切り替え** できるようにします。

## 例：`src/services/firebase.ts` に集約📦

* `VITE_APPCHECK_MODE` を使って

  * `off`（App Check 初期化しない＝壊す用💥）
  * `recaptcha`（本番想定🧿）
  * `debug`（ローカル救済🧪）
    を切り替えます。

```ts
import { initializeApp } from "firebase/app";
import {
  initializeAppCheck,
  ReCaptchaV3Provider,
} from "firebase/app-check";

const firebaseConfig = {
  // あなたの設定
};

export const app = initializeApp(firebaseConfig);

export function initAppCheck() {
  const mode = import.meta.env.VITE_APPCHECK_MODE as
    | "off"
    | "recaptcha"
    | "debug"
    | undefined;

  if (mode === "off") {
    // わざと壊す（強制ON時に落ちるのを確認する用）
    return;
  }

  if (mode === "debug") {
    // Debug Provider（このブラウザ・この端末に token を保存するモード）
    // 別ブラウザ/別PCで使う場合は true ではなく token 文字列を入れる（後述）
    (self as any).FIREBASE_APPCHECK_DEBUG_TOKEN = true;
  }

  if (mode === "recaptcha") {
    const siteKey = import.meta.env.VITE_RECAPTCHA_V3_SITE_KEY as string;
    initializeAppCheck(app, {
      provider: new ReCaptchaV3Provider(siteKey),
      isTokenAutoRefreshEnabled: true,
    });
    return;
  }

  // debug のとき：provider を渡さなくても debug token が使われる想定で初期化
  initializeAppCheck(app, {
    isTokenAutoRefreshEnabled: true,
  });
}
```

ポイント👀

* `initializeAppCheck` の `isTokenAutoRefreshEnabled: true` は必須寄り✅([Firebase][1])
* Debug token を “別ブラウザ/別PC” で使うなら、`true` ではなく **token文字列を直接セット**します🧪([Firebase][2])

---

## Step 1：Debug token を登録して「ローカル救済ルート」を作る🧪🔐

1. ローカルで `VITE_APPCHECK_MODE=debug` で起動
2. コンソールに **AppCheck debug token** が出る
3. Firebase Console → App Check → **Manage debug tokens** で登録（safelist）
4. 以後そのブラウザでは通る✅
5. 漏れたら即 revoke（取り消し）！🚨([Firebase][2])

---

## Step 2：Functions を“確実に落ちる場所”として用意する☎️💥

最終章は、**落ち方が分かりやすい** Callable Function を1個置くのが最高です😆

## Functions（Node/TS）側：App Check 強制 ON

```ts
import { onCall, HttpsError } from "firebase-functions/v2/https";
import { logger } from "firebase-functions";

export const adminOnlyCleanup = onCall(
  {
    enforceAppCheck: true, // App Check 無い/無効なら拒否🧿
    // 超重要な処理なら replay 対策（beta / Nodeのみ）も検討👇
    // consumeAppCheckToken: true,
  },
  async (request) => {
    logger.info("called", { app: request.app });

    // ここでは例として簡単に
    if (!request.auth) {
      throw new HttpsError("unauthenticated", "ログインしてね🙂");
    }

    return { ok: true };
  }
);
```

* `enforceAppCheck: true` は公式のやり方そのままです✅([Firebase][3])
* `consumeAppCheckToken: true` は **リプレイ対策（beta）**。ネットワーク往復が増えて遅くなるので「本当に重要なAPIだけ」に絞るのが普通です♻️🚫([Firebase][3])

---

## Step 3：AI Logic の “コスト事故防止” を仕上げる🤖💸

AI は「守れないと破産する」タイプなので、最後にここを締めます😇

## ✅ App Check（AI Logic）

AI Logic は App Check 連携で AI API を守れます。enforcement をONにすると未検証は拒否、という筋がはっきり書かれています🛡️([Firebase][4])

## ✅ per-user rate limit（AI Logic）

* Firebase AI Logic API の “per-user” レート制限は **デフォルト 100 RPM**（高い）
* 実アプリに合わせて下げるのが推奨です💡([Firebase][5])
* しかも 2026-02-05 更新のページに、モデルや制限の変更・注意が載っています（例：**Gemini 2.0 Flash / Flash-Lite が 2026-03-31 で retired** など）ので、運用手順書にも「定期点検」を入れておくのが安全です📅([Firebase][5])

---

## Step 4：いよいよ “強制ON” を段階的にやる🎛️🧿

ここからは **必ず「メトリクス見ながら」**。
しきい値を上げる時は「一時的に unenforce して影響を避けつつ監視」みたいな注意も公式にあります⚠️([Firebase][1])

おすすめ順番（事故りにくい）👇

1. Functions（上で作った Callable が分かりやすい）
2. AI Logic（コスト守り）
3. Firestore
4. Storage（アップロードは事故りやすいので最後寄り）

---

## ここが本番：テストシナリオ表（3モード×4サービス）👀✅

あなたは今から、同じ操作を **3つのモード** で試します。

## モードA：`off`（わざと壊す💥）

* 期待：**強制ONしているサービスが落ちる**
* 目的：「守りが効いてる」証明

## モードB：`recaptcha`（正規ルート🧿）

* 期待：全部動く
* 目的：本番の正常系

## モードC：`debug`（ローカル救済🧪）

* 期待：ローカルでも動く
* 目的：開発で詰まらない

チェック対象👇

* Firestore：メモ作成/更新📝
* Storage：画像アップロード📷
* Functions：Callable 実行☎️
* AI Logic：整形ボタン実行🤖

---

## 失敗時UXを“最終版”にする🙂🧯

強制ONでありがちな事故はこれ👇

* ユーザー側：「何も起きない…壊れた？」😇
* 開発側：「ログどこ…」😇

最低限これを入れると、運用が一気に楽になります✨

* App Check っぽい拒否のとき：

  * 「再読み込み」ボタン🔁
  * 「時間を置いて再試行」🕒
  * 「サポート導線」📩
* 画面には “技術用語を出さない” 🙅（ユーザーは App Check を知らない）

（強制ONで未検証が拒否されるのは前提なので、UXが無いと辛い…という話は Functions の enforcement の文脈でも自然に繋がります）([Firebase][3])

---

## 最終成果物：運用手順書（Runbook）テンプレ🧾✅

この章のゴールはここです。**これがある人が勝ちます**🏆✨

## ✅ 運用チェックリスト（例：12項目）

1. App Check のメトリクスで「未検証率」を確認👀([Firebase][1])
2. 強制ONする対象（Firestore/Storage/Functions/AI）を明文化📝
3. ローカル用 Debug token が safelist 済みか確認🔐([Firebase][2])
4. Debug token の漏えい対策（gitに入れない/共有禁止）✅([Firebase][2])
5. `VITE_APPCHECK_MODE` の切り替え手順（off/debug/recaptcha）を1行で書く🎛️
6. Functions は `enforceAppCheck` を入れて deploy 済みか確認☎️([Firebase][3])
7. （重要APIのみ）リプレイ対策 `consumeAppCheckToken` を使うか判断♻️([Firebase][3])
8. AI Logic の per-user rate limit を見直し（デフォ 100 RPM から調整）💸([Firebase][5])
9. AI のモデル変更/retired 情報の点検日を入れる📅（例：2026-03-31 retired 注意）([Firebase][5])
10. 失敗時UX（再試行/導線）が入っている🙂
11. ロールバック手順（unenforce に戻す場所/手順）を明記🧯([Firebase][1])
12. リリース後30分はメトリクス監視（増加があれば即対応）📈([Firebase][1])

---

## AIで“最終章”を爆速に仕上げる🚀🤖

## Antigravity：ミッション化して、抜け漏れ0へ🧩

Antigravity は Mission Control で、エージェントが **計画→実装→検証→Web調査** までやる思想の開発プラットフォームです（Windows でもOK）🚀([Google Codelabs][6])
👉 ここでは「Runbookを作る」「切替スイッチを導入」「E2E観点チェック」みたいにミッション化すると強いです💪

## Gemini CLI：リポジトリ全体レビュー係にする🔎

Gemini CLI はターミナルで使える **オープンソースAIエージェント**。ReAct ループでツールも使いながら進めます🧠⚙️([Google Cloud Documentation][7])
公式ブログでも「リサーチやタスク管理にも使える」系で紹介されています🧰([Google Cloud][8])

Gemini CLI に頼むなら、こういう依頼が刺さります👇

* 「App Check 初期化漏れ箇所を探して」
* 「直Firestore/直Storageアクセスを一覧化して」
* 「強制ON時に落ちる導線と、UX不足箇所を指摘して」

## Firebase Studio：環境の再現性を“最終形”に🧪

Firebase Studio は workspace を Nix で定義でき、`.idx/dev.nix` にツール類も書けます🧰
「この章の演習環境」を丸ごと再現しやすいのが強みです✨([Firebase][9])

---

## ミニ課題🎒✨（これで卒業🎓）

1. あなたのアプリの Runbook を **12〜15項目** に増やして完成させる🧾✅
2. `off / recaptcha / debug` の3モードで、4サービス全部の結果をスクショ or メモで残す📸📝
3. “事故った時の戻し方” を **30秒で実行できる手順** にする🧯

---

## チェック✅（ここが言えたら勝ち🏆）

* 「App Check を入れた＝即ブロック」ではなく、**enforcement がスイッチ**だと説明できる🙂([Firebase][1])
* ローカルは Debug token safelist で救える🧪([Firebase][2])
* Functions は `enforceAppCheck`、重要なら `consumeAppCheckToken` も検討できる☎️♻️([Firebase][3])
* AI Logic は App Check＋rate limit（デフォ 100RPM）で “破産を防ぐ” 発想になっている💸([Firebase][5])

---

ここまでできたら、もう「守りを入れたら怖い😱」じゃなくて、
「守りを入れても **運用でコントロールできる😎**」になります🎉🧿✨

[1]: https://firebase.google.com/docs/app-check/web/recaptcha-provider "Get started using App Check with reCAPTCHA v3 in web apps  |  Firebase App Check"
[2]: https://firebase.google.com/docs/app-check/web/debug-provider "Use App Check with the debug provider in web apps  |  Firebase App Check"
[3]: https://firebase.google.com/docs/app-check/cloud-functions "Enable App Check enforcement for Cloud Functions  |  Firebase App Check"
[4]: https://firebase.google.com/docs/ai-logic/app-check "Implement Firebase App Check to protect APIs from unauthorized clients  |  Firebase AI Logic"
[5]: https://firebase.google.com/docs/ai-logic/quotas "Rate limits and quotas  |  Firebase AI Logic"
[6]: https://codelabs.developers.google.com/getting-started-google-antigravity "Getting Started with Google Antigravity  |  Google Codelabs"
[7]: https://docs.cloud.google.com/gemini/docs/codeassist/gemini-cli "Gemini CLI  |  Gemini for Google Cloud  |  Google Cloud Documentation"
[8]: https://cloud.google.com/blog/ja/topics/developers-practitioners/introducing-gemini-cli "Gemini CLI : オープンソース AI エージェント | Google Cloud 公式ブログ"
[9]: https://firebase.google.com/docs/studio/get-started-workspace "About Firebase Studio workspaces"
