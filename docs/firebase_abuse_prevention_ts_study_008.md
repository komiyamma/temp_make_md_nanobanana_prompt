# 第08章：Firestoreを守る（RulesとApp Checkの役割分担）🗃️🛡️

この章は「Firestoreを安心して公開できる状態」にする回です🙂✨
ポイントはシンプルで、**守りは2枚重ね**にすること！

* **Firestore Rules**：*「誰が・何を・どこまで」できる？*（権限＆データの形チェック）
* **App Check**：*「本物のアプリから来た？」*（不正クライアント遮断）

App Checkは“正規アプリ証明”で、Firebaseのリソース乱用を減らすための仕組みです。([Firebase][1])
さらに、**Cloud Firestore は App Check の強制（enforcement）対象に含まれます**。([Firebase][2])

---

## 1) まず、何が怖いの？😱（Firestoreが狙われるパターン）

![Firestore Threats](./picture/firebase_abuse_prevention_ts_study_008_02_threats.png)

Firestoreは「読み書きが簡単」だからこそ、悪意ある人にも“叩きやすい”です🥶

* 🔓 **大量読み取り**：非公開メモやユーザーデータが抜かれる
* 🧨 **大量書き込み**：スパム投稿・ストレージ肥大・課金増
* 🧪 **不正な形のデータ投入**：アプリ側が想定しない型で壊される（例：文字列のはずが巨大配列）
* 🤖 **AI連携の踏み台**：Firestoreの内容をAI整形に流してると、連打されてコストが跳ねる（AIは特に危険⚠️）
  ※Firebase AI Logic は App Check 連携で“勝手に呼ばれにくく”できます。([Firebase][3])

---

## 2) 役割分担を「一言で」覚える🧠✨

![Double Defense Layers](./picture/firebase_abuse_prevention_ts_study_008_01_two_shields.png)

| 守り                 | 何を確認する？           | 例                           | 破られると…     |
| ------------------ | ----------------- | --------------------------- | ---------- |
| Firestore Rules 🧾 | ユーザー（認証）と権限、データの形 | 「自分のメモだけ読める」「titleは100文字まで」 | 情報漏洩・データ破壊 |
| App Check 🧿       | その通信が“正規アプリ由来”か   | 「ブラウザ拡張や改造クライアントを弾く」        | 乱用・連打・Bot  |

**Rulesは“中身のルール”**、**App Checkは“入口の身分証”**って感じです🙂👍

---

## 手を動かす：Firestoreアクセスを1画面に集約して「差」を見える化🧪👀

ここからは、ミニアプリの「メモ」機能を題材にします📝✨
狙い：**App Check をON/OFF（または強制ON前後）した時の挙動差**が、すぐ分かるようにする！

---

## Step A：Firestoreアクセスを「窓口ファイル」に寄せる📦

![Centralized Access](./picture/firebase_abuse_prevention_ts_study_008_03_repo_pattern.png)

React側のどこからでも直接Firestoreを叩くと、後で守りを入れるのが地獄になります😇
なので、**Firestore操作は1ファイルに寄せます**（あとで点検もしやすい！）

## 1) Firestore窓口（例：src/lib/memoRepo.ts）

```ts
import { getFirestore, collection, addDoc, query, orderBy, limit, getDocs, serverTimestamp } from "firebase/firestore";
import type { FirebaseApp } from "firebase/app";

export type Memo = {
  id: string;
  uid: string;
  title: string;
  body: string;
  createdAt?: unknown;
};

export function createMemoRepo(app: FirebaseApp) {
  const db = getFirestore(app);
  const col = collection(db, "memos");

  return {
    async addMemo(uid: string, title: string, body: string) {
      // ここで「大きすぎる投稿」などを先に弾くのも大事（UX的に優しい🙂）
      if (title.length > 100) throw new Error("titleは100文字までだよ🙂");
      if (body.length > 2000) throw new Error("bodyは2000文字までだよ🙂");

      const docRef = await addDoc(col, {
        uid,
        title,
        body,
        createdAt: serverTimestamp(),
      });

      return docRef.id;
    },

    async listLatest(limitCount = 20): Promise<Memo[]> {
      const q = query(col, orderBy("createdAt", "desc"), limit(limitCount));
      const snap = await getDocs(q);

      return snap.docs.map((d) => ({
        id: d.id,
        ...(d.data() as Omit<Memo, "id">),
      }));
    },
  };
}
```

> 💡ポイント
>
> * “どこでFirestore触ってるか”が一瞬で分かる
> * App Checkで詰まった時も、エラーの出どころが追いやすい👀

---

## Step B：「守り実験用」1画面を作る🧪🖥️

![Security Lab UI](./picture/firebase_abuse_prevention_ts_study_008_04_lab_ui.png)

例：SecurityLab というページを作って、
「読む」「書く」をボタンで実行できるようにします🙂

```tsx
import { useMemo, useState } from "react";
import type { FirebaseApp } from "firebase/app";
import { createMemoRepo, Memo } from "../lib/memoRepo";

// 例：ログイン済み前提のUID（本当はAuthから取る）
const DEMO_UID = "demo-uid";

export function SecurityLab({ app }: { app: FirebaseApp }) {
  const repo = useMemo(() => createMemoRepo(app), [app]);
  const [items, setItems] = useState<Memo[]>([]);
  const [msg, setMsg] = useState<string>("");

  async function onLoad() {
    setMsg("読み込み中…👀");
    try {
      const list = await repo.listLatest(20);
      setItems(list);
      setMsg(`OK！ ${list.length} 件読み込んだよ✅`);
    } catch (e: any) {
      setMsg(renderNiceError(e));
    }
  }

  async function onAdd() {
    setMsg("追加中…✍️");
    try {
      const id = await repo.addMemo(DEMO_UID, "テスト", "Firestore守りの実験中🙂");
      setMsg(`追加OK！ id=${id} ✅`);
      await onLoad();
    } catch (e: any) {
      setMsg(renderNiceError(e));
    }
  }

  return (
    <div style={{ padding: 16 }}>
      <h2>Security Lab 🧪🛡️</h2>

      <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
        <button onClick={onLoad}>読む（最新）📥</button>
        <button onClick={onAdd}>書く（追加）✍️</button>
      </div>

      <div style={{ marginBottom: 12 }}>{msg}</div>

      <ul>
        {items.map((m) => (
          <li key={m.id}>
            <b>{m.title}</b> / uid={m.uid}
          </li>
        ))}
      </ul>
    </div>
  );
}

function renderNiceError(e: any) {
  const code = e?.code ?? "";
  const message = e?.message ?? String(e);

  // だいたいここに「permission-denied」系が来る
  if (code.includes("permission-denied") || message.includes("permission")) {
    return "アクセスできなかったよ😢（守りが効いてる可能性あり）→ Rules と App Check を確認しよう🛡️";
  }
  return `エラー😇：${message}`;
}
```

---

## 3) Firestore Rules を書く🧾（“誰が何できる”を固定する）

![Rules Logic](./picture/firebase_abuse_prevention_ts_study_008_05_rules_logic.png)

FirestoreのRulesは「サーバー側で強制されるルール」です。
まずは基本の考え方（認証・データ検証）をここで固めます🙂
Rulesの入門＆シミュレーターの話は公式が分かりやすいです。([Firebase][4])
条件の書き方（request.auth や request.resource.data など）も公式が整理してくれてます。([Firebase][5])

## 例：memos コレクションは「本人のメモだけ」読み書きOKにする🔐

```rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    match /memos/{memoId} {

      // ✅ 認証必須（ログインしてない人はNG）
      function signedIn() {
        return request.auth != null;
      }

      // ✅ 作成データの最低限チェック
      function validMemoCreate() {
        return request.resource.data.keys().hasOnly(['uid','title','body','createdAt'])
          && request.resource.data.uid == request.auth.uid
          && request.resource.data.title is string
          && request.resource.data.body is string
          && request.resource.data.title.size() <= 100
          && request.resource.data.body.size() <= 2000;
      }

      // ✅ 読み：自分のメモだけ
      allow get, list: if signedIn() && resource.data.uid == request.auth.uid;

      // ✅ 作成：自分のuidで、形もOKなら許可
      allow create: if signedIn() && validMemoCreate();

      // ✅ 更新・削除：今回は一旦禁止（安全側🙂）
      allow update, delete: if false;
    }
  }
}
```

> 😊ここ、超大事！
>
> * Rulesは「**ユーザー**が正しいか」「**データの形**が正しいか」を守る
> * App Checkは「**アプリ**が正しいか」を守る
>   だから両方いるんです🧿🧾✨

---

## 4) App Check を Firestore に “強制ON” する🧿🔥（ここが本番）

**App Check enforcement を有効化すると、Cloud Firestore への未検証リクエストは拒否されます**。([Firebase][2])

## 手順（コンソール）

1. Firebase Console → App Check を開く
2. **Cloud Firestore** のメトリクス行を展開
3. **Enforce（強制）** を押す（確認ダイアログOK）([Firebase][2])

> 👀注意
> いきなり強制ONにすると、設定漏れがあるアプリは普通に死にます😇
> 第7章でやった「メトリクス監視」が効いてきます👍

---

## 5) 差が出る瞬間を観察しよう👀🧪（この章のゴール）

## ✅ パターン1：正規アプリ（App Check有効）→ 通る

* 「読む」「書く」が成功 ✅

## ❌ パターン2：App Checkが付いてない状態 → 落ちる

* 同じ画面で「読む」「書く」を押すと、エラー表示 😢
  （多くは permission-denied 系に見えるはず）

App CheckのWeb導入は、reCAPTCHA v3 などのプロバイダで初期化します。([Firebase][6])
ここが正しく入っていないと、Firestore強制ON後に詰みます😇

---

## 6) “サーバー側ライブラリで叩く”と、Rulesの守りをすり抜ける話（超重要）🚨

![Admin SDK Bypass](./picture/firebase_abuse_prevention_ts_study_008_06_bypass.png)

Firestoreには「サーバー用クライアント（Admin SDK / server client libraries）」があって、
それらは **Security Rules をバイパス**します。([Firebase][7])

つまり…

* ✅ **クライアント（Web/モバイル）**：Rules + App Check で守る
* ✅ **サーバー（Functions/バックエンド）**：IAMやサーバー側の設計で守る（別物）

この章の「守りの完成」は、まず **クライアントの入口（App Check）＋中身（Rules）** を固めるイメージです🙂🛡️

---

## 7) AIも絡めた“現実的な設計”🤖💸

![AI Cost Control](./picture/firebase_abuse_prevention_ts_study_008_07_ai_cost.png)

「メモ＋AI整形」って、実は**悪用された時の課金リスクが強い**です😱
だから、AIは最初から守り前提でいくのが正解！

* Firebase AI Logic は App Check と統合して、未検証クライアントを弾けます。([Firebase][3])
* さらにデフォルトのレート制限（例：ユーザーごとのRPM）など、“使いすぎ防止”の考え方も用意されています。([Firebase][8])

> ✅おすすめの順番
>
> 1. Firestoreを Rules + App Check で守る
> 2. AI整形ボタンは「App Check + レート制御」で段階解放
> 3. コストとUXを見ながら調整🎛️

---

## 8) AIエージェントで爆速チェック（Antigravity / Gemini CLI）🚀🤖

**Google Antigravity** は “Mission Control” 的にエージェントが計画・実装・Web調査までやる思想の開発環境として紹介されています。([Google Codelabs][9])
**Gemini CLI** はターミナル統合のオープンソースAIエージェントとして案内されています。([Google Cloud][10])

ここでの使いどころは「人間がミスりやすい点検」です🔎✨

## Antigravity（例：ミッション案）

* ✅「Firestoreアクセス箇所を列挙して、repo以外から直接触ってるコードがないか探して」
* ✅「App Check初期化より先にFirestoreが呼ばれてないかチェックして」
* ✅「Rulesの設計意図をコメントにまとめて、将来壊れにくくして」

## Gemini CLI（例：投げる質問）

* 「このリポジトリでFirestoreを呼んでる箇所を全部リストアップして。repo経由じゃないものは危険として理由も添えて」
* 「このRules、抜け道ない？ ‘他人のメモが読める/書ける’ 可能性を探して」

> 🧠コツ
> AIの提案は速いけど、**最終判断は人間**でOKです🙂👍

---

## ミニ課題（10〜20分）📝🔥

## お題：「Rules と App Check の役割分担」を“具体例”で書く✍️

次の2つを、各2〜3行でOKなので書いてください🙂

1. **Rules**が守ってくれる例（例：他人のメモが読めない、title長すぎ拒否）
2. **App Check**が守ってくれる例（例：改造クライアントの連打、Botの自動書き込み）

---

## チェック✅（この章を終えた判定）

* ✅ 「Rules＝誰が何できる」「App Check＝正規アプリか」を**例つきで説明できる**
* ✅ Firestore操作が“窓口ファイル”に集約されている📦
* ✅ Firestore強制ONで、未検証が落ちるのを確認できた👀([Firebase][2])
* ✅ Rulesで「本人だけ読める」「形が変なら拒否」が入っている🧾([Firebase][4])

---

## よくある詰まりポイント😇（先に回避！）

* 🧨 **強制ONしたら全部落ちた**
  → たいてい「App Check初期化漏れ」「サイトキー違い」「ローカルでの扱い」あたりが原因です。Webの導入手順（reCAPTCHA v3 / Enterprise）をもう一度確認すると直りやすいです。([Firebase][6])
* 🧩 **permission-denied が分からない**
  → Rulesで落ちてるのか、App Check強制で落ちてるのか、切り分けが大事。まずは「Rulesシミュレーター」でRules側を確実にOKにしてから、App Check強制へ進むと迷いにくいです🙂([Firebase][4])

---

次の第9章は **Storage（画像アップロード）** を守ります📷🛡️
ここがまた「狙われやすさMAX」なので、Firestoreで作った守りの考え方がそのまま活きますよ🙂🔥

[1]: https://firebase.google.com/docs/app-check?utm_source=chatgpt.com "Firebase App Check - Google"
[2]: https://firebase.google.com/docs/app-check/enable-enforcement?utm_source=chatgpt.com "Enable App Check enforcement - Firebase - Google"
[3]: https://firebase.google.com/docs/ai-logic/app-check?utm_source=chatgpt.com "Implement Firebase App Check to protect APIs from ... - Google"
[4]: https://firebase.google.com/docs/firestore/security/get-started?utm_source=chatgpt.com "Get started with Cloud Firestore Security Rules - Firebase"
[5]: https://firebase.google.com/docs/firestore/security/rules-conditions?utm_source=chatgpt.com "Writing conditions for Cloud Firestore Security Rules - Firebase"
[6]: https://firebase.google.com/docs/app-check/web/recaptcha-provider?utm_source=chatgpt.com "Get started using App Check with reCAPTCHA v3 in web apps"
[7]: https://firebase.google.com/docs/firestore/security/insecure-rules?utm_source=chatgpt.com "Fix insecure rules | Firestore - Firebase"
[8]: https://firebase.google.com/docs/ai-logic/quotas?utm_source=chatgpt.com "Rate limits and quotas | Firebase AI Logic - Google"
[9]: https://codelabs.developers.google.com/getting-started-google-antigravity?utm_source=chatgpt.com "Getting Started with Google Antigravity"
[10]: https://cloud.google.com/blog/ja/topics/developers-practitioners/introducing-gemini-cli?utm_source=chatgpt.com "Gemini CLI : オープンソース AI エージェント"
