# 複数マシン前提オーケストレーション（Kubernetes等）30章アウトライン 🚀🐳☸️

* Kubernetesの最新リリースは **v1.35.1（2026-02-10）**（同日に1.34系もパッチ更新あり）([Kubernetes][1])
* **Ingress NGINX** は “2026年3月までベストエフォート保守 → 以後はリリース/修正/脆弱性対応なし” の方針が公式に告知済み([Kubernetes][2])
* 代替の本命として **Gateway API がGA（v1.4.0）** として発表済み([Kubernetes][3])
* ローカル学習用は、**kind が v0.31.0（Kubernetes 1.35.0 をデフォルトに）**([GitHub][4])、**minikube は v1.38.0（2026-01-28）**([minikube][5])
* パッケージ管理は **Helm 4** がリリース済み（v3も猶予付きでサポート継続）([helm.sh][6])

## 第01章：Kubernetesって何を解決するの？🤔☸️

### 第01章：Kubernetesって何を解決するの？🤔☸️

* 🧠 Docker/Composeとの違い（「複数マシン」「自動回復」「宣言型」）をつかむ
* 🛠️ 例：Web/APIが落ちても勝手に復活するイメージを図で理解📈

### 第02章：クラスタの登場人物（Control Plane / Node / Pod）👥🗺️☸️

* 🧠 “どこで何が動いてるか”の地図を作る🗺️
* 🛠️ Podが「最小の実行単位」な理由を体感💡

### 第03章：ローカルで“擬似マルチノード”クラスタを作る🏗️🖥️☸️

* 🧠 1台PCでも「ノード複数」を再現できると学習が爆速⚡
* 🛠️ kind or minikube でクラスタ作成→ノード一覧を見る👀 ([GitHub][4])

### 第04章：kubectl はじめの10コマンド⌨️🎮

* 🧠 get / describe / logs / exec / delete の使い分け🧰
* 🛠️ 「困ったら describe と logs」ルーティンを作る🔁

### 第05章：マニフェスト入門（YAMLの読み方と“宣言型”）📄✨

* 🧠 apiVersion/kind/metadata/spec の型を覚える📦
* 🛠️ “手で書く→AIで整える→自分で読める”の順で慣れる🤖✅

🤖 **AIで楽するポイント（第1部）**

* 「このYAML何してる？」をAIに説明させる→自分の言葉で言い直す🗣️
* `kubectl describe` の出力を貼って「原因候補3つ」出させる🔎

---

## 第02章：クラスタの登場人物（Control Plane / Node / Pod）👥🗺️☸️

### 第06章：イメージを“クラスタに届ける”（レジストリ基礎）📦🚚

* 🧠 複数マシン＝各ノードがイメージを取りに行く、が基本🌍
* 🛠️ タグ設計（latest依存を減らす）＆pullできる状態にする🏷️

### 第07章：PodでNode/TS APIを動かす🍔🐳☸️

* 🧠 コンテナ起動・環境変数・ポートの基礎をK8s流に🔧
* 🛠️ まずは「1 Podで動いた！」を作る🎉

### 第08章：Deploymentで“落ちても戻る”を作る🛟🤖💥➡️😇

* 🧠 replicas / self-healing / rollout の入口🚪
* 🛠️ Podをわざと消して、勝手に復活するのを見る😈➡️😇

### 第09章：Serviceで“つなぐ”（サービスディスカバリ）🧷🧠✨

* 🧠 PodのIPは変わる→Serviceで固定化📌
* 🛠️ API→DB（ダミーでもOK）へ名前で接続してみる🔗

### 第10章：Namespace・Label・Selectorで“整理整頓”🧹🏷️🔎

* 🧠 大量のリソースを迷子にしない技🧭
* 🛠️ 「環境別」「機能別」で分けるミニ設計をやる📁

🤖 **AIで楽するポイント（第2部）**

* 「このDeploymentに足りない必須項目ある？」チェック係にする✅
* ラベル設計をAIに提案させて、自分の好みに寄せる🎨

---

## 第03章：ローカルで“擬似マルチノード”クラスタを作る🏗️🖥️☸️

### 第11章：ConfigMapで設定を外出しする🧩

* 🧠 コードと設定を分離して“環境差”に強くする🌱
* 🛠️ 1つ設定を変えて再デプロイ→挙動が変わるのを確認🔁

### 第12章：Secretの扱い方（やりすぎない安全）🔐✨

* 🧠 「置き場所」と「漏れ方」を先に知って事故を減らす🧯
* 🛠️ Secret参照でDBパスワードを注入してみる🧪

### 第13章：Probe（liveness / readiness / startup）で“壊れにくく”❤️‍🩹☸️

* 🧠 “起動中”と“故障中”を区別できるのが超重要⚖️
* 🛠️ readinessを入れて「起動直後の事故」を防ぐ🛡️

### 第14章：Rolling UpdateとRollback（安全に更新）🔄🛟

* 🧠 失敗しても戻せると、デプロイが怖くなくなる😌
* 🛠️ わざと壊した版を出す→即ロールバック🎢

### 第15章：Requests/Limits（CPU/メモリ）入門📏🍰☸️

* 🧠 “1台じゃなく皆で使う”ので、取り分の宣言が必要🍰
* 🛠️ Limit超過の挙動を見て、ログで気づけるようにする👀

🤖 **AIで楽するポイント（第3部）**

* 「このProbeの妥当値？」をAIにレビューさせる（理由付きで）🧠
* OOM/CPU不足っぽいログを貼って“何を見るべきか”を聞く🔍

---

## 第04章：kubectl はじめの10コマンド⌨️🎮

### 第16章：スケジューリング基礎（どのノードに置く？）🧲☸️

* 🧠 nodeSelector / affinity / taints&tolerations の感覚をつかむ🎯
* 🛠️ 「特定ノードにだけ置く」をやってみる🧪

### 第17章：HPAでオートスケール（負荷で増える）📈🔥

* 🧠 “トラフィック増＝Pod増”の基本パターン🚦
* 🛠️ CPU指標でHPA→負荷をかけて増えるのを見る🔥

### 第18章：Job/CronJob（バッチと定期実行）⏰🧑‍🍳📦

* 🧠 Webだけじゃない、裏方の仕事もK8sで回せる🧑‍🍳
* 🛠️ 日次の掃除タスク（ダミー）をCronJobで回す🧹

### 第19章：永続化（PV / PVC / StorageClass）💾🪴

* 🧠 “Podは消える”けど“データは残す”の仕組み🪴
* 🛠️ PVCを作って、再起動してもデータが残るのを確認✅

### 第20章：StatefulSet入門（DB系の扱い方）🧱🗃️

* 🧠 「名前が固定」「順序が大事」な世界に触れる🧠
* 🛠️ ミニDB（学習用）をStatefulSetで動かす📦

🤖 **AIで楽するポイント（第4部）**

* 「この要件、DeploymentとStatefulSetどっち？」を理由付きで判定させる⚖️
* PVC/Storageの用語を“超かみ砕き”で説明させる🥄

---

## 第05章：マニフェスト入門（YAMLの読み方と“宣言型”）📄✨

### 第21章：Ingressの基本と、2026年の注意点⚠️🌐🧭

* 🧠 Ingressは今でも頻出。でもコントローラ事情が超大事🧠
* 🛠️ “Ingress NGINXが引退予定”を踏まえ、代替ルートを先に知る📌 ([Kubernetes][2])

### 第22章：Gateway API入門（次世代の入口）🚪✨

* 🧠 GatewayClass / Gateway / Route の役割分担（“人の役割”っぽい）👥
* 🛠️ GAとして出ている前提で、HTTPルーティングの形を作る🧪 ([Kubernetes][3])

### 第23章：TLS（HTTPS）と証明書自動化の入口🔒📜

* 🧠 “手作業更新”を卒業する考え方🧘
* 🛠️ 学習用にTLS終端まで通す（小さく成功）✅

### 第24章：NetworkPolicyで“話していい相手”を決める🧱📡

* 🧠 マイクロサービス時代の“最小通信”の作法🧊
* 🛠️ API→DBだけ許可、みたいな制限を作ってみる🚧

### 第25章：RBAC入門（権限は最小が正義）👮‍♂️🔑🛡️

* 🧠 ServiceAccount/Role/RoleBinding の関係を理解🔗
* 🛠️ 「読めるだけ」「このnamespaceだけ」を実演🧪

🤖 **AIで楽するポイント（第5部）**

* 「このRoute設定、意図どおり？」をAIにテスト観点でレビューさせる🧪
* RBACはAIがミスりやすいので「最小権限になってる？」を必ず質問✅

---

## 第06章：イメージを“クラスタに届ける”（レジストリ基礎）📦🚚

### 第26章：SecurityContext（root回避・読み取り専用）🧷🛡️

* 🧠 “コンテナは安全そう”の幻想を捨てる😇➡️😈
* 🛠️ non-root＋readOnlyRootFilesystemを入れて動かす✅

### 第27章：観測性の入口（イベント・ログ・メトリクス）🔍📊✨

* 🧠 まずは kubectl で追える範囲を最大化する💪
* 🛠️ 典型障害を「イベント→ログ→原因」で辿る🧭

### 第28章：トラブルシュート道場（CrashLoop / Pending / NotReady）🥋🔥

* 🧠 ありがちな事故を“型”で処理できるようにする🧠
* 🛠️ わざと壊す→直す（最短手順をメモ化）📝

### 第29章：Helm 4 / Kustomizeで“配布・再利用”📦🎁

* 🧠 使い回せる形＝チーム/将来の自分が助かる🤝
* 🛠️ Helmでインストール→値差し替え→アップグレード体験🔄 ([helm.sh][6])

### 第30章：本番ロードマップ（マネージドK8s・アップグレード・GitOps）🗺️🏁🚀

* 🧠 「本番は自作しない」寄りが主流：AKS/EKS/GKEなどの考え方🧠
* 🛠️ GitOps（例：Argo CD）で“Gitが正”の運用に触れて締める🎉 ([GitHub][7])

🤖 **AIで楽するポイント（第6部）**

* 障害ログを貼って「最短の切り分け手順」を作らせる🧯
* Helm valuesの設計案を出させて、シンプルに削る✂️


## 第01章：Kubernetesって何を解決するの？🤔☸️

* (Auto-generated placeholder)

## 第02章：クラスタの登場人物（Control Plane / Node / Pod）👥🗺️☸️

* (Auto-generated placeholder)

## 第03章：ローカルで“擬似マルチノード”クラスタを作る🏗️🖥️☸️

* (Auto-generated placeholder)

## 第04章：kubectl はじめの10コマンド⌨️🎮

* (Auto-generated placeholder)

## 第05章：マニフェスト入門（YAMLの読み方と“宣言型”）📄✨

* (Auto-generated placeholder)

## 第06章：イメージを“クラスタに届ける”（レジストリ基礎）📦🚚

* (Auto-generated placeholder)

## 第07章：PodでNode/TS APIを動かす🍔🐳☸️

* (Auto-generated placeholder)

## 第08章：Deploymentで“落ちても戻る”を作る🛟🤖💥➡️😇

* (Auto-generated placeholder)

## 第09章：Serviceで“つなぐ”（サービスディスカバリ）🧷🧠✨

* (Auto-generated placeholder)

## 第10章：Namespace・Label・Selectorで“整理整頓”🧹🏷️🔎

* (Auto-generated placeholder)

## 第11章：ConfigMapで設定を外出しする🧩

* (Auto-generated placeholder)

## 第12章：Secretの扱い方（やりすぎない安全）🔐✨

* (Auto-generated placeholder)

## 第13章：Probe（liveness / readiness / startup）で“壊れにくく”❤️‍🩹☸️

* (Auto-generated placeholder)

## 第14章：Rolling UpdateとRollback（安全に更新）🔄🛟

* (Auto-generated placeholder)

## 第15章：Requests/Limits（CPU/メモリ）入門📏🍰☸️

* (Auto-generated placeholder)

## 第16章：スケジューリング基礎（どのノードに置く？）🧲☸️

* (Auto-generated placeholder)

## 第17章：HPAでオートスケール（負荷で増える）📈🔥

* (Auto-generated placeholder)

## 第18章：Job/CronJob（バッチと定期実行）⏰🧑‍🍳📦

* (Auto-generated placeholder)

## 第19章：永続化（PV / PVC / StorageClass）💾🪴

* (Auto-generated placeholder)

## 第20章：StatefulSet入門（DB系の扱い方）🧱🗃️

* (Auto-generated placeholder)

## 第21章：Ingressの基本と、2026年の注意点⚠️🌐🧭

* (Auto-generated placeholder)

## 第22章：Gateway API入門（次世代の入口）🚪✨

* (Auto-generated placeholder)

## 第23章：TLS（HTTPS）と証明書自動化の入口🔒📜

* (Auto-generated placeholder)

## 第24章：NetworkPolicyで“話していい相手”を決める🧱📡

* (Auto-generated placeholder)

## 第25章：RBAC入門（権限は最小が正義）👮‍♂️🔑🛡️

* (Auto-generated placeholder)

## 第26章：SecurityContext（root回避・読み取り専用）🧷🛡️

* (Auto-generated placeholder)

## 第27章：観測性の入口（イベント・ログ・メトリクス）🔍📊✨

* (Auto-generated placeholder)

## 第28章：トラブルシュート道場（CrashLoop / Pending / NotReady）🥋🔥

* (Auto-generated placeholder)

## 第29章：Helm 4 / Kustomizeで“配布・再利用”📦🎁

* (Auto-generated placeholder)

## 第30章：本番ロードマップ（マネージドK8s・アップグレード・GitOps）🗺️🏁🚀

* (Auto-generated placeholder)
---


[1]: https://kubernetes.io/releases/?utm_source=chatgpt.com "Releases"
[2]: https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/?utm_source=chatgpt.com "Ingress NGINX Retirement: What You Need to Know"
[3]: https://kubernetes.io/blog/2025/11/06/gateway-api-v1-4/?utm_source=chatgpt.com "Gateway API 1.4: New Features"
[4]: https://github.com/kubernetes-sigs/kind/releases?utm_source=chatgpt.com "Releases · kubernetes-sigs/kind - GitHub"
[5]: https://minikube.sigs.k8s.io/?utm_source=chatgpt.com "Welcome! | minikube"
[6]: https://helm.sh/blog/helm-4-released?utm_source=chatgpt.com "Helm 4 Released"
[7]: https://github.com/argoproj/argo-cd/releases?utm_source=chatgpt.com "Releases · argoproj/argo-cd"
