# 第45章：ファイルI/O境界（本物/偽物の判断）📁

![I/O境界](./picture/tdd_ts_study_045_io_boundary.png)

## 🎯 目的

* 「ファイル読む/書く」が混ざってテストが遅くなる問題を防げるようになるよ🛡️
* **ユニットテストは“偽物”で爆速**、**統合テストは“本物”で少数精鋭**にできるようになるよ⚡️🏃‍♀️

---

## 📚 この章で学ぶこと（超ざっくり結論）🌸

### ✅ ルールはこれだけ！

1. **ユニットテスト**：ファイルは触らない（偽物でOK）🧸
2. **統合テスト**：必要なところだけ本物のファイルで確認（少数）🧪
3. 実装は「中心（ロジック）」と「端（I/O）」を分ける（境界を作る）🚧

> Vitest公式でも「VitestはファイルシステムのモックAPIを内蔵してないから、手で `vi.mock` するより **memfs** みたいな仕組みを推奨するよ」って方針だよ📌 ([Vitest][1])
> さらに `vi.mock` は **`import` されたモジュールだけ**に効く（`require()` は対象外）って注意もあるよ⚠️ ([Vitest][2])

---

## 🧪 手を動かす：例題「設定ファイル(settings.json)を読む」💡

### 仕様（テスト＝仕様書📘）

* ✅ 正常：JSONが読めたら `Settings` を返す
* ✅ ファイルが無い：**デフォルト設定**を返す（落ちない）
* ✅ JSONが壊れてる：**意味が分かるエラー**を投げる（原因が追える）

---

## 🧱 設計：境界を“引数”で作る（いちばん簡単で強い）🎀

ポイントはこれ👇
**「読む処理（readText）」を引数でもらう**＝本物にも偽物にも差し替えできる✨

---

## 🧪 Step1：まずテスト（Red）🚦🔴

```ts
// src/settings/loadSettings.ts
export type Settings = {
  theme: 'light' | 'dark'
  language: 'ja' | 'en'
}

export class InvalidSettingsJsonError extends Error {
  constructor(public readonly path: string, message?: string) {
    super(message ?? `Invalid JSON in ${path}`)
    this.name = 'InvalidSettingsJsonError'
  }
}

export type ReadTextFile = (path: string) => Promise<string>

export async function loadSettings(
  path: string,
  readTextFile: ReadTextFile,
): Promise<Settings> {
  // ここは後で実装する（今は空でOK）
  throw new Error('not implemented')
}
```

```ts
// tests/loadSettings.test.ts
import { describe, it, expect, vi } from 'vitest'
import {
  loadSettings,
  InvalidSettingsJsonError,
  type Settings,
} from '../src/settings/loadSettings'

describe('loadSettings', () => {
  it('JSONが読めたらSettingsを返す', async () => {
    const readTextFile = vi.fn().mockResolvedValue(
      JSON.stringify({ theme: 'dark', language: 'ja' } satisfies Settings),
    )

    await expect(loadSettings('settings.json', readTextFile)).resolves.toEqual({
      theme: 'dark',
      language: 'ja',
    })
  })

  it('ファイルが無いときはデフォルトを返す', async () => {
    const err = Object.assign(new Error('not found'), { code: 'ENOENT' })
    const readTextFile = vi.fn().mockRejectedValue(err)

    await expect(loadSettings('settings.json', readTextFile)).resolves.toEqual({
      theme: 'light',
      language: 'ja',
    })
  })

  it('JSONが壊れてたら分かるエラーを投げる', async () => {
    const readTextFile = vi.fn().mockResolvedValue('{ broken json')

    await expect(loadSettings('settings.json', readTextFile)).rejects.toBeInstanceOf(
      InvalidSettingsJsonError,
    )
  })
})
```

---

## 🟢 Step2：最小実装（Green）🌱

```ts
// src/settings/loadSettings.ts
export type Settings = {
  theme: 'light' | 'dark'
  language: 'ja' | 'en'
}

export class InvalidSettingsJsonError extends Error {
  constructor(public readonly path: string, message?: string) {
    super(message ?? `Invalid JSON in ${path}`)
    this.name = 'InvalidSettingsJsonError'
  }
}

export type ReadTextFile = (path: string) => Promise<string>

const DEFAULT_SETTINGS: Settings = { theme: 'light', language: 'ja' }

function isENOENT(e: unknown): boolean {
  return typeof e === 'object' && e !== null && 'code' in e && (e as any).code === 'ENOENT'
}

export async function loadSettings(
  path: string,
  readTextFile: ReadTextFile,
): Promise<Settings> {
  let text: string
  try {
    text = await readTextFile(path)
  } catch (e) {
    if (isENOENT(e)) return DEFAULT_SETTINGS
    throw e
  }

  try {
    const obj = JSON.parse(text) as Settings
    return obj
  } catch {
    throw new InvalidSettingsJsonError(path)
  }
}
```

✅ ここでテストは全部通るはず〜！🎉

---

## ✨ Step3：リファクタ（Refactor）🧹

ここは“やりすぎない”でOKだよ☺️
例えば👇

* `JSON.parse` の結果が `theme/language` を満たすか軽く検証したい（将来の保険）🧯
* エラー文に「何が壊れてた？」を入れる（デバッグが楽）🔍

---

## 📁 “本物”のファイルで読むアダプタ（端っこ担当）🧩

中心ロジックは **`readTextFile` を受け取るだけ**。
本物のファイルを読むのは、別ファイルに隔離するよ〜！

```ts
// src/adapters/nodeReadTextFile.ts
import { readFile } from 'node:fs/promises'

export async function nodeReadTextFile(path: string): Promise<string> {
  // fs/promises は Promise で扱える（async/awaitしやすい）📘
  return await readFile(path, { encoding: 'utf8' })
}
```

`node:fs/promises` は PromiseベースのファイルAPIだよ📌 ([Node.js][3])
（あと、並列に同じファイルを同時更新すると壊れるかも…みたいな注意も公式にあるよ⚠️ ([Node.js][3])）

---

## 🧪 統合テスト（少数精鋭⭐️）：一回だけ“本物”で確認する

ユニットは偽物で十分だけど、安心のために **1本だけ** 本物でやるのはアリ😊

```ts
// tests/loadSettings.integration.test.ts
import { describe, it, expect } from 'vitest'
import { mkdtemp, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { loadSettings } from '../src/settings/loadSettings'
import { nodeReadTextFile } from '../src/adapters/nodeReadTextFile'

describe('loadSettings (integration)', () => {
  it('本物のファイルから読める', async () => {
    const dir = await mkdtemp(join(tmpdir(), 'tdd-settings-'))
    const file = join(dir, 'settings.json')
    await writeFile(file, JSON.stringify({ theme: 'dark', language: 'en' }), 'utf8')

    const settings = await loadSettings(file, nodeReadTextFile)
    expect(settings).toEqual({ theme: 'dark', language: 'en' })
  })
})
```

---

## 🧠 もう一段：既存コードが `node:fs` を直importしてる時は？（memfs作戦）🪄

「もう既に `import { readFileSync } from 'node:fs'` って書いてある😭」
みたいな時は、Vitest公式が **memfs推し**だよ📌 ([Vitest][1])

* `vi.mock('node:fs')` / `vi.mock('node:fs/promises')` で丸ごと差し替え
* `vol.fromJSON(...)` で仮想ファイルを作る
* テストが速い＆安全🏎️💨

（注意：`vi.mock` は `import` に効くやつなので、`require()` ベースだとハマりやすいよ⚠️ ([Vitest][2])）

---

## 🤖 AIの使いどころ（この章は特に効く！）💖

### ① 境界の切り方が分からない時

* 「この関数、どこからがI/O境界？引数DIにするならどんな型？」って聞く🧠

### ② 遅いテスト診断

* 「このテストが遅い理由を3つ挙げて。偽物化できる境界を提案して」🐢➡️⚡️

### ③ `ENOENT` みたいなエラー分岐

* 「このエラーを“仕様”として扱うとしたらテスト名どうする？」📝

---

## ✅ チェックリスト（合格ライン）🎓✨

* [ ] ユニットテストが **ファイルに触れてない**🧸
* [ ] “読む処理”が差し替え可能（引数DI）📦
* [ ] 統合テストは **1〜2本**に抑えてる⭐️
* [ ] 失敗時に「何が起きたか」分かるエラーになってる🔍

---

## 🧪 追加ミニ課題（10〜20分）🎀

* `loadSettings` に「JSONの型チェック」を足してみよ💪

  * 例：`theme` が `light/dark` 以外なら `InvalidSettingsJsonError` にする
  * テスト→実装→整理の順でね🚦✨

---

必要なら次は、**「書き込み（writeFile）を含む処理」**を同じやり方で境界化して、
「ログ出力」や「保存」もユニットでは偽物で高速に回す形まで一気にやれるよ〜！🧪💨

[1]: https://vitest.dev/guide/mocking/file-system "Mocking the File System | Vitest"
[2]: https://vitest.dev/api/vi.html "Vi | Vitest"
[3]: https://nodejs.org/api/fs.html "File system | Node.js v25.3.0 Documentation"
