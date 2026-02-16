# 第24章：NetworkPolicyで“話していい相手”を決める🧱📡

Kubernetesのクラスタ内って、何もしないと **「基本ぜんぶ通る」** ことが多いんですね😇
そこで登場するのが **NetworkPolicy**（Pod単位の通信ルール）です🔥

---

## この章のゴール🎯✨

* 「DBはAPIからしか喋れない」みたいな **最小通信（Allow-list）** を作れるようになる🛡️
* **Ingress（入ってくる）** と **Egress（出ていく）** を分けて考えられるようになる🧠
* “やりがちな事故”の代表 **DNSが死ぬ💀** を回避できるようになる🧯

---

## まず超大事なこと3つ🥇🥈🥉

1. **NetworkPolicyは L3/L4（IP/ポート）レベルの「許可ルール」** だよ🧱
   → HTTPのパス単位とかは「標準」ではやらない（別の仕組みや拡張が必要）📦
   しかも **ネットワークプラグイン（CNI）が対応してないと、書いても効かない** 🫠
   ([Kubernetes][1])

2. **ルールは“足し算”** ➕
   Podが複数のNetworkPolicyに当たってたら、許可は合算（Union）されるよ🧩
   ([Kubernetes][1])

3. 片側だけ許可してもダメなことがある⚠️
   接続はだいたい **「出ていく(Egress)」×「入ってくる(Ingress)」** の両方が揃って成立するイメージ🪄
   ([Kubernetes][1])

---

## イメージで理解🏢🔑（オフィスの入館管理）

* **Pod**：部屋👤
* **Service**：内線番号☎️（中の部屋が入れ替わっても番号は同じ）
* **NetworkPolicy**：入退室ルール🛂

  * Ingress = 「この部屋に入っていい人は誰？」
  * Egress = 「この部屋から出ていっていい先はどこ？」

---

## ハンズオン🔥「DBはAPIからだけ許可」してみる

> ここは “小さく壊して→直す” が最強です💪😆

## 1) サンプルをデプロイ🎬

まず `np-demo` 名前空間に、3人配置します👇

* api（curlできる人）
* db（nginxの部屋）
* attacker（攻撃役😈）

```yaml
## 01-demo-apps.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: np-demo
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: db
  namespace: np-demo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: db
  template:
    metadata:
      labels:
        app: db
    spec:
      containers:
        - name: nginx
          image: nginx:1.27-alpine
          ports:
            - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: db
  namespace: np-demo
spec:
  selector:
    app: db
  ports:
    - name: http
      port: 80
      targetPort: 80
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: np-demo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
        - name: curl
          image: curlimages/curl:8.6.0
          command: ["sh","-c","sleep 365d"]
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: attacker
  namespace: np-demo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: attacker
  template:
    metadata:
      labels:
        app: attacker
    spec:
      containers:
        - name: curl
          image: curlimages/curl:8.6.0
          command: ["sh","-c","sleep 365d"]
```

適用👇

```bash
kubectl apply -f 01-demo-apps.yaml
kubectl -n np-demo get pods -w
```

動作確認（まずは“全部通る世界”を体験）👇

```bash
kubectl -n np-demo exec deploy/api -- curl -sS -m 2 http://db | head
kubectl -n np-demo exec deploy/attacker -- curl -sS -m 2 http://db | head
```

両方通ったらOK✅（= まだ守りゼロ😇）

---

## 2) DBへのIngressを「いったん全拒否」🚧

DB（app=db）に対して **Ingressを空にする** と、DBは「隔離」されます🧊
（これが “default deny（まず閉じる）” の基本）
([Calico ドキュメント][2])

```yaml
## 10-db-default-deny-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: db-default-deny-ingress
  namespace: np-demo
spec:
  podSelector:
    matchLabels:
      app: db
  policyTypes:
    - Ingress
  ingress: []
```

```bash
kubectl apply -f 10-db-default-deny-ingress.yaml
```

確認👇（どっちも失敗するのが正解🎯）

```bash
kubectl -n np-demo exec deploy/api -- curl -sS -m 2 http://db || echo "blocked"
kubectl -n np-demo exec deploy/attacker -- curl -sS -m 2 http://db || echo "blocked"
```

> もし **まだ通っちゃう** 場合は、CNIがNetworkPolicyを実装してなくて “効いてない” 可能性が高いです🫠
> NetworkPolicyは「対応プラグインがいて初めて効く」仕様です。([Kubernetes][1])

---

## 3) 「APIからだけ」DBへのIngressを許可🟢

```yaml
## 11-db-allow-from-api.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: db-allow-from-api
  namespace: np-demo
spec:
  podSelector:
    matchLabels:
      app: db
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: api
      ports:
        - protocol: TCP
          port: 80
```

```bash
kubectl apply -f 11-db-allow-from-api.yaml
```

確認👇（apiは通る、attackerは死ぬ😈💥）

```bash
kubectl -n np-demo exec deploy/api -- curl -sS -m 2 http://db | head
kubectl -n np-demo exec deploy/attacker -- curl -sS -m 2 http://db || echo "blocked"
```

ここまでで章の本題はクリアです🎉

---

## 発展🔥：Egressも縛って「API→DB以外ムリ」にする

Ingressだけでも守りは強くなるけど、より堅くするなら **API側のEgress** も閉じます🔒

## 4) APIのEgressをいったん全拒否🚫

```yaml
## 20-api-default-deny-egress.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-default-deny-egress
  namespace: np-demo
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
    - Egress
  egress: []
```

```bash
kubectl apply -f 20-api-default-deny-egress.yaml
kubectl -n np-demo exec deploy/api -- curl -sS -m 2 http://db || echo "blocked"
```

ここで詰まるあるある👇

* **DNSが引けなくて** `http://db` が解決できない💀
* あるいは “出ていく通信” 自体が止まる🧱

---

## 5) API→DBのEgressを許可🟢

```yaml
## 21-api-allow-egress-to-db.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-allow-egress-to-db
  namespace: np-demo
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
    - Egress
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: db
      ports:
        - protocol: TCP
          port: 80
```

```bash
kubectl apply -f 21-api-allow-egress-to-db.yaml
```

---

## 6) DNS（kube-dns/CoreDNS）へのEgressを許可🌐🟢

まず DNS Pod のラベルを確認👇（`k8s-app=kube-dns` が多いです）

```bash
kubectl -n kube-system get pods -o wide | findstr dns
kubectl -n kube-system get pods -l k8s-app=kube-dns
```

（見つからないなら `k8s-app=coredns` なども試す👀）

そして許可ポリシー👇

```yaml
## 22-api-allow-dns.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-allow-dns
  namespace: np-demo
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
    - Egress
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
          podSelector:
            matchLabels:
              k8s-app: kube-dns
      ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
```

```bash
kubectl apply -f 22-api-allow-dns.yaml
kubectl -n np-demo exec deploy/api -- curl -sS -m 2 http://db | head
```

---

## “効いてるCNI”の代表例（2026年の定番）🧠✨

* Cilium：各ノードにPodが立って、Linux BPF（eBPF）でポリシーを実行するタイプ。Kubernetes公式ドキュメントにも手順があり、L3/L4だけでなくL7の例にも触れてます📘([Kubernetes][3])
* Calico：NetworkPolicyの定番。ingress/egressやdefault denyの考え方がめちゃ分かりやすいです🧠([Calico ドキュメント][2])

---

## よくある事故と対処🧯😵‍💫

## 事故1：ポリシーを書いたのに“何も変わらない”🫠

→ **CNIがNetworkPolicy非対応** だと “無視される” 仕様です。([Kubernetes][1])

## 事故2：いきなりEgress閉めてDNS死亡💀

→ **DNS(53/udp,tcp)だけ先に許可** をテンプレ化すると安定します🌱

## 事故3：適用直後だけ挙動がフワつく😵

→ プラグインは全ノードに同時反映できないことがあり、**適用に時間がかかる** 場合があります（Podが一瞬“守られてない状態”で走る可能性の注意もあり）。([Kubernetes][1])

---

## ミニ演習（おすすめ）📝✨

1. **namespaceを分ける**

* `front` namespace のPodだけが `api` に入れるようにしてみよう👣
  （namespaceSelector + podSelector を使うやつ）([Calico ドキュメント][2])

2. **外部へHTTPSだけ許可**

* `api` のEgressを `tcp/443` だけ `ipBlock` で許可してみよう🌍🔒
  ([Calico ドキュメント][2])

3. **namespace全体を default deny**

* `podSelector: {}` で “全部閉める” → 必要な通信だけ戻す🧊➡️🌸
  ([Calico ドキュメント][2])

---

## AI活用（最短で上達するやつ🤖⚡）

* 「この要件を満たすNetworkPolicy YAMLを2つに分けて（default deny / allow）作って。labelsはこう…」
* 生成されたら必ず👇をAIにチェックさせる

  * **podSelectorが“守りたい側”を選んでる？**
  * **from/toが“通していい相手”になってる？**
  * **DNS許可が必要な場面を潰してる？**
  * **policyTypesが意図どおり？**

AIはRBACほどではないけど、NetworkPolicyもわりとミスるので「説明つきでレビューして」って言うのがコツです😆👍

---

## 後片付け🧹

```bash
kubectl delete ns np-demo
```

---

必要なら、この第24章の続きとして **「HTTPパス単位で守りたいんだけど？」** を、Cilium のL7例（もしくはService Meshの超入口）として、超やさしく繋げる構成にもできますよ🚪✨

[1]: https://kubernetes.io/docs/concepts/services-networking/network-policies/ "Network Policies | Kubernetes"
[2]: https://docs.tigera.io/calico/latest/network-policy/get-started/kubernetes-policy/kubernetes-network-policy "Get started with Kubernetes network policy | Calico Documentation"
[3]: https://kubernetes.io/docs/tasks/administer-cluster/network-policy-provider/cilium-network-policy/ "Use Cilium for NetworkPolicy | Kubernetes"
