# 第15章：失敗時UX（通らない時の表示）🙂🧯

App Check を **強制（enforcement）ON** にすると、未検証リクエストは「普通に拒否」されます。つまり **“守りが強くなるほど、画面がコケやすくなる”** んですね😇
だからこの章は、守りを成功させるための **UX設計（ユーザー救済）** を作ります✨ ([Firebase][1])

---

## 1) 今日のゴール🏁✨

この章が終わると、こんな状態になります👇

* App Check が通らない時に、**画面が無言で止まらない**🙂
* ユーザーが次に押すべきボタン（再試行・再読み込み・サポート）まで用意できる🧭
* Firestore / Storage / Functions / AI それぞれで **“起きがちな失敗”** を分類できる📦
* 特に AI は **レート制限（デフォルト 100RPM）** も含めて、破産しない UX にできる💸🤖 ([Firebase][2])

---

## 2) “通らない”は3種類に分けると勝てる🥊🧠

UX を作るコツは「原因別に、出す案内を変える」ことです👇

## A. App Check のトークン取得が失敗🧿💥

例：reCAPTCHA が動かなかった、連続失敗で throttled になった、など。
この系は **“再試行しても直らないことがある”** のが特徴です（待つ・環境変える導線が要る）🕒🧯
JS SDK の代表例として `appCheck/recaptcha-error` や `appCheck/throttled` が報告されています。 ([GitHub][3])

## B. バックエンドが「未検証なので拒否」🚫🧱

App Check 強制後は、**未検証＝拒否** が基本です。ここで UI が沈黙すると最悪😇
Cloud Functions の callable は設定で「missing/invalid App Check tokens を reject」できます。 ([Firebase][1])

## C. AI の “回数制限・混雑” で失敗🤖⏳

AI は守り（App Check）に加えて、**回数制限（Rate limit）** が現実問題として効いてきます。
Firebase AI Logic には「アプリの per-user 的な制限として使える quota」があり、デフォルトは 100 RPM で調整推奨です。 ([Firebase][2])
さらに AI Logic 側でも App Check の導入が強く推奨され、未検証リクエストは拒否されます。 ([Firebase][4])

---

## 3) UXの鉄則：エラーは「次の一手」までセット🧭🙂

エラー表示で最低限入れるのはこの3点です👇

1. **何が起きたか**（短く）
2. **どうすればいいか**（1〜3手）
3. **ボタン**（再試行 / 再読み込み / サポート）

おすすめの UI パターンはこれ👇

* 軽い失敗（通信・一時的）→ 画面下トースト＋再試行🔁
* 重要機能が死ぬ（AI整形ボタン、画像アップロードなど）→ その機能の場所にインライン警告⚠️
* アプリ全体が動かない（初期化失敗）→ 全画面エラー＋導線🧯

---

## 4) まず実装の“芯”を作ろう🧱（Reactで共通ハンドラ）

ポイント：**全API呼び出しを1枚噛ませて、そこでエラーを「分類」して「文言」にする**🧠✨
（Firestore / Storage / Functions / AI を横断して同じ UX に寄せられます）

## 4-1. エラー分類（normalize）を作る🗂️

```ts
// src/lib/normalizeError.ts
import type { FirebaseError } from "firebase/app";

export type AppErrorKind =
  | "appcheck_failed"
  | "appcheck_throttled"
  | "rate_limited"
  | "permission"
  | "network"
  | "unknown";

export type AppErrorUI = {
  kind: AppErrorKind;
  title: string;
  message: string;
  primaryAction?: "retry" | "reload";
  secondaryAction?: "support";
  retryAfterSec?: number;
};

function isFirebaseError(e: unknown): e is FirebaseError {
  return typeof e === "object" && e !== null && "code" in e && "message" in e;
}

export function normalizeError(e: unknown): AppErrorUI {
  // 1) Firebase系
  if (isFirebaseError(e)) {
    const code = String(e.code ?? "");
    const msg = String(e.message ?? "");

    // App Check系（代表例）
    if (code.includes("appCheck/throttled") || msg.includes("appCheck/throttled")) {
      return {
        kind: "appcheck_throttled",
        title: "安全確認が一時的に止まりました🧿⏳",
        message:
          "しばらく待ってから、もう一度お試しください🙂（急いで連打すると悪化することがあります）",
        primaryAction: "reload",
        secondaryAction: "support",
      };
    }

    if (code.includes("appCheck/recaptcha-error") || msg.includes("recaptcha")) {
      return {
        kind: "appcheck_failed",
        title: "安全確認ができませんでした🧿💦",
        message:
          "再読み込みしても直らない時は、別ブラウザで試す・拡張機能を一時停止する、などをお試しください🙂",
        primaryAction: "reload",
        secondaryAction: "support",
      };
    }

    // ざっくり Permission 系（App Check強制でも起きうる）
    if (code.includes("permission-denied") || code.includes("unauthenticated")) {
      return {
        kind: "permission",
        title: "アクセスが拒否されました🚫",
        message:
          "安全確認（App Check）やログイン状態の確認に失敗している可能性があります。再読み込み後にもう一度お試しください🙂",
        primaryAction: "reload",
        secondaryAction: "support",
      };
    }
  }

  // 2) ネットワークっぽい
  if (e instanceof Error && /network|fetch|timeout/i.test(e.message)) {
    return {
      kind: "network",
      title: "通信が不安定みたいです📡💦",
      message: "電波が落ち着いたら再試行してください🙂",
      primaryAction: "retry",
    };
  }

  // 3) 不明
  return {
    kind: "unknown",
    title: "うまくいきませんでした😵",
    message: "再読み込みしても直らない場合は、サポートに連絡してください🙂",
    primaryAction: "reload",
    secondaryAction: "support",
  };
}
```

（`appCheck/recaptcha-error` や `appCheck/throttled` は JS SDK の事例として報告があります。） ([GitHub][3])

## 4-2. “守られたアクション”ラッパを作る🛡️🔁

```ts
// src/lib/guardedAction.ts
import { normalizeError, type AppErrorUI } from "./normalizeError";

export type GuardedResult<T> =
  | { ok: true; value: T }
  | { ok: false; error: AppErrorUI };

export async function guardedAction<T>(fn: () => Promise<T>): Promise<GuardedResult<T>> {
  try {
    const value = await fn();
    return { ok: true, value };
  } catch (e) {
    return { ok: false, error: normalizeError(e) };
  }
}
```

## 4-3. UIに出す（ボタン付き）🙂🧯

```tsx
// src/components/AppErrorBanner.tsx
import React from "react";
import type { AppErrorUI } from "../lib/normalizeError";

export function AppErrorBanner(props: {
  error: AppErrorUI;
  onRetry?: () => void;
}) {
  const { error, onRetry } = props;

  return (
    <div style={{ border: "1px solid #ddd", borderRadius: 12, padding: 12 }}>
      <div style={{ fontWeight: 700 }}>{error.title}</div>
      <div style={{ marginTop: 6 }}>{error.message}</div>

      <div style={{ display: "flex", gap: 8, marginTop: 10 }}>
        {error.primaryAction === "retry" && (
          <button onClick={onRetry}>もう一度ためす🔁</button>
        )}
        {error.primaryAction === "reload" && (
          <button onClick={() => location.reload()}>再読み込み🔄</button>
        )}
        {error.secondaryAction === "support" && (
          <button onClick={() => alert("サポート導線（メール/フォーム）へ")} >
            サポートに連絡📩
          </button>
        )}
      </div>
    </div>
  );
}
```

---

## 5) “App Check 由来の失敗”を減らすコツ🧿🧠

## 初期化の順番ミスを潰す（超重要）💥

App Check は「Firebaseの各サービスを触る前」に初期化するのが推奨です。 ([Firebase][5])
さらに、トークン自動更新はデフォルトでONじゃないので、明示的に有効化します。 ([Firebase][5])

## 強制ON後は “登録済みアプリだけが通る” を意識👀

強制ONすると、登録されていないアプリはバックエンドに届かなくなります。 ([Firebase][5])
（だからこそ、ユーザーに「今やるべきこと」をUIで出さないと詰みます🙂）

---

## 6) AI機能は「App Check失敗」と「回数制限」を別扱いにする🤖🧿⏳

AI整形ボタンでありがちな UX の地獄👇

* App Check 失敗 → そもそも拒否🧿🚫 ([Firebase][4])
* 使われすぎ → Rate limit（デフォルト 100RPM）で止まる💸⏳ ([Firebase][2])

なので文言も分けます👇

* **App Check失敗**：「安全確認ができませんでした。再読み込み／別環境で試してね🙂」
* **Rate limit**：「混み合ってます💦 30秒待ってもう一度🔁」

> AIは“守り”と“混雑対策”の二段で UX を作ると、ユーザーの納得感が爆上がりします🙂✨

---

## 7) “人間の日本語” エラー文テンプレ3つ📝🙂

そのままコピペで使えるやつ置いときます👇

1. **安全確認（App Check）NG**

* タイトル：安全確認ができませんでした🧿💦
* 本文：再読み込みしても直らない場合は、別ブラウザで試す／拡張機能を一時停止する、などをお試しください🙂
* ボタン：再読み込み🔄 / サポート📩

2. **一時的な混雑・制限（AI向け）**

* タイトル：ただいま混み合っています🤖⏳
* 本文：少し待ってからもう一度お願いします🙂（連打すると余計に止まりやすいです）
* ボタン：もう一度ためす🔁

3. **通信が不安定**

* タイトル：通信が不安定みたいです📡💦
* 本文：電波が落ち着いたら再試行してください🙂
* ボタン：もう一度ためす🔁

---

## 8) 手を動かす：失敗を“わざと起こして”UXを確認👀🧪

おすすめの確認シナリオ👇

* **ケース1：初期化ができてない状態**
  App Check 初期化前に Firestore/Storage/AI を触る → 何が出る？（あなたのUIは助けてくれる？🙂） ([Firebase][5])

* **ケース2：Functions を App Check 強制して拒否**
  callable を enforceAppCheck にして、未検証状態で叩く → あなたのUIは「次の一手」まで出せる？ ([Firebase][1])

* **ケース3：AI を短時間に連打して混雑UX**
  AI整形を連打 → Rate limit っぽい状況になった時、あなたのUIは「待ってね」が出せる？ ([Firebase][2])

---

## 9) ミニ課題🎯📝

## ミニ課題A（実装）💻

* guardedAction を使って、以下3箇所にエラーUIを出す

  1. メモ保存（Firestore）📝
  2. 画像アップロード（Storage）📷
  3. AI整形ボタン（AI Logic）🤖

## ミニ課題B（文章）✍️🙂

* エラー文を「やさしい」「普通」「ドライ」の3トーンで書く
  （ユーザー層で刺さる文体が変わるので、後で選べるようにしとくと強い💪）

## ミニ課題C（観察）👀

* App Check を強制ONにした瞬間に

  * どの画面が一番壊れやすい？
  * その画面の文言は “次の一手” になってる？
    をメモ📝

---

## 10) チェック✅（できたら勝ち🎉）

* 「App Check 失敗」と「AIの混雑（Rate limit）」を **別メッセージ** にできた🙂
* エラーが出たとき、ユーザーが **何をすればいいか迷わない** UIになった🧭
* App Check 初期化を「Firebaseサービスを触る前」に置けている🧿 ([Firebase][5])
* callable の enforceAppCheck で「未検証は拒否」を前提にUXを組めた🚫 ([Firebase][1])

---

## 11) AIで“UX文言作り”を爆速にする（開発時）🚀🤖

ここは開発者特権です😆
Google の Antigravity はエージェントで計画・調査・実装を回せる思想が紹介されています。 ([Google Codelabs][6])
GitHub リポジトリを読む流れなら Gemini CLI も「ターミナル統合のAIエージェント」として紹介されています。 ([Google Cloud][7])

たとえば Gemini にこう投げる👇

```text
あなたはUXライターです。
Firebase App Check / AI Logic の失敗時に出す日本語メッセージを作ってください。
条件：
- 文系大学生にもわかる
- 不安を煽らない
- 次にやること（再試行/再読み込み/待つ/サポート）を入れる
- 80文字以内 × 3パターン（やさしい/普通/ドライ）
```

---

次の第16章（段階的に強制ON）では、この章で作った UX を武器にして「怖くないリリース手順」に落とし込みます🎛️📈
（強制ON前のメトリクス監視や、一時的に unenforce を検討する注意も公式に触れられています。） ([Firebase][5])

[1]: https://firebase.google.com/docs/app-check/cloud-functions "Enable App Check enforcement for Cloud Functions  |  Firebase App Check"
[2]: https://firebase.google.com/docs/ai-logic/quotas "Rate limits and quotas  |  Firebase AI Logic"
[3]: https://github.com/firebase/firebase-js-sdk/issues/6708 "App Check works at first but fails to reconnect after sleep/background · Issue #6708 · firebase/firebase-js-sdk · GitHub"
[4]: https://firebase.google.com/docs/ai-logic/app-check "Implement Firebase App Check to protect APIs from unauthorized clients  |  Firebase AI Logic"
[5]: https://firebase.google.com/docs/app-check/web/recaptcha-provider "Get started using App Check with reCAPTCHA v3 in web apps  |  Firebase App Check"
[6]: https://codelabs.developers.google.com/getting-started-google-antigravity?utm_source=chatgpt.com "Getting Started with Google Antigravity"
[7]: https://cloud.google.com/blog/ja/topics/developers-practitioners/introducing-gemini-cli?utm_source=chatgpt.com "Gemini CLI : オープンソース AI エージェント"
