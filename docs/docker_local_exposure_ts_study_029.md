# 第29章：ログと観測の最小セット👂📈

この章のゴールはシンプルです👇
**「どこまで届いて、どこで落ちた？」を、ログで最短で特定できるようになる**こと🎯✨

---

## 1) まず“最小セット”って何？🧰✨

ローカルの複数アプリ共存（リバプロあり）で、まず揃えるのはこの3つだけでOKです👍

1. **入口（リバプロ）のアクセスログ**🚪📜
2. **中身（各コンテナ）の標準出力ログ**🐳🗣️
3. **“追いかける”コマンド（tail / since / 絞り込み）**🔍⏱️

この3点が揃うと、9割のトラブルは「犯人まで一直線」です😺✨

---

## 2) 入口ログ（リバプロ）を見る👀🚪

入口ログは“交通カメラ”です📸
**リクエストが来たか／どのURLか／何秒かかったか／ステータスは何か**が最速で分かります。

---

## 2-1) Caddy のアクセスログ（例）🍞📜

Caddy は `log` ディレクティブでアクセスログを有効化できます。
ログ出力先（stdout/ファイル）や形式（console/json）もここで指定します。([Caddy Web Server][1])

さらに大事ポイント👇
**Cookie/Authorization など“危険なヘッダ”は既定で `REDACTED` になります**（安全寄り！）([Caddy Web Server][1])

### 例：stdout に JSON で出す（まずはコレが楽）✨

```caddyfile
:80 {
  log {
    output stdout
    format json
  }

  reverse_proxy app:3000
}
```

* JSON にしておくと、あとで検索・加工がしやすいです🔎✨
* ファイルに出す場合、Caddy は**ログローテーション（肥大化対策）**も標準で入ってます🧯（ファイル出力の説明に「ロールされる」と明記）([Caddy Web Server][1])

---

## 2-2) Traefik のアクセスログ（例）🚦📜

Traefik はアクセスログが観測の中心。
**既定で stdout にテキスト形式**、設定で **JSON** や **ファイル出力**にできます。([Traefik Docs][2])

* 有効化：`accessLog: {}` または `--accesslog=true`([Traefik Docs][2])
* JSON：`accessLog.format=json`([Traefik Docs][2])
* ファイル：`accessLog.filePath=/path/to/access.log`([Traefik Docs][2])

### 例：docker compose の command で有効化（JSON + 4xx/5xx だけ残す）🧠✨

```yaml
services:
  traefik:
    image: traefik:v3
    command:
      - --accesslog=true
      - --accesslog.format=json
      - --accesslog.filters.statuscodes=400-599
```

* **フィルタ**は `statusCodes / retryAttempts / minDuration` が使えます（OR条件）([Traefik Docs][2])
* **出す項目やヘッダ**も「keep/drop/redact」で制御できます（ヘッダは既定 drop）🔐([Traefik Docs][2])
* タイムスタンプは **既定 UTC**（ローカル時間に寄せたいときは設定で調整）⏰([Traefik Docs][2])

---

## 3) “中身ログ”を見る：docker compose logs が主役🐳👂

入口で「届いた」のが分かったら、次は中身です。
ここで使うのが `docker compose logs` 👑

* `-f` 追従（tail -f 的なやつ）
* `--tail` 末尾だけ
* `--since` 直近だけ
* `-t` タイムスタンプ付き
  …が公式オプションとしてあります。([Docker Documentation][3])

## よく使うコマンド集（PowerShell）🪟✨

```powershell
## 全サービスのログを追いかける（まずはコレ）
docker compose logs -f

## 直近200行だけ見て、追いかける
docker compose logs -f --tail=200

## リバプロだけ見る（caddy / traefik など）
docker compose logs -f --tail=200 proxy

## APIだけ見る
docker compose logs -f --tail=200 api

## 直近10分だけ（トラブル直後に強い）
docker compose logs --since=10m api

## タイムスタンプ付き（“いつ起きた？”に強い）
docker compose logs -t --since=10m proxy
```

## Windows で“絞り込み”する小技🔍✨

PowerShell なら `Select-String` が便利です😺

```powershell
## 502 だけ拾う
docker compose logs --since=10m proxy | Select-String " 502 "

## "error" を拾う
docker compose logs --since=10m api | Select-String -Pattern "error|exception" -CaseSensitive:$false
```

---

## 4) 3分で特定する「切り分け手順」🕵️‍♂️⏱️

トラブル時は、**この順番**で見ると迷子になりにくいです🧭✨

## Step A：入口ログに“そのアクセス”は出てる？🚪📜

* **出てない**
  → 入口まで来てない（名前解決/hosts/URLミス/ブラウザが別URL叩いてる 等）😇
* **出てる**
  → 次へ✅

## Step B：入口ログのステータスは？📌

* **404**：ルーティングが合ってない（host/path/priority）
* **301/308**：リダイレクト設定が働いてる（想定通り？）
* **401/403**：認証・Cookie・ヘッダ周り（別章の地雷ゾーン🍪💣）
* **502/504**：中のサービスに届いてない（死んでる/ポート違い/起動遅い）
* **500**：中のアプリが落ちてる（例外・DB接続失敗など）

## Step C：502/504 のときの“鉄板チェック”🥊

1. `docker compose ps` で **対象サービスが Up か**を見る👀
2. Up なら **そのサービスの logs** を見る🐳
3. Down なら **起動ログ**で落ちた理由を読む💥
4. 入口ログで **どの upstream に投げようとしてるか**を確認（Traefikなら router/service 情報が手掛かりになりやすい）([Traefik Docs][2])

---

## 5) “ログの質”を上げる最小改善🧼✨

ここからは「困ったとき、未来の自分が助かる」やつです😺

## 5-1) まずは **stdout に出す**（ファイル直書きは後でOK）🗣️

Compose では **標準出力＝集約の中心**になりやすいので、
アプリ側は基本 stdout にログを出すのが楽です🐳✨

## 5-2) “秘密”をログに出さない🔐🙅‍♂️

* Authorization / Cookie / トークン / パスワードは出さない
* 入口側も **redact/drop** を活用する

  * Caddy は危険ヘッダを既定で `REDACTED` にします([Caddy Web Server][1])
  * Traefik はヘッダ既定 drop、必要なら keep/redact で調整できます([Traefik Docs][2])

## 5-3) （余裕が出たら）ログとトレースを“紐づける”🧵✨

将来的に「1リクエストの旅」を追いたくなったら、**Trace ID** が強いです🔥
OpenTelemetry は **traceparent ヘッダ**で文脈を伝播し、ログに Trace ID/Span ID を注入して相関できる、と整理されています。([OpenTelemetry][4])
（この章では“知っておく”だけでOK🙆‍♂️）

---

## 6) ミニ課題（手を動かすと一気に身につく）🧪🔥

## 課題1：わざと 404 を出して、入口ログで原因特定😈📜

1. 入口のルールを1つだけ間違える（host名 or path）
2. ブラウザでアクセス
3. 入口ログで **「どの host/path が来て、どう処理されたか」**を読む👀
4. 直して再アクセス → 200 を確認🎉

## 課題2：わざと 502 を出して、3分で復旧🧯

1. 中のサービスを止める（例：api）
2. ブラウザでアクセス（502/504 を確認）
3. 入口ログで 502 を確認
4. `docker compose logs api` で中身を見る
5. `docker compose up -d api` で戻す
6. 入口ログで 200 に戻るのを確認🎉

---

## 7) AIに聞く例（そのままコピペでOK）🤖✨

## ログ解釈（秘密は伏せる前提🔐）

* 「この `proxy` のアクセスログ（JSON/CLF）と `api` のログを貼るので、**原因候補を3つ**と、**次に打つコマンド**を順番に出して」
* 「502 が出た。入口ログでは upstream が〇〇っぽい。**起きがちな設定ミス（ポート/ネットワーク/起動順）**を優先度順に教えて」

## 設定生成（テンプレ化）📦✨

* 「Traefik v3 で access log を JSON にして、**4xx/5xx と 1秒超だけ**残す設定（compose の command 形式）を作って」
* 「Caddy の `log` を JSON + stdout にして、**必要最小限のフィールド**に絞る例を出して（機密ヘッダは出さない）」

---

もし今のあなたの構成が **Caddy版**か **Traefik版**か（または両方）で、
「この章のサンプル（compose/Caddyfile/labels）をあなたの実プロジェクト形に寄せた“完成版テンプレ”」も作れます📦🚀
いま使ってる proxy サービス名（例：`proxy`/`traefik`/`caddy`）だけ教えてくれたら、それに合わせて一発で組み立てます😺✨

[1]: https://caddyserver.com/docs/caddyfile/directives/log "log (Caddyfile directive) — Caddy Documentation"
[2]: https://doc.traefik.io/traefik/v3.0/observability/access-logs/ "Traefik Access Logs Documentation | Traefik | v3.0"
[3]: https://docs.docker.com/reference/cli/docker/compose/logs/ "docker compose logs | Docker Docs"
[4]: https://opentelemetry.io/docs/concepts/context-propagation/ "Context propagation | OpenTelemetry"
