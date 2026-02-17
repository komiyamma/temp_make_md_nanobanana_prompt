# 第04章：kubectl はじめの10コマンド⌨️🎮

この章は「クラスタの中を“覗く＆いじる”ためのリモコン＝**kubectl**」を、最短で手になじませる回だよ〜😄✨
やることはシンプル！**“困ったら describe と logs”** を軸に、調査→原因→対処のループを回せるようにする🧠🔁

---

## ゴール🎯

* 迷子にならずに、いまクラスタで何が起きてるか確認できる👀
* Podが落ちた/動かないとき、まず何を見るべきか分かる🧯
* “よく使う10コマンド”をコピペで回せるようになる⌨️✨

---

## 今日の「はじめの10コマンド」一覧🔟🧰

> まずは名前だけでもOK！このあと実際に手を動かして覚えるよ👍

1. `kubectl version`：クライアント/クラスタのバージョン確認🧾
2. `kubectl config`：接続先（context）を確認・切り替え🗺️
3. `kubectl get`：一覧を見る（基本はこれ）📋
4. `kubectl describe`：詳細＋イベントを見る（超重要）🔍⚡
5. `kubectl logs`：ログを見る（超重要）📜🔥
6. `kubectl exec`：Podの中でコマンド実行（現場感）🧑‍🔧
7. `kubectl port-forward`：ローカルにポート転送して動作確認🔌
8. `kubectl apply`：マニフェストを反映（宣言型の入口）📄✅
9. `kubectl delete`：消す（検証→片付け）🧹
10. `kubectl explain`：YAMLの“辞書”を見る（次章の予告編）📚

※ 公式のコマンド一覧はここが基準だよ🧭 ([Kubernetes][1])

---

![Kubectl Remote](./picture/docker_multi_orch_ts_study_004_01_kubectl_remote.png)

## 0️⃣ まずは“詰まった時の型”を覚える🧠🥋

Kubernetesで困ったら、だいたいこの順番でOK👇

1. `kubectl get ...` で **状態** を見る👀
2. `kubectl describe ...` で **イベント**（何が起きたか）を見る⚡
3. `kubectl logs ...` で **アプリの声** を聞く📜
4. 必要なら `kubectl exec ...` で **中を調べる**🧰

この「イベント→ログ」の流れは公式のデバッグ手順でも基本になってるよ🧯 ([Kubernetes][2])

---

## 1️⃣ `kubectl version`：まず“ズレ”を潰す🧾🔧

最初にここで「見えない地雷」を消しておくと、後が楽😌

```bash
kubectl version --client --output=yaml
kubectl version --output=yaml
```

## よくあるポイント⚠️

* **kubectl のバージョンはクラスタと“±1マイナー以内”が基本**（例：v1.35のkubectlは、v1.34〜v1.36のControl Planeと会話できる）📏 ([Kubernetes][3])
* 直近のパッチ更新も把握しておくと安心（例：1.35.1のターゲット日程など）🗓️ ([Kubernetes][4])

---

## 2️⃣ `kubectl config`：いまどこ見てる？🗺️👀

「あれ？別クラスタ見てた😇」事故を防ぐやつ！

```bash
kubectl config current-context
kubectl config get-contexts
```

* `current-context`：**今の接続先**が一発で分かる✅
* `get-contexts`：候補一覧が出る📋

（クラスタを作る系のツールとして、学習では kind がKubernetes 1.35系をデフォルトにする更新が入ってたりするので、contextの見間違いはマジで起きやすい💥） ([GitHub][5])

---

![Get Command](./picture/docker_multi_orch_ts_study_004_02_get_command.png)

## 3️⃣ `kubectl get`：まずは一覧📋✨

K8sの基本動作は「とりあえず get」😄

```bash
kubectl get nodes
kubectl get pods
kubectl get deploy
kubectl get svc
kubectl get events
```

## よく使うオプション🎛️

```bash
kubectl get pods -o wide
kubectl get pods -w
kubectl get pods -A
kubectl get pods -n kube-system
kubectl get pods -l app=hello
```

* `-o wide`：Node配置やIPなど“現場情報”が増える🧠
* `-w`：状態変化を追いかける（Pending→Runningとか）👀
* `-A`：全Namespace（迷子になったらこれ）🧭
* `-n`：Namespace指定（「出てこない！」の9割はこれ）😇

---

![Describe Command](./picture/docker_multi_orch_ts_study_004_03_describe_command.png)

## 4️⃣ `kubectl describe`：詳細＋イベントで“犯人探し”🔍⚡

**困ったらこれ！**
最後の方に出る **Events** が宝の山💎

```bash
kubectl describe pod <pod-name>
kubectl describe node <node-name>
kubectl describe deploy <deploy-name>
```

## Eventsでよく見るやつ👀

* `ImagePullBackOff`：イメージ取れない📦❌
* `CrashLoopBackOff`：起動→落ちるのループ💥🔁
* `FailedScheduling`：置き場所がない（リソース不足/制約など）🪑❌

この “describeで状況→原因を絞る” は公式デバッグでも定番🧯 ([Kubernetes][2])

---

![Logs Command](./picture/docker_multi_orch_ts_study_004_04_logs_command.png)

## 5️⃣ `kubectl logs`：アプリの本音を聞く📜🔥

```bash
kubectl logs <pod-name>
kubectl logs -f <pod-name>
kubectl logs --since=10m <pod-name>
kubectl logs --tail=200 <pod-name>
```

マルチコンテナPodのときは `-c` が必須になることがあるよ👇

```bash
kubectl logs <pod-name> -c <container-name>
```

---

![Exec Command](./picture/docker_multi_orch_ts_study_004_05_exec_command.png)

## 6️⃣ `kubectl exec`：Podの中に入って調べる🧑‍🔧🧰

「環境変数どうなってる？」「ファイルある？」みたいな確認に便利✨

```bash
kubectl exec <pod-name> -- env
kubectl exec -it <pod-name> -- sh
```

💡 **注意**：イメージによっては `sh` が無い（distroless等）こともあるよ😇
その場合は `exec -- <実在するコマンド>` で調べる感じ！

---

![Port Forward](./picture/docker_multi_orch_ts_study_004_06_port_forward.png)

## 7️⃣ `kubectl port-forward`：ローカルから動作確認🔌🧪

「Ingress？Service？まだ早い！」って段階で、まず動作だけ見たいときの神コマンド✨
（`port-forward` はkubectlの正式コマンドだよ） ([Kubernetes][1])

```bash
kubectl port-forward pod/<pod-name> 8080:80
## または Deployment へ
kubectl port-forward deploy/<deploy-name> 8080:80
```

PowerShell なら、リクエスト確認はこれが分かりやすい👇

```powershell
curl.exe http://localhost:8080/
```

---

![Apply Command](./picture/docker_multi_orch_ts_study_004_07_apply_command.png)

## 8️⃣ `kubectl apply`：宣言型の入口📄✅

次章でYAMLの読み書きを本格的にやるけど、ここでは「反映する感覚」を掴もう😄

## コピペ用：ミニDeployment（nginx）🧪

VS Codeで `k8s/hello.yaml` を作って貼り付けてOK👇

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hello
spec:
  replicas: 1
  selector:
    matchLabels:
      app: hello
  template:
    metadata:
      labels:
        app: hello
    spec:
      containers:
        - name: web
          image: nginx:1.27-alpine
          ports:
            - containerPort: 80
```

反映！🚀

```bash
kubectl apply -f k8s/hello.yaml
```

確認！👀

```bash
kubectl get pods -l app=hello -o wide
```

---

## 9️⃣ `kubectl delete`：片付けもセット🧹✨

```bash
kubectl delete -f k8s/hello.yaml
```

または個別に👇

```bash
kubectl delete deploy/hello
```

---

## 🔟 `kubectl explain`：YAMLの“辞書”📚✨

「このフィールドって何？どんな型？」を **kubectl自身に聞ける** のが強い😄
次章（マニフェスト入門）で超効く！

```bash
kubectl explain deployment
kubectl explain deployment.spec
kubectl explain deployment.spec.template.spec.containers
```

---

## 🎯 ミニ演習（10分）⏱️😄

1. `kubectl apply -f k8s/hello.yaml` ✅
2. `kubectl get pods -l app=hello -o wide` 👀
3. `kubectl describe pod <pod-name>`（Eventsを読む）⚡
4. `kubectl port-forward deploy/hello 8080:80` 🔌
5. 別ターミナルで `curl.exe http://localhost:8080/` 🧪
6. `kubectl logs <pod-name> --tail=50`（アクセスログが出るか確認）📜
7. `kubectl exec -it <pod-name> -- sh`（中に入れたら勝ち）🏆
8. `kubectl delete -f k8s/hello.yaml` 🧹

---

## よくある詰まりポイント集😇🧯

* **何も出てこない** → `-n` 間違いが多い！`kubectl get pods -A` で全体を見る🧭
* **PodがPending** → `kubectl describe pod ...` の Events に答えがある率高い⚡
* **ログが出ない** → そもそもリクエスト飛んでない/コンテナ違い（`-c`）を疑う📜
* **kubectlが繋がらない** → `kubectl config current-context` で接続先チェック🗺️

---

## 🤖 AI（Copilot/Codex等）で楽する小ワザ✨

* `kubectl describe pod ...` の出力を貼って
  「**原因候補を3つ**」「**次に打つkubectlコマンドを順番で**」って聞く🔎🧠
* `kubectl logs ...` を貼って
  「**アプリ側の原因**と**K8s側の原因**を分けて説明して」って頼む🧩
* ただし **Secretっぽい値やトークンは貼らない** 🔐🙅‍♂️（そこは慎重に！）

---

次の第5章は、今日ちょい出てきた **YAML（マニフェスト）** を「読める＆自分で直せる」ようにしていくよ📄✨
必要なら、この章の演習用に **“わざと壊したYAML”**（CrashLoop版 / ImagePull失敗版）も作って、`describe` と `logs` の練習問題にできるよ😈➡️😇

[1]: https://kubernetes.io/docs/reference/kubectl/?utm_source=chatgpt.com "Command line tool (kubectl)"
[2]: https://kubernetes.io/docs/tasks/debug/debug-application/debug-running-pod/?utm_source=chatgpt.com "Debug Running Pods"
[3]: https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/?utm_source=chatgpt.com "Install and Set Up kubectl on Linux"
[4]: https://kubernetes.io/releases/patch-releases/?utm_source=chatgpt.com "Patch Releases"
[5]: https://github.com/kubernetes-sigs/kind/releases?utm_source=chatgpt.com "Releases · kubernetes-sigs/kind"
