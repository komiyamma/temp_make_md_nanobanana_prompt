# 第25章：RBAC入門（権限は最小が正義）👮‍♂️🔑🛡️

この章は、**「誰が（Subject）」「何を（Role）」「どこで（Namespace/Cluster）」「できるようにする（Binding）」**を、**手を動かして**覚える回です💪
RBACはKubernetes運用の“免許制度”みたいなもの。うっかり強すぎる権限を渡すと、事故の火力がデカくなります🔥😇

---

## 1) 今日のゴール🎯✨

* **Role / ClusterRole の違い**を体感する🧠
* **RoleBinding / ClusterRoleBinding の違い**を体感する🧠
* **ServiceAccount を「何もできない状態」→「必要最小限だけできる状態」**に育てる🌱
* **`kubectl auth can-i`で“権限テスト”できる**ようになる✅ ([Kubernetes][1])

---

## 2) RBACの超ざっくり地図🗺️（ここだけ覚えればOK）

![RBAC Four Pillars](./picture/docker_multi_orch_ts_study_025_rbac_components.png)

RBACの登場人物は4つだけです👇 ([Kubernetes][2])

* **Role**：あるNamespaceの中だけの「許可リスト」📄
* **ClusterRole**：クラスタ全体（または複数Namespace）に使える「許可リスト」🌍
* **RoleBinding**：Role/ClusterRole を **特定Namespace内で** 誰かに渡す紐づけ🧵
* **ClusterRoleBinding**：ClusterRole を **クラスタ全体で** 誰かに渡す紐づけ🧵🌍

そして大事な性質：

* RBACは**足し算だけ（denyは基本なし）**です➕（「あとで取り消し」は Binding を外す） ([Kubernetes][2])

---

## 3) 最初に“安全の鉄則”だけ👮‍♂️⚠️（ここで事故が減る）

![Least Privilege Principle](./picture/docker_multi_orch_ts_study_025_least_privilege.png)

Kubernetes公式のRBAC推奨に沿って、超重要ポイントだけ先に置きます🧯 ([Kubernetes][3])

* ✅ **まずNamespace内で閉じる**（RoleBinding優先）
* ❌ **ワイルドカード（`*`）は極力避ける**（未来のリソースにも権限が伸びて危険） ([Kubernetes][3])
* ❌ **`cluster-admin`は基本封印**（“必要な時だけ”） ([Kubernetes][3])
* ❌ **`system:masters`に人を入れない**（ほぼ無敵になっちゃう） ([Kubernetes][3])
* ✅ **強いServiceAccountトークンを配りまくらない**（漏れるとヤバい） ([Kubernetes][3])
* ✅ **ServiceAccountトークンの自動マウントを見直す**（不要ならOFF） ([Kubernetes][3])
* ⚠️ **Pod作成権限は“実質いろいろ触れる”**（Secret/ConfigMapマウント等で権限が広がる） ([Kubernetes][3])

---

## 4) ハンズオン：最小権限を“作って検証”する🧪✅

> ここは「コピペ → 叩く → `can-i`で確かめる」の繰り返しでOKです😆
> `--as`は**なりすまし（impersonation）**なので、手元が管理者権限だと通りやすいです（学習用） ([Kubernetes][1])

---

## 4-1) 検証用Namespaceと、適当なアプリを用意🧱🐣

```bash
kubectl create ns demo-rbac

## 例として nginx を1個だけ動かす（何でもOK）
kubectl -n demo-rbac create deploy hello --image=nginx:stable-alpine --replicas=1
kubectl -n demo-rbac get pod
```

---

## 4-2) ServiceAccountを作る（まずは“何もできない”が正義）🧑‍🔧🔒

![kubectl auth can-i](./picture/docker_multi_orch_ts_study_025_auth_can_i.png)

```bash
kubectl -n demo-rbac create sa app-sa
```

権限テスト（最初はだいたい **No** になってほしい）👇

```bash
kubectl -n demo-rbac auth can-i list pods \
  --as=system:serviceaccount:demo-rbac:app-sa
```

`kubectl auth can-i`は「この操作、許可されてる？」を聞ける公式コマンドです✅ ([Kubernetes][1])

---

## 4-3) Roleを作る（読むだけ係👀）→ RoleBindingで渡す🎁

## ✅ “読むだけRole”（Pods/Deployments/Servicesなどを閲覧）

```yaml
## rbac-app-read.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: app-read
  namespace: demo-rbac
rules:
  # コアAPI（apiGroups: [""]）
  - apiGroups: [""]
    resources: ["pods", "services", "configmaps", "events"]
    verbs: ["get", "list", "watch"]

  # apps API（Deploymentなど）
  - apiGroups: ["apps"]
    resources: ["deployments", "replicasets"]
    verbs: ["get", "list", "watch"]
```

## ✅ “app-saにRoleを渡すBinding”

```yaml
## rbac-app-read-binding.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: app-read-binding
  namespace: demo-rbac
subjects:
  - kind: ServiceAccount
    name: app-sa
    namespace: demo-rbac
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: app-read
```

適用👇

```bash
kubectl apply -f rbac-app-read.yaml
kubectl apply -f rbac-app-read-binding.yaml
```

できるようになったか確認👇

```bash
kubectl -n demo-rbac auth can-i list pods \
  --as=system:serviceaccount:demo-rbac:app-sa

kubectl -n demo-rbac auth can-i delete pods \
  --as=system:serviceaccount:demo-rbac:app-sa
```

* `list pods` → **yes** が理想🎉
* `delete pods` → **no** が理想🎉（最小権限！）

---

## 4-4) “ログを見る権限”と“execする権限”は分けよう🪓🧯

![Role Separation](./picture/docker_multi_orch_ts_study_025_role_separation.png)

現場あるある：

* 「ログだけ見たい」人に exec まで渡すと事故りやすい😇💥
* なので **別Role** に分割が安全です

## ✅ ログ閲覧Role（pods/log）

```yaml
## rbac-pod-logs.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-logs
  namespace: demo-rbac
rules:
  - apiGroups: [""]
    resources: ["pods/log"]
    verbs: ["get"]
```

Binding（app-sa に付ける例）👇

```yaml
## rbac-pod-logs-binding.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: pod-logs-binding
  namespace: demo-rbac
subjects:
  - kind: ServiceAccount
    name: app-sa
    namespace: demo-rbac
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: pod-logs
```

適用👇

```bash
kubectl apply -f rbac-pod-logs.yaml
kubectl apply -f rbac-pod-logs-binding.yaml
```

ログ権限のテスト（サブリソース）👇
※公式例にも `--subresource=log` が載ってます✅ ([Kubernetes][1])

```bash
kubectl -n demo-rbac auth can-i get pods --subresource=log \
  --as=system:serviceaccount:demo-rbac:app-sa
```

## ✅ exec用Role（pods/exec）は “create” が必要

```yaml
## rbac-pod-exec.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-exec
  namespace: demo-rbac
rules:
  - apiGroups: [""]
    resources: ["pods/exec"]
    verbs: ["create"]
```

> execは強いので、**運用では別ServiceAccount／別ユーザーにだけ**渡すのが定石です🔐✨（“デバッグ係”を分離） ([Kubernetes][3])

---

## 5) よくある事故パターン3つ💥😇（ここ踏む人多い）

![Scope Comparison (Namespace vs Cluster)](./picture/docker_multi_orch_ts_study_025_scope_comparison.png)

## 事故1：うっかりClusterRoleBindingを作って全クラスタ権限😱🌍

* Namespace内だけでいいのに、**ClusterRoleBinding** を作ると影響範囲が広がる
* 基本は **RoleBinding** で閉じよう🧊 ([Kubernetes][3])

## 事故2：`*`（ワイルドカード）で未来のリソースまで許可😵

* 今は存在しないCRDが増えた瞬間に、権限が伸びることがある
* できるだけ **resources/verbsを具体的に** ✍️ ([Kubernetes][3])

## 事故3：default ServiceAccountに権限を付けて、全Podが強くなる😇🔥

* Podが `serviceAccountName` を指定しないと **default SA** を使います
* default SAに権限を付けると「そのNamespaceの“全部のPod”」が強くなりがち🧨 ([Kubernetes][2])
* さらにトークンの自動マウントをOFFにする選択肢もあります（不要ならOFF） ([Kubernetes][3])

---

## 6) “最小権限設計”の型（超かんたん版）🧠📌

1. **やりたい作業を日本語で列挙**📝
   例：

   * Pod一覧を見たい
   * ログを見たい
   * たまにexecしたい

2. **resources / verbs に落とす**🔧

   * Pod一覧 → `pods` に `get/list/watch`
   * ログ → `pods/log` に `get`
   * exec → `pods/exec` に `create`

3. **`kubectl auth can-i`でテストして調整**✅

   * “足りない権限だけ”追加していく（最小をキープ） ([Kubernetes][1])

---

## 7) AIに手伝わせるコツ🤖✨（RBACは特に“検証前提”で！）

RBACはAIが**盛りがち**なので、使い方はこれが安全👇

* ✅ YAMLはAIに書かせてOK
* ✅ でも必ず **「権限が最小か？」** を追加で質問
* ✅ 最後に **`kubectl auth can-i` のテストコマンドも一緒に出させる** ([Kubernetes][1])

使える投げ方例（そのままコピペでOK）👇

* 「この作業（Pod一覧、ログ閲覧）に必要な**最小のresources/verbs**だけでRole/RoleBindingを作って。`*`は禁止。`cluster-admin`は禁止。テスト用に `kubectl auth can-i` も出して」🧪✅
* 「`pods/log` や `pods/exec` のような**サブリソース**を見落としてないか確認して」👀

---

## 8) まとめ🎉

![How Binding Works](./picture/docker_multi_orch_ts_study_025_binding_mechanism.png)

* RBACは **Role（許可）＋Binding（配布）** のセット🎁
* まずは **Namespace内で閉じる**、次に **最小権限**、最後に **can-iで検証**✅ ([Kubernetes][3])
* 「ログ」と「exec」は分離すると、運用が平和になります🕊️😇

---

## おまけ：理解チェックミニ問題🧩😆

1. RoleとClusterRoleの最大の違いは？
2. あるNamespaceだけで権限を渡したい。RoleBinding？ClusterRoleBinding？
3. ログ閲覧は `resources` 何を書く？
4. 「Pod作成権限がある人」が危険になりやすい理由は？

（答えはこの章の本文に全部あります😉）

---

次は、RBACを“現場っぽく”していくなら、**「人間用の閲覧ロール」「CI用ロール」「運用ブレイクグラス（緊急）ロール」**みたいに、役割ごとに切っていくのが気持ちいいです🧑‍🚒🧑‍💻🤖

[1]: https://kubernetes.io/docs/reference/kubectl/generated/kubectl_auth/kubectl_auth_can-i/ "kubectl auth can-i | Kubernetes"
[2]: https://kubernetes.io/docs/reference/access-authn-authz/rbac/ "Using RBAC Authorization | Kubernetes"
[3]: https://kubernetes.io/docs/concepts/security/rbac-good-practices/ "Role Based Access Control Good Practices | Kubernetes"
