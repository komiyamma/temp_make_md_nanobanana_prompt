# 第20章：Prometheus導入：スクレイプのしくみを知る 🕸️📥

## ① 今日のゴール 🎯

![Prometheus Pull Mechanism](./picture/docker_observability_ts_study_020_pull_mechanism.png)

* Prometheusが **pull型（取りに来る）**でメトリクスを集めるのが分かる 💪
* **targets（監視対象）**が「UP」になるのを確認できる ✅
* `scrape_interval`（取りに来る頻度）の意味がざっくり分かる ⏱️

---

## ② まずは1枚イメージ図 🖼️

* **API（あなたのNodeアプリ）**が `/metrics` を公開 🌱
* **Prometheus** が一定間隔で `http://api:3000/metrics` を取りに行く 🕷️
* 取ったデータは Prometheus 内の時系列DBにたまる 📦
* （次章）**Grafana** が Prometheus にクエリして可視化する 🖥️✨

イメージ（超ざっくり）👇

![Prometheus Architecture Flow](./picture/docker_observability_ts_study_020_architecture_flow.png)

```text
[Browser]       [Prometheus] ----scrape----> [API /metrics]
   |                |
   |                +---- store time-series ----+
   |                                            |
   +----(next) Grafana queries Prometheus <-----+
```

---

## ③ ここが大事：Prometheusの基本用語（最小）🧠

* **scrape（スクレイプ）**：Prometheusがメトリクスを取りに行くこと 🕷️
* **target**：取りに行く相手（URL）🎯
* **job**：targetのグルーピング名（例：`api`）🧩
* **scrape_interval**：取りに行く間隔（例：5秒、15秒、1分）⏱️

  ![Scrape Interval Timeline](./picture/docker_observability_ts_study_020_scrape_interval_timeline.png)

  ちなみにデフォルトは **1分**（`1m`）です（設定で変えられるよ）([prometheus.io][1])

---

## ④ バージョンの話（めっちゃ大事）📌

![Version Pinning Safety](./picture/docker_observability_ts_study_020_version_pinning.png)

DockerでPrometheusを動かすとき、**`:latest` を使うと「いつの間にか中身が変わる」**ことがあります 😇💥
なので教材でも **「バージョン固定」**がおすすめです。

* 2026-02-13 時点での Prometheus 最新リリース表示：**3.9.1（2026-01-07）** ([prometheus.io][2])
* LTS（長期サポート）枠もあり、例として **3.5 系**がLTSに入っています ([prometheus.io][3])
* Docker Hub には `latest` タグや多数のタグがあります ([Docker Hub][4])
  （運用では “latest頼み” を避けよう、の気持ち🙏）

この章では例として `v3.9.1` 固定で進めます（※あなたの環境で最新が更新されていたら、同じ考えで “その版に固定” してOK👍）([prometheus.io][2])

---

## ⑤ ハンズオン：ComposeでPrometheusを追加する 🛠️📦

## Step 0. ファイル配置（例）📁

こんな感じの構成にします（既存プロジェクトに追加するだけ）👇

* `compose.yml`
* `prometheus/`

  * `prometheus.yml`

---

## Step 1. `prometheus/prometheus.yml` を作る 📝

![prometheus.yml Structure](./picture/docker_observability_ts_study_020_config_tree.png)

ポイントは3つだけ👇

1. `scrape_interval`（取りに行く頻度）
2. `job_name`（グループ名）
3. `targets`（取りに行く先）

```yaml
global:
  scrape_interval: 5s   # 学習用に短め（動きが見えて楽しい😆）

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["prometheus:9090"]

  - job_name: "api"
    metrics_path: /metrics
    static_configs:
      - targets: ["api:3000"]
```

✅ ここ超重要：`api:3000` は **Composeのサービス名**です！

![Docker Localhost Trap](./picture/docker_observability_ts_study_020_localhost_trap.png)

Prometheusコンテナの中から見ると、`localhost:3000` は “Prometheus自身” になっちゃうので注意😵‍💫

設定項目の全体像は公式ドキュメントにもあります（`scrape_configs` や `static_configs` など）([prometheus.io][5])

---

## Step 2. `compose.yml` に Prometheus を追加する ➕

あなたの `api` サービスが既にある前提で、Prometheusを足します。

```yaml
services:
  api:
    # ここは既存のままでOK（例：build, ports, environment など）
    ports:
      - "3000:3000"

  prometheus:
    image: prom/prometheus:v3.9.1
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
    command:
      - "--config.file=/etc/prometheus/prometheus.yml"
```

* `9090` は Prometheus のWeb画面のポートです 🖥️
* `volumes` で設定ファイルをコンテナに渡してます 📦

Docker Hub の prom/prometheus イメージ情報（タグなど）([Docker Hub][6])

---

## Step 3. 起動する 🚀

VS Codeのターミナルで👇

```bash
docker compose up -d
docker compose ps
```

`prometheus` と `api` が `Up` になってたらOK✅

---

## ⑥ 動作確認：targets を見る 👀🎯

## 1) Prometheusの画面を開く 🌐

ブラウザで👇
`http://localhost:9090`

## 2) Targets を開く ✅

![Targets Page Mockup](./picture/docker_observability_ts_study_020_targets_ui_mock.png)

メニューから **Status → Targets** を開きます。
ここで `job="api"` が **UP** になってたら勝ち🏆✨

裏側ではAPIとしても targets 情報が取れます（/api/v1/targets）([prometheus.io][7])

---

## ⑦ ちょいクエリ体験（最小）📈

Prometheus画面の **Graph** で、これを試すと “取れてる感” が出ます😆

* `up`
  → Prometheusが取れてるtargetは `1`、死んでると `0`

* `up{job="api"}`
  → APIだけ見たい時の絞り込み🎯

（次章でGrafanaに渡すと、ここが一気に楽しくなるよ〜✨）

---

## ⑧ つまづきポイント 3つ 🪤😵‍💫

## 1) targetがDOWNのまま 😭

よくある原因👇

* `targets: ["localhost:3000"]` にしてしまった（罠）
* APIが `/metrics` を生やしてない or ルーティングが違う
* APIコンテナが落ちてる（`docker compose logs api` で確認）

## 2) /metrics が重い（CPU上がる）🔥

* `scrape_interval: 1s` とかにすると、取りに来る回数が増えて負荷が上がります⚠️
  学習中は短くてもOKだけど、本番運用は慎重にね🙏

## 3) メトリクスが増えすぎる 🤯

* Prometheusは時系列をためるので、ラベル設計が雑だと爆発します💣
  （この話は後半の運用章でじわじわ効いてくるやつ🧠）

---

## ⑨ ミニ課題（15分）⏳💪

1. `scrape_interval` を `5s → 15s` に変える
2. Prometheusを再起動
3. Targetsの `Last Scrape` の更新が遅くなるのを確認する

再起動はこれでOK👇

```bash
docker compose restart prometheus
```

---

## ⑩ AIに投げるプロンプト例（コピペOK）🤖📋

## プロンプト1：DOWNの原因あてゲーム🎯

```text
PrometheusのTargetsで job="api" が DOWN になります。
Docker Compose 構成で、Prometheusは api:3000/metrics をscrapeしています。
考えられる原因を「可能性が高い順」に10個挙げて、確認コマンドもセットで教えてください。
```

## プロンプト2：prometheus.yml をレビューしてもらう🧑‍🔧

```text
この prometheus.yml を初心者向けにレビューして、危険ポイントと改善案を教えて。
（特に scrape_interval と targets の書き方）
---ここに貼る---
```

---

## ⑪ この章のまとめ 🧾✨

* Prometheusは **pull型**で `/metrics` を取りに来る 🕷️
* Composeでは target は **サービス名:ポート** が基本（`api:3000`）🎯
* Targetsで **UPを確認**できれば、導入は成功 ✅
* 次章のGrafanaで「うおお見える！」が来ます😆🖼️✨

---

次の **第21章（Grafanaで可視化）**に向けて、もし今の `api` 側の `/metrics` が「どんなメトリクス名を出してるか」も一緒に整理したいなら、`/metrics` の出力を少し貼ってくれたら、**“最初に作るべきダッシュボード用クエリ”**までセットで作るよ〜📈🤝✨

[1]: https://prometheus.io/docs/prometheus/1.8/configuration/configuration/?utm_source=chatgpt.com "Configuration"
[2]: https://prometheus.io/download/?utm_source=chatgpt.com "Download | Prometheus"
[3]: https://prometheus.io/docs/introduction/release-cycle/?utm_source=chatgpt.com "Long-term support"
[4]: https://hub.docker.com/r/prom/prometheus/tags?utm_source=chatgpt.com "prom/prometheus - Docker Image"
[5]: https://prometheus.io/docs/prometheus/latest/configuration/configuration/?utm_source=chatgpt.com "Configuration"
[6]: https://hub.docker.com/r/prom/prometheus?utm_source=chatgpt.com "prom/prometheus - Docker Image"
[7]: https://prometheus.io/docs/prometheus/latest/querying/api/?utm_source=chatgpt.com "HTTP API"
