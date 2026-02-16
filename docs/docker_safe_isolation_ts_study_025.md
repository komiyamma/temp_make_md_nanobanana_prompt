# 第25章：ローテーション＆失効：漏れた前提の復旧手順を作る🚑🔁

この章はひとことで言うと――
**「秘密はいつか漏れる」前提で、焦らず復旧できる“手順書（Runbook）”を完成させる回**です😌📘✨

---

## 25.1 まず用語をそろえる（ここがブレると事故る）🧠🔤

* **ローテーション（rotation）**：秘密を“新しい値に入れ替える”こと🔁
  例）DBパスワードを新しくして、アプリ側もそれに切り替える
* **失効（revoke / invalidate）**：古い秘密を“使えない状態にする”こと🛑
  例）漏れたAPIトークンを管理画面で無効化する、ユーザーを無効化する

ポイント👇
✅ **ローテーション＝新しい鍵を配る**
✅ **失効＝古い鍵を折る**
両方セットで考えます💪🔐

---

## 25.2 “ローテできる設計”が安全（変えられない秘密は地雷）💣🧱

秘密を変えるのが怖い設計だと、こうなりがち👇😇

* 「動いてるし…今は触りたくない」
* 「漏れたかも…でも停止が怖い」
* 「結局、放置」→ 被害が拡大💥

だから最初から **“いつでも差し替えられる”形**にしておきます✨

---

## 25.3 いちばん強い基本技：「バージョン付き secret」＋「中のパス固定」📌🔐

## なにが嬉しい？😊

* 秘密の名前を `db_password_v1` → `db_password_v2` と増やしていける
* でも、コンテナ内の読み取り先は **ずっと同じ**（例：`/run/secrets/db_password`）
* 切替がシンプル＆ロールバックも楽🎮🔁

Docker Compose の secret はコンテナ内で `/run/secrets/<name>` にファイルとして載ります📄🔒（環境変数より漏れにくい理由もここ） ([Docker Documentation][1])
さらに、サービス側の secrets は **long syntax で `target` を固定**できます✅ ([Docker Documentation][2])
（※ `uid/gid/mode` は Compose の file secret だと制約がある点も同ページに明記されてます） ([Docker Documentation][2])

## 例：`target` を固定してローテ可能にする（超重要）⭐

```yaml
services:
  app:
    build: .
    secrets:
      # v2 を db_password という固定名で /run/secrets/ に置く
      - source: db_password_v2
        target: db_password

secrets:
  db_password_v1:
    file: ./secrets/db_password_v1.txt
  db_password_v2:
    file: ./secrets/db_password_v2.txt
```

アプリ側は **ずっと** `/run/secrets/db_password` を読むだけでOK😄📌
ローテ時は `source` を `v3` に変えるだけで切替できます🔁✨

ちなみに Docker の Swarm secrets でも「更新/ロールバックのために secret 名にバージョン番号や日付を入れる」考え方が推奨されています（運用の定石） ([Docker Documentation][3])

---

## 25.4 “止めないローテ”の王道：二段階（A/B）切替 🟦🟩🔁

## 手順（テンプレ）🧾

1. **新しい秘密を発行**（New）🆕
2. **アプリを新秘密に切替**（Deploy）🚀
3. **動作確認**（Verify）✅
4. **古い秘密を失効**（Revoke）🛑
5. **再発防止のメモ**（Learn）📝

これが“焦らない型”です😌✨

---

## 25.5 Compose でのローテ実務（Windowsでもこの流れでOK）🪟🐳

## ① 新しい secret ファイルを作る🆕

例：`./secrets/db_password_v3.txt` を用意（中身は新パス）

## ② compose.yml を v3 に差し替える🔁

`source: db_password_v3` に変更（`target: db_password` は固定）

## ③ 再作成して反映（基本はこれ）♻️

```bash
docker compose up -d --force-recreate
```

> Compose は “コンテナは作り直すもの” の思想が強いので、再作成は普通の運用です🙂🔁
> ※「変更があれば作り直される」系の挙動はコミュニティでも一般的に説明されています ([Docker Community Forums][4])

---

## 25.6 DB系は「_FILE 文化」に乗る（自作より安全）🧠📦

公式イメージ（MySQL/Postgres など）には、環境変数の代わりに `*_FILE` で **“ファイルから読む”**流儀があります💡
Compose secrets の例でも `_FILE` が紹介されています ([Docker Documentation][1])

```yaml
services:
  db:
    image: mysql:latest
    environment:
      MYSQL_ROOT_PASSWORD_FILE: /run/secrets/db_root_password
    secrets:
      - db_root_password

secrets:
  db_root_password:
    file: ./secrets/db_root_password_v1.txt
```

この方式にすると「値そのもの」を環境変数に置かずに済みます👍（ログやデバッグで事故りにくい） ([Docker Documentation][1])

---

## 25.7 “ビルド時の秘密”はローテの作法が別（レイヤに残さない）🏗️🤫

`npm token` や `private repo` の鍵など、**ビルド中だけ必要**な秘密は
BuildKit の **build secrets** を使うのが安全寄りです✅

* シークレットは **ビルド命令の間だけ一時的に見える**
* 画像レイヤに残さない設計になってるのがポイント ([Docker Documentation][5])

（この章では深掘りしないけど、ローテ時は「ビルド専用トークンを再発行→CI設定を更新→古いの失効」の流れになります🔁）

---

## 25.8 CI/CD（GitHub Actions）も“長生き秘密”を減らすとローテが楽🎯🔐

CIでクラウドに触るなら、**長期トークンを置かない**方向が強いです。

GitHub の Actions は **OIDC を使って、長期シークレットを減らす**選択肢を公式に案内しています✨ ([GitHub Docs][6])
→ これ、ローテの地獄をかなり減らせます😇🔁

---

## 25.9 事故対応Runbook（これをコピペして“自分用”に埋めて完成）🧾🚑

ここが本章のゴールです🎯✨
「漏れたかも」で手が震えても、この順でやればOK😌🫶

## A. まず“被害の拡大”を止める🧯

* 漏れた可能性のある **トークン/鍵を失効** 🛑
* 影響が大きいなら一時的に **外部公開（ポート/URL）を止める** 🚪🔒
* “秘密を貼りがち”な場所（Issue/Chat/AI）に貼ってないか確認🤖⚠️

## B. どれが漏れたか特定する🔍

* 種類：DB？API？JWT署名鍵？SSH？CI？
* 範囲：どのサービスが使ってる？（Compose の `secrets:` を見る）
* いつから：ログ/監査ログで「変なアクセス」有無👀

## C. 新しい秘密を発行する🆕

* 可能なら “権限を絞った新トークン” を作る（最小権限）✂️🔐
* 命名：`api_token_2026-02-11` みたいに日付付きがわかりやすい📅

## D. 切替（Deploy）する🚀

* `source` を新バージョンに変える（`target` は固定）📌
* `docker compose up -d --force-recreate` で反映♻️
* ヘルスチェック/簡易E2Eで動作確認✅

## E. 古い秘密を失効する🛑

* “切替が成功したのを確認してから”失効（事故ると復旧がさらに地獄）😇
* 失効したら、古い secret ファイルはアクセス権見直し＆削除候補🗑️🔒

## F. 事後処理（次の自分を救う）📝

* 「なぜ漏れたか」1行でいいから記録
* “次から自動で検知できるポイント”をメモ（ログに残すべきイベントなど）📌
* 可能ならローテ周期を決める（例：重要トークンは月1〜四半期）🗓️

---

## 25.10 ハンズオン演習：TSアプリで“ローテ→失効”を疑似体験しよう🎮🔁

狙い：**「差し替えが怖くない」状態を体に入れる**💪✨

## 演習1：secret をファイルで読む（/run/secrets）📄🔐

* Compose secret は `/run/secrets/<name>` に載る ([Docker Documentation][1])
* TS側は「ファイルを読んで使う」だけにする

`src/secret.ts`

```ts
import { readFileSync } from "node:fs";

export function readSecret(path: string): string {
  // 余計な trim は事故ることがあるので、最後の改行だけ落とすイメージ
  return readFileSync(path, "utf8").replace(/\n$/, "");
}

export function mask(s: string): string {
  if (s.length <= 8) return "********";
  return `${s.slice(0, 4)}...${s.slice(-4)}`;
}
```

`src/index.ts`

```ts
import http from "node:http";
import { readSecret, mask } from "./secret";

const secretPath = process.env.API_KEY_FILE ?? "/run/secrets/api_key";
const apiKey = readSecret(secretPath);

const server = http.createServer((req, res) => {
  if (req.url === "/health") {
    res.writeHead(200);
    res.end("ok");
    return;
  }
  res.writeHead(200, { "content-type": "text/plain; charset=utf-8" });
  res.end(`apiKey=${mask(apiKey)}\n`);
});

server.listen(3000, () => console.log("listening :3000"));
```

`compose.yml`

```yaml
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      API_KEY_FILE: /run/secrets/api_key
    secrets:
      - source: api_key_v1
        target: api_key

secrets:
  api_key_v1:
    file: ./secrets/api_key_v1.txt
  api_key_v2:
    file: ./secrets/api_key_v2.txt
```

起動：

```bash
docker compose up -d --build
```

## 演習2：ローテしてみる（v1→v2）🔁🆕

1. `./secrets/api_key_v2.txt` を新しく作る
2. `source: api_key_v2` に変える
3. 反映：

```bash
docker compose up -d --force-recreate
```

## 演習3：失効の練習🛑

* “v1 を失効したつもり”で、`api_key_v1.txt` を削除 or 中身を無効値にして保存
* `source` を v1 に戻したら **壊れる**のを確認（＝失効が効いてる）😈✅
* その後 v2 に戻して復旧（ロールバック訓練）🧯

---

## 25.11 最後に：今日の完成物🎉📦

この章が終わった時点で、手元に残っていれば勝ちです🏆✨

* ✅ **バージョン付き secret** の運用（v1/v2/v3…）
* ✅ **コンテナ内の読み取り先を固定**（`target` で `/run/secrets/...` を一定に） ([Docker Documentation][2])
* ✅ **事故対応Runbook（チェックリスト）**
* ✅ （発展）CIは **OIDC で長期secretを減らす**方針も検討できる ([GitHub Docs][6])

次の章で「ネットワーク隔離」や「AI時代の被害半径」と合体すると、さらに事故りにくい“総合防御”になります🛡️🤖✨

[1]: https://docs.docker.com/compose/how-tos/use-secrets/ "Secrets in Compose | Docker Docs"
[2]: https://docs.docker.com/reference/compose-file/services/ "Services | Docker Docs"
[3]: https://docs.docker.com/engine/swarm/secrets/?utm_source=chatgpt.com "Manage sensitive data with Docker secrets"
[4]: https://forums.docker.com/t/creation-of-new-container-when-there-is-update-in-docker-compose-file/146016?utm_source=chatgpt.com "Creation of new container when there is update in docker compose file"
[5]: https://docs.docker.com/build/building/secrets/?utm_source=chatgpt.com "Build secrets - Docker Docs"
[6]: https://docs.github.com/en/actions/concepts/security/openid-connect?utm_source=chatgpt.com "OpenID Connect - GitHub Docs"
