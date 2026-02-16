# 第21章：Grafanaで可視化：最初のダッシュボード 🖼️✨

## ① 今日のゴール 🎯

* **Grafana** を `docker compose` に追加して起動できる 🧱🚀
* **Prometheus** をデータソースとして繋げられる 🔌📥
* **最初の4パネル（RPS / エラー率 / p95 / メモリ）** を作れる 📊✨
* `/slow` や `/boom` を叩くとグラフが **ちゃんと動く** のを確認できる 🐢💥➡️📈

（参考：本日時点の最新版は Grafana 12.3.3（2026-02-12）と表示されています。）([Grafana Labs][1])
（参考：Prometheus の Latest は 3.9.1（2026-01-07）です。）([prometheus.io][2])

---

## ② 図（1枚）🖼️（頭の中の地図）

```text
ブラウザ
  │  http://localhost:3000
  ▼
Grafana（ダッシュボード）
  │  Prometheus をデータソースとして参照
  ▼
Prometheus（時系列DB）
  │  /metrics を取りに行く（scrape）
  ▼
Node/TS API（/metrics を公開）
```

---

## ③ 手を動かす（手順 5〜10個）🛠️✨

### 0) まず “ぶつかりがち” なのがポート問題 😇🧨

Grafana はデフォルトで `http://localhost:3000` を使います。([Grafana Labs][3])
もし **あなたのAPIがすでに 3000 をホスト側で使ってる**なら、先にどちらかをズラしましょう👇（おすすめは「APIのホスト側ポートだけ変更」）

---

### 1) `compose.yml` に Grafana を追加する ➕🖼️

以下は「Prometheus が `prometheus` というサービス名で動いている」前提の最小例です（すでにある `prometheus` / `api` は“追記 or 調整”してね）👍

```yaml
services:
  # 既存の api（例：コンテナ内 3000 → ホスト 8080 に逃がす）
  api:
    ports:
      - "8080:3000"

  # 既存の prometheus（例）
  prometheus:
    image: prom/prometheus:v3.9.1
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro

  # ★追加：grafana
  grafana:
    image: grafana/grafana:12.3.3
    ports:
      - "3000:3000"
    environment:
      # 初回ログイン用（後で変更する前提）
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
    depends_on:
      - prometheus

volumes:
  grafana-data:
```

💡パスワードはこの章では “まず動かす” 優先で `admin/admin` にしています（あとでちゃんと変えようね🔒）。
Grafana は初回サインイン時に `admin/admin` を使い、ログイン後に変更を促す挙動がドキュメントに書かれています。([Grafana Labs][3])
また、Docker 環境でパスワードを環境変数やシークレットで渡す方法も公式に案内があります。([Grafana Labs][4])

---

### 2) 起動する 🚀

```bash
docker compose up -d
docker compose ps
```

* Grafana: `http://localhost:3000`
* Prometheus: `http://localhost:9090`
* API: `http://localhost:8080`（例）

---

### 3) Grafana にログインする 🔑🖥️

1. ブラウザで `http://localhost:3000` を開く
2. ユーザー名 `admin`、パスワード `admin` でログイン
3. 「パスワード変えてね」的な画面が出たら変更（開発用でも変える癖つけると偉い👏）([Grafana Labs][3])

---

### 4) Prometheus をデータソースとして追加する 🔌📥

Grafana の画面から（UIの文言はバージョンで多少変わるけど流れは同じ）👇

* **Connections / Data sources** → **Add data source** → **Prometheus**
* **URL** にこれを入れる：

  * `http://prometheus:9090`（Compose内のサービス名で解決するパターン）
  * もしくはホスト参照なら `http://host.docker.internal:9090` も候補

⚠️超大事：**Grafanaコンテナ内での `localhost` は “Grafana自身”** を指します。Prometheus ではありません。
公式ドキュメントでも「Docker Compose ならホスト名（サービス名）を使ってね」と注意されています。([Grafana Labs][5])

* 最後に **Save & test**（テストが緑になったら勝ち🎉）

---

### 5) ダッシュボードを作る（4パネル）📊✨

Grafana の **Dashboards → New → New dashboard** → **Add visualization** で作っていきます。

ここからは「PromQL（プロムクエル）」っていうクエリをコピペでOKです 😄📋
（メトリクス名が違う場合は後述の“つまづき”を見てね🪤）

---

## ✅ パネル1：RPS（秒あたりリクエスト数）🏃‍♂️💨

**Query（PromQL）**：

```promql
sum(rate(http_requests_total[1m]))
```

* 単位：`req/s`（Grafana側で Unit を “requests/sec” とかにすると気持ちいい✨）
* 期待：`/ping` を連打すると上がる 📈

---

## ✅ パネル2：エラー率（5xx％）🧯🔥

**Query（PromQL）**（%表示）：

```promql
100 *
sum(rate(http_requests_total{status=~"5.."}[5m]))
/
sum(rate(http_requests_total[5m]))
```

* 期待：`/boom` を叩くと **グワッと上がる** 💥📈

---

## ✅ パネル3：p95（95%のリクエストはこれ以下）⏱️📉

**Query（PromQL）**（ヒストグラム前提）：

```promql
histogram_quantile(
  0.95,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
)
```

* Unit：seconds（“s”）にすると良いよ ⏱️
* 期待：`/slow` を叩くと p95 が上がる 🐢➡️📈

---

## ✅ パネル4：メモリ（プロセスの使用量）🧠💾

まずはこれ（よく使うやつ）👇

```promql
process_resident_memory_bytes
```

`prom-client` のデフォルトメトリクスには Node.js/プロセス系が含まれ、イベントループ遅延なども入ります（OSによって差がある旨も書かれてます）。([GitHub][6])
また `process_resident_memory_bytes` は Node プロセスが実際に使っているメモリ量（バイト）として解説されています。([Max Kim Blog][7])

💡もし “Heap” を見たいなら、こういう系もあります（環境による）👇

* `nodejs_heap_size_used_bytes`

---

### 6) グラフを “動かす” 実験（PowerShell）🧪📈

「データが無いとグラフは動かない」ので、意図的に叩きます 😆

例：API が `http://localhost:8080` の場合👇

```powershell
## /ping をたくさん
1..50 | % { irm http://localhost:8080/ping | Out-Null }

## /slow を混ぜる（p95が上がる）
1..10 | % { irm http://localhost:8080/slow | Out-Null }

## /boom を混ぜる（エラー率が上がる）
1..5 | % { try { irm http://localhost:8080/boom | Out-Null } catch {} }
```

Grafana の時間範囲を **Last 15 minutes** とかにして、右上の Refresh をちょいちょい押すと楽しいよ 😆🔄

---

## ④ 期待する見た目（チェック項目）✅👀

* RPS：連打した瞬間に **山ができる** 🏔️
* エラー率：`/boom` 叩いた直後に **%が上がる** 📛
* p95：`/slow` の直後に **遅延が上がる** 🐢⏱️
* メモリ：基本はなだらか、リークがあるとじわじわ上がる 📈🧠

---

## ⑤ つまづきポイント（3つ）🪤😵‍💫

1. **Prometheus のURLを `localhost:9090` にしてしまう**
   → Grafanaコンテナ内の localhost になるのでダメです🙅‍♂️
   → Composeなら `http://prometheus:9090` を使うのが基本。([Grafana Labs][5])

2. **No data（データ無い）**
   → まずリクエストを発生させよう（PowerShell連打）🏃‍♂️💨
   → 時間範囲が「Last 5 minutes」になってて外してることも多い ⏳

3. **メトリクス名が違う**
   → `http://localhost:8080/metrics`（あなたのAPIの /metrics）を開いて、
   そこに出てる “本当の名前” をコピペするのが最短です ✂️📋
   → Grafana のクエリ欄には “Metrics browser” 的な候補も出ます 👀✨

---

## ⑥ ミニ課題（15分）⏳🏆

次のどっちか1個でOK！

**A. ルート別RPSを出す** 🚪📈

```promql
sum by (route) (rate(http_requests_total[1m]))
```

（※ label が `route` じゃないなら、あなたのメトリクスのラベル名に合わせてね）

**B. “今のエラー率” を Stat パネルで出す** 🚨

* パネルを “Time series” じゃなく “Stat” にして、
* エラー率クエリを入れて、表示を “Last” にする

---

## ⑦ AIに投げるプロンプト例（コピペOK）🤖📋

```text
GrafanaでPrometheusを可視化したいです。
/metrics には次のメトリクスがあります：
（ここに /metrics の該当部分を貼る）

やりたいのは：
1) RPS（req/s）
2) 5xxエラー率（%）
3) p95レイテンシ
4) メモリ量

それぞれのPromQLと、Grafanaパネル設定（Unit/Legend/おすすめの時間範囲）を提案してください。
```

```text
Grafanaで “No data” になります。
状況：
- GrafanaとPrometheusはdocker compose
- Data source URL は（ここにURL）
- Prometheus targets は（UP/DOWNをここに）
- /metrics は（取れてる/取れてない）
原因候補を優先度順に出して、確認手順を最短で教えてください。
```

---

次の第22章（アラート）に行く前に、今のダッシュボードに **「赤信号（エラー率）」と「黄信号（p95）」** が見えてる状態にしておくと、アラートの話が一気に気持ちよくなります 🚦😆

[1]: https://grafana.com/grafana/download "Download Grafana | Grafana Labs"
[2]: https://prometheus.io/download/ "Download | Prometheus"
[3]: https://grafana.com/docs/grafana/latest/setup-grafana/sign-in-to-grafana/?utm_source=chatgpt.com "Sign in to Grafana | Grafana documentation"
[4]: https://grafana.com/docs/grafana/latest/setup-grafana/configure-docker/?utm_source=chatgpt.com "Configure a Grafana Docker image"
[5]: https://grafana.com/docs/grafana/latest/datasources/prometheus/configure/?utm_source=chatgpt.com "Configure the Prometheus data source"
[6]: https://github.com/siimon/prom-client?utm_source=chatgpt.com "siimon/prom-client: Prometheus client for node.js"
[7]: https://maxkim-j.github.io/en/posts/nodejs-server-monitoring/?utm_source=chatgpt.com "Understanding your Nodejs server monitoring environment ..."
