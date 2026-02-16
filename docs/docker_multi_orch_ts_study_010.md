# 第10章：Namespace・Label・Selectorで“整理整頓”🧹🏷️🔎

Kubernetesのリソースって、慣れてくると **あっという間に数十〜数百** になります😇
そこで今日は、迷子を防ぐ三種の神器👇を“手で動かして”覚えます💪✨

* **Namespace**：箱（フォルダ）📦
* **Label**：タグ（付せん）🏷️
* **Selector**：タグ検索（絞り込み）🔎

ちなみに本日時点のKubernetesは **v1.35.1（2026-02-10）** が最新です🆕 ([Kubernetes][1])

---

## 10.1 ゴール🎯（ここまでできたら勝ち🏆）

* Namespaceで「環境別」「チーム別」に分けられる📦
* Labelの付け方・設計のコツがわかる🏷️
* Selectorで狙ったリソースだけを一瞬で拾える🔎
* **Serviceが“どのPodに流すか”がSelectorで決まる**のを体感する🚰

---

## 10.2 まず超ざっくり理解🧠✨（3行でOK）

* **Label**は「同じ種類のものに共通で付ける目印」🏷️（例：`app=api`）
* **Selector**は「その目印でグループを選ぶ仕組み」🔎（ServiceもこれでPodを選びます） ([Kubernetes][2])
* **Namespace**は「そもそも置き場所を分ける仕切り」📦（dev/prodを混ぜない）

---

## 10.3 ハンズオン①：Namespaceで“箱”を作る📦🧪

まず、環境別に2つ作ります（dev / prod）🌱🔥

```bash
kubectl get ns
kubectl create namespace demo-dev
kubectl create namespace demo-prod
kubectl get ns
```

**使い分けの基本**👇

* `demo-dev`：実験用。壊してOK😈
* `demo-prod`：本番想定。勝手に壊さない😇

そして「毎回 `-n` 書くのだるい…」ってなるので、**作業中だけデフォルトnamespaceを切り替え**します（超便利）✨

```bash
kubectl config set-context --current --namespace=demo-dev
kubectl config view --minify | findstr namespace
```

> 🔥あるある：namespaceを切り替えたの忘れて `prod` に適用して事故る
> → まずは `kubectl get ns` より **`kubectl config view --minify`** の癖を付けるのおすすめです😎

---

## 10.4 ハンズオン②：Labelを付ける（タグ付け）🏷️🧩

Labelは「整理整頓の主役」です🏷️✨
そしてKubernetes公式が推奨してる“共通ラベル”がこれ👇（`app.kubernetes.io/*` 系） ([Kubernetes][3])

よく使うセット（まずはこれだけでOK）👇

* `app.kubernetes.io/name`：アプリ名（例：`todo-api`）
* `app.kubernetes.io/instance`：環境・インスタンス（例：`dev` / `prod`）
* `app.kubernetes.io/part-of`：何の一部？（例：`todo-system`）
* `app.kubernetes.io/managed-by`：管理ツール（例：`helm` など）

Labelの文字ルールもあります（地味にハマる）😵

* キー/値は基本 **63文字以内**
* `- . _` はOK
* 必要なら `example.com/key` みたいなプレフィックスもOK ([Kubernetes][4])

---

## 10.5 ハンズオン③：DeploymentにLabelを付けて動かす🚀🏷️

ここでは「すでに第7〜9章でDeployment/Serviceを触ってる」前提で、最小の例を作ります🧪
（無い場合でも、これを貼ってそのまま動かせます👌）

**1) demo-dev に Deployment を作る**🍔

```yaml
## k8s/deploy-dev.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-api
  labels:
    app.kubernetes.io/name: todo-api
    app.kubernetes.io/instance: dev
    app.kubernetes.io/part-of: todo-system
spec:
  replicas: 2
  selector:
    matchLabels:
      app.kubernetes.io/name: todo-api
      app.kubernetes.io/instance: dev
  template:
    metadata:
      labels:
        app.kubernetes.io/name: todo-api
        app.kubernetes.io/instance: dev
        app.kubernetes.io/part-of: todo-system
    spec:
      containers:
        - name: api
          image: nginx:stable
          ports:
            - containerPort: 80
```

```bash
kubectl apply -n demo-dev -f k8s/deploy-dev.yaml
kubectl get deploy -n demo-dev
kubectl get pods -n demo-dev --show-labels
```

> ✅ここでの超重要ポイント：
> `spec.selector.matchLabels` と `template.metadata.labels` は **一致してないとダメ** です⚠️
> （一致してるから、DeploymentがPodをちゃんと管理できます👍）

---

## 10.6 ハンズオン④：Selectorで“絞り込み検索”🔎✨（一気に気持ちよくなるやつ）

Labelが付いたら、Selectorで取り放題です😋

**等価ベース（シンプル）**👇

```bash
kubectl get pods -n demo-dev -l app.kubernetes.io/name=todo-api
kubectl get pods -n demo-dev -l app.kubernetes.io/name=todo-api,app.kubernetes.io/instance=dev
```

**否定もできる**👇

```bash
kubectl get pods -n demo-dev -l 'app.kubernetes.io/instance!=prod'
```

SelectorはKubernetesの“グルーピングの核”です（ドキュメントでもそう言い切ってます） ([Kubernetes][2])

---

## 10.7 ハンズオン⑤：ServiceはSelectorで“接続先Pod”を決める🚰➡️📦

ここが今日の一番おいしいところです😆🍖
Serviceは「このラベルのPodに流してね〜」ってSelectorで決めます。

```yaml
## k8s/svc-dev.yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-api
  labels:
    app.kubernetes.io/name: todo-api
    app.kubernetes.io/instance: dev
spec:
  type: ClusterIP
  selector:
    app.kubernetes.io/name: todo-api
    app.kubernetes.io/instance: dev
  ports:
    - port: 80
      targetPort: 80
```

```bash
kubectl apply -n demo-dev -f k8s/svc-dev.yaml
kubectl get svc -n demo-dev
```

**接続先（Endpoint/EndpointSlice）ができてるか確認**👀

```bash
kubectl describe svc -n demo-dev todo-api
kubectl get endpoints -n demo-dev todo-api
kubectl get endpointslices -n demo-dev
```

> 😇 もし `Endpoints: <none>` みたいになってたら…
> だいたい **Serviceのselector と Podのlabel がズレてます**（超あるある）💥
> → まず `kubectl get pods --show-labels` で現実確認が最速です🏃‍♂️💨

---

## 10.8 “整理整頓ミニ設計”の型📁✨（初心者が迷わないやつ）

まずはこの2段構えがラクです👇

## ① Namespace：大きな境界（環境・チーム）📦

* `demo-dev`, `demo-prod` みたいに **環境で分ける**🌱🔥
* チームが増えたら `team-a`, `team-b` みたいに **チームで分ける**👥

## ② Label：横断検索（アプリ・役割・環境）🏷️

* アプリ名：`app.kubernetes.io/name`
* 環境：`app.kubernetes.io/instance`
* まとまり：`app.kubernetes.io/part-of`

> ✋ 注意：Labelに「ユーザーID」とか「リクエストID」とか入れない！
> → 値が増えすぎると管理も検索も地獄になります😇（高カーディナリティ問題🔥）

---

## 10.9 よくある事故TOP5😇💥（先に潰す）

1. **namespace指定忘れ**で「ない！」ってなる
   → `-n demo-dev` or `kubectl config set-context --current --namespace=...` を固定💪

2. **Serviceが繋がらない（Endpointなし）**
   → selectorとlabelのズレ。`pods --show-labels` で照合🔎

3. **labelキー/値のルール違反**（地味に怒られる）
   → 文字・長さ制限を思い出す ([Kubernetes][4])

4. **ラベル増やしすぎ**で収拾不能🌀
   → “検索に使うラベルだけ”に絞る✂️

5. **環境が混ざる**（devとprodが同居）
   → Namespaceをまず分ける📦（Labelだけで頑張らない）

---

## 10.10 AI活用（ここ、めっちゃ相性いい🤝🤖）

AIには「設計のたたき台」と「ズレ検出」をやらせるのが強いです💪

✅おすすめ投げ方（コピペでOK）👇

```text
このKubernetesマニフェストに、公式推奨の app.kubernetes.io/* ラベルを最小セットで付けて。
環境は dev / アプリ名は todo-api / part-of は todo-system。
また、ServiceのselectorとPod側labelsの不一致が起きないようにチェックして修正案を出して。
```

> 🤖ポイント：AIはたまに **selectorとlabelsを微妙にズラす** ので、
> 最後に自分で「一致してる？」だけ確認すれば勝てます😎✨

---

## 10.11 まとめ🧠✨（今日の合言葉）

* Namespace＝箱📦、Label＝タグ🏷️、Selector＝タグ検索🔎
* ServiceはSelectorで“接続先Pod”を決める🚰
* 推奨ラベル（`app.kubernetes.io/*`）を使うと未来の自分が助かる🛟 ([Kubernetes][3])

---

## 10.12 ミニ課題🎒💪（10分でOK）

1. `demo-prod` にも同じDeploymentを作って、`instance: prod` にしてみよう🔥
2. `demo-prod` のServiceだけ、わざと `instance: dev` にして壊してみよう😈
3. `Endpoints: <none>` を確認したら、正しく直して復旧させよう😇
4. 最後にこれを言える？👇

   * 「**壊れた原因は selector と label の不一致**」🗣️✨

---

次の章（ConfigMap/Secretあたり）に進むと、**“環境差分”が一気に現実味**を帯びます🌱🔥
その前に第10章の整理整頓だけは、体に染み込ませちゃいましょ〜🧹💖

[1]: https://kubernetes.io/releases/?utm_source=chatgpt.com "Releases"
[2]: https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/?utm_source=chatgpt.com "Labels and Selectors"
[3]: https://kubernetes.io/docs/concepts/overview/working-with-objects/common-labels/?utm_source=chatgpt.com "Recommended Labels"
[4]: https://kubernetes.io/docs/reference/kubectl/generated/kubectl_label/?utm_source=chatgpt.com "kubectl label"
