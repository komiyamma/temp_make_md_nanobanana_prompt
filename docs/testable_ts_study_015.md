# 第15章：interfaceは“最小の約束”にする📜✨

![testable_ts_study_015_minimal_interface.png](./picture/testable_ts_study_015_minimal_interface.png)

この章はひとことで言うと、**「境界のinterfaceを“ちいさく・目的別”にして、巨大interface地獄を避けよう」**です🧸💡
（I/O境界の分離がうまくいくかどうか、けっこうここで決まります…！😳）

---

## 1) この章でできるようになること🎯✨* 「このinterface、デカすぎない…？😵」を嗅ぎ分けられる👃

💨


* interfaceを **“必要最低限の操作だけ”** に削れる✂️
* HTTP/DBの依存を、**中心（ロジック）から見て自然な形**にできる🌱
* テストで **スタブ/フェイク** を作るのがめちゃ楽になる🧪🎀

---

## 2) そもそもinterfaceって何？（この講座の文脈）

🧠📌この講座でのinterfaceは、



* **中心（ロジック）が「外側（I/O）」にお願いする“約束”** 🤝
* つまり **「ポート（Port）」** です🚪✨（Ports & Adaptersの考え方）

ポイントはこれ👇
✅ **interfaceは“外側の都合”を表すものじゃない**
✅ **中心が「これだけできれば仕事できるよ」って言う最小セット**

---

## 3) なぜ“最小”が大事？（巨大interfaceが生む地獄）

🔥😇### 地獄①：テストがつらい（ダブルが作れない）

🧪💥interfaceが10個/20個メソッドあると、スタブ作るだけで疲れます😵‍💫
「今回使わないメソッド」まで実装させられるの、しんどい…！

### 地獄②：変更が伝染する（波及が止まらない）

🌊😱1メソッド追加しただけで
実装クラス全部・モック全部・テスト全部が壊れる…！🔨

### 地獄③：中心がI/O詳細に染まる（境界が溶ける）

🫠「HTTPのヘッダ」「SQL文字列」「ステータスコード」みたいな
**外側事情**が中心に入ってくると、分離が崩れます💔

---

## 4) “最小の約束”にするための7つのコツ✂️

🌟### コツ1：interfaceは「使う側（中心）

」が定義する🧠➡️📜中心が欲しい形で決めるのが正解✨
外側が先に「汎用HttpClient作ったよ！」ってやると、だいたいデカくなります😇

### コツ2：1ユースケース（目的）

につき、1つ作る🎯「何でもできるinterface」より、
「これをやるためのinterface」が強い💪

### コツ3：戻り値は“中心がほしい形（ドメイン型）

”にする💎JSONそのまま、HTTPレスポンスそのまま、SQL結果そのまま…は境界で止める🛑



### コツ4：メソッド数はまず1〜3個を疑う👀4個以上になったら、「分けられる？」って一回考える✂️

### コツ5：CRUD全部を生やさない（使ってないなら不要）

🚫`create/update/delete/list/getById/findBy...` を全部置くのはやりがち😵
中心が使ってる分だけでOK✨

### コツ6：「問い合わせ（Query）

」と「更新（Command）」を混ぜない🍱“読む”と“書く”が混ざると、膨らみやすいです💨
（CQSのミニ版だと思ってOK🙂）

### コツ7：名前は“技術”じゃなく“目的”で付ける🧸`HttpClient` / `DbClient` より
`AddressLookup` / `SubscriberRepository` みたいにすると自然に小さくなる✨

---

## 5) アンチパターン集👃

💨（見つけたら赤信号）### ❌ アンチ：汎用すぎるHTTP interface

```ts
export interface HttpClient {
  get(url: string, headers?: Record<string, string>): Promise<{ status: number; body: unknown }>;
  post(url: string, body: unknown): Promise<{ status: number; body: unknown }>;
  put(url: string, body: unknown): Promise<{ status: number; body: unknown }>;
  delete(url: string): Promise<{ status: number; body: unknown }>;
}
```

これ、中心が **URL/ヘッダ/ステータス** を知り始めます😇（溶ける🫠）

### ✅ こうする：目的interface（中心が欲しい形）

```ts
export interface AddressLookup {
  lookup(zip: ZipCode): Promise<Address | null>;
}

export type ZipCode = string;

export type Address = {
  prefecture: string;
  city: string;
  line1: string;
};
```

中心が欲しいのは「住所」なので、それだけ✨

---

## 6) ハンズオン①：HTTPのinterfaceを“最小化”する✂️

🌐### お題：郵便番号→住所を取って、表示文を作る🧾✨#### まずは“つらい版”（中心がI/O詳細を知ってる）

```ts
// center/usecase.ts
export async function buildShippingLabel(
  zip: string,
  http: { get: (url: string) => Promise<any> }
): Promise<string> {
  const res = await http.get(`https://example.com/api/address?zip=${zip}`);
  // resの形、中心が知っちゃってる…
  return `${res.pref}${res.city}${res.line1}`;
}
```

#### ✅ ゴール：中心は“住所が欲しい”だけ

```ts
// center/ports.ts
export interface AddressLookup {
  lookup(zip: string): Promise<Address | null>;
}
export type Address = { prefecture: string; city: string; line1: string };

// center/usecase.ts
export async function buildShippingLabel(zip: string, lookup: AddressLookup): Promise<string> {
  const addr = await lookup.lookup(zip);
  if (!addr) return "住所が見つかりませんでした🥲";
  return `${addr.prefecture}${addr.city}${addr.line1}`;
}
```

#### 外側（adapter）

がHTTPの都合を全部持つ🌐🧩

```ts
// infra/addressLookupAdapter.ts
import type { AddressLookup, Address } from "../center/ports";

export class AddressLookupByHttp implements AddressLookup {
  constructor(private readonly baseUrl: string) {}

  async lookup(zip: string): Promise<Address | null> {
    const res = await fetch(`${this.baseUrl}/api/address?zip=${encodeURIComponent(zip)}`);
    if (!res.ok) return null;

    const json = await res.json();
    // 変換は境界でやる（中心にJSONを持ち込まない）
    return {
      prefecture: String(json.pref),
      city: String(json.city),
      line1: String(json.line1),
    };
  }
}
```

---

## 7) ハンズオン②：DBのinterfaceを“最小化”する✂️

🗄️### お題：メルマガ登録（保存＆重複チェック）

📩✨#### ❌ ありがちな“デカいDB interface”

```ts
export interface DbClient {
  query<T>(sql: string, params?: unknown[]): Promise<T[]>;
  begin(): Promise<void>;
  commit(): Promise<void>;
  rollback(): Promise<void>;
  close(): Promise<void>;
  // …増える増える増える😇
}
```

中心がSQLを書き始めたら、境界が溶けます🫠

#### ✅ ゴール：中心が必要な操作だけ

```ts
// center/ports.ts
export type Subscriber = { email: string };

export interface SubscriberRepository {
  findByEmail(email: string): Promise<Subscriber | null>;
  save(sub: Subscriber): Promise<void>;
}
```

中心（ユースケース）はこうなる👇

```ts
// center/subscribeUsecase.ts
import type { SubscriberRepository, Subscriber } from "./ports";

export async function subscribe(email: string, repo: SubscriberRepository): Promise<string> {
  const existing = await repo.findByEmail(email);
  if (existing) return "すでに登録済みだよ〜🙂";

  const sub: Subscriber = { email };
  await repo.save(sub);
  return "登録できたよ！🎉";
}
```

#### テストが超ラク（フェイクRepo）

🧪🎀

```ts
import { describe, it, expect } from "vitest";
import { subscribe } from "./subscribeUsecase";
import type { SubscriberRepository, Subscriber } from "./ports";

class FakeRepo implements SubscriberRepository {
  private map = new Map<string, Subscriber>();

  async findByEmail(email: string) {
    return this.map.get(email) ?? null;
  }
  async save(sub: Subscriber) {
    this.map.set(sub.email, sub);
  }
}

describe("subscribe", () => {
  it("初回は登録できる🎉", async () => {
    const repo = new FakeRepo();
    const msg = await subscribe("a@example.com", repo);
    expect(msg).toContain("登録できた");
  });

  it("2回目は登録済み🙂", async () => {
    const repo = new FakeRepo();
    await subscribe("a@example.com", repo);
    const msg = await subscribe("a@example.com", repo);
    expect(msg).toContain("登録済み");
  });
});
```

> ここ大事💡：interfaceが小さいほど、フェイクが一瞬で書けます✍️✨
> テストの“めんどい”が消えていきます🫶

---

## 8) 仕上げチェックリスト✅🧸（interface最小化の判定）

interfaceを作ったら、これを確認👇



* [ ] **中心の言葉で命名**できてる？（Http/Dbじゃなく目的）🎯
* [ ] **メソッドは必要最低限**？（使ってないの混ざってない）✂️
* [ ] **I/O詳細（URL/SQL/Status）を漏らしてない**？🫠
* [ ] **戻り値が中心の型**になってる？（JSONそのまま卒業）💎
* [ ] **フェイクを30秒で実装**できそう？🧪⚡

---

## 9) AI（Copilot/Codex系）

を使うときの“勝ちプロンプト”🤖🎀### ✅ ケース1：interfaceを小さくしたい

```text
このユースケースが必要としている操作だけに絞って、最小のTypeScript interfaceを提案して。
条件：
- HttpClient/DbClientのような汎用インターフェースは禁止
- 目的ベースの命名にする
- メソッドは1〜3個まで
- 戻り値はドメイン型（JSONやHTTPレスポンスは禁止）
```

### ✅ ケース2：巨大interfaceを分割したい

```text
このinterfaceが肥大化しています。利用箇所ごとに責務を分けて、小さなinterfaceへ分割案を出して。
- 分割単位は「ユースケース（目的）」優先
- “読む”と“書く”は可能なら分ける
- 使われていないメソッド候補も指摘して
```

---

## 10) 2026年の“最新ミニ情報”📰✨

（この章に効くところだけ）* TypeScriptは **5.9** のリリースノートで、`import defer`（副作用の実行タイミングを遅らせる提案に対応）が入っています。**「副作用（I/O）と仲良くする」**文脈と相性いいやつです🧊✨ ([TypeScript][1])


* TypeScriptの“ネイティブ実装（TypeScript 7の流れ）”のプレビュー/進捗も継続的に共有されています（開発体験の高速化が狙い）。 ([InfoQ][2])
* テストランナーは、Vitestが **4.0** リリース（2025/10）で大きく進み、移行ガイドも整備されています🧪✨ ([Vitest][3])
* Jestは **30** がStableとして案内されています。 ([Jest][4])
* Node.jsは **v25系がCurrent**、**v24系がActive LTS** などの枝が動いていて、直近もセキュリティ更新が出ています🔐（依存更新は大事！） ([Node.js][5])

---

## 章末ミッション🎒✨

（提出物イメージ）1. 何か1つ「HTTPっぽい処理」を選ぶ🌐
2. `HttpClient` みたいな汎用interfaceをやめて、**目的interface 1個**に置き換える✂️
3. そのinterfaceで **フェイクを作ってユースケースをユニットテスト**🧪🎀
4. 「中心が知ってるI/O情報」が減ったかチェック👀✨

---

次の第16章では、ここで作った“小さいinterface”を差し替えるための道具（スタブ/モック/スパイ）を、スッキリ整理して使えるようにしていきます🧸👀🧪
もしよければ、あなたの題材（HTTP/DBが絡む処理）を1つ決め打ちして、**“巨大→最小”のビフォーアフター**を一緒に作っていこ〜！💪💕

[1]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"
[2]: https://www.infoq.com/news/2026/01/typescript-7-progress/?utm_source=chatgpt.com "Microsoft Share Update on TypeScript 7"
[3]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
[4]: https://jestjs.io/versions?utm_source=chatgpt.com "Jest Versions"
[5]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
