# 第12章：Firestore一覧を“管理画面の表”で出す 🗃️📋✨

この章は「**管理画面っぽさ**」が一気に出る回です😆
やることはシンプル👇

* Firestoreから **ユーザー一覧を取得** 📥
* Reactで **テーブル表示** 🧱
* **並び替え（新しい順）** を入れる 🔃
* `loading / error / data` の3点セットも忘れない💡

---

## 1) まず “Firestoreの形” をイメージしよう 🧠🧩

Firestoreは **ドキュメント** が **コレクション** に入ってる感じです📦
（SQLのテーブル/行とは考え方が違うよ〜）🗂️ ([Firebase][1])

今回の例はこんな感じ👇

* コレクション: `users`
* ドキュメント: `users/{userId}`（自動IDでもOK）
* フィールド例:

  * `displayName`（表示名）
  * `role`（権限: `"admin" | "editor" | "viewer"`）
  * `updatedAt`（更新日時）
  * `createdAt`（作成日時）

ポイント🎯
**並び替えで使うフィールド（今回なら `updatedAt`）は、全ドキュメントに必ず入れる**のが超大事です！
`orderBy()` は「そのフィールドが存在するドキュメントだけ」を対象にする挙動があるため、無いと一覧から消えます😇 ([Firebase][2])

---

## 2) Consoleでサンプルデータを入れる 🧪🧑‍💼

最初はUIづくりが目的なので、Consoleで手で数件作るのが早いです⚡

1. Firestore Database を開く
2. `users` コレクションを作る
3. 3〜5件、ドキュメントを追加
4. `updatedAt` は「今の時刻」でOK（後で“サーバー時刻で統一”に進化させる👌）

---

## 3) npmの Firebase SDK を入れておく（念のため確認）📦✅

Web/React側は `firebase` パッケージを使います。npm上の最新は **12.9.0**（2026-02-05時点）になってます。 ([npmjs.com][3])

PowerShell例👇

```powershell
npm i firebase
```

---

## 4) “一覧取得” は getDocs + query が基本 📥✨

Firestoreの取得方法は大きく3つ（1回取得 / リアルタイム監視 / バンドル）があります。
この章は「**1回取得**」でいきます🙂 ([Firebase][4])

## 4-1) 型を作る（まずはゆるめでOK）🧾

`src/types/user.ts`

```ts
import { Timestamp } from "firebase/firestore";

export type UserRole = "admin" | "editor" | "viewer";

export type UserDoc = {
  displayName: string;
  role: UserRole;
  updatedAt: Timestamp; // 並び替えで使うので必須にしちゃう
  createdAt?: Timestamp;
};

export type UserRow = {
  id: string;
  displayName: string;
  role: UserRole;
  updatedAt: Date; // UI用に Date に変換して持つ
};
```

> `Timestamp` はFirestoreの日時型です（あとで `.toDate()` で `Date` にできます）🕒 ([Firebase][5])

---

## 4-2) 取得サービスを書く（servicesに寄せる）🧰

`src/services/users.ts`

```ts
import {
  collection,
  getDocs,
  limit,
  orderBy,
  query,
} from "firebase/firestore";
import { db } from "../firebase"; // 第10章で作ったやつ想定
import type { UserDoc, UserRow } from "../types/user";

const USERS_COL = "users";

export async function fetchUsersNewestFirst(pageSize = 20): Promise<UserRow[]> {
  // 新しい順に並べて、最大 pageSize 件だけ取る
  // orderBy + limit は公式の基本パターン👍
  const q = query(
    collection(db, USERS_COL),
    orderBy("updatedAt", "desc"),
    limit(pageSize)
  );

  const snap = await getDocs(q);

  return snap.docs.map((d) => {
    const data = d.data() as UserDoc;

    return {
      id: d.id,
      displayName: data.displayName ?? "(no name)",
      role: data.role ?? "viewer",
      updatedAt: data.updatedAt.toDate(),
    };
  });
}
```

ここで使ってる `orderBy()` と `limit()` は公式で推奨されてる基本の組み合わせです📚 ([Firebase][2])

---

## 5) React側：useUsersフックで “3点セット” を回す 🔁😵‍💫✨

`src/hooks/useUsers.ts`

```ts
import { useCallback, useEffect, useState } from "react";
import type { UserRow } from "../types/user";
import { fetchUsersNewestFirst } from "../services/users";

export function useUsers(pageSize = 20) {
  const [data, setData] = useState<UserRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const rows = await fetchUsersNewestFirst(pageSize);
      setData(rows);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Unknown error";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [pageSize]);

  useEffect(() => {
    void reload();
  }, [reload]);

  return { data, loading, error, reload };
}
```

---

## 6) UI：管理画面っぽいテーブルを作る 🧱📊✨

`src/components/UsersTable.tsx`

```tsx
import type { UserRow } from "../types/user";

type Props = {
  rows: UserRow[];
  onRowClick?: (id: string) => void;
};

function formatDate(d: Date) {
  return d.toLocaleString("ja-JP");
}

export function UsersTable({ rows, onRowClick }: Props) {
  return (
    <div className="rounded-xl border bg-white shadow-sm overflow-hidden">
      <div className="px-4 py-3 border-b flex items-center justify-between">
        <h2 className="font-bold">Users</h2>
        <span className="text-sm text-gray-500">{rows.length}件</span>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-[720px] w-full text-sm">
          <thead className="bg-gray-50 text-gray-600">
            <tr>
              <th className="text-left px-4 py-3">名前</th>
              <th className="text-left px-4 py-3">権限</th>
              <th className="text-left px-4 py-3">更新日</th>
            </tr>
          </thead>

          <tbody>
            {rows.map((r) => (
              <tr
                key={r.id}
                className="border-t hover:bg-gray-50 cursor-pointer"
                onClick={() => onRowClick?.(r.id)}
              >
                <td className="px-4 py-3 font-medium">{r.displayName}</td>
                <td className="px-4 py-3">
                  <span className="inline-flex items-center rounded-full border px-2 py-0.5">
                    {r.role}
                  </span>
                </td>
                <td className="px-4 py-3 text-gray-600">{formatDate(r.updatedAt)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {rows.length === 0 && (
        <div className="p-6 text-center text-gray-500">
          0件です 🙃（データを追加すると表示されます）
        </div>
      )}
    </div>
  );
}
```

---

## 7) ページ側で合体！🧩🚀

`src/pages/UsersPage.tsx`（ルーティングは第4章前提のイメージ）

```tsx
import { useNavigate } from "react-router-dom";
import { UsersTable } from "../components/UsersTable";
import { useUsers } from "../hooks/useUsers";

export function UsersPage() {
  const nav = useNavigate();
  const { data, loading, error, reload } = useUsers(20);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">ユーザー一覧</h1>
        <button
          className="rounded-lg border px-3 py-2 text-sm hover:bg-gray-50"
          onClick={() => void reload()}
        >
          再読み込み 🔄
        </button>
      </div>

      {loading && <div className="text-gray-500">読み込み中… ⏳</div>}
      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-red-700">
          取得に失敗 😭：{error}
        </div>
      )}

      {!loading && !error && (
        <UsersTable
          rows={data}
          onRowClick={(id) => nav(`/users/${id}`)} // 第13章で詳細へ
        />
      )}
    </div>
  );
}
```

---

## 8) 並び替え（新しい順）の“注意点”⚠️🧯

## ✅ orderBy したフィールドが無いと “出てこない”

さっき触れた通り、`orderBy("updatedAt")` は `updatedAt` を持たないドキュメントが結果に入らないことがあります😇 ([Firebase][2])
だから **`updatedAt` を必須運用**にしちゃうのが一番ラクです👍

---

## 9) よくある詰まりポイント（ここ超大事）🧱💥

## 9-1) 「The query requires an index」って怒られた😵

複数条件（例：`where + orderBy`）を組むと **複合インデックス** が必要になることがあります📌
その時はエラーに「作成リンク」が出るので、それを踏んで作るのが基本です🛠️ ([Firebase][6])

## 9-2) Permission denied（権限エラー）🔒

Rulesが原因のことが多いです。Rulesは“最初ゆるい→あとで事故る”があるので、危ないパターンも早めに知っておくと安心です😇 ([Firebase][7])

---

## 10) ミニ課題 🎯🔥（管理画面っぽさUP）

## ミニ課題A：並び替えボタンを付ける 🔃

* 「新しい順 / 古い順」をボタンで切り替え
* `orderBy("updatedAt", "desc" | "asc")` を切り替えるだけでOK👌 ([Firebase][2])

## ミニ課題B：roleフィルタを付ける 🧑‍⚖️

* `role === "admin"` だけ表示、みたいなフィルタ
* `where("role","==","admin")` を組む（※インデックスが必要になる場合あり）🧯 ([Firebase][6])

---

## 11) チェック✅（ここまでできたら勝ち！🏆）

* [ ] テーブルで `名前 / 権限 / 更新日` が出た 🧾
* [ ] 0件でも崩れず「0件です」が出る 🙃
* [ ] `loading / error / data` が揃ってる 🔁
* [ ] `updatedAt` が全ドキュメントに入っていて、並び替えが安定 🔃
* [ ] インデックスエラーが出たら対処できる 🛠️ ([Firebase][6])

---

## 12) AIをここに絡めると強い🤖✨（この章の“使いどころ”）

## 12-1) ダミーデータをAIに作らせて流し込む 🧪⚡

* 役割（admin/editor/viewer）を混ぜた “それっぽいユーザー” を20件くらい自動生成
* あなたはUIに集中できる😆

Firebase AI Logic は、クライアントSDK＋プロキシで生成AIをアプリに組み込みやすくする仕組みです（後の章で「AIボタン」に直結するやつ！）🤖 ([Firebase][8])

## 12-2) Gemini CLIで「型の見直し」「例外処理の穴」をチェックしてもらう🧰🔍

Gemini CLIはターミナルからAIエージェント的に手伝ってくれるやつです🧠 ([Google Cloud Documentation][9])
たとえば👇みたいにお願いすると便利です（文章でOK）

* 「`fetchUsersNewestFirst` を型安全にして、nullケースも丁寧にして」
* 「UIのローディング/エラー表示をもっと親切にして」

## 12-3) Antigravityで“表UIの磨き”を一気に進める🛸✨

ミッション型で、表の改善（列追加・見た目調整・アクセシビリティ）をガッとやるのに相性いいです💪 ([Google Codelabs][10])

---

次の第13章では、このテーブルの行クリックで **詳細フォームに飛んで編集→保存** を作ります📝🔥
第12章のうち「**並び替えボタン**」まで入れてから行くと、気持ちよさが段違いです😆

[1]: https://firebase.google.com/docs/firestore/data-model?utm_source=chatgpt.com "Cloud Firestore Data model | Firebase - Google"
[2]: https://firebase.google.com/docs/firestore/query-data/order-limit-data?utm_source=chatgpt.com "Order and limit data with Cloud Firestore - Firebase - Google"
[3]: https://www.npmjs.com/package/firebase?utm_source=chatgpt.com "firebase"
[4]: https://firebase.google.com/docs/firestore/query-data/get-data?utm_source=chatgpt.com "Get data with Cloud Firestore | Firebase - Google"
[5]: https://firebase.google.com/docs/reference/js/v8/firebase.firestore.Timestamp?utm_source=chatgpt.com "Timestamp | JavaScript SDK | Firebase JavaScript API reference"
[6]: https://firebase.google.com/docs/firestore/query-data/indexing?utm_source=chatgpt.com "Manage indexes in Cloud Firestore - Firebase - Google"
[7]: https://firebase.google.com/docs/firestore/security/insecure-rules?utm_source=chatgpt.com "Fix insecure rules | Firestore - Firebase"
[8]: https://firebase.google.com/docs/ai-logic?utm_source=chatgpt.com "Gemini API using Firebase AI Logic - Google"
[9]: https://docs.cloud.google.com/gemini/docs/codeassist/gemini-cli?utm_source=chatgpt.com "Gemini CLI | Gemini for Google Cloud"
[10]: https://codelabs.developers.google.com/getting-started-google-antigravity?utm_source=chatgpt.com "Getting Started with Google Antigravity"
