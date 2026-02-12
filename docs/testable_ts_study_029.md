# 第29章：AI拡張と上手に進める（丸投げしないコツ）🤖🎀

![testable_ts_study_029_ai_partner.png](./picture/testable_ts_study_029_ai_partner.png)

## この章のゴール🎯✨

AI（Copilot / Codex など）を**“テスタブル設計（I/O境界の分離）”の味方**にしつつ、
**境界の判断は自分で握ったまま**スピードを上げられるようになることだよ〜😊🫶

---

## 29-1. まず大事な考え方：AIは「手」🖐️

、設計は「脳」🧠💗AIが得意🥰



* テストケースの洗い出し（抜け漏れ探し）🧪🔍
* スタブ/スパイ/モックの下書き🧸
* 既存コードの読解・要約・命名案だし📚✍️
* 小さめのリファクタ案の提案（段取りを作る）🛠️🗺️
* 「I/Oが混ざってない？」みたいなレビュー👀✨

AIに丸投げしない🙅‍♀️

* **どこが境界か**（中心と外側の線引き）✂️
* 仕様の解釈（「割引って端数どうするの？」とか）📏
* 例外/エラーの扱い方針（ドメイン vs インフラ）🚨
* セキュリティ/個人情報/秘密情報の扱い🔐
* 「それっぽいけど違う」API・古い情報の採用🥲

> コツは **“AIに作らせる前に、先にルールを渡す”** だよ〜💡😊

---

## 29-2. 2026年っぽいAI機能の使い分け（知ってるだけで勝ち）

🏆✨## ① Copilot Edits：複数ファイル編集の2モード🧩

🧹* **Edit mode**：触らせるファイルを自分で選んで、提案を見ながら進める（コントロール重視）🫶


* **Agent mode**：タスクを渡すと、Copilot が自律的に編集＆必要ならコマンド提案までして進める（スピード重視）🚀
  ([GitHub Docs][1])

👉 テスタブル設計ではおすすめ運用はこれ👇

* **境界を作る/変える作業** → まずは **Edit mode**（暴れにくい）😊
* ルールが固まった後の機械作業（テスト追加、命名揃え、薄いアダプタ量産） → **Agent mode** 🚀
  ([GitHub Docs][1])

---

## ② VS Code の Agent Skills（実験機能）

：AIに“家庭教師プリセット”を渡せる📁🧠VS Code 1.108（2025年12月アップデート）あたりで、**Agent Skills（実験）**が入っていて、
「フォルダに置いた指示・スクリプト・資料」を Copilot が必要に応じて読み込める、みたいな方向が進んでるよ〜📦✨（設定キー `chat.useAgentSkills`）
([Visual Studio Code][2])

これ、テスタブル設計と相性バツグンで👇

* 「中心は純粋関数だけ！」🍰
* 「中心では Date/fetch/env/DB/FS を触らない！」🚫
* 「I/Oは adapter に押し出して interface 越し！」🔌
  …みたいな **プロジェクトの掟** を“スキル”として置けるのが強い💪💖
  ([Visual Studio Code][2])

---

## ③ Copilot CLI（public preview）

：ターミナルからAIに頼める🧑‍💻✨Copilot CLI は **ターミナルで自然言語→提案**ができるやつで、プレビュー扱いだよ〜🧪
([GitHub Docs][1])

おすすめは👇

* 「このログ出た、原因候補3つ出して」🕵️‍♀️
* 「このコマンドの意味ざっくり説明して」📖
* 「テスト失敗の読み解き」🧪

逆に、いきなり「全部直して」は危険⚠️（I/O境界ごと壊す事故あるある🥲）

---

## ④ OpenAI Codex IDE extension：IDE横で“エージェント”できる🧠🤖Codex の VS Code 拡張は、IDEの横で **読んで・直して・実行まで**を支援する方向で、クラウドに作業を委任する流れもあるよ〜☁️

✨
([OpenAI Developers][3])

注意点として、**Windows対応は experimental**で、より良い体験には **WSLワークスペース**推奨って書かれてるよ🪟⚠️
([OpenAI Developers][3])

---

## 29-3. テスタブル設計を守る「AI利用3ルール」🧪🛡

️✨## ルールA：先に“境界ルール”を宣言する📣AIは放っておくと、平気で中心に `Date.now()` とか `fetch()` とか混ぜるよ〜😇💥
だから最初のプロンプトでこれを言う👇

* 中心（ロジック）は **純粋関数**
* I/O は **adapter**
* 境界は **interface**
* テストは中心はユニット、外側は最小限の結合🧪

## ルールB：いきなりコードを書かせず「設計→テスト→実装」🗺

️🧪🛠️順番が逆だと、AIが「動けばOK」をやりがち🥲
まずは

1. 境界図（どれがI/O？）
2. interface案
3. テストケース
4. 実装
   の順が安定💕

## ルールC：AIの変更は“差分レビュー前提”👀* 余計な依存追加してない？📦


* 中心にI/O混ざってない？🚫
* テストが実ネットワーク叩いてない？🌐💥
* ランダム・時刻が固定化されてる？⏰🎲

ここは人間の仕事💪😊

---

## 29-4. すぐ使える✨

「良いプロンプト」テンプレ集📝🤖## ① テストケース洗い出し（最強に便利）

🧪🔍

```text
あなたはテスト設計の相棒です🧪
次の純粋関数仕様に対して、AAA形式でテストケースを列挙してね。
条件：
- I/Oは一切ない前提
- 正常系/境界値/異常系をバランスよく
- 「何を確認するか」を日本語で1行説明付き

仕様：
- 入力：items(価格), coupon(割引), taxRate
- 出力：小計/税/合計
- 端数処理：税は四捨五入
- couponは小計を下回らない（下回るなら0）
```

👉 返答が「テスト名だけ」なら追加で
「期待値の数字も例で出して」って言うと超よい😊💕

---

## ② interface とテストダブル（スタブ/スパイ）

を作らせる🧸✨

```text
次のinterfaceに対して、テスト用の
- Stub（固定値を返す）
- Spy（呼び出し記録を取る）
をTypeScriptで作ってください。
制約：
- 外部ライブラリ追加なし
- できるだけ小さく
- 使い方の例も1つ

interface:
export interface Clock { now(): Date }
export interface Logger { info(msg: string, meta?: Record<string, unknown>): void }
```

---

## ③ I/O境界分離リファクタ（段取り→小さいPR）

✂️🧹

```text
次のコードを「中心（純粋ロジック）」と「外側（I/O）」に分離したいです。
いきなり全修正せず、まずは段取りを提案してね。

出力フォーマット：
1) 境界の候補（I/O一覧）
2) 新しく作るinterface案（最小）
3) まず切り出す純粋関数のシグネチャ案
4) 1PR目でやる変更（小さく）
5) 2PR目でやる変更

コード：
（ここに対象ファイルを貼る）
```

ここでちゃんと段取りが出てきたら、次に
「じゃあ1PR目の差分だけコードで」って進めると安全🫶✨

---

## ④ 境界違反レビュー（AIに“監視役”をやらせる）

👀🚨

```text
あなたは「I/O境界の分離」レビュワーです🕵️‍♀️
次の差分を見て、中心にI/Oが混ざっていないかチェックして。
観点：
- Date / Random / fetch / fs / env / DB / console など
- interface越しになってるか
- テストが不安定（時刻や乱数が固定されてない）になってないか

差分：
（diffを貼る）
```

---

## 29-5. ダメ回答の見抜き方（赤信号🚥あるある）

😵‍💫AIの提案がこうだったら黄色信号⚠️



* 「中心の関数の中で `fetch()` して計算して保存してログ出す」🌀
* 「テストで実API叩いてます」🌐💥
* 「`Date.now()` をそのまま使って期待値が日によって変わる」⏰😇
* 「便利だから新ライブラリ入れました！（大量）」📦📦📦
* 「interfaceが巨大（Repositoryに100メソッド）」📜😱
* 「例外がなんでも `throw new Error()`」🚨🧯

こういうときは、AIに言い直す👇

* 「中心は純粋関数、I/O禁止」
* 「境界は最小interface」
* 「テストは安定（時刻/乱数固定）」
  って“掟”を再掲すると戻りやすいよ😊✨

---

## 29-6. ハンズオン：AIと一緒に“境界を守る”練習しよ🎮🧪💗## お題：クーポン適用つき合計計算🛒🎟️

最初はわざと「ぐちゃぐちゃ版」からスタート😈



### ぐちゃぐちゃ版（例）

```ts
export async function checkout(userId: string, items: { price: number }[]) {
  const couponApi = process.env.COUPON_API!;
  const res = await fetch(`${couponApi}/coupon?user=${userId}`);
  const coupon = await res.json() as { amountOff: number };

  const subtotal = items.reduce((a, x) => a + x.price, 0);
  const discounted = Math.max(0, subtotal - coupon.amountOff);

  const taxRate = Number(process.env.TAX_RATE ?? "0.1");
  const tax = Math.round(discounted * taxRate);

  console.log("checkout at", new Date().toISOString());
  return { subtotal, tax, total: discounted + tax };
}
```

👀 どこがI/O？

* `process.env`（設定）⚙️
* `fetch`（HTTP）🌐
* `console.log`（ログ）📝
* `new Date()`（時刻）⏰

---

## ステップ1：AIに“境界図”を作らせる🗺

️✨プロンプト例👇



```text
この関数のI/Oを列挙して、中心（純粋ロジック）に残すべきものと
外側（adapter）へ出すべきものを分けて。
最後に、中心関数のシグネチャ案を1つ出してね。
```

✅ ここで欲しい答えは

* 中心：合計計算、割引、税計算（純粋）🍰
* 外側：クーポン取得、設定読み、ログ、時刻⛩️（外の世界）

---

## ステップ2：最小interfaceを作る（ここが勝負✂️

）こんな感じに“薄く”するのが理想だよ〜😊



```ts
export interface CouponClient {
  getAmountOff(userId: string): Promise<number>;
}

export interface Config {
  taxRate: number;
}

export interface Clock {
  now(): Date;
}

export interface Logger {
  info(msg: string, meta?: Record<string, unknown>): void;
}
```

---

## ステップ3：中心（純粋関数）

を作って、先にテスト🧪🎉中心はI/Oゼロでいこ💖



```ts
export type CheckoutResult = { subtotal: number; tax: number; total: number };

export function calcCheckout(
  items: { price: number }[],
  amountOff: number,
  taxRate: number
): CheckoutResult {
  const subtotal = items.reduce((a, x) => a + x.price, 0);
  const discounted = Math.max(0, subtotal - Math.max(0, amountOff));
  const tax = Math.round(discounted * taxRate);
  return { subtotal, tax, total: discounted + tax };
}
```

ここでAIに「テストケース列挙」を投げると速いよ🧪💨（テンプレ①）

---

## ステップ4：外側で組み立て（I/Oはここだけ）

🔌🏗️

```ts
export function makeCheckout(deps: {
  couponClient: CouponClient;
  config: Config;
  clock: Clock;
  logger: Logger;
}) {
  return async function checkout(userId: string, items: { price: number }[]) {
    const amountOff = await deps.couponClient.getAmountOff(userId);

    const result = calcCheckout(items, amountOff, deps.config.taxRate);

    deps.logger.info("checkout", {
      at: deps.clock.now().toISOString(),
      userId,
      subtotal: result.subtotal,
      total: result.total,
    });

    return result;
  };
}
```

こうなると、中心はテストが超ラク🥹✨
外側は最小限の結合テストでOK👍

---

## 29-7. さらに一歩：AIに“掟”を覚えさせる📁🧠（Agent Skills 的発想）

VS Code の Agent Skills は「AIに読ませる指示フォルダ」みたいな方向で、Copilot にドメイン知識や手順を渡せる設計が進んでるよ〜（実験）📦✨
([Visual Studio Code][2])

例えば「skills/iosplit/README」にこんな掟を書いておくイメージ👇

* 中心は純粋関数
* I/Oはadapter
* interfaceは最小
* テストは AAA
* Clock/Random/Logger/Config は注入

こういう“プロジェクト憲法”があると、Agent mode を使っても事故りにくくなる😊🫶
（Copilot Edits の agent mode 自体も「自律で編集してタスク完了まで反復する」方向だよ）([GitHub Docs][1])

---

## 29-8. まとめ（今日の持ち帰り🍀

✨）* AIは **テストケース列挙🧪** と **下書き📝** と **レビュー👀** に最強


* でも **境界の判断✂️** は自分で握る！
* 進め方は **設計→テスト→実装** が安定🗺️🧪🛠️
* Agent系（Copilot Edits / Agent Skills / Codex）を使うほど、先に“掟”を渡すのが大事📜💗
* WindowsでCodex拡張は experimental なので、使うなら注意してね（WSL推奨）🪟⚠️ ([OpenAI Developers][3])

---

* [The Verge](https://www.theverge.com/news/669339/github-ai-coding-agent-fix-bugs?utm_source=chatgpt.com)
* [IT Pro](https://www.itpro.com/software/development/github-copilot-ai-model-deprecation-openai-anthropic-google?utm_source=chatgpt.com)
* [Windows Central](https://www.windowscentral.com/artificial-intelligence/microsoft-adds-googles-gemini-2-5-pro-to-github-copilot-but-only-if-you-pay?utm_source=chatgpt.com)

[1]: https://docs.github.com/en/copilot/get-started/features "GitHub Copilot features - GitHub Docs"
[2]: https://code.visualstudio.com/updates?utm_source=chatgpt.com "December 2025 (version 1.108)"
[3]: https://developers.openai.com/codex/ide/ "Codex IDE extension"
