# 第54章：DOM/コンポーネントの最小テスト（必修）🧱

![時計の修理](./picture/tdd_ts_study_054_repair_clock.png)

## 🎯 目的

TDDって「回転数」が命だよね🌀
ここでは **“テストが遅くて回らない問題”を、原因別にサクッと潰せる** ようになるよ💪✨

---

## 📚 学ぶこと（遅さの原因はだいたい5種類）

遅い理由って、ほぼこのどれか👇😵‍💫

1. **待ち時間が入ってる**（setTimeout / retry / polling）⏳
2. **外部I/Oしてる**（ファイル・DB・ネット）🌐📁
3. **重い環境で回してる**（jsdomを全部に適用してる等）🧱
4. **準備（Arrange）が重い**（巨大データ・重いbeforeEach）🧺
5. **走らせ方がもったいない**（フィルタできてない／並列の使い方）🏃‍♀️💨

---

## 🧪 手を動かす：最短の「診断→改善」ルート🔍➡️🛠️

## ① まず「どれが遅いか」見える化する👀

**テストごとの時間が見える**出力にするのが最初の一歩✨
Vitestは `--reporter=verbose` があるよ📣 ([v2.vitest.dev][1])

```bash
npx vitest run --reporter=verbose
```

## ② “狙い撃ち”で1個だけ回す🎯

遅いテストを直す時は、全体実行より **1個だけ回して高速ループ**にするのがコツ💡

* **ファイル名で絞る**（パスに含まれる文字でフィルタ） ([Vitest][2])
* **テスト名で絞る**（`-t` / `--testNamePattern`） ([Vitest][3])
* **Vitest 3以降**は「ファイル:行番号」でも絞れる（便利！） ([Vitest][4])

例👇

```bash
## ファイル名で絞る
npx vitest run user

## テスト名で絞る（正規表現っぽく使える）
npx vitest run -t "should retry"
```

---

## 🧪 改善レシピ 1：setTimeout / retry を “待たずに” テストする⏳➡️⚡️

## 💥 よくある遅いテスト（実時間で待っちゃう）

「リトライは2回まで、待ち時間は100ms→200ms…」みたいなやつね🥲

```ts
// src/retry.ts
export async function retry<T>(
  fn: () => Promise<T>,
  { retries, delayMs }: { retries: number; delayMs: number },
): Promise<T> {
  let lastError: unknown;

  for (let i = 0; i <= retries; i++) {
    try {
      return await fn();
    } catch (e) {
      lastError = e;
      if (i === retries) break;
      await new Promise<void>((r) => setTimeout(r, delayMs * (i + 1)));
    }
  }
  throw lastError;
}
```

```ts
// tests/retry.test.ts（遅いやつ）
import { describe, it, expect, vi } from "vitest";
import { retry } from "../src/retry";

describe("retry", () => {
  it("should retry and finally succeed (SLOW)", async () => {
    let count = 0;
    const fn = vi.fn(async () => {
      count++;
      if (count < 3) throw new Error("fail");
      return "OK";
    });

    const result = await retry(fn, { retries: 2, delayMs: 200 });
    expect(result).toBe("OK");
  });
});
```

これ、**合計で 200ms + 400ms = 600ms くらい待つ**から、積み重なると地獄🐢💦

---

## ✅ 解決：Fake Timers で “時間を進める” ⏱️✨

Vitestは `vi.useFakeTimers()` でタイマーを偽装して、`vi.advanceTimersByTimeAsync()` みたいに **擬似的に時間を進められる**よ🎮
（`setTimeout / setInterval / Date` などをラップしてくれる） ([Vitest][5])

```ts
// tests/retry.test.ts（速いやつ）
import { describe, it, expect, vi, afterEach } from "vitest";
import { retry } from "../src/retry";

afterEach(() => {
  vi.useRealTimers(); // 後片付け大事🧹✨
});

describe("retry", () => {
  it("should retry and finally succeed (FAST)", async () => {
    vi.useFakeTimers(); // ⏱️ 偽タイマーON :contentReference[oaicite:5]{index=5}

    let count = 0;
    const fn = vi.fn(async () => {
      count++;
      if (count < 3) throw new Error("fail");
      return "OK";
    });

    const promise = retry(fn, { retries: 2, delayMs: 200 });

    // 200ms + 400ms 分を一気に進める（非同期タイマー対応） :contentReference[oaicite:6]{index=6}
    await vi.advanceTimersByTimeAsync(600);

    await expect(promise).resolves.toBe("OK");
    expect(fn).toHaveBeenCalledTimes(3);
  });
});
```

## 🧠 コツ（超重要）✨

* **Fake Timersは必ず戻す**（戻し忘れ＝別テストが壊れる💣）
* Promiseが絡むときは `advanceTimersByTimeAsync` が安心（“非同期でセットされたタイマー”も含められる） ([Vitest][5])
* もしFake Timers絡みで変なハングが出たら、実行プール設定（threads/forks）との相性も疑う（Vitest側も注意を書いてるよ） ([Vitest][5])

---

## 🧪 改善レシピ 2：ファイルI/Oをやめて “注入” する📁➡️🧸

## 💥 よくある遅いテスト：実ファイルを読んでる

```ts
// src/loadConfig.ts
import { readFile } from "node:fs/promises";

export async function loadConfig(path: string) {
  const json = await readFile(path, "utf-8");
  return JSON.parse(json) as { theme: string };
}
```

```ts
// tests/loadConfig.test.ts（遅くなりがち）
import { it, expect } from "vitest";
import { loadConfig } from "../src/loadConfig";

it("loadConfig reads theme", async () => {
  const cfg = await loadConfig("tests/fixtures/config.json");
  expect(cfg.theme).toBe("dark");
});
```

小規模ならOKだけど、増えると **ディスク依存が増えて遅い＆不安定**になりやすいよ🥲📁

---

## ✅ 解決：読む部分だけ差し替え可能にする（依存注入）💉✨

```ts
// src/loadConfig.ts（改善版）
export type ReadText = (path: string) => Promise<string>;

export async function loadConfig(path: string, readText: ReadText) {
  const json = await readText(path);
  return JSON.parse(json) as { theme: string };
}
```

```ts
// tests/loadConfig.test.ts（爆速）
import { it, expect, vi } from "vitest";
import { loadConfig } from "../src/loadConfig";

it("loadConfig reads theme (FAST)", async () => {
  const readText = vi.fn(async () => `{"theme":"dark"}`);
  const cfg = await loadConfig("any/path.json", readText);
  expect(cfg.theme).toBe("dark");
  expect(readText).toHaveBeenCalledTimes(1);
});
```

🎉 これで **I/Oゼロ**！爆速！安定！最高！⚡️⚡️⚡️

---

## 🧪 改善レシピ 3：jsdom を “必要なテストだけ” にする🧱➡️🌿

UIじゃないテストまで全部jsdomだと、地味に重くなりやすいよ〜😵‍💫
Vitestは環境を選べて、`happy-dom` は **jsdomより速いことが多い**って位置づけだよ（ただしAPI差はある） ([Vitest][6])

✅ ファイル単位で環境を切り替えできる👇（docblock/コメント） ([Vitest][6])

```ts
// @vitest-environment node
import { it, expect } from "vitest";

it("pure logic test", () => {
  expect(1 + 1).toBe(2);
});
```

---

## 🧪 改善レシピ 4：走らせ方で速くする（Threads / フィルタ / カバレッジ）🏃‍♀️💨

## ✅ フィルタして “関係あるテストだけ” 回す

さっきの `vitest run user` と `-t` は、最強の時短セット🎯 ([Vitest][2])

## ✅ さらに全体が重いなら `--pool=threads` を検討

Vitestはデフォルトで複数プロセス並列だけど、さらに速くしたいなら **worker_threads を使う `--pool=threads`** があるよ（相性問題が出るライブラリもあるから注意） ([Vitest][7])

```bash
npx vitest run --pool=threads
```

## ✅ カバレッジは「いつもON」にしない（計測時は切る）

カバレッジは便利だけど、速度は落ちやすい…！
必要なときだけ `vitest run --coverage` に寄せるのが無難だよ📈 ([Vitest][8])

---

## 🤖 AI の使いどころ（診断が爆速になるよ）🤖💡

## ✨プロンプト例1：遅い原因の分類

「この `--reporter=verbose` の結果で遅いテストがあります。
遅さの原因を (待ち時間 / I/O / 環境 / 準備 / 走らせ方) に分類して、最小の修正案を3つ出して」

## ✨プロンプト例2：Fake Timers 置き換え

「このテストが setTimeout 待ちで遅いです。
Vitestの `vi.useFakeTimers` と `vi.advanceTimersByTimeAsync` を使って、待たないテストに書き換えて」

（※AIが出したコードは、そのまま採用じゃなくて **“意図に合ってるか”だけは必ず確認**ね😉🧪）

---

## ✅ チェック（できたら合格）🎓💮

* ✅ 遅いテストを **`--reporter=verbose` で特定**できた ([v2.vitest.dev][1])
* ✅ **`-t` で狙い撃ち実行**して高速ループできた ([Vitest][3])
* ✅ setTimeout待ちを **Fake Timers** に置き換えて、体感で速くなった ([Vitest][5])
* ✅ I/Oを注入にして **外部ゼロのユニットテスト**にできた 🧸✨
* ✅ jsdomを必要な所だけにして、重さを減らせた ([Vitest][6])

---

## 🌸おまけ：2026年の“足元”メモ（最新確認）

「遅い＝環境のせい」もたまにあるので、ランタイムが古すぎないかは確認ポイントだよ🔧
ちなみに **Node.js 24 系が LTS としてリリースされてる**（2026-01-13のリリース情報）よ📌 ([Node.js][9])

---

次の章（第55章）は「たまに落ちる（フレーク）」を潰す手順だよ💥🧯
第54章で“速さ”を取り戻したら、次は“信頼”を取り戻そ〜！✨

[1]: https://v2.vitest.dev/guide/reporters?utm_source=chatgpt.com "Reporters | Guide"
[2]: https://vitest.dev/guide/cli?utm_source=chatgpt.com "Command Line Interface | Guide"
[3]: https://vitest.dev/config/testnamepattern?utm_source=chatgpt.com "testNamePattern | Config"
[4]: https://vitest.dev/guide/filtering?utm_source=chatgpt.com "Test Filtering | Guide"
[5]: https://vitest.dev/api/vi.html "Vi | Vitest"
[6]: https://vitest.dev/guide/environment?utm_source=chatgpt.com "Test Environment | Guide"
[7]: https://vitest.dev/guide/features?utm_source=chatgpt.com "Features | Guide"
[8]: https://vitest.dev/config/coverage?utm_source=chatgpt.com "coverage | Config"
[9]: https://nodejs.org/en/blog/release/v24.13.0?utm_source=chatgpt.com "Node.js 24.13.0 (LTS)"
