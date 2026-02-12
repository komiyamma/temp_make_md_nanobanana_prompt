# 第35章：unionで状態を表す（ifを減らす）🧷

![ユニオン型とピン](./picture/tdd_ts_study_035_union_pin.png)

## 🎯 目的

「状態が増えても壊れにくい」書き方にするために、**union（特に discriminated union）で状態を表現**できるようになるよ🙌
そして、`if`だらけの分岐を **スッキリ読みやすく**していくよ〜🌸

---

## 📚 学ぶこと（この章のキーワード）🧠💡

* **リテラル型**：`"idle"` みたいに「この文字列だけ」って固定する型🧷
* **union型**：`A | B | C` みたいに「どれか」って表す型🎲
* **discriminated union**：`kind: "idle" | "loading" ...` みたいに、**目印（識別子）で分岐できるunion**🌟 ([typescriptlang.org][1])
* **narrowing**：`if (state.kind === "success")` で型が絞られて安全になるやつ🧤 ([typescriptlang.org][2])

---

## 🌷 まずイメージ：状態を「1つの型」に詰め込むと地獄になる😵‍💫

![画像を挿入予定](./picture/tdd_ts_study_035_state_boxes.png)

ありがちなやつ👇（見た目は簡単だけど…）

```ts
type User = { id: string; name: string };

type AuthStateBad = {
  status: "idle" | "loading" | "success" | "error";
  user?: User;            // success のとき本当は必須
  errorMessage?: string;  // error のとき本当は必須
};
```

これ、**矛盾した状態が作れちゃう**のが問題💥

* `status: "success"` なのに `user` が無い…😱
* `status: "error"` なのに `errorMessage` が無い…😵

---

## ✅ 解決：状態を union で「正しい形だけ」にする💖

### ✨ “状態ごとに型を分ける” がコツ

TypeScript公式でもよく出てくるパターンだよ〜🧸 ([typescriptlang.org][1])

```ts
type User = { id: string; name: string };

type Idle = { kind: "idle" };
type Loading = { kind: "loading"; email: string };
type Success = { kind: "success"; user: User };
type ErrorState = { kind: "error"; message: string };

export type AuthState = Idle | Loading | Success | ErrorState;
```

これで…
✅ `success` のときは `user` が必ずある
✅ `error` のときは `message` が必ずある
✅ 変な状態が「型で」作れない 🎉

---

## 🧪 手を動かす：ログイン状態をTDDで作るよ🧁💻

## つくるもの🎁

* `reduceAuth(state, event)`：状態遷移（state machineの超ミニ版）🔁
* `viewModel(state)`：画面表示用の情報を作る（if地獄になりがちな所！）🖥️✨

---

## ① テストを書く（Red🔴）🧪

`src/auth/auth.test.ts` みたいな感じでOK！

```ts
import { describe, it, expect } from "vitest";
import { reduceAuth, viewModel } from "./auth";
import type { AuthState } from "./state";

describe("auth state", () => {
  it("idle で SUBMIT したら loading になる", () => {
    const state: AuthState = { kind: "idle" };
    const next = reduceAuth(state, { type: "SUBMIT", email: "a@b.com" });
    expect(next).toEqual({ kind: "loading", email: "a@b.com" });
  });

  it("loading で RESOLVE したら success になる", () => {
    const state: AuthState = { kind: "loading", email: "a@b.com" };
    const next = reduceAuth(state, { type: "RESOLVE", user: { id: "u1", name: "Mia" } });
    expect(next).toEqual({ kind: "success", user: { id: "u1", name: "Mia" } });
  });

  it("loading で REJECT したら error になる", () => {
    const state: AuthState = { kind: "loading", email: "a@b.com" };
    const next = reduceAuth(state, { type: "REJECT", message: "パスワードが違うよ" });
    expect(next).toEqual({ kind: "error", message: "パスワードが違うよ" });
  });

  it("viewModelは状態に応じて表示文言を返す（例：success）", () => {
    const vm = viewModel({ kind: "success", user: { id: "u1", name: "Mia" } });
    expect(vm.headline).toBe("ようこそ、Mia さん🎉");
    expect(vm.canSubmit).toBe(false);
  });
});
```

> Vitestの `expect` はこういう感じで使うよ〜🧁 ([Vitest][3])

---

## ② 最小実装（Green🟢）🧩

`src/auth/state.ts`

```ts
export type User = { id: string; name: string };

export type AuthState =
  | { kind: "idle" }
  | { kind: "loading"; email: string }
  | { kind: "success"; user: User }
  | { kind: "error"; message: string };

export type AuthEvent =
  | { type: "SUBMIT"; email: string }
  | { type: "RESOLVE"; user: User }
  | { type: "REJECT"; message: string }
  | { type: "RESET" };
```

`src/auth/auth.ts`

```ts
import type { AuthEvent, AuthState } from "./state";

export function reduceAuth(state: AuthState, event: AuthEvent): AuthState {
  // ✅ まずは「通す」優先（あとで綺麗にする✨）
  if (state.kind === "idle" && event.type === "SUBMIT") {
    return { kind: "loading", email: event.email };
  }
  if (state.kind === "loading" && event.type === "RESOLVE") {
    return { kind: "success", user: event.user };
  }
  if (state.kind === "loading" && event.type === "REJECT") {
    return { kind: "error", message: event.message };
  }
  if (event.type === "RESET") {
    return { kind: "idle" };
  }
  return state; // それ以外は現状維持（ここは方針次第で変えてOK）
}

export function viewModel(state: AuthState): { headline: string; canSubmit: boolean; error?: string } {
  // ✅ if を減らしたいので、ここは switch が相性よし🌟
  switch (state.kind) {
    case "idle":
      return { headline: "ログインしてね🙂", canSubmit: true };
    case "loading":
      return { headline: "ログイン中…⏳", canSubmit: false };
    case "success":
      return { headline: `ようこそ、${state.user.name} さん🎉`, canSubmit: false };
    case "error":
      return { headline: "ログイン失敗💦", canSubmit: true, error: state.message };
  }
}
```

ここ、**`state.kind` を見るだけで、必要なプロパティが自動で安全に扱える**のが気持ちいいポイント🫶
（これが narrowing だよ〜！） ([typescriptlang.org][2])

---

## ③ Refactor（キレイにする✨）🧼

### 💡 リファクタの狙い

* 「状態」ごとの情報が **混ざらない** ✅
* `if (status === ...) { if (user) ... }` みたいな **二段チェックが消える** ✅
* 将来 `kind: "twoFactor"` が増えても **追加しやすい** ✅

---

## 🤖 AIの使いどころ（この章の勝ちパターン）💪🤖

AIに丸投げじゃなくて、「案を量産させて、選ぶ」感じが強いよ〜✨

## 💬 プロンプト例（コピペOK）📎

* 「ログイン状態を discriminated union で設計して。`idle/loading/success/error` で、各状態に必要な情報も提案して。2案ちょうだい🌸」
* 「`reduceAuth` のテストケース、抜けてる観点を5つ挙げて（でも実装方針は押し付けないで）🧪」
* 「`viewModel` が if 地獄にならない書き方にして。switch 版と関数分割版を見せて🙂」

---

## ✅ チェック（できたら合格💮）🎀

* ✅ `success` なのに `user` が無い、みたいな“矛盾”を型で防げてる
* ✅ `viewModel` が「状態ごとに読むだけ」で安全に書ける
* ✅ 状態が1つ増えても「どこを直すか」すぐ分かる（追加に強い）💪
* ✅ `if` の二重チェック（`status`見て、さらに`user?`見る）が減ってる✨

---

## 📝 おまけメモ（2026っぽい最新トピック）📌

TypeScript 5.9系では、Nodeの挙動に合わせた安定オプション（例：`--module node20`）みたいな“ブレにくい設定”も増えてて、環境差で困りにくくなってるよ〜🧩 ([typescriptlang.org][4])
Node側もLTS/メンテLTSが並走してるから、プロジェクト方針に合わせて選ぶ感じになるよ🪄 ([nodejs.org][5])

---

## 🎉 まとめ（超短く）

* 状態は **1つの型に詰め込まない**🙅‍♀️
* **状態ごとに型を分けて union にする**🧷
* `kind` で分岐すると、**ifが減って安全**になる✨

---

次の章（36：ブランド型）に行く前に、もし余力があったら👇やると超強いよ💪💖
「`twoFactor` 状態（例：`kind: "twoFactor"; phone: string`）を追加して、テスト→実装→整理を1サイクル回す」📲🧪

[1]: https://www.typescriptlang.org/docs/handbook/unions-and-intersections.html?utm_source=chatgpt.com "Handbook - Unions and Intersection Types"
[2]: https://www.typescriptlang.org/docs/handbook/2/narrowing.html?utm_source=chatgpt.com "Documentation - Narrowing"
[3]: https://vitest.dev/api/expect.html?utm_source=chatgpt.com "expect"
[4]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"
[5]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
