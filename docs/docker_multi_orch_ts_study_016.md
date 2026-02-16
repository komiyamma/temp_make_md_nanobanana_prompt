# 第16章：スケジューリング基礎（どのノードに置く？）🧲☸️

> 「Podの席決め」をコントロールできると、**マルチノードっぽさ**が一気に出ます😎✨
> でも最初は“やりすぎる”と **Pending地獄**になるので、ほどほどに行きましょ🫠💦

---

## 1) この章でできるようになること 🎯✨

* ノードに **ラベル**を貼って、Podを「このノードに置く！」ができる 🏷️➡️🧲
* **nodeSelector / Node Affinity** の違いを体感できる 🤝
* **Taints & Tolerations** で「このノードは関係者以外立ち入り禁止🚧」ができる 👮‍♂️🔐
* うっかり条件を絞りすぎて **Pending** になった時に直せる 🛠️😇

参考（公式）

* Podを特定ノードに寄せる考え方（推奨はラベルセレクタ） ([Kubernetes][1])
* ラベルとセレクタ（ノード選択にも使うよ） ([Kubernetes][2])
* Taints & Tolerations（ノードがPodを追い返す側） ([Kubernetes][3])

---

## 2) まず「Kubernetesの席決め」って何？🪑🗺️

KubernetesはPodを配置するとき、ざっくりこう動きます👇

1. **候補ノードを絞る（フィルタ）** 🔍

   * 条件に合わないノードは落とす
2. **候補を採点する（スコア）** 🏆

   * いい感じに分散したり、余裕があるノードを選んだりする

そして、席決めを人間が“ちょい足し”で指示する道具がこの章の3つ👇

* **nodeSelector**：超シンプル「このラベルのノードに置いて！」🧷
* **Node Affinity**：もう少し柔軟「必須/なるべく、条件いろいろ」🎛️
* **Taints & Tolerations**：ノード側が「関係者以外お断り」🚫（Pod側は許可証＝toleration）🪪

---

## 3) ハンズオン：まずは「特定ノードにだけ置く」🧪✨

## 3-1. ノードを確認する 👀

まずノード名を把握します。

```bash
kubectl get nodes -o wide
```

「control-plane」と「worker」が複数見えてたら勝ちです🏁😆
（もし1台しかなければ、前章で作った擬似マルチノードを使ってる想定でOK👌）

---

## 3-2. ノードにラベルを貼る 🏷️✨

例：片方のworkerを「api専用席」にしてみます🍔

```bash
kubectl label node <worker-node-name> workload=api
kubectl get nodes --show-labels
```

* ラベルは「付箋」みたいなもの📌
* あとで検索・指定・分類に使います ([Kubernetes][2])

---

## 3-3. nodeSelectorで「この付箋の席に座って！」🧷🪑

DeploymentのPodテンプレートに nodeSelector を足すだけでOKです。

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ts-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ts-api
  template:
    metadata:
      labels:
        app: ts-api
    spec:
      nodeSelector:
        workload: api
      containers:
        - name: ts-api
          image: ghcr.io/your-org/ts-api:1.0.0
          ports:
            - containerPort: 3000
```

適用👇

```bash
kubectl apply -f ts-api.deployment.yaml
kubectl get pods -o wide
```

**見るポイント👀✨**

* Podの「NODE」列が、workload=api を貼ったノードになってるか？✅
* 2つとも同じノードに寄ったり、分かれたりします（状況次第）🙂

> nodeSelector は「簡単だけど融通がききにくい」代表です🧷
> もっと細かくやりたくなったら次へ🚶‍♂️💨

---

## 4) Node Affinity：nodeSelectorの上位互換っぽいやつ🎛️✨

nodeSelectorは「完全一致」だけですが、Node Affinityは

* **必須（hard）** と **なるべく（soft）** を分けられるのが強いです💪

公式の“ノード選択”でも、ラベルセレクタ系のやり方が基本ルートです ([Kubernetes][1])

---

## 4-1. 必須条件（hard）：ここに置けないならスケジュールしない🧱

```yaml
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
          - matchExpressions:
              - key: workload
                operator: In
                values:
                  - api
```

**意味🎈**

* workload=api のノード以外は **候補にすら入れない** 😤

---

## 4-2. なるべく条件（soft）：できればここがいいな〜🍵

```yaml
spec:
  affinity:
    nodeAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
        - weight: 80
          preference:
            matchExpressions:
              - key: workload
                operator: In
                values:
                  - api
```

**意味🎈**

* 可能ならworkload=apiへ置く
* 無理なら他でもいい（Pending回避しやすい）😇✨

---

## 5) Taints & Tolerations：「関係者以外立入禁止」を作る🚧🛡️

## 5-1. ノードに taint を付ける（追い返し機能）🚫

例：このノードは「専用席」なので、許可証がないPodは入れない！

```bash
kubectl taint nodes <worker-node-name> dedicated=api:NoSchedule
```

公式の説明どおり、**taintはノードがPodを“押し返す”側**です ([Kubernetes][3])

この状態で、toleration無しのPodを作ると **Pending** になりやすいです🫠
確認👇

```bash
kubectl get pods
kubectl describe pod <pod-name>
```

describe の Events に「taintが理由で置けない」系が出たら当たり🎯

---

## 5-2. Pod側に toleration（許可証）を付ける🪪✨

DeploymentのPodテンプレにこれを足します👇

```yaml
spec:
  tolerations:
    - key: dedicated
      operator: Equal
      value: api
      effect: NoSchedule
```

これで **dedicated=api:NoSchedule** のノードにも座れます🪑✨

---

## 5-3. 後片付け（超大事）🧹😇

実験が終わったら消して戻します。

* ラベル削除（末尾にハイフン）

```bash
kubectl label node <worker-node-name> workload-
```

* taint削除（末尾にハイフン）

```bash
kubectl taint nodes <worker-node-name> dedicated=api:NoSchedule-
```

---

## 6) Pending地獄の「ありがち原因」Top5 🫠📛

1. **条件を絞りすぎ**（nodeSelector/required affinity が強すぎ）🧱
2. **taint付けたのに toleration 付け忘れ** 🪪忘れ
3. **ラベルのキー/値のタイプミス**（api と API とか）🔤
4. **リソース不足**（requestsが大きくて入らない）🍰不足
5. **ノードが Ready じゃない**（そもそも動けない）😵‍💫

困ったらこの黄金コンボです👇✨

```bash
kubectl get pods -o wide
kubectl describe pod <pod-name>
kubectl get nodes -o wide
```

---

## 7) “設計の超入門”としての使い分けメモ 🧠📝

* まずは **何も指定しない**：Kubernetesの自動配置を信じてみる🤖✨
* 次に **nodeSelector**：単純な「専用ノード」程度ならこれで十分🧷
* もっと柔軟にしたいなら **Node Affinity**：

  * 迷ったら「なるべく（preferred）」から入る🍵
* **Taints & Tolerations** は強力：

  * 「このノードは特別枠！」を守りたい時に使う🚧
  * ただし使うほど“置ける場所”は減る＝Pending増えやすい⚠️

---

## 8) 演習ミッション（手を動かすやつ）🕹️🔥

## ミッションA：席の指定🪑

* worker1 に workload=api
* worker2 に workload=batch
* API Deployment は api へ、バッチJobは batch へ置く

## ミッションB：なるべく分散（軽め）🧁

* Node Affinity の preferred を使って

  * 「できれば api ノード」
  * 無理なら他でもOK
    にして Pending を避ける

## ミッションC：立入禁止ゾーン🚧

* worker1 を dedicated=api:NoSchedule
* toleration無しのPodが入れないのを確認
* toleration付きなら入れるのを確認

---

## 9) AIに頼ると爆速になるポイント 🤖⚡（コピペでOK）

* 「このYAML、nodeSelector から nodeAffinity（required/preferred両方）に書き換えて」✍️
* 「このPodがPending。describeのEvents貼るから、原因候補を3つと直し方を出して」🧯
* 「taints/tolerations って結局どっちが何を持つの？たとえ話で！」🪪🚧

---

## 10) まとめ 🎉☸️

* **ラベルで“席のカテゴリ”を作る** 🏷️
* **nodeSelector＝シンプル指名** 🧷
* **Node Affinity＝必須/なるべくを使い分け** 🎛️
* **Taints＝立入禁止、Tolerations＝許可証** 🚧🪪
* そして最重要：**絞りすぎるとPending** 🫠💦

次の章（HPA）に行く前に、ここで「席決めの感覚」が入ってると超ラクになりますよ〜📈✨

[1]: https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/?utm_source=chatgpt.com "Assigning Pods to Nodes"
[2]: https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/?utm_source=chatgpt.com "Labels and Selectors"
[3]: https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/?utm_source=chatgpt.com "Taints and Tolerations"
