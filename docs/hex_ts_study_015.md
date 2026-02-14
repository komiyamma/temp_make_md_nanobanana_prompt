# 第15章：フォルダ構成を固定（迷子防止）📁🧭

![hex_ts_study_015[(./picture/hex_ts_study_015_the_domain_layer.png)

ファイルが増えてくるとね、**「どこに何置くんだっけ…？」**って迷子になりがち😵‍💫
この章はそれを防ぐために、**フォルダの“住所”を最初に固定**しちゃう回だよ〜！🎀✨

---

## 15.1 迷子が起きる理由あるある 😵‍💫🌀

* `todo.ts` が3つある（どれが本体！？）😇
* `controller` にルールが混ざって修正が怖い💥
* DB/HTTP/画面の都合が中心に入り込んでゴチャゴチャ🤯

なので、**最初に “置き場所ルール” を決めて守る**のが勝ち🥇✨

---

## 15.2 3点セットで固定するよ！📦✨

この教材は、まずこれだけ覚えればOK🙆‍♀️💕

* `domain/`：**ルールと状態**（一番大事な中心🛡️）
* `app/`：**ユースケース**（手順＋判断）🎮➡️🧠
* `adapters/`：**外側の都合**（CLI/HTTP/DB/ファイル…）🌍🔁

> ✨ポイント：**「中心（domain/app）」を守るために、外側（adapters）を隔離する**感じだよ〜🏰🛡️

---

## 15.3 今回のToDoミニの“完成フォルダ”見本 📁✨

まずゴール形を置いちゃうね！（これに寄せていく）🧩

```text
your-app/
├─ src/
│  ├─ domain/
│  │  ├─ todo/
│  │  │  ├─ Todo.ts
│  │  │  ├─ TodoId.ts
│  │  │  └─ errors.ts
│  │  └─ index.ts
│  │
│  ├─ app/
│  │  ├─ ports/
│  │  │  ├─ TodoRepositoryPort.ts
│  │  │  └─ ClockPort.ts
│  │  ├─ usecases/
│  │  │  ├─ AddTodoUseCase.ts
│  │  │  ├─ CompleteTodoUseCase.ts
│  │  │  └─ ListTodosUseCase.ts
│  │  ├─ dto/
│  │  │  ├─ AddTodoDTO.ts
│  │  │  └─ TodoView.ts
│  │  └─ index.ts
│  │
│  ├─ adapters/
│  │  ├─ inbound/
│  │  │  └─ cli/
│  │  │     ├─ parseArgs.ts
│  │  │     └─ cliAdapter.ts
│  │  ├─ outbound/
│  │  │  ├─ memory/
│  │  │  │  └─ InMemoryTodoRepositoryAdapter.ts
│  │  │  └─ file/
│  │  │     └─ FileTodoRepositoryAdapter.ts
│  │  └─ index.ts
│  │
│  └─ main.ts   ← Composition Root（組み立て場所）🧩🏗️
│
├─ eslint.config.js
├─ tsconfig.json
└─ package.json
```

💡`index.ts` は「このフォルダから外に出していいもの」をまとめる“出口”🚪✨
（後で import がキレイになるよ〜！）

---

## 15.4 import ルール（依存の向き）を固定するよ 🧭🔥

ここが迷子防止の**最強ルール**💪✨

✅ **OK（許可）**

* `app` → `domain` を使う👌
* `adapters` → `app` / `domain` を使う👌

❌ **NG（禁止）**

* `domain` → `app` / `adapters` を参照しない🙅‍♀️
* `app` → `adapters` を参照しない🙅‍♀️

イメージはこれ👇✨

```text
domain   ← だれにも依存しない🛡️
  ↑
app      ← domain だけ知ってOK🎮
  ↑
adapters ← app/domain を呼び出してOK🌍
```

---

## 15.5 命名ルール（迷子にならない名前の付け方）🏷️✨

フォルダだけじゃなく、**ファイル名も型**みたいに効くよ〜😆✨

### 🔌 Port（約束）側

* `〜Port` で「これは約束だよ！」が一瞬で分かる✨
  例：
* `TodoRepositoryPort`
* `ClockPort`

### 🧩 Adapter（実装）側

* `〜Adapter` で「これは変換・接続役だよ！」が分かる✨
  例：
* `InMemoryTodoRepositoryAdapter`
* `FileTodoRepositoryAdapter`
* `CliAdapter`

---

## 15.6 パスを短くする（tsconfig の paths）🪄📦

深い相対パスって、地味に心を削るよね…🥹
なので `@domain/*` みたいに短くしちゃう✨

```json
// tsconfig.json（例）
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@domain/*": ["src/domain/*"],
      "@app/*": ["src/app/*"],
      "@adapters/*": ["src/adapters/*"]
    }
  }
}
```

⚠️ここ大事：`paths` は **TypeScriptの解決ルール**であって、`tsc` の出力（実行時）を自動で書き換える機能ではないよ〜！
（実行方法やテスト側で別途対応が必要になる場合あり）📌✨ ([typescriptlang.org][1])

---

## 15.7 “ルールを守れてるか”を機械に見張らせる 👮‍♀️🧹✨（超おすすめ）

「気をつける」って人間は忘れるので…
**ESLintに怒ってもらう**のが最強💥😆

### ✅ ESLint は “flat config（eslint.config.js）” が今の主流

ESLint v9 から新しい設定方式（flat config）がデフォルトだよ📌✨ ([ESLint][2])

### まずは最小：`no-restricted-imports` で “逆流” を止める🛑

例：`domain` から `adapters` を import できないようにする（ざっくりガード）💪
このルールは `paths` / `patterns` 指定ができるよ📌 ([ESLint][3])

```js
// eslint.config.js（例：超ミニの方向性ガード）
export default [
  {
    files: ["src/domain/**/*.ts"],
    rules: {
      "no-restricted-imports": ["error", {
        "patterns": [
          { "group": ["@adapters/*", "../adapters/*", "../../adapters/*"], "message": "domain から adapters は参照しないでね🛡️" },
          { "group": ["@app/*", "../app/*", "../../app/*"], "message": "domain から app も参照しないでね🛡️" }
        ]
      }]
    }
  }
];
```

> これだけでも「うっかり逆向き」をかなり防げるよ〜😆🛡️

---

## 15.8 もっと強く守る：JS Boundaries で “フォルダ境界” をガチガチにする 🧱✨

「domain/app/adapters の関係」を**ルールとして宣言**できるやつ！めちゃ便利😍
`boundaries/elements` で要素を定義して、`boundaries/element-types` で依存ルールを書く感じだよ📌 ([jsboundaries.dev][4])

```js
// eslint.config.js（例：domain/app/adapters の3点セットを強制）
import boundaries from "eslint-plugin-boundaries";

export default [
  {
    plugins: { boundaries },
    settings: {
      "boundaries/elements": [
        { type: "domain", pattern: "src/domain/**", mode: "file" },
        { type: "app", pattern: "src/app/**", mode: "file" },
        { type: "adapters", pattern: "src/adapters/**", mode: "file" }
      ]
    },
    rules: {
      "boundaries/element-types": [2, {
        default: "disallow",
        rules: [
          { from: ["domain"], allow: ["domain"] },
          { from: ["app"], allow: ["app", "domain"] },
          { from: ["adapters"], allow: ["adapters", "app", "domain"] }
        ]
      }]
    }
  }
];
```

これで、もし `app` から `adapters` を直接 import したら
**「ダメ〜〜！」ってビシッと怒ってくれる**😆💥

---

## 15.9 VS Code で迷子にならない小技 🧭✨

* `Ctrl+P`：ファイル名で瞬間移動🚀
* `Ctrl+Shift+F`：プロジェクト全体検索🔎
* `src/domain` / `src/app` / `src/adapters` を**常に見える位置**に置く（開いておく）📌✨
* `index.ts` を“出口”にしておくと import が整う💅✨

---

## 15.10 AIに頼むならここ！🤖💖（フォルダ作りは得意）

AIには「設計の芯」じゃなくて、**骨組み作り**を任せるのが安全🙆‍♀️✨
そのまま使えるお願いテンプレ👇

```text
あなたはTypeScriptプロジェクトの雛形作り担当です。
Hexagonalの方針で src/domain, src/app, src/adapters を作り、
各フォルダに index.ts を置き、Todoミニアプリ向けの空ファイルも作ってください。
ただし domain/app は adapters を import しない前提で、依存の向きをコメントで明記してください。
```

---

## 15.11 まとめ（この章の合格ライン）🎀✅

* `domain / app / adapters` の3点セットが作れてる📁✨
* **依存の向き**が守れてる🧭🛡️
* Port と Adapter の命名がブレてない🔌🧩
* できれば ESLint で “逆流” を止めてる👮‍♀️✨

---

## 自主課題（5分でOK）📝💖

1. いまのプロジェクトに `src/domain`, `src/app`, `src/adapters` を作る📁
2. `domain` に仮で `Todo.ts` を置く📝
3. わざと `domain` から `adapters` を import してみる（怒られたら勝ち😆💥）

---

必要なら次の章（ドメイン＝ルール置き場🏠📌）へつなげて、**「じゃあ domain に何を書けばいいの？」**を気持ちよくやっていこ〜！😊✨

[1]: https://www.typescriptlang.org/tsconfig/paths.html "TypeScript: TSConfig Option: paths"
[2]: https://eslint.org/blog/2025/03/flat-config-extends-define-config-global-ignores/ "Evolving flat config with extends - ESLint - Pluggable JavaScript Linter"
[3]: https://eslint.org/docs/latest/rules/no-restricted-imports "no-restricted-imports - ESLint - Pluggable JavaScript Linter"
[4]: https://www.jsboundaries.dev/docs/rules/dependencies/ "Rule element-types | JS Boundaries"
