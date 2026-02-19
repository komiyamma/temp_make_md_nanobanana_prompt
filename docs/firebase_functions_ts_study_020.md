# 第20章：Firestore更新→Slack通知を完成（実務の形に）🏁🔥

この章では、**Firestoreのドキュメント更新をきっかけに、Slackへ自動通知**を飛ばして「現場でそのまま使える」形に仕上げます📣✨
（ポイントは **重複・順序・失敗** をちゃんと受け止めること！）

---

## この章で完成するもの 🎯✨

![Overall Flow](./picture/firebase_functions_ts_study_020_01_overall_flow.png)

* `reports/{reportId}` が更新されたら、Slackに **「何が変わったか」** を投稿🧾➡️🔔
* **二重通知を防ぐ**（＝同じイベントで何回呼ばれても1回だけ）🛡️
* 失敗しても **ログで追える**＆（必要なら）**再試行しやすい**形にする🧯👀

---

## まず押さえる「現実」3つ 🧠⚡

![Event Quirks](./picture/firebase_functions_ts_study_020_02_event_quirks.png)

Firestoreトリガーは便利だけど、現場だとこういう“クセ”があります👇

1. **順序は保証されない**（連続更新だと想定と違う順番で来ることがある）🔀
2. **少なくとも1回は届く（＝複数回呼ばれることもある）**📨📨
3. **フィールド単位のトリガーは作れない**（コード側で差分判定する）🧩
   さらに、Functionsの読み書きは **Security Rulesの対象外**（権限が強い）なので、設計とログが超大事です🧨
   ([Firebase][1])

---

## 1) ざっくり設計図 🗺️

![Dedupe Schema](./picture/firebase_functions_ts_study_020_03_dedupe_schema.png)

## 触るコレクション案 📚

* 監視対象：`reports/{reportId}`

  * 例：`title`, `status`, `updatedAt`, `updatedBy` など
* 重複防止用（新規）：`_functionDedupe/{eventId}`

  * 「このイベントIDは処理済み？」を1発で判断するための箱📦

> **eventId は CloudEvent の id** を使うのが分かりやすいです（イベントごとにユニークなID）🆔
> ([jsDocs.io][2])

---

## 2) Secret（Webhook URL）を “安全に” 使う 🔐🗝️

SlackのWebhook URLは漏れると危険なので、**コードに直書き禁止**🙅‍♂️
Cloud Functions側は **Secret Manager と連携**できます。

* `defineSecret()` で “使うよ宣言”
* 関数定義で `secrets: [...]` を指定
* 実行時は `secret.value()` で取り出す

この流れが公式の推奨ルートです✅
([Firebase][3])

---

## 3) 実装（TypeScript）🛠️🔥

![Idempotency Logic](./picture/firebase_functions_ts_study_020_04_idempotency_logic.png)

## ✅ ここで作る関数

* `reports/{reportId}` の **作成・更新・削除** のどれでも起動する `onDocumentWritten`
* ただし実際は「更新だけ通知」みたいに **中で絞る**（重要）🎛️
  `onDocumentWritten` 自体の挙動や no-op（変更なし更新はイベントが出ない）などの前提もここで効いてきます
  ([Firebase][1])

---

## コード例（1ファイルで完結版）📄✨

```ts
import * as admin from "firebase-admin";
import { logger } from "firebase-functions";
import { defineSecret } from "firebase-functions/params";
import { onDocumentWritten } from "firebase-functions/v2/firestore";

admin.initializeApp();
const db = admin.firestore();

// Secret Managerに入れておいたWebhook URL
const SLACK_WEBHOOK_URL = defineSecret("SLACK_WEBHOOK_URL");

/**
 * reports/{reportId} の変更を Slack へ通知する
 */
export const notifyReportToSlack = onDocumentWritten(
  {
    document: "reports/{reportId}",
    secrets: [SLACK_WEBHOOK_URL],
    // 日本ならここは東京寄りにすると遅延が減りやすい（例）
    region: "asia-northeast1",
  },
  async (event) => {
    // CloudEvent の id（イベントごとにユニーク）を重複防止キーにする
    const eventId = event.id ?? "no-event-id";
    const reportId = event.params.reportId;

    const change = event.data;
    const beforeSnap = change?.before;
    const afterSnap = change?.after;

    const beforeExists = !!beforeSnap?.exists;
    const afterExists = !!afterSnap?.exists;

    // 「更新だけ通知したい」なら、更新以外はスキップ
    // - 作成: beforeなし / afterあり
    // - 更新: beforeあり / afterあり
    // - 削除: beforeあり / afterなし
    const isUpdate = beforeExists && afterExists;
    if (!isUpdate) {
      logger.info("Skip (not update)", { eventId, reportId, beforeExists, afterExists });
      return;
    }

    const before = beforeSnap!.data() as Record<string, unknown>;
    const after = afterSnap!.data() as Record<string, unknown>;

    // 監視したいフィールドだけ差分を見る（フィールド単位トリガーは作れないので自前で絞る）
    const watchKeys = ["title", "status"];
    const changedKeys = watchKeys.filter((k) => before?.[k] !== after?.[k]);

    if (changedKeys.length === 0) {
      logger.info("Skip (no watched field changed)", { eventId, reportId });
      return;
    }

    // -------- 重複防止（idempotency）--------
    // 先に「処理ロック」を作る（create は既に存在すると失敗するので atomic っぽく使える）
    const dedupeRef = db.collection("_functionDedupe").doc(eventId);
    try {
      await dedupeRef.create({
        createdAt: admin.firestore.FieldValue.serverTimestamp(),
        kind: "notifyReportToSlack",
        reportId,
      });
    } catch (e) {
      // 既に処理済み（または並行実行）なら通知しない
      logger.info("Skip (deduped)", { eventId, reportId });
      return;
    }

    try {
      const url = SLACK_WEBHOOK_URL.value();

      // Slack へ送る本文（Blocks を使うと読みやすい）
      const payload = buildSlackPayload({
        reportId,
        changedKeys,
        before,
        after,
        eventId,
      });

      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json; charset=utf-8" },
        body: JSON.stringify(payload),
      });

      const text = await res.text();

      if (!res.ok) {
        // 失敗したらロック解除しておく（再実行の邪魔をしない）
        await dedupeRef.delete().catch(() => {});
        logger.error("Slack post failed", {
          eventId,
          reportId,
          status: res.status,
          body: text,
        });

        // ここで throw すると「再試行」を有効化している場合にリトライ対象になる
        throw new Error(`Slack webhook failed: ${res.status}`);
      }

      // 成功ログ
      logger.info("Slack posted", { eventId, reportId, body: text });
    } catch (err) {
      // すでに dedupeRef.delete() してるけど、念のため
      await dedupeRef.delete().catch(() => {});
      throw err;
    }
  }
);

function buildSlackPayload(args: {
  reportId: string;
  changedKeys: string[];
  before: Record<string, unknown>;
  after: Record<string, unknown>;
  eventId: string;
}) {
  const { reportId, changedKeys, before, after, eventId } = args;

  const lines = changedKeys.map((k) => {
    const b = stringifyShort(before[k]);
    const a = stringifyShort(after[k]);
    return `• *${k}*: \`${b}\` → \`${a}\``;
  });

  return {
    text: `Report updated: ${reportId}`,
    blocks: [
      { type: "header", text: { type: "plain_text", text: "🧾 Report Updated", emoji: true } },
      {
        type: "section",
        text: {
          type: "mrkdwn",
          text: `*reportId:* \`${reportId}\`\n*changed:* ${changedKeys.join(", ")}`,
        },
      },
      { type: "section", text: { type: "mrkdwn", text: lines.join("\n") } },
      { type: "context", elements: [{ type: "mrkdwn", text: `eventId: \`${eventId}\`` }] },
    ],
  };
}

function stringifyShort(v: unknown) {
  if (v === null) return "null";
  if (v === undefined) return "undefined";
  const s = typeof v === "string" ? v : JSON.stringify(v);
  return s.length > 60 ? s.slice(0, 57) + "..." : s;
}
```

## このコードの「効いてるところ」💡

![Diff Logic](./picture/firebase_functions_ts_study_020_05_diff_check.png)

* `event.id` をキーに `_functionDedupe/{eventId}` を **create**
  → 同じイベントが複数回来ても **2回目以降はスキップ**🛡️
  （イベントが少なくとも1回配信＝複数回呼ばれる可能性がある、という前提に対応）([Firebase][1])
* Slack送信に失敗したら **dedupe を消してから throw**
  → 「再実行」や「リトライ設定」を邪魔しない🧯
* フィールド単位トリガーが作れないので、`watchKeys` で **差分フィルタ**🎛️
  ([Firebase][1])

---

## 4) Slack側のメッセージ整形（読みやすさ＝正義）🧾✨

![Slack Blocks](./picture/firebase_functions_ts_study_020_06_slack_blocks.png)

Incoming Webhooksは **Webhook URL に JSON をPOST**するだけでOK👌
`text` に加えて `blocks` を使うと、通知が一気に「仕事の通知」っぽくなります📌
([Slack開発者ドキュメント][4])

## そして地味に大事：レート制限 ⏱️🚦

更新が連打されると、Webhookが **429（Too Many Requests）** を返すことがあります。
Slackはレート制限の考え方を明示しているので、**大量通知があり得る設計**なら「まとめる」「キューに入れる」も検討対象です📦➡️📨
([Slack開発者ドキュメント][5])

---

## 5) 動作テスト手順（最短）🧪✅

1. Firestore に `reports/{reportId}` を作る（この章のコードは “更新のみ通知” なので、作った後に更新）✍️
2. `title` か `status` を更新🔁
3. Slack に通知が来るか確認📲
4. 同じ更新を短時間で何回かやって「重複しない」ことを見る👀
5. Functions のログで `eventId` と `reportId` が追えることを確認🧯

---

## 6) “本番で怖いポイント” を言語化しよう（チェック）✅🧠

![Safety Summary](./picture/firebase_functions_ts_study_020_07_safety_summary.png)

* [ ] **順序が保証されない**のに耐えられる？（最新だけ出す/まとめる等）🔀 ([Firebase][1])
* [ ] **複数回呼ばれても1回だけ**になってる？🛡️ ([Firebase][1])
* [ ] Webhook URL は **Secret** で管理できてる？🔐 ([Firebase][3])
* [ ] 429（多すぎ）や 5xx（失敗）で **ログから追える**？🧯
* [ ] Functions は権限が強いので、想定外の書き込みをしてない？🧨 ([Firebase][1])

---

## 7) AIで“仕上げ速度”を上げる 🤖🛸✨

## Gemini CLI で「レビュー前提の加速」🧰

* 「この関数、二重通知の穴ある？」
* 「429のときの方針、初心者向けに選択肢3つにして」
* 「blocks をもっと読みやすく（短く）して」

みたいな相談を **コードとログ込みで**投げると、直すのが速いです🚀
（Firebase向けの Gemini CLI 拡張＆AI支援系ドキュメント）([Firebase][6])

## MCP server で “Firebase操作の補助” も視野 👀

AIエージェント側が、Firebase周辺の作業を安全に手伝えるようにする仕組みも案内されています🧩
([Firebase][7])

---

## 8) おまけ：ランタイムの最新版メモ（この章の立ち位置）🧩📌

* Node は **22 / 20 がサポート、18 は deprecated**（2026年時点）
  ([Firebase][8])
* Python など他言語も計画に入れるなら、同じ通知フローを “別実装” で再現できます（ただしこの章は TS を主軸にして完成させるのが最短）🧠

---

## ミニ課題（ちょい実務寄せ）🎒✨

1. `watchKeys` を増やして「差分がある時だけ通知」を育てる🌱
2. `status` が `done` になった時だけ通知、みたいな “業務ルール” を入れる📘
3. 通知が多い想定で「まとめ通知（10秒ごとに1回）」の案を考える（実装は次の発展）⏱️📦

---

ここまでできたら、**Firestore更新→Slack通知**はもう「使える自動化」になってます🏁🔥
次に伸ばすなら「大量通知のキュー化（Cloud Tasks等）」「AIで通知文の要約（Genkit）」あたりが気持ちいい伸び方です🤖📨

[1]: https://firebase.google.com/docs/functions/firestore-events?utm_source=chatgpt.com "Cloud Firestore triggers | Cloud Functions for Firebase - Google"
[2]: https://www.jsdocs.io/package/firebase-functions "firebase-functions@7.0.5 - jsDocs.io"
[3]: https://firebase.google.com/docs/functions/config-env?utm_source=chatgpt.com "Configure your environment | Cloud Functions for Firebase"
[4]: https://docs.slack.dev/messaging/sending-messages-using-incoming-webhooks?utm_source=chatgpt.com "Sending messages using incoming webhooks"
[5]: https://docs.slack.dev/apis/web-api/rate-limits/?utm_source=chatgpt.com "Rate limits | Slack Developer Docs"
[6]: https://firebase.google.com/docs/ai-assistance/gcli-extension?utm_source=chatgpt.com "Firebase extension for the Gemini CLI"
[7]: https://firebase.google.com/docs/ai-assistance/mcp-server?utm_source=chatgpt.com "Firebase MCP server | Develop with AI assistance - Google"
[8]: https://firebase.google.com/docs/functions/manage-functions?utm_source=chatgpt.com "Manage functions | Cloud Functions for Firebase - Google"
