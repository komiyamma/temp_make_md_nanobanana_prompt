# 第29章：Helm 4 / Kustomizeで“配布・再利用”📦🎁

この章は、「KubernetesのYAMLをコピペで増やして地獄を見る前に」😇➡️😱、**“配れる形”**にまとめる回です！
作ったアプリ（例：Node/TS API）を **別環境（dev/stg/prod）へ安全に展開**したり、**将来の自分/チームに渡せる形**にします🤝✨

---

## 1) 今日のゴール🎯✨

最後にこうなれば勝ちです🏆

* **Kustomize**で「base + overlays（環境差分）」を作れる🧩
* **Helm 4**で「Chart化 → install/upgrade」できる📦🔄
* 「どっち使う？」を**判断**できる⚖️
* “配布できる形”の最低限の作法（バージョン、値、差分）を知る🏷️

---

## 2) まずは超ざっくり：Helm vs Kustomize🤔

## Kustomize（カスタマイズ）🧩

* **元になるYAML（base）**を置いて、環境ごとの差分を**overlay**として重ねます🎂
* テンプレート言語なしで、基本は「YAMLにパッチ当て」🩹
* `kubectl apply -k` でそのまま適用できるのが強い💪
  （Kustomizeはスタンドアロンとしても存在し、kubectlにも統合されています）([Kubernetes][1])

## Helm（パッケージ）📦

* Kubernetesリソース一式を **Chart（パッケージ）**として配れます🎁
* `values.yaml`（設定値）を変えるだけで、同じChartを別環境に展開できる🪄
* Chartは「複数ファイルの決まった構造」を持ちます（あとで触ります）([Helm][2])

> ざっくり使い分け：
>
> * 自作アプリを「base＋差分」で管理 → **Kustomize**が気持ちいい🧼
> * いろんな人/環境に「インストールできる形」で配る → **Helm**が強い📦

---

## 3) ハンズオンA：Kustomizeで “base + overlays” を作る🧩🔥

## 3-1. ディレクトリ構成（まず形から）📁

こんな感じにします👇

```text
k8s/
  base/
    deployment.yaml
    service.yaml
    kustomization.yaml
  overlays/
    dev/
      kustomization.yaml
    prod/
      kustomization.yaml
      patch-replicas.yaml
```

## 3-2. base（共通の土台）🌱

`k8s/base/kustomization.yaml`

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - deployment.yaml
  - service.yaml
```

`k8s/base/deployment.yaml`（最小例）

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-api
spec:
  replicas: 1
  selector:
    matchLabels:
      app: todo-api
  template:
    metadata:
      labels:
        app: todo-api
    spec:
      containers:
        - name: api
          image: ghcr.io/your-org/todo-api:1.0.0
          ports:
            - containerPort: 3000
```

`k8s/base/service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-api
spec:
  selector:
    app: todo-api
  ports:
    - port: 80
      targetPort: 3000
```

## 3-3. overlay（dev）🌿

`k8s/overlays/dev/kustomization.yaml`

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - ../../base

namePrefix: dev-

images:
  - name: ghcr.io/your-org/todo-api
    newTag: 1.0.0-dev
```

## 3-4. overlay（prod）🏭

`k8s/overlays/prod/kustomization.yaml`

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - ../../base

namePrefix: prod-

images:
  - name: ghcr.io/your-org/todo-api
    newTag: 1.0.0

patchesStrategicMerge:
  - patch-replicas.yaml
```

`k8s/overlays/prod/patch-replicas.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-api
spec:
  replicas: 3
```

## 3-5. 生成結果を見てから適用する👀✨

Kustomizeは「最終的にどんなYAMLになるか」を見てから安心して適用できます😌

```bash
## 生成（確認）
kubectl kustomize k8s/overlays/dev

## 適用
kubectl apply -k k8s/overlays/dev
```

`kubectl kustomize` や `kubectl apply -k` は公式ドキュメントでも案内されている基本形です([Kubernetes][1])

---

## 4) ハンズオンB：Helm 4で “Chart化して配る”📦🚀

## 4-1. Helm Chartの“箱”を作る📦

まず雛形を作ります（雛形は便利だけど、そのままだと不要物も多いので整理します✂️）

```bash
helm create todo-api
```

## 4-2. Chartの構造（超重要）🧠

Helm Chartは、だいたいこういう構造になります👇
（`values.yaml` や `templates/`、そして任意で `values.schema.json` が置けます）([Helm][2])

* `Chart.yaml`：Chartのメタ情報（名前・バージョンなど）([Helm][2])
* `values.yaml`：デフォルト設定値([Helm][2])
* `templates/`：Kubernetesマニフェストのテンプレ（値を埋めて生成）([Helm][2])
* `values.schema.json`：値のJSON Schema（任意だけど超おすすめ）([Helm][2])

> ここでの感覚：
> **templates = 設計図** 🏗️
> **values = 設定** ⚙️
> だから「同じ設計図を、設定だけ変えて配れる」わけです🎁

## 4-3. 最低限のvalues設計（“触っていい場所”を決める）🧷

`values.yaml` の例（触らせたいものだけ用意するのがコツ）✨

```yaml
replicaCount: 1

image:
  repository: ghcr.io/your-org/todo-api
  tag: "1.0.0"
  pullPolicy: IfNotPresent

service:
  port: 80
  targetPort: 3000
```

## 4-4. templates側で values を使う🪄

`templates/deployment.yaml` のイメージ（超ミニ例）

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: {{ .Release.Name }}
  template:
    metadata:
      labels:
        app: {{ .Release.Name }}
    spec:
      containers:
        - name: api
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - containerPort: {{ .Values.service.targetPort }}
```

## 4-5. “インストールせずに”まず生成して確認👀

いきなり入れない！まず見る！これ超大事です🧯✨

```bash
helm template dev ./todo-api
```

## 4-6. install / upgrade を体験する🔄

```bash
## 初回インストール（または upgrade --install で統一）
helm upgrade --install dev ./todo-api -f values-dev.yaml

## 値だけ変えてアップグレード
helm upgrade --install dev ./todo-api -f values-dev.yaml --set replicaCount=2
```

## 4-7. values.schema.json で事故を減らす🛡️

`values.schema.json` を置くと、**間違った値（型違い・必須抜け）**を早めに検出しやすくなります✅
これはChart構造として公式に用意されている仕組みです([Helm][2])

ミニ例👇

```json
{
  "$schema": "http://json-schema.org/schema#",
  "type": "object",
  "properties": {
    "replicaCount": { "type": "integer", "minimum": 1 },
    "image": {
      "type": "object",
      "properties": {
        "repository": { "type": "string" },
        "tag": { "type": "string" }
      },
      "required": ["repository", "tag"]
    }
  },
  "required": ["replicaCount", "image"]
}
```

---

## 5) 2026の最新ポイント：Helm 4で何が変わった？🆕✨

初心者でも「ここだけ押さえる」と後で詰みにくいです🧠

* **Helm 4は新機能が増えて、内部も大きく進化**（プラグイン刷新、Server-side apply対応、kstatusベースのwait改善など）([Helm][3])
* Helm 4の概要として、**Wasmベースのプラグイン**や**OCI関連の強化**などが整理されています([Helm][4])
* **壊れやすい注意点**として、たとえば

  * Post-rendererは「実行ファイル直指定」ではなく**プラグイン扱い**になったり([Helm][4])
  * `helm registry login` が **フルURLを受けず“ドメインのみ”**になったり([Helm][4])
    みたいな“地味に効く変更”があります⚠️
* そして超現実的な話：**Helm 3は移行猶予あり**（バグ修正は2026-07-08まで、セキュリティ修正は2026-11-11まで）([Helm][3])
  → だから「今から学ぶならHelm 4の作法」でOKです👍

---

## 6) じゃあ結局どっち？判断のコツ⚖️😺

迷ったらこのルールでOKです👇

* **自分のアプリ**（YAMLを素直に保ちたい）
  → Kustomize（base + overlays）🧩
* **配布したい**（他人/別チーム/別環境に“インストール体験”を渡したい）
  → Helm（Chartとして配る）📦
* **現場あるある**：

  * 自作はKustomizeで管理
  * 外部製品（DBや監視ツール等）はHelmで入れる
    みたいに“併用”がめちゃ多いです🤝✨

---

## 7) ありがち事故と直し方🧯🛠️

## Kustomizeの事故😵

* **patchが当たらない**
  → `metadata.name` が base と一致してるか確認（namePrefix付ける前の名前に当てるのが基本）📝
* **どんなYAMLが出るかわからなくなる**
  → `kubectl kustomize` で必ず生成結果を見る👀([Kubernetes][1])

## Helmの事故😵‍💫

* **valuesの型がズレて壊れる（"1" と 1 とか）**
  → `values.schema.json` で守る🛡️([Helm][2])
* **`helm template` を見ずに入れて混乱**
  → まず `helm template`（ここだけは宗教にしてOK）🙏✨
* **“触っていい値”が多すぎてカオス**
  → valuesは絞る✂️（「利用者が安全に触れるノブだけ」）

---

## 8) AIで爆速にするプロンプト例🤖⚡（そのままコピペOK）

* 「このKustomize構成、dev/prodで差分を最小にしたい。overlay設計を提案して」🧩
* 「このHelm templatesに対して、values.yamlの“公開していい項目”を最小にリファクタして」✂️
* 「values.schema.json を作って。型・必須・最小値も入れて」🛡️
* 「`helm template` の出力を見て、危険な点（ラベル不整合、selector不一致など）をチェックして」🔍

---

## 9) ミニ演習（やると一気に腹落ち）🏋️‍♂️🔥

1. Kustomizeで `dev` と `prod` を作り、`replicas` と `image tag` を変える🧩
2. 同じ内容をHelm Chart化して、`values-dev.yaml` / `values-prod.yaml` を作る📦
3. `values.schema.json` を追加して、「replicaCountを文字列にしてわざと失敗」させる😈➡️✅
4. `helm upgrade --install` を2回やって、「差分更新」の感覚を掴む🔄

---

## まとめ🎉

* Kustomizeは **YAMLを土台に差分を重ねる**のが得意🧩([Kubernetes][1])
* Helmは **Chartとして配って、値で切り替える**のが得意📦([Helm][2])
* Helm 4は機能強化が多いので「Helm 4前提」で学ぶのが自然🆕([Helm][3])

次の章（第30章）は、ここで作った“配れる形”を、**本番運用の流れ（マネージドK8s・アップグレード・GitOps）**へつなげていく感じになります🗺️🏁

[1]: https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/ "Declarative Management of Kubernetes Objects Using Kustomize | Kubernetes"
[2]: https://helm.sh/docs/topics/charts/ "Charts | Helm"
[3]: https://helm.sh/blog/helm-4-released "Helm 4 Released | Helm"
[4]: https://helm.sh/docs/overview/ "Helm 4 Overview | Helm"
