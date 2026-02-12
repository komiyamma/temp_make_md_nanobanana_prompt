# 第17章：Assert基礎②（オブジェクト比較）🧸

![オブジェクト比較](./picture/tdd_ts_study_017_comparison.png)

> 今日は「返ってきたオブジェクト、どう検証するのが正解？」をスッキリさせる章だよ〜🫶💕

---

## 🎯この章のゴール

* 「**参照一致**」「**深い一致**」「**部分一致**」を使い分けられるようになる✨
* テストが **壊れにくく**（でも **弱すぎない**）オブジェクト検証が書けるようになる💪

---

## 📚まず最重要：オブジェクト比較は3種類あるよ🧠

### 1) 参照一致（同じ“モノ”か？）👉 `toBe`

![017 reference vs deep](./picture/tdd_ts_study_017_reference_vs_deep.png)


* `toBe` は **同じインスタンス（参照）**かどうかを見るやつ！
* 「中身が同じ」ではなく「同一人物か？」みたいな比較ね👀
  Vitestでも `toBe` は “オブジェクトは参照一致” の用途だよ。 ([Vitest][1])

✅ 使いどころ

* キャッシュやシングルトンみたいに「同じ参照で返すべき」仕様のときだけ！

---

### 2) 深い一致（中身が同じか？）👉 `toEqual` / `toStrictEqual`

![017 strict equal](./picture/tdd_ts_study_017_strict_equal.png)


* `toEqual`：**プロパティを再帰的に比較**して “構造が同じ” を見るやつ✨ ([Vitest][1])
* `toStrictEqual`：`toEqual` より **さらに厳密**（`undefined` のキーや配列の穴、クラスの型なども見る）🧐 ([Vitest][1])

✅ 使いどころ

* 返すオブジェクトが **完全に決まってる**（=仕様として固定）とき！

---

### 3) 部分一致（“必要なとこだけ”合ってるか？）👉 `toMatchObject` / `toHaveProperty` / `objectContaining`

![017 partial match](./picture/tdd_ts_study_017_partial_match.png)


* `toMatchObject`：オブジェクトが **期待のサブセット（部分）を満たす**かを見る✨ ([Vitest][1])
* `toHaveProperty`：**特定のプロパティ**をピンポイントで検証（ネストもいける）🎯 ([Vitest][1])
* `expect.objectContaining`：部分一致の “部品” として使える（Jest互換の非対称マッチャ）🧩 ([jestjs.io][2])

✅ 使いどころ

* 返り値に `createdAt` とか `debugInfo` とか、**仕様の主役じゃない情報が混ざる**とき！
* 「大事なのはここ！」を守って、テストを壊れにくくする💞

---

## 🧭チートシート（迷ったらこれ）🧾✨

* **同じ参照を返す仕様** → `toBe`
* **返る形が完全固定** → `toEqual`
* **型や undefined まで厳密に固定** → `toStrictEqual`
* **大事な一部だけ見たい** → `toMatchObject`
* **ネストの1点だけ見たい** → `toHaveProperty`
* **部分一致を組み立てたい** → `expect.objectContaining(...)`

---

## 🧪手を動かす：同じ仕様を「完全一致」と「部分一致」で書いてみよう🧸✨

題材：プロフィール表示用の“カード”を作る関数だよ💡
ポイントは「テストが壊れやすい項目（例：createdAt）」をどう扱うか！

---

### ① 実装（まずは仕様を想像できる形にする）🛠️

* `createdAt` は外から渡す形にして、テストを安定させるよ（依存注入の超ミニ版）💕

```ts
// src/buildUserCard.ts
export type User = {
  id: string
  name: string
  birthday?: string // "2004-01-19" みたいなISO想定（無ければ年齢グループ不明）
}

export type UserCard = {
  id: string
  displayName: string
  ageGroup: 'teen' | 'twenties' | 'unknown'
  meta: {
    createdAt: string
    source: 'signup' | 'import'
  }
}

export function buildUserCard(
  user: User,
  meta: { createdAt: string; source: UserCard['meta']['source'] },
): UserCard {
  const ageGroup: UserCard['ageGroup'] = user.birthday
    ? (() => {
        const year = Number(user.birthday.slice(0, 4))
        const age = 2026 - year // ここは簡略（本当は日付計算する）
        if (age < 20) return 'teen'
        if (age < 30) return 'twenties'
        return 'unknown'
      })()
    : 'unknown'

  return {
    id: user.id,
    displayName: user.name,
    ageGroup,
    meta: {
      createdAt: meta.createdAt,
      source: meta.source,
    },
  }
}
```

---

### ② テストA：完全一致（`toEqual`）✅

「返ってくる形がこれ！」って仕様が固いときに強い✨
`toEqual` はオブジェクトを再帰的に比較してくれるよ。 ([Vitest][1])

```ts
// tests/buildUserCard.test.ts
import { describe, it, expect } from 'vitest'
import { buildUserCard } from '../src/buildUserCard'

describe('buildUserCard', () => {
  it('ユーザー情報から表示カードを組み立てる（完全一致）', () => {
    const card = buildUserCard(
      { id: 'u1', name: 'Mika', birthday: '2006-04-10' },
      { createdAt: '2026-01-19T10:00:00.000Z', source: 'signup' },
    )

    expect(card).toEqual({
      id: 'u1',
      displayName: 'Mika',
      ageGroup: 'teen',
      meta: {
        createdAt: '2026-01-19T10:00:00.000Z',
        source: 'signup',
      },
    })
  })
})
```

✅ 良いところ：仕様が明確に読める📘
⚠️ 注意：`createdAt` みたいに “本来は変動する値” を入れると壊れやすい（今回は固定入力だからOK）

---

### ③ テストB：部分一致（`toMatchObject`）🧩

「大事なのはここだけ！」にできるのが `toMatchObject`。
Vitestでも “サブセット一致” として説明されてるよ。 ([Vitest][1])

```ts
import { describe, it, expect } from 'vitest'
import { buildUserCard } from '../src/buildUserCard'

describe('buildUserCard', () => {
  it('大事な項目だけ検証する（部分一致）', () => {
    const card = buildUserCard(
      { id: 'u1', name: 'Mika', birthday: '2006-04-10' },
      { createdAt: '2026-01-19T10:00:00.000Z', source: 'signup' },
    )

    expect(card).toMatchObject({
      id: 'u1',
      displayName: 'Mika',
      ageGroup: 'teen',
      meta: {
        source: 'signup',
      },
    })
  })
})
```

✅ 良いところ：将来 `meta` に別情報が増えても壊れにくい🥰
⚠️ 注意：何でも部分一致にすると弱くなるから「主役の項目」はちゃんと入れようね✨

---

### ④ テストC：ピンポイント検証（`toHaveProperty`）🎯

ネストでもいけるし、差分も読みやすいことが多いよ〜！
Vitestの例でも、ドット記法や配列指定で深い参照ができるって載ってるよ。 ([Vitest][1])

```ts
import { describe, it, expect } from 'vitest'
import { buildUserCard } from '../src/buildUserCard'

describe('buildUserCard', () => {
  it('meta.source をピンポイントで検証する', () => {
    const card = buildUserCard(
      { id: 'u1', name: 'Mika' },
      { createdAt: '2026-01-19T10:00:00.000Z', source: 'import' },
    )

    expect(card).toHaveProperty('meta.source', 'import')
    expect(card).toHaveProperty('meta.createdAt') // 値は見ない（存在だけ）
  })
})
```

---

### ⑤（おまけ）`toStrictEqual` が刺さる瞬間🧊

`toStrictEqual` は “同じ構造でも意味が違う” を弾けるのがポイント！
クラスインスタンス vs リテラルオブジェクトの違いも見てくれるよ。 ([Vitest][1])

* 「APIのDTOは plain object だけ許す」みたいなルールを守りたいときに便利✨
* 逆に、柔軟にしたいなら `toEqual` / `toMatchObject` を選ぶのが多いよ☺️

---

## 🧠壊れないオブジェクトテストのコツ（超だいじ）💎

### ✅ “仕様の主役” だけをガッチリ固定する

![017 main vs side](./picture/tdd_ts_study_017_main_vs_side.png)


* 例：`id`, `displayName`, `ageGroup` は主役 → しっかり見る
* 例：ログ用 `debug` や `createdAt` は脇役 → 部分一致や存在チェックでOK

### ✅ 迷ったら「まず toMatchObject、必要なら強くする」

* 最初から完全一致にすると、未来の変更でテストが折れやすい😵‍💫

![017 fragile test](./picture/tdd_ts_study_017_fragile_test.png)

* ただし「壊れてほしい変更」（破壊的変更）には `toEqual` が強い💪

---

## 🤖AIの使い方（この章向けテンプレ）🪄✨

![017 ai consultant](./picture/tdd_ts_study_017_ai_consultant.png)


コピペして使ってOKだよ！

* ✅ **マッチャ選び相談**
  「この返り値オブジェクト、`toEqual` / `toMatchObject` / `toHaveProperty` のどれが適切？理由も3つで！」

* ✅ **壊れやすさ診断**
  「このテスト、将来どこが壊れやすい？“仕様の主役/脇役”で分類して！」

* ✅ **テスト名改善**
  「落ちた瞬間に原因が分かるテスト名を3案ください（Given/When/Then風で）」

---

## ✅チェックリスト（合格ライン）🎓💮

* [ ] オブジェクトに `toBe` を使うのが「参照一致」だと説明できる ([Vitest][1])
* [ ] `toEqual` と `toStrictEqual` の違いを1つ以上言える ([Vitest][1])
* [ ] “主役だけ固定” のために `toMatchObject` を使える ([Vitest][1])
* [ ] ネスト1点なら `toHaveProperty` を選べる ([Vitest][1])

---

## 🌸ミニ宿題（10〜15分）🧪✨

1. `buildUserCard` の返り値に `meta.debugId` を追加してみてね（適当な文字列でOK）
2. **完全一致テスト**と**部分一致テスト**のどっちが壊れるか確認👀
3. 「どっちが仕様として正しい壊れ方？」を一言メモ📝💕

---

必要なら次に、「同じ仕様を `objectContaining`（非対称マッチャ）で組み立てる版」も作って、部分一致の表現力をもう一段上げるよ〜🫶✨（VitestはJest互換のマッチャも提供してるよ。 ([Vitest][3])）

[1]: https://vitest.dev/api/expect.html "expect | Vitest"
[2]: https://jestjs.io/docs/expect?utm_source=chatgpt.com "Expect"
[3]: https://vitest.dev/api/expect.html?utm_source=chatgpt.com "expect"
