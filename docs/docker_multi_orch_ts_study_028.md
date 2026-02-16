# 第28章：トラブルシュート道場（CrashLoop / Pending / NotReady）🥋🔥

この章は「事故っても直せる人」になる回です😎✨
Kubernetesは“落ちたら勝手に立ち上げ直す”のが得意。でも、**なぜ落ちたか**を放置すると永遠に苦しみます😂
ここでは **ありがち3大事故**を、**最短ルートで切り分ける“型”**として体に入れます🧠💪
（Kubernetes v1.35系の最新ドキュメント内容を前提にしています）([Kubernetes][1])

---

## 0) 道場の“型” 🥷（困ったらこれだけ）

## まずは30秒ルーティン⏱️

1. **現象確認**：Podが何状態？（CrashLoop？Pending？RunningだけどReady=0？）
2. **証拠採取**：`describe` と `logs` と `events`
3. **原因を分類**：

   * アプリが死んでる？（exit / 例外 / 設定ミス）
   * クラスタ都合？（スケジューリング / リソース / ノード）
   * 設定ミス？（env / volume / probe / image）

Kubernetes公式も、CrashLoopBackOffは「指数バックオフで再起動を繰り返す状態」で、まず **ログ / イベント / 設定 / リソース**を見ろって言ってます🧾([Kubernetes][1])

---

## 1) 道場の準備（練習用namespace）🏗️

PowerShellでOKです🪟✨

```powershell
kubectl create namespace dojo
kubectl config set-context --current --namespace=dojo
```

「dojo」内だけで壊して直すので安心😌🛡️

---

## 2) CrashLoopBackOff 道場 💥🔁（“落ちて→起きて→また落ちる”）

## 2-1) わざと壊す（最小のCrashLoop）😈

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: crashloop-sample
spec:
  containers:
    - name: app
      image: busybox:1.36
      command: ["sh", "-c", "echo boom; sleep 1; exit 1"]
  restartPolicy: Always
```

```powershell
kubectl apply -f .\crashloop.yaml
kubectl get pods -w
```

しばらくすると `CrashLoopBackOff` が出ます👀
これはKubernetesが「すぐ再起動→また失敗」を繰り返すので、**再起動間隔を指数的に伸ばしてる**状態です（過負荷防止）([Kubernetes][1])

---

## 2-2) 最短3手で切り分ける ✂️

## 手1：状態を掴む（終了理由・ExitCode）🧾

```powershell
kubectl describe pod crashloop-sample
```

見る場所（超重要）👇

* `State:` / `Last State:`（Terminated の reason / exit code）
* `Events:`（BackOff / probe失敗 / 取得失敗 など）

## 手2：ログを見る（“直前に何が起きたか”）🪵

```powershell
kubectl logs crashloop-sample
```

## 手3：**ひとつ前の落ちた回**のログを見る（これ神🙏）

```powershell
kubectl logs crashloop-sample --previous
```

`--previous` は、再起動を繰り返してる時の鉄板ムーブです🧠([Kubernetes][2])

---

## 2-3) 典型原因と“直し方テンプレ”🧰✨

Kubernetes公式が挙げる代表原因はこんな感じ👇（ここ、まんま現場で出ます）([Kubernetes][1])

* **アプリが落ちる**（例外・exit 1）
  → まずログ。次に設定（env/ConfigMap/Secret）を疑う
* **設定ミス**（環境変数名ミス、必要ファイルが無い、volume mount先違い）
  → `describe` の Events がヒントをくれることが多い
* **リソース不足**（メモリ足りず起動できない、OOMKill）
  → `describe` で `OOMKilled` とか出る。requests/limits見直し
* **probe失敗**（起動に時間かかるのにreadiness/livenessが厳しすぎ）
  → `startupProbe` を入れる or 初期猶予を伸ばす（前章のprobe知識が活きる❤️‍🩹）

---

## 2-4) “直ったか確認”の儀式 ✅🎉

```powershell
kubectl get pods -o wide
kubectl describe pod crashloop-sample
kubectl logs crashloop-sample --previous
```

* Readyが `1/1` になった？
* Eventsが落ち着いた？
* `--previous` に致命ログが残ってない？

---

## 2-5) 2026っぽい小ネタ（CrashLoopの“仕様”が言語化された）📌

v1.35系のPod Lifecycleドキュメントでは、CrashLoopBackOffの仕組み（指数バックオフ・リセット条件など）がかなり明確に整理されています🧠
「なぜ間隔がどんどん伸びるの？」って疑問がスッと消えます😄([Kubernetes][1])

---

## 3) Pending 道場 ⏳🚧（“スケジュールできない”）

Pendingは一言でいうと👇
**「実行する席（ノード）が決まらない／座れない」**状態です🪑💦

## 3-1) わざとPendingにする（CPU要求を盛りすぎ）🍚盛りすぎ注意

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pending-sample
spec:
  containers:
    - name: app
      image: nginx:1.27
      resources:
        requests:
          cpu: "100"     # わざと無茶
          memory: "256Mi"
```

```powershell
kubectl apply -f .\pending.yaml
kubectl get pods -w
```

---

## 3-2) Pendingの最短3手 ✂️

## 手1：まずEventsを見る（答えが書いてある率高い）📣

```powershell
kubectl describe pod pending-sample
```

`Events:` にだいたいこういうのが出ます👇

* `FailedScheduling`
* `Insufficient cpu` / `Insufficient memory`
* `node(s) had taint ...`
* `0/3 nodes are available` など

公式ドキュメントでも、Pendingは `describe` のイベント確認が基本ムーブです🧭([Kubernetes][2])

## 手2：Node側の状況をざっくり見る 🏢

```powershell
kubectl get nodes
kubectl describe node <node-name>
```

## 手3：要求（requests）と条件（nodeSelector/affinity/taint）を疑う🔍

* **requestsが強すぎ** → まず下げる / Pod数を減らす
* **nodeSelector / affinity が厳しすぎ** → 合うノードが無い
* **taint に弾かれてる** → toleration無いと座れない（次の節）
* **PVC未バインド** → ストレージが確保できず詰む（PV/PVC回の復習💾）

---

## 3-3) Pending原因ランキング（体感）🏆

## ① requests盛りすぎ問題 🍔

複数マシン世界では「みんなの冷蔵庫」なので、**取り分宣言**が強すぎると席が無い😂
requests/limitsの基本は公式タスクにもまとまってます([Kubernetes][3])

## ② taintで弾かれてる問題 🧷

代表例：Control Planeに「アプリ載せるな」taintが付いてる、など。
tolerationが無いPodは `NoSchedule` で弾かれます🚫([Kubernetes][4])

## ③ 条件が厳しすぎ問題（nodeSelector/affinity）🎯

「このラベルのノードにしか置かない！」って言ってるのに、そんなノードが存在しない、よくある🥲

---

## 4) NotReady 道場 🚑🧱（“ノードが病んでる”）

NotReadyは、ざっくり言うと👇
**「そのノードのkubeletがControl Planeに健康報告できてない」**状態です📡💥
GKEのトラブルシュートでも、NotReadyは「kubeletが正しく報告できてない状態」で、新しいPodを載せられなくなって容量が減る＝障害につながる、と整理されています([Google Cloud Documentation][5])
またKubernetes公式のクラスタデバッグでも、NotReadyが続くとPodが追い出され得る点に触れています([Kubernetes][6])

---

## 4-1) まずは現象確認 👀

```powershell
kubectl get nodes -o wide
kubectl describe node <node-name>
```

`Conditions:` のここを見る👇

* `Ready`
* `MemoryPressure` / `DiskPressure` / `PIDPressure`
* `NetworkUnavailable`

---

## 4-2) ローカル練習：kindなら“ノード停止”で再現できる 🧪（任意）

kindはノードがDockerコンテナなので、止めるとそれっぽく再現できます😈
（※普段の環境を壊したくない人は読み物としてOK）

```powershell
docker ps --format "table {{.Names}}\t{{.Status}}"
## 例: kind-worker, kind-control-plane などが見える
docker stop kind-worker
kubectl get nodes -w
```

---

## 4-3) NotReadyの原因“あるある”と復旧の方向性🧯

* **ノードが落ちてる／ネットワーク不通**
  → そのノードが復帰するまで待つ or 再起動 or 交換
* **ディスク逼迫（DiskPressure）**
  → ログ/イメージが溜まりすぎ、など
* **コンテナランタイム／kubeletが死んでる**
  → “kubeletが報告できない”系（NotReadyの本丸）([Google Cloud Documentation][5])

ローカル学習では「ノード（VM/コンテナ）再起動」で戻ることが多いですが、本番だと **ノード交換（自動修復）**が基本戦略になります🛠️（ここは第30章の運用ロードマップにつながる🗺️）

---

## 5) “最後の切り札” kubectl debug（エフェメラルコンテナ）🪄🕵️‍♂️

アプリのコンテナが **distroless** とかで「シェル無い！curl無い！」って時、普通に中に入れなくて詰みます😂
そんな時に `kubectl debug` で **デバッグ用コンテナを横付け**できます🚀
公式ドキュメントに手順がまとまっています([Kubernetes][2])

例（BusyBoxを一時的に差し込むイメージ）👇

```powershell
kubectl debug -it crashloop-sample --image=busybox:1.36 --target=app
```

* `--target` は「同じPod内の対象コンテナの名前」を指定する用途（環境によって要否あり）
* ここで `nslookup` / `wget` / `cat /etc/resolv.conf` みたいな“現場チェック”ができます🧰

---

## 6) チートシート（この章の持ち帰り）🧾✨

## CrashLoopBackOff の型 💥

1. `kubectl describe pod <pod>`
2. `kubectl logs <pod> --previous`
3. **原因分類**：アプリ／設定／リソース／probe
   （公式の整理がこの順で効く）([Kubernetes][1])

## Pending の型 ⏳

1. `kubectl describe pod <pod>` の `FailedScheduling` を読む
2. requests / nodeSelector / taint / PVC を疑う
3. `kubectl describe node <node>` で根拠を取る([Kubernetes][2])

## NotReady の型 🚑

1. `kubectl describe node <node>` の Conditions/Events
2. Pressure系（Disk/Memory/PID）か、kubelet報告断かを切る
3. ローカルはノード再起動、本番はノード交換が基本線([Google Cloud Documentation][5])

---

## 7) AIに投げる用テンプレ（コピペOK）🤖🧠

* CrashLoop用：

  * 「以下は `kubectl describe pod` と `kubectl logs --previous` です。**原因候補を3つ**、それぞれ **確認コマンド**と **直し方**もセットで出して」
* Pending用：

  * 「この `FailedScheduling` のEventsを読んで、**最も可能性が高い原因**と、**マニフェスト修正案**を出して」
* NotReady用：

  * 「この `kubectl describe node` のConditionsとEventsから、**疑う順番**を作って。ローカル(kind/minikube)前提の対処も添えて」

---

次の第29章（Helm 4 / Kustomize）に進む前に、ここで一度だけ自分にご褒美をあげてください🍰
**CrashLoop/Pending/NotReadyを“意図的に作って”→“最短で直す”**を1周すると、Kubernetesが一気に怖くなくなります😆🥋

[1]: https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/ "Pod Lifecycle | Kubernetes"
[2]: https://kubernetes.io/docs/tasks/debug/debug-application/debug-running-pod/ "Debug Running Pods | Kubernetes"
[3]: https://kubernetes.io/docs/tasks/configure-pod-container/resize-container-resources/?utm_source=chatgpt.com "Resize CPU and Memory Resources assigned to Containers"
[4]: https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/?utm_source=chatgpt.com "Taints and Tolerations"
[5]: https://docs.cloud.google.com/kubernetes-engine/docs/troubleshooting/node-notready?utm_source=chatgpt.com "Troubleshoot nodes with the NotReady status in GKE"
[6]: https://kubernetes.io/ja/docs/tasks/debug/debug-cluster/?utm_source=chatgpt.com "クラスターのトラブルシューティング"
