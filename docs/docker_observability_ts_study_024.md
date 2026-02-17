# 第24章：ヘルスの考え方：生存/準備/起動の違い 👶➡️🏃‍♂️

## ① 今日のゴール 🎯✨

この章が終わったら、次の3つを「一言＋例」で説明できるようになります👇

* **liveness（生存）**：死んでたら再起動したい？🔁
* **readiness（準備）**：今、リクエスト受けていい？🚦
* **startup（起動）**：起動中に誤判定で殺されたくない…😇

（Kubernetesの定義が一番わかりやすい“教科書”なので、それを軸に理解します）([Kubernetes][1])

---

## ② まずは超ざっくりイメージで掴む 🧠💡

![Three Probes Characters](./picture/docker_observability_ts_study_024_01_three_probes_characters.png)

### 🫀 liveness（生存）＝「心臓が動いてる？」

* 目的：**固まってたら再起動して復活させる**
* 典型例：アプリが**デッドロック**して応答不能になったら、再起動が正義💥🔁
  Kubernetesでは、livenessが失敗し続けると**コンテナを再起動**します。([Kubernetes][1])

### 🚦 readiness（準備）＝「今、お客さん入れていい？」

* 目的：**準備できてないなら“受け口”から外す（でも再起動はしない）**
* 典型例：DB接続中、キャッシュ温め中、移行処理中…この状態でトラフィック受けると事故りやすい😵‍💫
  Kubernetesではreadinessが失敗すると、Podを**Serviceのエンドポイントから外して**トラフィックを止めます。([Kubernetes][1])

### 🐣 startup（起動）＝「起動中だから待って！」

* 目的：**起動に時間がかかる系アプリが、起動途中で誤って“死亡扱い”されるのを防ぐ**
* 重要ポイント：startup probeを設定すると、**それが成功するまでliveness/readinessを無効化**してくれます。([Kubernetes][1])

---

## ③ 図で理解する 🖼️✨

![Probe Lifecycle Flow](./picture/docker_observability_ts_study_024_02_probe_lifecycle_flow.png)

```text
[コンテナ起動] 
   |
   v
[startup OK？]  ----(まだ)----> 起動準備中 🐣（待ってほしい）
   |
  OK
   v
[readiness OK？] --(NG)--> トラフィック停止 🚦（でも生かしておく）
   |
  OK
   v
[通常運転]  ←→  (定期チェック) liveness OK？ 🫀
   |
 (NGが続く)
   v
[再起動] 🔁
```

---

## ④ 「Dockerだけの世界」だとどう考える？🐳🧩

![Docker Healthcheck Params](./picture/docker_observability_ts_study_024_03_docker_healthcheck_params.png)

ここが混乱ポイントです😵‍💫
Docker（単体）には **“liveness/readiness/startup” の3種類がそのまま存在するわけじゃなくて**、基本は **HEALTHCHECK（健康チェック）1本**です。

### Docker HEALTHCHECK の要点 🧪

* health状態は最初 **starting** → 成功で **healthy** → 失敗が続くと **unhealthy**
* オプションで

  * **interval / timeout / retries**
  * **start-period（起動猶予）** ← 起動直後の失敗をノーカンにできる🙏
  * **start-interval**（start-period中の間隔）※ **Docker Engine 25.0+** が必要
    …みたいにチューニングできます。([Docker Documentation][2])

### Composeで「依存が準備できたら起動」をやる 🚥

Composeは、ただの起動順だけだと「動いてるけど準備できてない」を待てません。
なので **depends_on + condition: service_healthy** を使うと、「依存がhealthcheckでhealthyになるまで待つ」ができます。([Docker Documentation][3])

---

## ⑤ じゃあ結局、どう設計すると事故らない？🧯✨

![Probe Design Rules](./picture/docker_observability_ts_study_024_04_probe_design_rules.png)

ここは“現場で効く型”として覚えましょう👇

### ✅ ルール1：liveness は「軽い・単純」が正義 🫀⚡

* **依存サービス（DB/Redis/外部API）を見に行かない**のが基本

  * 依存が落ちてるだけで再起動ループすると地獄👹
* 「アプリが固まってないか」を見る（＝**自分のプロセスが健全か**）

Kubernetesでもlivenessは「固まり検知→再起動」に使う、と明確に書かれています。([Kubernetes][1])

### ✅ ルール2：readiness は「受けていい状態か？」を正直に 🚦🧩

* DB接続できない、必須リソースが揃ってない、負荷で自衛したい
  → **readinessをNGにして“入口を閉じる”**のが強い💪
  Kubernetesはreadiness失敗でエンドポイントから外します。([Kubernetes][1])

### ✅ ルール3：startup は「起動直後だけ特別扱い」🐣⏳

* 起動処理が重いアプリは、livenessで誤判定されがち
  → startupで「起動完了」まで守る🛡️
  成功するまでliveness/readinessを止める仕様です。([Kubernetes][1])

---

## ⑥ ミニ課題：「DBが落ちてる時、/healthはどう返す？」🤔🧠

![DB Down Scenario](./picture/docker_observability_ts_study_024_05_db_down_scenario.png)

あなたがAPI作者だとして、次を決めてください👇

* **ケースA：DBが落ちてる**（ただしAPIプロセス自体は元気）

  * 🫀 liveness：どうする？
  * 🚦 readiness：どうする？

おすすめ回答（超よくある安全設計）👇

* 🫀 liveness：**OK（200）**

  * 理由：DB障害でコンテナ再起動しても直らないことが多い💦（再起動ループの芽）
* 🚦 readiness：**NG（503など）**

  * 理由：準備できてないのでトラフィック止める🚦

※「HTTPコードで判定する」文化が強いです。Kubernetes APIサーバの health/live/ready でも **200ならOK**として扱う、と明記されています。([Kubernetes][4])

---

## ⑦ つまづきポイント（あるある3つ）🪤😵‍💫

![Restart Loop Trap](./picture/docker_observability_ts_study_024_06_restart_loop_trap.png)

1. **ヘルスでDBを見に行って再起動ループ**👹🔁
   → livenessは軽く。依存はreadiness側へ。

2. **ヘルスが重くて、ヘルス自体がボトルネック**🐢
   → 「1秒以内で返す」くらいの気持ちで。重い集計や外部APIは避ける。

3. **起動が遅いのに start-period / startup を入れてなくて誤判定**😇
   → Dockerなら start-period、Kubernetesなら startup probe をちゃんと用意。

---

## ⑧ 15分ハンズオン（設計だけやる）📝✨

![API Health Endpoints](./picture/docker_observability_ts_study_024_07_api_health_endpoints.png)

次章で実装に入る前に、まず「仕様」を固めます👇

### あなたのミニAPIに追加するエンドポイント案

* `/health`（liveness用）🫀
* `/ready`（readiness用）🚦
* `/startup`（startup用）🐣（もしくは “起動完了フラグ” を内部で持つ）

### “判断材料”の例（コピペしてメモにしてOK）📌

* `/health`：プロセスが応答できる（イベントループが詰まってない）
* `/ready`：DBに軽い疎通ができる、必須設定が揃った
* `/startup`：初期化（マイグレーション/キャッシュ準備）が終わった

---

## ⑨ AIに投げるプロンプト例（コピペOK）🤖📋

```text
あなたはSRE兼バックエンド設計レビュー担当です。
Node/TypeScriptのAPIに health を設計します。

要件：
- /health は liveness 用（依存サービスを見ない）
- /ready は readiness 用（DB疎通など “受けてよい状態” を見る）
- 起動が遅いので startup の考え方も入れたい
- 返すHTTPコード（200/503など）とJSON例を提案して
- よくあるアンチパターン（再起動ループ等）も指摘して
```

---

## ⑩ まとめ 💚✨

* 🫀 **liveness**：ダメなら再起動したい“致命的停止”の検知
* 🚦 **readiness**：準備できてないなら“入口を閉じる”
* 🐣 **startup**：起動中の誤判定を防ぐ“保護期間”

次の第25章では、まず **/health を「固定200で軽く」** 作って、ヘルスの土台を置きます ✅🚀

[1]: https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/ "Liveness, Readiness, and Startup Probes | Kubernetes"
[2]: https://docs.docker.com/reference/dockerfile/ "Dockerfile reference | Docker Docs"
[3]: https://docs.docker.com/compose/how-tos/startup-order/ "Control startup order | Docker Docs"
[4]: https://kubernetes.io/docs/reference/using-api/health-checks/?utm_source=chatgpt.com "Kubernetes API health endpoints"
