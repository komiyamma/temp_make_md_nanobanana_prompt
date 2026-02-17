# 第08章：Deploymentで“落ちても戻る”を作る🛟🤖💥➡️😇

この章は **「Kubernetesっぽさ、ここで一気に来る」** 回です🙌
Pod を直接動かすだけだと「落ちたら終わり」になりがち。でも **Deployment** を使うと、**落ちても勝手に復活**します🔥
（そして更新も “いい感じに” してくれます🔄）

> ちなみに本日時点の Kubernetes の最新安定は **v1.35.1（2026-02-10）** です📅 ([Kubernetes][1])
> ローカル学習で kind を使う場合、**v0.31.0 が Kubernetes 1.35.0 をデフォルト**にしています🧪 ([GitHub][2])

---

## この章でできるようになること🎯✨

* **Deployment** を作って、Node/TS の API を “常駐” させる🏠
* **replicas**（複製数）で、落ちにくい形にする👯‍♂️
* Pod をわざと消して、**自動復活（self-healing）** を目で見る😈➡️😇
* 画像タグを変えて、**ローリング更新（rollout）** を体験する🔄
* `kubectl rollout status / history / undo / restart` を触る✋ ([Kubernetes][3])

---

## まずは超ざっくり理解🧠🍙

## Deploymentってなに？🤔

**「理想の状態（desired state）」を宣言して、現実を合わせ続ける係**です📌
たとえば…

* 「Podを **2個** 走らせたい」👯
* 「コンテナはこのイメージ（タグ）で動かしたい」📦
* 「更新するときは、止めずに少しずつ入れ替えたい」🔄

…と書いておくと、Kubernetes が **監視して勝手に調整**してくれます👀✨

## ざっくり関係図👪

![deployment_hierarchy](./picture/docker_multi_orch_ts_study_008_deployment_hierarchy.png)

Deployment は裏で **ReplicaSet** を作り、ReplicaSet が **Pod の数を維持**します🧩
（だから Pod を消しても戻る！）

---

## ハンズオン①：Deploymentを作る🏗️📄

ここでは例として `my-api` という Node/TS API を動かす想定でいきます🍔
（第7章で作った API コンテナをそのまま使うイメージ！）

## 1) deployment.yaml を作る📝

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-api
  labels:
    app: my-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: my-api
  template:
    metadata:
      labels:
        app: my-api
    spec:
      containers:
        - name: my-api
          image: YOUR_REGISTRY/YOUR_IMAGE:1.0.0
          ports:
            - containerPort: 3000
          env:
            - name: PORT
              value: "3000"
```

ポイントだけ🎯

* `replicas: 2` ← ここが「落ちにくさ」の第一歩👯‍♂️
* `selector.matchLabels` と `template.metadata.labels` は **同じにする**（超重要）🧷

---

## 2) 反映して状態を見る👀

```bash
kubectl apply -f deployment.yaml
kubectl get deploy
kubectl get rs
kubectl get pods -l app=my-api -o wide
```

見どころ👀✨

* `deploy/my-api` ができる
* `rs`（ReplicaSet）ができる
* `pods` が 2個 起動する（replicas=2 だから）🎉

---

## ハンズオン②：Podをわざと消して“復活”を観察😈➡️😇

![self_healing_mechanism](./picture/docker_multi_orch_ts_study_008_self_healing_mechanism.png)

## 1) Podを監視しながら消す🕵️‍♂️

まず監視：

```bash
kubectl get pods -l app=my-api -w
```

別ターミナルで、Pod 名を1つ消す：

```bash
kubectl get pods -l app=my-api
kubectl delete pod <消したいPod名>
```

すると…

* 消えた！💥
* でもすぐ **新しい Pod が作られる**！🧟‍♂️✨
  これが **self-healing（自動回復）** です🛟

> Deployment は “Pod を直接守る” というより、**「この数いるはず」** を守る仕組みです🧠
> だから Pod は使い捨て感覚で OK 🙆‍♂️

---

## ハンズオン③：replicas を増減して “強さ” を変える💪📈

![replicas_resilience](./picture/docker_multi_orch_ts_study_008_replicas_resilience.png)

```bash
kubectl scale deployment/my-api --replicas=3
kubectl get pods -l app=my-api
```

減らすのも同じ：

```bash
kubectl scale deployment/my-api --replicas=1
kubectl get pods -l app=my-api
```

感覚としてはこれ👇

* replicas=1：**落ちたら一瞬止まる**（作り直しはされるけど）😵
* replicas>=2：**片方が落ちても、片方が生きてる**☺️（※Service があると更に実感できる。次章！🧷）

---

## ハンズオン④：ロールアウト（安全に更新）を体験🔄🧪

![rolling_update_flow](./picture/docker_multi_orch_ts_study_008_rolling_update_flow.png)

Deployment の “うまみ” は **更新の自動運転**にもあります🚗💨
（止めずに、少しずつ入れ替える）

## 1) イメージタグを更新して apply 🏷️

`deployment.yaml` のイメージを `:1.0.1` に変える：

```yaml
image: YOUR_REGISTRY/YOUR_IMAGE:1.0.1
```

反映：

```bash
kubectl apply -f deployment.yaml
```

## 2) 更新の進み具合を見る👀

```bash
kubectl rollout status deployment/my-api
kubectl get rs
kubectl get pods -l app=my-api
```

* 新しい ReplicaSet が増える📈
* 古い ReplicaSet が減る📉
* Pod が “総入れ替え” ではなく **順番に差し替わる**🔄

これは Deployment がやってくれるローリング更新の基本ムーブです📚 ([Kubernetes][3])

---

## ハンズオン⑤：やらかした！を“戻す”（Rollback）🧯⏪

![rollback_undo](./picture/docker_multi_orch_ts_study_008_rollback_undo.png)

## 1) 履歴を見る📜

```bash
kubectl rollout history deployment/my-api
```

## 2) ひとつ前に戻す⏪

```bash
kubectl rollout undo deployment/my-api
```

`undo` は公式コマンドとして用意されています🧯 ([Kubernetes][4])

---

## 便利ワザ：再起動だけしたい（rollout restart）🔁

設定を変えた（ConfigMap/Secret など）けど、同じイメージで **Pod を作り直したい**ことってあります。
そんな時はこれ👇

```bash
kubectl rollout restart deployment/my-api
kubectl rollout status deployment/my-api
```

公式の `rollout restart` です🔁 ([Kubernetes][5])

---

## よくある事故ポイント集😇💥（そして直し方）

## 1) Pod が増えない / 0 のまま😵

![label_selector_match](./picture/docker_multi_orch_ts_study_008_label_selector_match.png)

* `selector` と `template.labels` がズレてる可能性大🧷
  → YAML を見直す（この章の最重要罠⚠️）

## 2) `ImagePullBackOff` 😭

* イメージ名・タグ間違い、またはレジストリ認証の問題🔐
  → まずこれ👇

```bash
kubectl describe pod <Pod名>
```

## 3) `CrashLoopBackOff` 🤕

* アプリが起動直後に落ちてる
  → まずログ👇

```bash
kubectl logs <Pod名>
```

---

## ミニ課題（やると理解が固定される）📌📝

1. replicas=1 にして Pod を消す → “止まる感” を自分の目で確認😵
2. replicas=2 に戻して Pod を消す → “戻る感” を確認😇
3. イメージタグを 1.0.2 → 1.0.3 と2回更新して、`rollout history` が増えるのを見る📜✨
4. `rollout undo` で戻す（戻ったら `get rs` も見てね）⏪

---

## AIで楽するポイント🤖✨（コピペでOK）

* 「この Deployment YAML、初心者がやりがちなミスを3つ指摘して」🧠
* 「`kubectl describe` の出力を貼るので、原因候補を優先順位付きで」🔍
* 「CrashLoop のログを貼るので、次に打つ kubectl コマンドを順番に」🥋
* 「rollout が進まない。`kubectl rollout status` と `get rs` の見方を超かみ砕いて」🥄

---

次の第9章で **Service** を入れると、replicas>=2 の強さがさらに気持ちよく分かります🧷🚀
「Podが差し替わっても、同じ名前でつながる」世界へ突入です😎

[1]: https://kubernetes.io/releases/?utm_source=chatgpt.com "Releases"
[2]: https://github.com/kubernetes-sigs/kind/releases?utm_source=chatgpt.com "Releases · kubernetes-sigs/kind"
[3]: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/?utm_source=chatgpt.com "Deployments"
[4]: https://kubernetes.io/docs/reference/kubectl/generated/kubectl_rollout/kubectl_rollout_undo/?utm_source=chatgpt.com "kubectl rollout undo"
[5]: https://kubernetes.io/docs/reference/kubectl/generated/kubectl_rollout/kubectl_rollout_restart/?utm_source=chatgpt.com "kubectl rollout restart"
