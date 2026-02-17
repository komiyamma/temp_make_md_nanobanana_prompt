# 第14章：“集めて検索”の入門：Lokiで探せるログにする 🧲🔍📊

## ① 今日のゴール 🎯

* `docker logs`（CLI）だけじゃなく、ブラウザの検索UIでログを探せるようになる 😆🖥️
* ログに **「ラベル（検索タグ）」** を付けて、

  * `service=api` で絞る
  * `reqId=xxxx` で追う
  * `status=500` だけ拾う
    みたいなことができるようになる 🏷️🔎
* ついでに重要ニュース：**PromtailはLTSが2026-02-28まで、EOLが2026-03-02予定**。これからは **Grafana Alloy** 側に開発が寄っていく流れなので、この章もAlloyでやるよ〜🧠✨ ([Grafana Labs][1])

---

## ② 全体図（1枚）🖼️

![Log Collection Architecture](./picture/docker_observability_ts_study_014_01_log_collection_flow.png)

「アプリが吐いたログ」を「ためて」「検索する」までの道のり👇

```text
[Node/TS API]  --(stdout/stderr)-->  [Docker]  --(Alloyが回収)-->  [Lokiに送信]
                                                                     |
                                                                     v
                                                               [Grafanaで検索🔍]
```

* **Loki**：ログの保管庫（ただし“全文検索エンジン”というより、**ラベルで高速に絞る**思想）🧺
* **Alloy**：ログを集めてLokiへ送る係（今後の本命）🚚
* **Grafana**：検索UI＆可視化の画面担当 🖥️✨

（参考：Lokiは本日時点で **v3.6.5（2026-02-06）** が最新リリース 🆕 ([GitHub][2])）

---

## ③ 手を動かす（手順 5〜10個）🛠️

ここからは「最小構成」でいくよ〜！🥳
**Grafanaがポート3000を使う**ので、あなたのAPIが `3000` を使ってたら **API側を 3001 にずらす**のが安全 👍

### Step 0) フォルダ構成を作る 📁

![Project Directory Structure](./picture/docker_observability_ts_study_014_02_folder_structure.png)

こんな感じにする（シンプル命）🧹

```text
chapter14-loki/
  docker-compose.yml
  loki/
    loki.yaml
  alloy/
    config.alloy
  grafana/
    provisioning/
      datasources/
        loki.yaml
```

---

### Step 1) `docker-compose.yml` を用意する 🧩

ポイントは3つ👇

* Loki（ログ保管）
* Alloy（ログ回収→Lokiへ送信）
* Grafana（検索UI）

```yaml
name: chapter14

services:
  # あなたのミニAPI（すでにある想定）
  # 例として build を置いてるけど、既存のサービス定義に合わせてOK👌
  api:
    build: ./app
    ports:
      - "3001:3000"  # ← Grafanaが3000を使うのでズラす
    environment:
      - NODE_ENV=development

  loki:
    image: grafana/loki:3.6.5
    command: ["-config.file=/etc/loki/loki.yaml"]
    ports:
      - "3100:3100"
    volumes:
      - ./loki/loki.yaml:/etc/loki/loki.yaml:ro
      - loki-data:/loki

  grafana:
    image: grafana/grafana:12.3.3
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning:ro
    depends_on:
      - loki

  alloy:
    image: grafana/alloy:v1.13.0
    command: ["run", "--server.http.listen-addr=0.0.0.0:12345", "/etc/alloy/config.alloy"]
    ports:
      - "12345:12345" # Alloyの状態を見る用（任意）
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./alloy/config.alloy:/etc/alloy/config.alloy:ro
    depends_on:
      - loki

volumes:
  loki-data:
  grafana-data:
```

* Grafanaは **v12.3.3（2026-02-12）** が最新リリースだよ 🆕 ([GitHub][3])
* もし `grafana/grafana:12.3.3` が pull できなかったら、`12.3.2` に一段下げるとだいたい動くよ（Dockerタグ事情でたまにズレるやつ）😇

---

### Step 2) Lokiの設定 `loki/loki.yaml` を書く 🧺

「ローカル用（シングル構成）」の鉄板パターン。
元ネタは Loki のローカル設定（`loki-local-config.yaml`）を読みやすく整形＆保存先を `/loki` に寄せた感じだよ 🧠 ([GitHub][4])

```yaml
auth_enabled: false

server:
  http_listen_port: 3100
  grpc_listen_port: 9096
  log_level: info

common:
  instance_addr: 127.0.0.1
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    kvstore:
      store: inmemory

schema_config:
  configs:
    - from: 2020-10-24
      store: tsdb
      object_store: filesystem
      schema: v13
      index:
        prefix: index_
        period: 24h

query_range:
  results_cache:
    cache:
      embedded_cache:
        enabled: true
        max_size_mb: 100

limits_config:
  metric_aggregation_enabled: true
  enable_multi_variant_queries: true

pattern_ingester:
  enabled: true

## もし「匿名の利用統計」を止めたいなら👇（元設定にコメントで案内あり）
## analytics:
##   reporting_enabled: false
```

---

### Step 3) Alloy設定 `alloy/config.alloy` を書く 🚚

![Alloy Relabeling Process](./picture/docker_observability_ts_study_014_03_alloy_relabeling.png)

ここがこの章のキモ！🧠✨
Alloyは **Dockerソケット**からコンテナを発見して、ログを読んで、Lokiへ送るよ。

* `discovery.docker`：Dockerのコンテナを見つける
* `discovery.relabel`：**ラベル整形**（Composeのproject/serviceをラベルにする）

  * Dockerラベル名は `.` が `_` に変換される仕様もあるよ（例：`com.docker.compose.project` → `__meta_docker_container_label_com_docker_compose_project`）🧼 ([Grafana Labs][5])
* `loki.source.docker`：ログを読む ([Grafana Labs][6])
* `loki.write`：Lokiへ送る

```hcl
discovery.docker "local" {
  host = "unix:///var/run/docker.sock"
}

discovery.relabel "docker_logs" {
  targets = discovery.docker.local.targets

  # ✅ このComposeプロジェクトのコンテナだけに絞る（name: chapter14 を使って固定してる）
  rule {
    action        = "keep"
    source_labels = ["__meta_docker_container_label_com_docker_compose_project"]
    regex         = "chapter14"
  }

  # ✅ service=api みたいな「安定してる名前」をラベルにする
  rule {
    source_labels = ["__meta_docker_container_label_com_docker_compose_service"]
    target_label  = "service"
  }

  # ✅ env は固定ラベル（ローカル学習用）
  rule {
    target_label = "env"
    replacement  = "local"
  }

  # ✅ ついでに container も残す（デバッグに便利）
  rule {
    source_labels = ["__meta_docker_container_name"]
    regex         = "/(.*)"
    target_label  = "container"
  }
}

loki.source.docker "docker" {
  host          = "unix:///var/run/docker.sock"
  targets       = discovery.docker.local.targets
  forward_to    = [loki.write.local.receiver]
  relabel_rules = discovery.relabel.docker_logs.rules

  # Lokiは「最低1個はラベルが必要」なので、保険で1個入れとく（安全策）🛡️
  labels = {
    job = "docker"
  }
}

loki.write "local" {
  endpoint {
    url = "http://loki:3100/loki/api/v1/push"
  }
}
```

* `discovery.relabel` の `action="keep"` は「マッチしたやつだけ通す」動き（Alloyのrelabellingは“フィルタ”用途が王道）🧹 ([Grafana Labs][7])
* 公式の「Docker監視シナリオ」や「ComposeでLokiを入れる導線」も、Alloyを使う方向に寄ってるよ 🧭 ([Grafana Labs][8])

---

### Step 4) GrafanaにLokiを自動登録する（Provisioning）⚡

手でポチポチしなくて済むやつ！最高！😆

`grafana/provisioning/datasources/loki.yaml`

```yaml
apiVersion: 1

datasources:
  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    isDefault: true
```

---

### Step 5) 起動する 🚀

PowerShellでOK！

```powershell
cd chapter14-loki
docker compose up -d --build
docker compose ps
```

動作チェック（ざっくり）👇

* Grafana：`http://localhost:3000`（admin / admin）🖥️
* Loki：`http://localhost:3100/ready` が `ready` ならOKっぽい ✅
* Alloy：`http://localhost:12345`（見れたらOK・見なくてもOK）👀

---

## ④ Grafanaでログを検索してみよう 🔎✨

### 1) まず「APIを叩いてログを発生」させる 🏃‍♂️💨

```powershell
curl.exe http://localhost:3001/ping
curl.exe http://localhost:3001/slow
curl.exe http://localhost:3001/boom
```

### 2) Grafanaで見る（Explore）🧭

![Grafana Explore UI](./picture/docker_observability_ts_study_014_04_grafana_explore.png)

Grafanaにログ探索UIがあるよ（最近のGrafanaはログ探索まわりも強化されがち）🧠 ([Grafana Labs][9])

* 左メニュー → **Explore** 🔭
* Datasource が **Loki** になってるのを確認 ✅
* まずはこれ👇

```text
{service="api", env="local"}
```

出たら勝ち！🏆🎉

---

## ⑤ “reqIdで検索” と “status=500で絞る” をやってみる 🧵🪪

![JSON Log Filtering](./picture/docker_observability_ts_study_014_05_json_filtering.png)

ここからが「集めて検索」の気持ちよさ😆✨

### ✅ 1) reqIdで追跡する

（第10章で「全ログにreqIdを入れる」をやってる前提）

```text
{service="api", env="local"} | json | reqId="あなたのreqId"
```

* `| json` は「ログ本文がJSONなら、フィールドとして扱える」って感じ（超便利）🧱🔎

### ✅ 2) status=500だけにする（/boom を叩いた後に）

アクセスログに `status` を入れてる前提で👇

```text
{service="api", env="local"} | json | status=500
```

「500だけ出る」＝障害対応でめちゃ使う動き 🧯🔥

---

## ⑥ ラベル設計のコツ（超入門）🏷️🧠

![Label Cardinality (Good vs Bad)](./picture/docker_observability_ts_study_014_06_label_cardinality.png)

Lokiは特にここが大事！

* 👍 **ラベルに向いてるもの（種類が少ない）**

  * `service`（api / worker / db…）
  * `env`（local / staging / prod…）
  * `level`（info / error… ※ただし実装次第）
* 👎 **ラベルにしちゃダメ寄り（種類が爆発する）**

  * `userId`、`orderId`、`reqId`、`sessionId` みたいな「ほぼ無限」系 💥
    → それらは **ログ本文（JSONフィールド）** に入れて、検索時に `| json` で拾うのが安全 ✅

---

## ⑦ つまづきポイント（3つ）🪤😵‍💫

1. **Grafanaは開けるのにログが出ない**

   * `docker compose logs -f alloy` を見る 👀
   * LokiのURL（`http://loki:3100/...`）が間違ってないか確認 🔍

2. **ラベルが期待通りじゃない**

   * Composeラベルは `.` が `_` に変換される仕様を思い出す（超あるある）🧼 ([Grafana Labs][5])

3. **Promtailでやろうとして混乱する**

   * いまはPromtailがEOL間近なので、Alloyに寄せた方が未来が明るい 🔆 ([Grafana Labs][1])

---

## ⑧ ミニ課題（15分）⏳💪

1. `/slow` を10回叩いてログを増やす 🐢
2. Grafanaで `{service="api"}` で絞る
3. `|= "slow"` でさらに絞る（文字列フィルタ）🔎
4. `| json` を付けて、`ms`（処理時間）が見えるログだけにする
5. 「遅い時に見るクエリ」を自分用メモに1つ残す 📝✨

---

## ⑨ AIに投げるプロンプト例（コピペOK）🤖📋

* 「Alloyの `discovery.relabel` で、`service` と `env` のラベルを付けたい。docker-composeの `com.docker.compose.service` と `com.docker.compose.project` を使う設定例を出して」
* 「Loki（LogQL）で、JSONログから `status=500` と `reqId` を使って絞り込むクエリ例を5つ出して」
* 「ラベルにしてはいけない項目（高カーディナリティ）を、初心者向けに例付きで説明して」

---

次の章（メトリクス編）に入ると「ログ＝点」だけじゃなく「数字＝面」で傾向が見えるようになって、さらに楽しくなるよ〜📈😆

[1]: https://grafana.com/docs/loki/latest/send-data/promtail/ "Promtail agent | Grafana Loki documentation
"
[2]: https://github.com/grafana/loki/releases?utm_source=chatgpt.com "Releases · grafana/loki"
[3]: https://github.com/grafana/grafana/releases "Releases · grafana/grafana · GitHub"
[4]: https://raw.githubusercontent.com/grafana/loki/v3.6.5/cmd/loki/loki-local-config.yaml "raw.githubusercontent.com"
[5]: https://grafana.com/docs/alloy/latest/reference/components/discovery/discovery.docker/?utm_source=chatgpt.com "discovery.docker | Grafana Alloy documentation"
[6]: https://grafana.com/docs/alloy/latest/reference/components/loki/loki.source.docker/?utm_source=chatgpt.com "loki.source.docker | Grafana Alloy documentation"
[7]: https://grafana.com/docs/alloy/latest/reference/components/discovery/discovery.relabel/?utm_source=chatgpt.com "discovery.relabel | Grafana Alloy documentation"
[8]: https://grafana.com/docs/loki/latest/setup/install/docker/ "Install Loki with Docker or Docker Compose | Grafana Loki documentation
"
[9]: https://grafana.com/docs/grafana/latest/whatsnew/whats-new-in-v12-3/?utm_source=chatgpt.com "What's new in Grafana v12.3"
