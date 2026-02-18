# 第06章：HTTPトリガー入門（Web APIの入口）🌐

この章は **「Functionsで“自分のAPI”を生やす最初の一歩」** だよ〜😆✨
HTTPリクエスト（GET/POSTなど）で関数を呼べるので、**Web APIの入口**が作れます。([Firebase][1])

---

## 0) まずイメージをつかもう🧠✨

HTTPトリガーは超ざっくり言うと👇

* ブラウザやアプリ（React）から **URLを叩く**
* Functions側で **リクエストを受ける**（`req`）
* Functions側で **レスポンスを返す**（`res`）
* それがそのまま **API** になる🌐

そしてHTTP関数は `GET/POST/PUT/DELETE/OPTIONS` などのメソッドを扱えます。([Firebase][1])

---

## 1) 今日作るもの：`GET /health` ✅🩺

運用でめちゃ使うやつです😎
**「生きてる？」を返すだけのAPI**を1本作ります。

* 監視ツールが叩ける
* 障害時に「Functionsが落ちてるのか、DBが死んでるのか」切り分けやすい
* 後でAIやDBを足して「準備OK？」チェックもできる🤖✅

---

## 2) HTTP関数の基本：`onRequest` 🌐

2nd genのHTTP関数は `onRequest` で作るのが基本です。
さらに **オプション（region / timeout / cors）** を付けられます。([Firebase][1])

* `region`：配置場所（近いほど速い🚀）([Firebase][1])
* `timeoutSeconds`：最大1時間まで設定できる([Firebase][1])
* `cors`：ブラウザから別オリジンで叩くときの壁🧱（デフォルトは未設定）([Firebase][1])

> 注意：HTTP関数は **必ずレスポンスを返して終わる** 必要があるよ！終わらないとムダ課金・ムダ実行になりがち😱([Firebase][1])

---

## 3) 実装してみよう：Health関数🛠️✨

ここでは **TypeScript** で書きます✍️
（第5章の分割方針があるなら `src/http/health.ts` に置くのがキレイ👍）

## ✅ `functions/src/http/health.ts`

```ts
import { onRequest } from "firebase-functions/v2/https";

export const health = onRequest(
  {
    region: "asia-northeast1",
    // CORSはこの章では触るだけ。Reactから叩くのは第8章でしっかりやるよ🙂
    cors: false,
  },
  (req, res) => {
    // GET以外は拒否（APIっぽさUP✨）
    if (req.method !== "GET") {
      res.status(405).json({ ok: false, error: "Method Not Allowed" });
      return;
    }

    // “生きてる”だけ返す（軽く！速く！）
    res.status(200).json({
      ok: true,
      service: "functions",
      time: new Date().toISOString(),
    });
  }
);
```

（`region / cors` などのHTTPオプションは `onRequest({ ... }, handler)` で指定できます。([Firebase][1])）

## ✅ `functions/src/index.ts`

```ts
export { health } from "./http/health";
```

---

## 4) ついでに“全関数にregion統一”する小ワザ🗾✨（おすすめ）

関数が増えると毎回 `region:` 書くのダルいよね😂
2nd genでは **グローバル設定** でまとめられます。

```ts
import { setGlobalOptions } from "firebase-functions/v2";

setGlobalOptions({ region: "asia-northeast1" });
```

こういう書き方が公式の2nd gen移行ガイドにも出ています。([Firebase][2])

---

## 5) デプロイして叩く🚀➡️🌐

## デプロイ（healthだけ）

```bash
firebase deploy --only functions:health
```

## 叩いて確認（Windows / PowerShell）💻

PowerShellは `curl` が別物になりがちなので、確実に `curl.exe` を使うのが安全👍

```powershell
curl.exe -i https://<あなたのhealthのURL>
```

または PowerShellの定番👇

```powershell
Invoke-RestMethod https://<あなたのhealthのURL>
```

## URLはどこで分かる？👀

* デプロイ時の出力
* Firebase Console / Cloud Console の関数詳細

2nd genは **deterministic URL（`cloudfunctions.net`）が付く** 形になっていて、昔の `run.app` のURLも継続して動く、という流れが明記されています。([Google Cloud Documentation][3])

---

## 6) 2nd genの“地味に大事”ポイント：同時処理（concurrency）⚡

2nd genは **1つのインスタンスが同時に複数リクエスト**を処理できるのが強み💪
デフォルト `concurrency: 80`、最大 `1000` まで設定できます。([Firebase][2])

ただし！ここで初心者が踏みやすい罠👇😱

* **グローバル変数**に「リクエストごとの状態」を入れると、同時処理で壊れることがある
* 迷ったら「1リクエスト＝1処理」っぽく書く（関数内のローカル変数中心）✅

（移行ガイドにも “グローバル変数の監査” って話が出ます）([Firebase][2])

---

## 7) CORSは“次章で本格的に”🧱（でも今ちょい予告🙂）

Reactから別オリジンで叩くと、デフォルトだとCORSで怒られます😇
公式にも「デフォルトはCORS未設定なのでブロックされるよ」って例が出ています。([Firebase][1])

この章では `/health` を **ブラウザ直叩き** or `curl` で確認できればOK👌
Reactから呼ぶのは第8章で勝ちに行こう🔥

---

## 8) AIで爆速にする🤖🛸（Gemini CLI × Firebase）

ここ、ちゃんと最新を押さえるよ〜😆
**Gemini CLIにFirebase拡張**が用意されていて、導入やコマンド補助ができます。([Firebase][4])

## 8-1) 拡張を入れる（例）

```bash
gemini extensions install firebase
```

この形がドキュメントに載っています。([Firebase][4])

## 8-2) “AIに頼むと強い”お題（そのまま投げてOK）📝✨

Gemini CLI（チャット）にこう頼むのがおすすめ👇

* 「`onRequest`（v2）で `GET /health` を作って。`GET以外は405`、JSONで返して。」
* 「`region` を `asia-northeast1` に固定して。」
* 「レスポンスに `time` を入れて。」
* 「後でAI機能を足せるように、ファイル分割案も提案して。」

さらに、拡張には **初期化/デプロイを助けるコマンド**も用意されています（例：`/firebase:init` や `/firebase:deploy`）。([Firebase][4])

---

## 9) FirebaseのAIサービスと“つながる形”にしておく🤖🔌

この章の `/health` は軽量でOKなんだけど、後でAIを足すときに困らないように
**「AI機能の準備できてる？」のチェック枠**を最初から持たせるのが実務っぽい👍

例：将来的に👇みたいな情報を足せる

* `aiConfigured: true/false`（秘密情報は絶対返さない🙅‍♂️）
* `aiProvider: "firebase-ai-logic"` みたいなタグ（目印）

FirebaseのAI支援やAI機能の導線自体も「Gemini in Firebase / Firebase AI Logic」方向へ整備が進んでいるので、ここを入口にしておくと後の章（Genkit連携など）で気持ちよく繋がるよ😆🔥([Firebase][4])

---

## 10) 補足：ランタイムの最新メモ（Node / Python / .NET）🧩

* Firebase FunctionsのNodeランタイムは **Node.js 22 / 20** がサポート、**18はdeprecated**。14/16は2025年初頭に無効化されています。([Firebase][5])
* Pythonは `firebase.json` で **python310 / python311** を選ぶ例が公式に載っています。([Firebase][5])
* C#（.NET）で“関数ランタイムとして”やりたい場合は、Firebaseの外側（Cloud Run functions側）で **.NET 8** がGA対応、という流れが公式リリースノートに出ています。([Google Cloud Documentation][3])

---

## ミニ課題（5〜10分）🏃‍♂️💨

`/health` をちょい強化しよう！

1. `GET /health?detail=1` のときだけ
   `nodeVersion`（`process.version`）を返す
2. `detail` が無いときは今のまま（軽量）
3. **秘密情報は絶対に返さない**（APIキーやSecret名とかもNG🙅‍♂️）

---

## ✅ チェックリスト（この章のゴール）

* `onRequest` でHTTP関数を1本作れた🌐([Firebase][1])
* `GET` 以外を `405` で弾けた🧱
* デプロイしてURLを叩き、JSONが返るのを確認できた✅
* 「HTTP関数はレスポンス返して終わる」が腹落ちした🧯([Firebase][1])
* Gemini CLI（Firebase拡張）に実装補助を頼むイメージが付いた🤖([Firebase][4])

---

次の第7章では、このHTTP入口を **“APIっぽく”** していくよ📦✨（JSON・ステータスコード・入力チェック）

[1]: https://firebase.google.com/docs/functions/http-events "Call functions via HTTP requests  |  Cloud Functions for Firebase"
[2]: https://firebase.google.com/docs/functions/2nd-gen-upgrade "Upgrade 1st gen Node.js functions to 2nd gen  |  Cloud Functions for Firebase"
[3]: https://docs.cloud.google.com/functions/docs/release-notes "Cloud Run functions (formerly known as Cloud Functions) release notes  |  Google Cloud Documentation"
[4]: https://firebase.google.com/docs/ai-assistance/gcli-extension "Firebase extension for the Gemini CLI  |  Develop with AI assistance"
[5]: https://firebase.google.com/docs/functions/manage-functions "Manage functions  |  Cloud Functions for Firebase"
