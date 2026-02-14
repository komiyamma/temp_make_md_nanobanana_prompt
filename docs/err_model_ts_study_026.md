# 第26章：UI側の例外境界（見せ方を揃える）🎀🪞

この章は「**どんな失敗が起きても、UIの見せ方がブレない**」状態を作るよ〜！😊✨
“その場しのぎ”で `alert()` や適当トーストを増やしちゃうと、あとで地獄を見るので…🥹💥 ここでスッキリ統一しよっ💪💖

---

## 1. UIがグチャる“あるある” 😵‍💫📱

こんな経験ない？💭

* 同じ失敗なのに、画面Aはトースト、画面Bはダイアログ…🤯
* 「失敗しました」しか出なくて、ユーザーが次に何すればいいか分からない🥲
* フォームでどの項目が悪いのか分からず、全部やり直し😇
* 画面が真っ白で「え、なに？」ってなる☁️🕳️

これって要するに、**UIの“最後の受け皿（境界）”が設計されてない**のが原因なの💡

---

## 2. UIの失敗表現は「4種類」だけ覚えよ🧠✨

UIの見せ方って、実はだいたいこの4つに整理できるよ〜😊🎨

1. **フォーム項目エラー** 📝👉（例：メールが不正です）
2. **トースト/バナー** 🍞🔔（軽め・非致命的）
3. **ダイアログ** 🪟⚠️（止めるべき・判断が必要）
4. **画面全体（ページ）エラー** 🧯🖥️（壊れた・続行不可）

ポイントはこれ👇✨
**「エラーの種類」→「UI表現」へ、毎回“同じルール”で変換する**こと！

---

## 3. UI例外境界ってなに？🚪🪄（超やさしく）

**UI例外境界 = UIが受け取った失敗を、統一した見せ方に変換して出す場所**だよ😊🎀

* どこかで例外が飛ぶ（or ResultでErrが返る）
* それを **App標準のError（ドメイン/インフラ/バグ）** に正規化（第15章あたりの話）
* 最後に UI境界で **「どう見せる？」を決定**する✨

つまりUI側は、

> 「エラーをどう表示するか」の“司令塔”を1つ作る📣👑

って感じ！

---

## 4. UI表示用の“共通フォーマット”を決めよう📦✨

まず、UIが扱う形を揃えると超ラクになるよ😊
例：**UiError** みたいな「表示の設計図」を作る🎀

```ts
// UIが“表示するためだけ”に持つ情報の形
export type UiError =
  | {
      kind: "field";
      message: string;
      fieldErrors: Record<string, string>; // name -> message
    }
  | {
      kind: "toast";
      message: string;
      action?: { label: string; onAction: () => void };
    }
  | {
      kind: "dialog";
      title: string;
      message: string;
      primary?: { label: string; onClick: () => void };
      secondary?: { label: string; onClick: () => void };
    }
  | {
      kind: "page";
      title: string;
      message: string;
      primary?: { label: string; onClick: () => void };
    };
```

この「kind」が超重要で、さっきの4種類に対応してるよ🎀🪞

![UI境界の鏡：エラーの実体を、トーストやダイアログとして映し出す[(./picture/err_model_ts_study_026_ui_boundary_mirror.png)

---

## 5. “変換ルール”が本体だよ🗺️✨（AppError → UiError）

次に、あなたのアプリの標準エラー（例：`DomainError / InfraError / BugError`）を、UiErrorへ変換するよ😊

### 変換の基本ルール（おすすめ）💡

| 失敗の種類                 | UI表現           | ねらい                 |
| --------------------- | -------------- | ------------------- |
| Domain（入力ミス/業務ルール）💗  | field / dialog | 直せる場所をピンポイントで伝える    |
| Infra（通信/外部API/DB）🌩️ | toast / dialog | 再試行導線をつける🔁         |
| Bug（不変条件違反）⚡          | page           | ユーザーに責任を押しつけない＆復帰導線 |

> ReactのError Boundaryは「レンダー中のエラー」を受け止める仕組みで、try/catchでは代替できないよ〜という整理も公式やLintで語られてるよ🧠✨ ([React][1])

### 変換関数の例🧼🧺

```ts
type AppError =
  | { type: "Domain"; code: string; message: string; field?: string }
  | { type: "Infra"; code: string; message: string; retryable: boolean }
  | { type: "Bug"; code: string; message: string };

export function toUiError(err: AppError): UiError {
  switch (err.type) {
    case "Domain": {
      if (err.field) {
        return {
          kind: "field",
          message: "入力を確認してね😊",
          fieldErrors: { [err.field]: err.message },
        };
      }
      return {
        kind: "dialog",
        title: "入力を確認してね📝",
        message: err.message,
        primary: { label: "OK", onClick: () => {} },
      };
    }

    case "Infra": {
      if (err.retryable) {
        return {
          kind: "toast",
          message: "通信が不安定かも…もう一回試してみよ？📶🔁",
          // onAction は呼び出し側で差し込む設計でもOK
        };
      }
      return {
        kind: "dialog",
        title: "接続に失敗したよ🌩️",
        message: "時間をおいて試すか、ネットワークを確認してね😊",
        primary: { label: "閉じる", onClick: () => {} },
      };
    }

    case "Bug": {
      return {
        kind: "page",
        title: "ごめんね、画面の表示に失敗したよ🥲",
        message: "操作をやり直しても直らない場合は、時間をおいて試してね🙏",
        primary: { label: "再読み込み", onClick: () => location.reload() },
      };
    }
  }
}
```

ここまでできると、あとは「kindごとに描画」するだけ🎨✨

---

## 6. Reactの「Error Boundary」って何を守ってくれるの？🛡️⚛️

ReactのError Boundaryは、**レンダー中（render）やライフサイクル中の例外**をキャッチして、アプリが真っ白になるのを防ぐ仕組みだよ🧯✨ ([React][2])
ただし注意！🚨

* **イベントハンドラの例外はキャッチしない**（例：ボタンのonClick内のthrow） ([React][2])
  → こういうのは普通に `try/catch` で拾うのが基本だよ😊

### ざっくり指針💡

* **画面を描く途中で落ちる** → Error Boundary（ページ/セクション境界）
* **ユーザー操作で失敗する** → try/catch + UiError（toast/dialog/field）

---

## 7. Next.js（App Router）だと“境界”が標準装備🧱✨

Next.js（App Router）では、ルートセグメントに `error.tsx` を置いて、**その範囲のエラーを受け止めてフォールバックUIを出す**仕組みがあるよ😊 ([Next.js][3])
さらに、ルート全体のエラーは `global-error.tsx` で扱える（ルートレイアウトを置き換えるので `<html><body>` が必要など注意点あり）って公式が説明してるよ🪄 ([Next.js][4])

> 「境界を置く場所」をフレームワークがガイドしてくれるの、かなり助かるやつ〜🥹💖

---

## 8. react-error-boundary を使うと“実務が楽”💐✨

ReactのError Boundaryは基本「class」で書く仕様だけど、`react-error-boundary` を使うと、使い勝手がかなり良くなるよ😊
`fallback` を出したり、**リトライ（reset）** ボタンも作りやすい✨ ([npmjs.com][5])

```ts
import { ErrorBoundary } from "react-error-boundary";

function ErrorFallback({
  error,
  resetErrorBoundary,
}: {
  error: Error;
  resetErrorBoundary: () => void;
}) {
  return (
    <div role="alert">
      <p>ごめんね、表示に失敗しちゃった🥲</p>
      <button onClick={resetErrorBoundary}>もう一回やってみる🔁</button>
    </div>
  );
}

export function PageShell({ children }: { children: React.ReactNode }) {
  return (
    <ErrorBoundary FallbackComponent={ErrorFallback}>
      {children}
    </ErrorBoundary>
  );
}
```

---

## 9. UI側の「表示コンポーネント」を1セット持とう🎀🧩

さっきの `UiError` を受けて、表示を揃える部品を作るよ😊✨
（UIライブラリは何でもOK。ここは概念が大事🎓）

```ts
export function presentUiError(err: UiError) {
  switch (err.kind) {
    case "toast":
      // showToast(err.message, err.action)
      return;

    case "dialog":
      // openDialog(err.title, err.message, err.primary, err.secondary)
      return;

    case "field":
      // setFormErrors(err.fieldErrors)
      return;

    case "page":
      // これはErrorBoundaryのfallbackで描画する方が自然なことが多い✨
      return;
  }
}
```

ここまで来ると、アプリ内の各所はこう書ける👇

* 失敗したら `toUiError()` に投げる
* `presentUiError()` で出す
* **画面ごとのノリで表示を変えない**🙅‍♀️✨

---

## 10. “同じ失敗”を3種類のUIに変換してみよう（ミニ演習）📝🎀

題材：**「外部APIの支払い処理がタイムアウト」** 🌩️⏳

1. **トースト版** 🍞

* 文言：短く
* 行動：再試行ボタン🔁

2. **ダイアログ版** 🪟

* 文言：少し丁寧に
* 行動：再試行 / キャンセル

3. **ページ版（フォールバック）** 🧯

* 文言：責任をユーザーに押しつけない
* 行動：再読み込み or トップへ

> コツ：**「次に何してほしいか」を必ず入れる**😊✨

---

## 11. UI文言の“トーン統一”テンプレ💬🎀

UIメッセージって、統一されてると安心感が爆上がりするよ🫶✨
おすすめテンプレ👇

* 状況：何が起きた？（短く）
* 次：何してほしい？（1個）
* 逃げ道：ダメならどうする？（1個）

例：
「通信が不安定かも📶 もう一回試してみてね🔁（ダメなら時間をおいてね😊）」

---

## 12. AI活用🤖💖（この章で効くプロンプト集）

### ① 失敗 → UI表現の判定を手伝わせる🧠

* 「この失敗は toast/dialog/field/page のどれが適切？理由も一緒に！」

### ② 文言を“統一トーン”にする💬✨

* 「このエラーメッセージを、やさしく短く、次の行動が分かる形に直して😊」

### ③ 変換表（マッピング）を増やす🗺️

* 「Domain/Infra/Bug それぞれ、ありがちなケースを10個ずつ挙げて、推奨UIも付けて📋」

---

## 13. まとめ🎓✨（この章のゴール）

* UIの失敗表現は **4種類に固定**（field/toast/dialog/page）🎀
* **AppError → UiError への変換ルール**が本体🗺️✨
* React/Next.jsの **Error Boundary** は「レンダー中のクラッシュ防止」に強い🧯（でもイベントやPromiseは別） ([React][2])
* `react-error-boundary` を使うと実務のリトライUIが作りやすい🔁 ([npmjs.com][5])

---

次の章（第27章）では、このUI境界で出した失敗を **「安全にログに残す」** 方へつなげるよ〜🔎🧾🔒
もし、題材を「フォーム中心」「一覧＋詳細中心」「決済や予約中心」みたいに寄せたいなら、その前提で第26章のコード例もそれに合わせて作り直すね😊💖

[1]: https://react.dev/reference/eslint-plugin-react-hooks/lints/error-boundaries?utm_source=chatgpt.com "error-boundaries"
[2]: https://legacy.reactjs.org/docs/error-boundaries.html?utm_source=chatgpt.com "Error Boundaries"
[3]: https://nextjs.org/docs/13/app/building-your-application/routing/error-handling?utm_source=chatgpt.com "Routing: Error Handling"
[4]: https://nextjs.org/docs/app/getting-started/error-handling?utm_source=chatgpt.com "Getting Started: Error Handling"
[5]: https://www.npmjs.com/package/react-error-boundary?utm_source=chatgpt.com "react-error-boundary"
