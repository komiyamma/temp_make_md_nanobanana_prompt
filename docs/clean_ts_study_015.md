# 第15章：Input Boundary：Requestモデル設計📥

([Past chat][1])([Past chat][2])([Past chat][3])([Past chat][4])([Past chat][5])

この章はね、「外から来た入力（ユーザー操作・JSON・フォーム）」を **UseCaseが食べやすい形に整えるための“型（モデル）”を決める回**だよ〜😊💕

ポイントはこれ👇

* UseCaseの入力は **HTTPとかUIの都合を一切持ち込まない** 🚫🌐
* でも、外から来る入力はだいたい **汚い（欠けてる/型が違う/余計なものが混ざる）** 😵‍💫
* だから **Requestモデル＝“関所”** みたいにして、UseCaseを守る🛡️✨

TypeScriptの最新(本日時点)は **TypeScript 5.9** が公式リリースノートとして提供されてるよ📌 ([typescriptlang.org][6])

---

## 1) 今日のゴール🎯💖

この章が終わったら、こんな状態になってるのが理想だよ✨

* ✅ Create/Complete/List の **Requestモデルを型で定義**できる
* ✅ Requestに **HTTPっぽい言葉（req/res, statusCode, headers…）を混ぜない**で済む
* ✅ 「外から来たデータ」を **Requestへ詰め替える時のルール**が決まる
* ✅ テストしやすい（Requestがただのデータになる）🧪✨

---

## 2) Requestモデルってなに？📦🧸

Requestモデルは、UseCaseに渡す入力を **“UseCase都合の形”にした箱**だよ🎁✨

例：CreateTaskなら

* 外側（UI/HTTP）では `"title"` が空かも / 数字かも / 変な空白が混ざるかも 😇
* でもUseCaseは「タスクを作る」ために **最低限これだけ欲しい** → `title: string`

だから、Requestモデルはこうなる👇

* **CreateTaskRequest**：`title` だけ
* **CompleteTaskRequest**：`taskId` だけ
* **ListTasksRequest**：フィルタがあればそれだけ

![Requestモデルのフィルタリングイメージ](./picture/clean_ts_study_015_request_model.png)

---

## 3) 絶対ルール：Requestに入れちゃダメなもの🚫🧨

![Forbidden Items in Request](./picture/clean_ts_study_015_forbidden_items.png)

Requestは **UseCase層のもの**だから、外側の匂いを入れると崩れやすいよ🥲

入れないでね👇

* ❌ `Request`, `Response`, `headers`, `cookies`, `statusCode`
* ❌ `express.Request` みたいなフレームワーク型
* ❌ DBっぽいもの（`row`, `record`, `limit/offset(SQL都合)`）
* ❌ UI都合の名前（`titleInputValue` とか `formState` とか）

「UseCaseが欲しい入力の最小セット」だけを、静かに置くのが勝ち✨🏆

---

## 4) Requestモデル設計のコツ5つ🧠✨

### コツ1：**“UseCaseの質問”にだけ答える形にする**💬

CreateTaskは「タイトル何？」だけ聞いてるのに、`createdAt` とか入れない😌

### コツ2：**内側の言葉で命名する**📖

`taskId`, `title` みたいに業務語彙で統一✨

### コツ3：**idはなるべく“ブランド型”にする**🆔✨

ただの `string` だと、`userId` と `taskId` 間違えても気づきにくい😭
TypeScriptなら“ブランド型”で事故を減らせるよ🚑✨

### コツ4：**Requestは基本 immutable（readonly）に寄せる**🧊

![Immutable Request Object](./picture/clean_ts_study_015_immutable_request.png)

「あとから書き換えOK」にすると、原因不明バグが増える😵‍💫

### コツ5：**“型(コンパイル時)”と“実行時チェック”を混同しない**⚠️

TypeScriptの型は実行時に消えるよね。
外から来る入力（JSON等）は、必要なら **実行時バリデーション**も使う（後でController側で）🧪✨
Zodみたいなライブラリは「parseしたら型安全」って発想ができるよ📌 ([Zod][7])

---

## 5) 実装してみよう💻✨（Requestモデル3つ）

### 5-1. 型の土台：Brand型を用意🧷✨

![Brand Type Safety](./picture/clean_ts_study_015_brand_type.png)

`src/usecases/_shared/brand.ts`

```ts
export type Brand<T, B extends string> = T & { readonly __brand: B };
```

`TaskId` を作る👇
`src/entities/task-id.ts`（Entitiesに置いてもOK。ここでは分かりやすさ優先で例として）

```ts
import type { Brand } from "../usecases/_shared/brand";

export type TaskId = Brand<string, "TaskId">;

export const TaskId = {
  // ここでは「ブランド付け」だけ。実行時チェックは別でやる想定。
  of(value: string): TaskId {
    return value as TaskId;
  },
};
```

> ブランド型は「型の事故防止」のためのテクだよ✨
> ちなみに `satisfies` 演算子（TypeScript 4.9〜）も “型を守りつつ推論を壊さない” のに便利！📌 ([typescriptlang.org][8])

---

### 5-2. CreateTaskRequest📥🗒️

![Request Model Examples](./picture/clean_ts_study_015_request_examples.png)

`src/usecases/create-task/create-task-request.ts`

```ts
export type CreateTaskRequest = Readonly<{
  title: string;
}>;
```

設計ポイント💡

* `id` は入れない（IdGenerator Portが作る予定だから）
* `title` だけで十分✨

---

### 5-3. CompleteTaskRequest✅🆔

`src/usecases/complete-task/complete-task-request.ts`

```ts
import type { TaskId } from "../../entities/task-id";

export type CompleteTaskRequest = Readonly<{
  taskId: TaskId;
}>;
```

設計ポイント💡

* `taskId` は **ただのstringじゃなく TaskId** にして事故を防ぐ🛡️✨

---

### 5-4. ListTasksRequest👀📋

`src/usecases/list-tasks/list-tasks-request.ts`

```ts
export type ListTasksRequest = Readonly<{
  onlyIncomplete?: boolean; // 例：未完了だけ欲しい
}>;
```

設計ポイント💡

* 「一覧」が必要とする条件だけ
* SQLの `limit/offset` はここでは入れない（DB都合だから）🙅‍♀️

---

## 6) Requestを作る側（外側）での“詰め替え”ルール🧃✨

![Controller Refilling Process](./picture/clean_ts_study_015_controller_refill.png)

ここ超大事〜！
Requestモデル自体はUseCase側に置くけど、**Requestを作るのは外側（Controller/Inbound Adapter）** だよ🚪✨
（本格的な変換は第31章でやるけど、この章でも“ルール”だけ固めちゃおう）

### ルール✅

![satisfies Operator Check](./picture/clean_ts_study_015_satisfies_check.png)

* 外側の生データは `unknown` として受ける（信用しない😇）
* 変換した結果が Request
* Requestを作るとき、`satisfies` で形チェックすると安全✨ ([typescriptlang.org][8])

例（Controller側のイメージ）：

```ts
import type { CreateTaskRequest } from "../usecases/create-task/create-task-request";

const req = {
  title: String(input.title ?? "").trim(),
} satisfies CreateTaskRequest;
```

ここで「余計なプロパティ」や「足りないプロパティ」を早めに気づけるのが嬉しいやつ🥰

---

## 7) よくある失敗あるある😵‍💫💥

* ❌ Requestに `statusCode` とか入れ始める（HTTPの侵食）
* ❌ Requestに `TaskRecord`（DB行）をそのまま入れる（DBの侵食）
* ❌ UIのフォーム状態をそのまま入れる（UIの侵食）
* ❌ 「便利そう」で巨大Requestにする（UseCaseがブヨブヨに）🐷

合言葉はこれ👉
**Requestは“UseCaseが欲しい最小セット”だけ**🌸

---

## 8) 練習問題✍️💕

### Q1 ✅

CreateTaskRequest に `id` を入れたくなりました。なぜやめた方がいい？（一言でOK）

### Q2 ✅

ListTasksRequest に `limit/offset` を入れたくなりました。どこに置くのが筋？（層で答えてね）

### Q3 ✅（発展）

新ユースケース「RenameTask」を追加するなら、Requestはどんな形にする？
（ヒント：UseCaseが必要な最小情報だけ✨）

---

## 9) AI相棒プロンプト（コピペ用）🤖✨

* 💡Request設計案を出させる

```text
Create/Complete/List のUseCaseに対して、UseCaseが必要な最小入力だけで Request 型を設計して。
HTTP/DB/UI都合の項目は入れないで。各Requestの理由も1行で。
```

* 💡命名チェック

```text
このRequest名/プロパティ名は「内側の言葉」になってる？外側(HTTP/DB/UI)の匂いがあれば改善案を出して。
```

* 💡Brand型の導入チェック

```text
TaskIdをstringのまま使うリスクを列挙して、Brand型にした場合の改善点と注意点を教えて。
```

---

## まとめ🎀✨

* Requestモデルは **UseCaseに渡す“きれいな入力箱”** 📦
* **外側の言葉（HTTP/DB/UI）を入れない**のが最重要🚫
* TypeScriptでは **Brand型**や **satisfies** で事故を減らせる🛡️✨ ([typescriptlang.org][8])
* 実行時チェックが必要なら、Zodみたいな仕組みを“外側”で使うと相性いいよ🧪✨ ([Zod][7])

次の第16章は **Output Boundary：Response設計📤** だね！
RequestとResponseが揃うと、UseCaseがめちゃくちゃ美しくなるよ〜🥰✨

[1]: https://chatgpt.com/c/6971bcc8-dcec-8321-aa8a-5b588cbb6f33 "設計優先度リスト"
[2]: https://chatgpt.com/c/6971d6d0-718c-839e-b2b4-05253bfae8eb "クリーンアーキテクチャ第8章"
[3]: https://chatgpt.com/c/697221c0-b428-8323-8d09-2fe36db55daa "Dependency Rule 解説"
[4]: https://chatgpt.com/c/6971e907-4230-8324-b9af-b752f9f7198e "Input Port設計ガイド"
[5]: https://chatgpt.com/c/6971c11c-aabc-8323-ba7a-40fd6f4ac1b8 "設計教材確認"
[6]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"
[7]: https://zod.dev/?utm_source=chatgpt.com "Zod: Intro"
[8]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html?utm_source=chatgpt.com "Documentation - TypeScript 4.9"
