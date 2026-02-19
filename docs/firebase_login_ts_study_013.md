# 第13章：Cookie制限時代のベストプラクティス：Redirectで事故らない🛡️

この章のゴールはこれ👇
**「Googleログインを redirect でやっても、Cookie/ストレージ制限が強い環境で“詰まらない”作り」**を、設計と実装とテストまで一気に固めることです💪✨
Firebase公式も「本番で全ブラウザ対応したいなら、必ず“どれかの対策オプション”を採用してね」と明言しています。([Firebase][1])

---

## 0) まず何が起きるの？🍪😵‍💫

![Broken Redirect Flow](./picture/firebase_login_ts_study_013_01_broken_redirect.png)

`signInWithRedirect()` は内部的に **クロスオリジン iframe** を使って「リダイレクト前後の状態」を受け渡しします。ところが最近は、ブラウザ側が **第三者ストレージ（≒3rd party cookies/ストレージ）をブロック**することが増えて、ここが壊れやすいです。([Firebase][1])

しかもこれは「Chromeだけの話」じゃなくて、**Safari系**や「プライバシー強め設定のユーザー」でも普通に起きます🥲
（補足：Chromeの“3rd party cookie完全廃止”は、2025年4月の時点で“現状の方針を維持する（ユーザー選択中心）”へ方針転換が出ています。それでも **ブロックされる環境は残る**ので、対策の価値は下がりません。）([Privacy Sandbox][2])

---

## 1) 読む（5〜8分）📚👀

* Firebase公式：**Redirectが壊れる条件と、回避のためのオプション一覧**（Option 1〜5）([Firebase][1])
* テスト観点：**「3rd party cookieがブロックされた状態」をChromeで再現する考え方**([Privacy Sandbox][3])
* （発展）FedCM：**Cookie依存を減らす方向の標準API**（※Firebase Auth直結というより “周辺の変化を読む” 用）([Chrome for Developers][4])

---

## 2) 方針決め：あなたのアプリはどの“Option”を使う？🧭✨

![Option Selection Compass](./picture/firebase_login_ts_study_013_02_option_compass.png)

Firebase公式の推奨は「状況別に Option を選んでね」です。([Firebase][1])
ここでは初心者がハマりにくい順に並べます👇

## いちばんラク（おすすめ）✅

**Option 1：`authDomain` を “今アクセスしているドメイン” に合わせる**

* 特に **`.web.app` ドメインや独自ドメイン**で運用するなら、この考え方が強いです。([Firebase][1])

## 次にラク✅

**Option 2：可能なら Popup を使う**

* Redirectが壊れる環境でも、Popupが通ることがあります（ただしPopupブロック問題あり）。([Firebase][1])

## ちょい上級（でも強い）🧠

**Option 3：`/__/auth` をプロキシして “同一オリジン” に寄せる**([Firebase][1])
**Option 4：Firebase Hostingを使って auth handler を同一オリジンで配る**([Firebase][1])
**Option 5：Firebase JS SDK の helper を自前ホスト（最後の手段）**([Firebase][1])

この章の“手を動かす”では、まず **実装面の事故（ループ/結果未取得/エラーが出ても黙る）**を潰しつつ、最後に **Option選択**まで落とし込みます🛠️🔥

---

## 3) 手を動かす：Redirectの“戻り処理”をちゃんと作る🔁✅

## 3-1) クリック時：redirect開始フラグを立てる🚩

![Redirect Flag Logic](./picture/firebase_login_ts_study_013_03_redirect_flag.png)

**ポイント**：

* redirect はページ遷移するので、**「今redirect中だよ」**を `sessionStorage` に持たせると、
  戻ってきたときに **“結果が取れなかった”** を判定しやすいです👍

```ts
// authRedirect.ts
import { auth } from "./firebase";
import { GoogleAuthProvider, signInWithRedirect } from "firebase/auth";

const provider = new GoogleAuthProvider();

export async function startGoogleRedirect() {
  // ループ検知・失敗診断用のフラグ
  sessionStorage.setItem("auth:redirect:attempt", String(Date.now()));
  await signInWithRedirect(auth, provider);
}
```

---

## 3-2) アプリ起動時：`getRedirectResult()` を「1回だけ」実行する🧩

![Result Check Logic](./picture/firebase_login_ts_study_013_04_result_check.png)

**ポイント**：

* `getRedirectResult()` は **アプリ起動時に1回だけ**やる（Reactなら `useEffect`）
* `result` が `null` のときも普通にある（redirect復帰じゃないだけ）
* でも「attemptフラグがあるのに `null`」なら、Cookie/ストレージ制限が疑わしい😇

```ts
// useAuthRedirectResult.ts
import { useEffect, useState } from "react";
import { auth } from "./firebase";
import { getRedirectResult } from "firebase/auth";

export function useAuthRedirectResult() {
  const [checked, setChecked] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    (async () => {
      try {
        const result = await getRedirectResult(auth);

        if (cancelled) return;

        const attemptedAt = sessionStorage.getItem("auth:redirect:attempt");

        if (result) {
          // ✅ 成功：auth.currentUser も復元されているはず
          sessionStorage.removeItem("auth:redirect:attempt");
          setMessage("ログインできたよ〜！🎉");
        } else if (attemptedAt) {
          // ⚠️ redirectはしたっぽいのに結果が取れない
          setMessage(
            "ログインに戻ってきたけど、結果が取れなかったよ…🥲\n" +
              "Cookie/ストレージ制限が原因かも。次の『Option診断』を見てね👇"
          );
        }
      } catch (e) {
        if (cancelled) return;
        sessionStorage.removeItem("auth:redirect:attempt");
        setMessage("ログインに失敗したよ…😵‍💫（あとで原因を表示するね）");
        // ここで e をログに出す / 画面に詳細出す、など
      } finally {
        if (cancelled) return;
        setChecked(true);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, []);

  return { checked, message };
}
```

---

## 3-3) UIに組み込む（超ざっくり）🖥️✨

```tsx
import { startGoogleRedirect } from "./authRedirect";
import { useAuthRedirectResult } from "./useAuthRedirectResult";

export function LoginPage() {
  const { checked, message } = useAuthRedirectResult();

  if (!checked) return <div>確認中…⏳</div>;

  return (
    <div>
      {message && <pre>{message}</pre>}
      <button onClick={() => void startGoogleRedirect()}>
        Googleでログイン（Redirect）🌈
      </button>
    </div>
  );
}
```

---

## 4) 手を動かす：Option診断（“設定ミス”を最短で潰す）🧯🔍

ここが本番で一番効きます🔥
Firebase公式の Option を“自分の状況”に当てはめるチェックリストです。([Firebase][1])

## 4-1) Option 1 を採るときのチェック✅

![Option 1 Checklist](./picture/firebase_login_ts_study_013_05_option1_check.png)

やることは概ねこの3つ👇（公式に書いてある要点です）([Firebase][1])

1. **Firebase初期化の `authDomain` を、今使うドメインに合わせる**
2. **OAuth provider側の redirect URI に `https://<authDomain>/__/auth/handler` を入れる**
3. **Firebase Console側の Authorized domains にそのドメインを入れる**

> ここが揃ってないと、`unauthorized-domain` 系で落ちたり、戻り処理が変になったりします😇

---

## 4-2) Option 4 / 5 になる目安🧠

* 「どうしてもアプリのドメインをいじれない」
* 「プロキシやHosting構成で同一オリジンに寄せたい」
* 「最悪、SDKの helper を自前で配る」

この辺は公式で選択肢として提示されています。([Firebase][1])

---

## 5) テスト：わざと“Cookie制限あり”で試す🧪🍪

本番前にこれをやるだけで事故が激減します🙏✨

## 5-1) Chrome / Edge で “3rd party cookieブロック” を再現する🧪

![Cookie Block Testing](./picture/firebase_login_ts_study_013_06_cookie_test.png)

Chrome系は、**ブロック状態をテストするための案内**が用意されています。([Privacy Sandbox][3])
（設定場所はUIが変わることがあるので、迷ったら “third-party cookies / tracking protection” で検索すると早いです🔎）

チェックすること👇

* redirect開始 → Googleログイン → 戻る
* `getRedirectResult()` が取れる？
* 取れないなら、Option 1〜5 のどれで直す？（まずOption 1を疑う）

---

## 6) ミニ課題：AIで“原因説明”をやさしくする🤖💬✨

redirect失敗時って、ユーザーに
「Cookieが〜」「ストレージが〜」って言っても伝わりにくいんですよね🥲

そこで、**開発者向け/ユーザー向け**に分けて、説明文をAIに作らせます✍️
Firebase AI Logic は **WebからGeminiを安全寄りに呼ぶためのSDK**が用意されています。([Firebase][5])

## 6-1) Firebase AI Logic（Web）の最小呼び出し例🤖✨

![AI Fix Guide](./picture/firebase_login_ts_study_013_07_ai_fix_guide.png)

公式のWeb例はこんな感じです（`firebase/ai` から使う）([Firebase][6])

```ts
import { initializeApp } from "firebase/app";
import { getAI, getGenerativeModel, GoogleAIBackend } from "firebase/ai";

const firebaseApp = initializeApp({ /* ... */ });

// Gemini Developer API backend
const ai = getAI(firebaseApp, { backend: new GoogleAIBackend() });

// 例：モデル指定（用途に合わせて）
const model = getGenerativeModel(ai, { model: "gemini-2.5-flash" });

export async function aiExplainRedirectFailure(input: {
  hostname: string;
  authDomain: string;
  attempted: boolean;
}) {
  const prompt =
    "あなたはWebアプリのサポート担当です。\n" +
    "Googleログイン（redirect）が失敗しました。\n" +
    `状況: hostname=${input.hostname}, authDomain=${input.authDomain}, attempted=${input.attempted}\n` +
    "ユーザー向けに、短く・やさしく・次に何をすればいいか、3行で案内して。";

  const result = await model.generateContent(prompt);
  return result.response.text();
}
```

> なお、AIまわりはモデルの入れ替わりもあるので、公式のアナウンスは定期的に見てね📣
> 例：Firebase AI Logicの案内では、特定モデルのリタイア告知（2026-03-31など）も出ています。([Firebase][6])

---

## 7) よくある詰まりどころ（ここだけ見ても助かる）🧯😇

* **無限ループする🔁**
  → `signInWithRedirect()` を「ログイン画面表示のたびに自動実行」してない？
  → この章の `sessionStorage` フラグ方式で“1回だけ”に制御しよ✅

* **戻ってきたのに `getRedirectResult()` が `null` のまま**
  → Cookie/ストレージ制限の可能性大。Option 1（`authDomain`合わせ）から疑う🧠([Firebase][1])

* **設定は合ってるはずなのに環境によって失敗**
  → ブラウザ側の制限を“再現テスト”して、Option見直しが最短です🧪([Privacy Sandbox][3])

---

## 8) チェック（できた？）✅🎯

* [ ] redirect後にアプリへ戻ってきて、**1回だけ** `getRedirectResult()` を拾えている
* [ ] attemptフラグがあるのに結果が取れないとき、**ユーザーに案内が出る**
* [ ] Chrome/Edgeで“Cookie制限あり”を再現しても、挙動が破綻しない（or Optionで直せる）([Privacy Sandbox][3])
* [ ] （発展）AIで「次にやること」をやさしく出せる🤖✨([Firebase][5])

---

必要なら、あなたの今の構成（デプロイ先URLのドメインと `authDomain` の値）を前提に、**Option 1〜5のどれが最短で安全か**を、この章の内容に沿って“決め打ち”で整理して書きますよ🧭🔥

[1]: https://firebase.google.com/docs/auth/web/redirect-best-practices "Best practices for using signInWithRedirect on browsers that block third-party storage access  |  Firebase"
[2]: https://privacysandbox.google.com/blog/privacy-sandbox-next-steps "Next steps for Privacy Sandbox and tracking protections in Chrome"
[3]: https://privacysandbox.google.com/cookies "Third-party cookies  |  Privacy Sandbox"
[4]: https://developer.chrome.com/docs/identity/fedcm/overview?utm_source=chatgpt.com "FedCM: A privacy-preserving identity federation API"
[5]: https://firebase.google.com/docs/ai-logic?utm_source=chatgpt.com "Gemini API using Firebase AI Logic - Google"
[6]: https://firebase.google.com/docs/ai-logic/get-started "Get started with the Gemini API using the Firebase AI Logic SDKs  |  Firebase AI Logic"
