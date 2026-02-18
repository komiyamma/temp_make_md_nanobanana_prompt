# 第12章：AIを守る（Firebase AI Logic × App Check）🤖🧿

この章でやるのはコレ👇✨

* ✅ 「AI整形ボタン（要約・言い換え）」をアプリに実装する
* ✅ **App Check を効かせて** “正規アプリ以外” のAI呼び出しを落とす🧿
* ✅ **レート制限（Quota）で破産を防ぐ**💸🚫
* ✅ **AI監視（AI monitoring）で異常に気づける**👀📈

---

## 1) まず腹落ち：AIは “お金が燃えやすいAPI” 🔥💸

![AI Cost Risk](./picture/firebase_abuse_prevention_ts_study_012_01_ai_risk.png)

FirestoreやStorageも狙われるけど、AIは特にヤバいです😇
理由はシンプル👇

* **1回のリクエストが高い**（しかも出力が長いとさらに高い）💸
* **連打・自動化が簡単**（ボットが大好物）🤖
* **「想定外の使われ方」**が起きやすい（プロンプト悪用、無限生成など）🌀

だからAIは、**最初から守りを前提に設計**した方がラクです🙂🧿

---

## 2) Firebase AI Logic で “守れるAI呼び出し” にする🛡️🤖

![AI Proxy Gate](./picture/firebase_abuse_prevention_ts_study_012_02_proxy_verification.png)

Firebase AI Logic の大事ポイントはここ👇

* アプリ → Firebase AI Logic の **プロキシ（中継）** を通って Gemini / Imagen に行く🚪
* そのプロキシで **App Check トークンを検証できる**🧿✅
* 特に Gemini Developer API を使う場合、**Gemini API key をアプリに埋め込まない運用**が超重要（キーはバックエンド側で使われる）🔐
  そして “本気で作り始めたら App Check 統合がクリティカル” とはっきり書かれてます。([Firebase][1])

さらに、Firebase AI Logic は **App Check / Remote Config / AI monitoring に対応**と明記されています。([Firebase][1])

---

## 3) 守りの基本セットは3つ🧰🧿

![Three Tools](./picture/firebase_abuse_prevention_ts_study_012_03_defense_tools.png)

## A. App Check（必須）🧿

AI Logic のプロキシが App Check を検証できるので、**正規アプリだけ通す**ができます。([Firebase][2])

## B. “limited-use” App Check トークン（強め）⏱️🧿

AI呼び出しみたいな「コスト高い・悪用されやすい」場面では、**短命の limited-use トークン**が推奨されています（TTL 5分）。([Firebase][2])
ただし **追加の通信が増える**ので、全部に常時ONというより「AIだけON」が現実的👍([Firebase][2])

## C. レート制限（Quota）💥🚦

Firebase AI Logic API には **“1ユーザーあたり/1分あたり” の上限**があり、デフォルトは **100 requests/min/user** と書かれています。([Firebase][2])
超えると **429（Quota exceeded）** になります。([Firebase][2])
そして重要：**特定ユーザーだけ別上限**みたいなのは（少なくとも現時点では）できない、という注意もあります。([Firebase][2])

---

## 4) 手を動かす：AI整形ボタンを作る🧩⚛️🤖

## 4-1. まずは最小で “AI整形” 関数を作る🛠️

![Secure Client Code](./picture/firebase_abuse_prevention_ts_study_012_04_client_code.png)

ポイントは👇

* モデルは新しめを使う（古いのが退役予定だったりする）🧯
  例として、公式ガイドは `gemini-2.5-flash` 系を普通に出してます。([Firebase][3])
* 退役予定の注意：`gemini-2.0-flash` は **2026-03-31 に退役予定**と書かれています（なので今から新規で選ぶ意味は薄い）。([Firebase][4])

例：`src/lib/aiPolish.ts`

```ts
import { getApp } from "firebase/app";
import { getAI, getGenerativeModel, GoogleAIBackend } from "firebase/ai";

/**
 * メモを「読みやすく」整形する（要約＋言い換え）
 */
export async function polishMemo(raw: string): Promise<string> {
  const ai = getAI(getApp(), {
    backend: new GoogleAIBackend(),
    // AI呼び出しは“悪用されやすい”ので短命トークンを推奨（後述）
    useLimitedUseAppCheckTokens: true,
  });

  const model = getGenerativeModel(ai, {
    model: "gemini-2.5-flash",
  });

  const prompt = [
    "あなたは文章の編集者です。",
    "次のメモを、意味を変えずに読みやすく整形してください。",
    "条件：",
    "- 箇条書きOK",
    "- 1〜2行の要約を先頭に付ける",
    "- 口調は丁寧すぎず自然に",
    "",
    "メモ本文：",
    raw,
  ].join("\n");

  const result = await model.generateContent(prompt);
  return result.response.text();
}
```

`firebase/ai` を使って `getAI` → `getGenerativeModel` → `generateContent()` の流れは公式ガイドにも載っているパターンです。([Firebase][3])

> 💡 `useLimitedUseAppCheckTokens: true` は、AI Logic の App Check ガイドにある推奨オプションです（Web SDK v12.3.0+）。([Firebase][2])

---

## 4-2. React 側に「AI整形」ボタンを付ける⚛️🖱️

例：`src/components/MemoPolishButton.tsx`

```tsx
import { useState } from "react";
import { polishMemo } from "../lib/aiPolish";

export function MemoPolishButton(props: {
  value: string;
  onApply: (next: string) => void;
}) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onClick() {
    setLoading(true);
    setError(null);

    try {
      const polished = await polishMemo(props.value);
      props.onApply(polished);
    } catch (e: any) {
      // だいたいここに「App Check」か「Quota」か「ネットワーク」系が飛んでくる
      const message =
        typeof e?.message === "string" ? e.message : "AI整形に失敗しました";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <button disabled={loading} onClick={onClick}>
        {loading ? "整形中…🤖" : "AIで整形✨"}
      </button>

      {error && (
        <p style={{ marginTop: 8 }}>
          ⚠️ {error}
          <br />
          <small>（時間をおいて再実行、または再読み込みを試してね🙂）</small>
        </p>
      )}
    </div>
  );
}
```

---

## 5) ON/OFF比較で “守れてる感” を体感👀🧿

![Verification Process](./picture/firebase_abuse_prevention_ts_study_012_05_verification.png)

ここ、めちゃ大事です🔥
**守りは「効いてるか確認」しないと、ただの気分**になりがち😇

## 手順（おすすめ）

1. Firebase Console で **App Check を「監視（enforceしない）」状態**にしておく👀
2. AI整形ボタンを押して、普通に動くのを確認✅
3. 次に、Console 側で **AI Logic への enforcement をON**（= 未検証を拒否）🧿🚫
4. その状態で、わざと App Check 初期化を外したビルド（または別の未設定クライアント）から叩いてみる

   * ここで **失敗（拒否）** すれば勝ち🎉

AI Logic は App Check 統合がサポートされていて、プロキシが App Check トークンを検証できる構成になっています。([Firebase][1])

---

## 6) レート制限（Quota）で “破産しない” を作る💸🚦

![Rate Limiting](./picture/firebase_abuse_prevention_ts_study_012_06_quota.png)

Firebase AI Logic API の quota は、ざっくりこう考えるとラク👇

* **通常運用**：1ユーザーあたり 100回/分 は多い（普通のアプリなら十分）
* **事故るパターン**：

  * 無限連打ボタン
  * バグで自動リトライ地獄
  * 悪意あるスクリプト

公式ドキュメント上、デフォルトは **100 requests/min/user**。([Firebase][2])
また、クォータは RPM/RPD/TPM/TPD のどれか超過でもエラーになるよ、という説明もあります。([Firebase][2])

## 実運用のコツ🎛️

* 最初は **控えめ（例：30〜60 rpm/user）** にして様子見👀
* 問題なければ上げる（逆はUX事故りやすい）🙂
* **特定ユーザーだけ上げる**は現状できない前提で設計（管理者だけ別枠にするなら、別経路/別バックエンドを検討）([Firebase][2])

---

## 7) “構造化出力(JSON)” を使うと事故が減る🧾🤖

![Structured JSON](./picture/firebase_abuse_prevention_ts_study_012_07_structured_output.png)

AIの戻りがただの文章だと👇が起きがち😵‍💫

* JSONのつもりが崩れる
* 余計な説明が混ざる
* UI側のパースで死ぬ

Firebase AI Logic は **responseMimeType と responseSchema** で構造化出力を作れます。([Firebase][5])

例：整形結果を `{ summary, body }` のJSONで返させる

```ts
import { getApp } from "firebase/app";
import { getAI, getGenerativeModel, GoogleAIBackend, Schema } from "firebase/ai";

export async function polishMemoAsJson(raw: string) {
  const ai = getAI(getApp(), {
    backend: new GoogleAIBackend(),
    useLimitedUseAppCheckTokens: true,
  });

  const schema = Schema.object({
    properties: {
      summary: Schema.string(),
      body: Schema.string(),
    },
  });

  const model = getGenerativeModel(ai, {
    model: "gemini-2.5-flash",
    generationConfig: {
      responseMimeType: "application/json",
      responseSchema: schema,
    },
  });

  const prompt = [
    "次のメモを読みやすく整形してJSONで返して。",
    "summary: 1〜2行の要約",
    "body: 整形後本文（箇条書きOK）",
    "",
    raw,
  ].join("\n");

  const result = await model.generateContent(prompt);
  return result.response.text(); // JSON文字列（ここをJSON.parseしてUIへ）
}
```

この `responseMimeType: "application/json"` と `responseSchema` の形は公式の例に沿っています。([Firebase][5])

---

## 8) AI monitoring で “異常の早期発見” 👀📈

AIは **「気づいた時には請求が…」** が起きがちなので、監視は保険です🧯💸

AI monitoring については👇が書かれています：

* Web だと **Firebase JS SDK v11.8.0+** が必要
* データ収集の **オプトイン設定**が必要([Firebase][1])
* さらに、観測（Cloud Observability）側のコストが発生しうる点にも注意、とあります([Firebase][6])

---

## 9) AIでAI実装を加速（Antigravity / Gemini CLI）🚀🤖

ここは “作業が早くなる” おまけコーナー🎁✨（でも超実戦的）

* **Antigravity**：エージェントが計画〜実装まで進める思想の入門が公開されています。([Google Codelabs][7])
* **Gemini CLI**：ターミナル統合のオープンソースAIエージェントとして紹介されています。([Google Cloud Documentation][8])
* **Firebase Studio**：ワークスペース（環境再現）まわりの説明があります。([Firebase][9])

## 使い方の例（そのまま投げてOK）🗣️🤖

* 「`firebase/ai` を使ってる場所を全検索して、`useLimitedUseAppCheckTokens` が必要な箇所を提案して」🔎
* 「AIボタンが連打された時に、UIで“クールダウン”する実装案を出して」🧊
* 「429の時のUX文言を3案、優しめで」🙂

---

## ミニ課題🎯✨

次の3つをやったら、この章は “勝ち” です🏆

1. ✅ AI整形ボタンが動く（最低1回成功）🤖
2. ✅ App Check enforcement をONにして、未検証リクエストが落ちるのを確認🧿🚫
3. ✅ Quota を「自分のアプリに合う値」に調整して、429時の表示も作る💸🚦

---

## チェック✅（理解できたらOK）

* ✅ 「AIはコストが読みにくいから、App Check＋Quotaで守る」が言える🙂
* ✅ limited-use トークンは “AIみたいな高コストAPIに寄せる” のが納得できる⏱️🧿([Firebase][2])
* ✅ 429（Quota）と 403系（App Check/認可っぽい）を **UIで分けて扱う**イメージがある🚦🧯

---

次の章（第13章）は **Debug Provider** で「ローカル開発が詰まらない」ようにするやつです🧪🧿
でも先に、あなたのプロジェクト構成に合わせて「AI整形ボタンの置き場所（services層/hooks化）」を最適化する版も作れますよ⚛️✨

[1]: https://firebase.google.com/docs/ai-logic/faq-and-troubleshooting "FAQ and troubleshooting  |  Firebase AI Logic"
[2]: https://firebase.google.com/docs/ai-logic/app-check "Implement Firebase App Check to protect APIs from unauthorized clients  |  Firebase AI Logic"
[3]: https://firebase.google.com/docs/ai-logic/get-started "Get started with the Gemini API using the Firebase AI Logic SDKs  |  Firebase AI Logic"
[4]: https://firebase.google.com/docs/ai-logic/production-checklist "Production checklist for using Firebase AI Logic  |  Firebase AI Logic"
[5]: https://firebase.google.com/docs/ai-logic/generate-structured-output "Generate structured output (like JSON and enums) using the Gemini API  |  Firebase AI Logic"
[6]: https://firebase.google.com/docs/ai-logic/monitoring "Monitor costs, usage, and other metrics  |  Firebase AI Logic"
[7]: https://codelabs.developers.google.com/getting-started-google-antigravity "Getting Started with Google Antigravity  |  Google Codelabs"
[8]: https://docs.cloud.google.com/gemini/docs/codeassist/gemini-cli "Gemini CLI  |  Gemini for Google Cloud  |  Google Cloud Documentation"
[9]: https://firebase.google.com/docs/studio/get-started-workspace "About Firebase Studio workspaces"
