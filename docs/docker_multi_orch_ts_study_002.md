# 第02章：クラスタの登場人物（Control Plane / Node / Pod）👥🗺️☸️

この章は「Kubernetesクラスタの“地図”を頭に入れる回」です🧠✨
ここがスッと入ると、以後の設定やトラブル対応がめちゃ楽になります👍

---

![Control Plane vs Node](./picture/docker_multi_orch_ts_study_002_01_cp_vs_node.png)

## 0. まずは“全体地図”だけ暗記でOK🗺️📌

Kubernetesクラスタは、ざっくりこの2階建てです👇

* **Control Plane（司令塔）**：何をどこで動かすか決めて、全体を管理する🧠
* **Worker Node（実行部隊）**：実際にアプリ（Pod）を動かす💪

公式ドキュメントでもこの切り分けで説明されています。([Kubernetes][1])

---

![Control Plane Components](./picture/docker_multi_orch_ts_study_002_02_cp_components.png)

## 1. Control Plane って何してるの？🧠📣

Control Plane は「クラスタの脳みそ🧠」です。
“状態（あるべき姿）”を見て、現実をそこへ寄せ続けます（宣言型のコア感覚）✨

代表的な部品たちはこんな感じ👇（役割イメージ付き🎭）

* **kube-apiserver**：クラスタの“受付”🚪
  `kubectl` も他の部品も、基本ここに話しかけます。
* **etcd**：クラスタの“台帳（データベース）”📚
  「いまの状態」「あるべき状態」が保存されます。
* **kube-scheduler**：配置の“割り振り係”🧑‍🍳
  新しいPodを「どのNodeに置くか」を決めます。
* **kube-controller-manager**：状態を保つ“監督”👮
  「足りないなら増やす」「壊れたら作り直す」などを回します。
* **cloud-controller-manager**：クラウド連携の“窓口”☁️
  LBやノード情報など、クラウド側の事情とつなぎます。

この構成は公式のアーキテクチャ説明でも整理されています。([Kubernetes][2])

🧠覚え方（超ざっくり）
**API Server＝入口🚪 / etcd＝記憶🧠 / scheduler＝席決め🪑 / controller＝整合性の維持🧹**

---

![Node Components](./picture/docker_multi_orch_ts_study_002_03_node_components.png)

## 2. Node（ワーカーノード）って何してるの？🖥️🏃‍♂️

Node は「Podを走らせるマシン（またはその概念）」です🏃‍♂️💨
Node上には、だいたい次の部品がいます👇

* **kubelet**：Nodeの“現場監督”🧑‍🔧
  「このPodを動かせ」という指示を受け、コンテナを起動・監視します。
* **container runtime**：コンテナを実際に動かす“エンジン”⚙️
* **kube-proxy（任意/環境によっては不要）**：通信の“さばき係”📡
  Service周りの転送などに関わります（ただし“optional”扱いのケースもあります）。([Kubernetes][2])

---

![Pod Concept](./picture/docker_multi_orch_ts_study_002_04_pod_concept.png)

## 3. Pod（ポッド）って何？なぜ“最小の実行単位”なの？🧩🐣

Podは「Kubernetesが管理する“最小の実行単位”」です🐣
ここ、Dockerの感覚だとズレやすいので丁寧にいきます🙂

![Pod Networking](./picture/docker_multi_orch_ts_study_002_05_pod_networking.png)

## Podのポイント3つ✅✅✅

1. **Podは“1個以上のコンテナ”をまとめる箱**📦

* たいていは **1 Pod = 1 コンテナ** で運用されがち
* でも **複数コンテナ** もできる（例：ログ収集のサイドカー🪵）

2. **Pod内のコンテナは“同じネットワーク空間”を共有**🌐

* 同じPod内なら `localhost` で話せたりします🔁

3. **Podは“作り直される前提”**🔁

* 落ちたら作り直すのが基本（「壊れたら直す」より「壊れたら交換」🧯➡️🆕）

この「Control Plane / Node / Pod」の整理は、公式の“Components / Architecture”の軸そのものです。([Kubernetes][1])

---

![Architecture Diagram](./picture/docker_multi_orch_ts_study_002_07_architecture_diagram.png)

## 4. いったんこのASCII図を頭に貼ろう🧠📌

```text
あなた（kubectl）
   |
   v
[ Control Plane ]  ← 司令塔（API Server / Scheduler / Controllers / etcd）
   |
   v
+-------------------+      +-------------------+
|     Node A        |      |     Node B        |
|  kubelet + runtime|      |  kubelet + runtime|
|   [ Pod ] [ Pod ] |      |   [ Pod ] [ Pod ] |
+-------------------+      +-------------------+
```

---

## 5. ミニ実験：いま“どこで何が動いてるか”を覗く👀🔎

> ここでは「見るだけ」でOKです🙆
> （実際にクラスタ作るのは次の章でがっつり🏗️）

## 5.1 Node一覧を見る🖥️

```bash
kubectl get nodes -o wide
```

見るポイント👀

* Node名（ローカル学習だと「control-plane」「worker」みたいに出たり）
* OS/Kernel/Container Runtime
* INTERNAL-IP（環境によって見え方が違う）

## 5.2 いま動いてるPodを全部見る（まずは眺める）📦

```bash
kubectl get pods -A -o wide
```

見るポイント👀

* `kube-system` に “クラスタ運営メンバー” がいる
* PodがどのNodeに乗ってるか（`NODE`列）🪑

## 5.3 「Control Planeっぽいもの」を探す🧠

環境によって見え方は違いますが、だいたい `kube-system` にいます👇

```bash
kubectl get pods -n kube-system -o wide
```

## 5.4 Nodeを1つ選んで、詳細を読む🧾

```bash
kubectl describe node <node-name>
```

ここが宝の山💎

* **Conditions**（Readyか？）✅
* **Capacity/Allocatable**（どれだけ載せられる？）🍰
* **Events**（最近なにが起きた？）🧯

---

## 6. “初心者あるある”誤解を先に潰す😈➡️😇

![Disposable Pod](./picture/docker_multi_orch_ts_study_002_06_disposable_pod.png)

## 誤解1：Pod = コンテナ でしょ？🤔

**近いけど違う！**
Podは「コンテナを包む“実行単位の箱”📦」で、複数コンテナもあり得ます🐙

## 誤解2：Node = VM でしょ？🤔

多くの現場ではVM/物理マシンですが、**概念としては“Podを動かす場所”**です🧭
ローカル学習では、裏でコンテナやVMが使われます🧰

## 誤解3：Control Plane はアプリと無関係？🤔

アプリを動かすのはWorkerですが、**「いつ/どこで/何個」動かすかを決め続ける**のはControl Planeです🧠✨

---

## 7. ミニクイズ（3問だけ）📝🎯

1. **「PodをどのNodeに置くか」を決めるのは誰？**
2. **クラスタの“台帳（状態を保存）”はどれ？**
3. **Node上で「Podを起動しろ！」を実行する担当は？**

<details>
<summary>答えを見る👀</summary>

1. kube-scheduler 🧑‍🍳
2. etcd 📚
3. kubelet 🧑‍🔧

（ぜんぶ公式の構成要素の説明に載ってます）([Kubernetes][1])

</details>

---

## 8. AIで楽するポイント（第2章）🤖✨

* `kubectl describe node ...` の結果を貼って
  「**このNodeで怪しい点を3つ**」「**次に見るコマンドを順番に**」って聞く🔎🧭
* Pod/Node/Control Planeの違いを
  「**高校生でも分かる例え**で」って頼む📚🙂

---

## まとめ🏁✨

* **Control Plane**＝司令塔🧠（状態を保存し、配置を決め、整合性を保つ）([Kubernetes][2])
* **Node**＝実行部隊💪（kubelet + runtime が現場で動かす）([Kubernetes][2])
* **Pod**＝最小の実行単位🐣（コンテナを包む箱、作り直される前提）([Kubernetes][1])

---

## 次章チラ見せ👀🏗️

次はローカルに“擬似マルチノード”環境を作って、今日の地図を現実の出力に紐付けます🔥
ちなみに最近の流れだと、ローカル学習では kind / minikube が定番で、kindはKubernetes 1.35系をデフォルトにしているリリースも出ています。([GitHub][3])

---

必要なら、この章の内容に合わせて「用語カード（10枚）🃏」と「小テスト（穴埋め）✍️」も作るよ🙂💫

[1]: https://kubernetes.io/docs/concepts/overview/components/?utm_source=chatgpt.com "Kubernetes Components"
[2]: https://kubernetes.io/docs/concepts/architecture/?utm_source=chatgpt.com "Cluster Architecture"
[3]: https://github.com/kubernetes-sigs/kind/releases?utm_source=chatgpt.com "Releases · kubernetes-sigs/kind"
