# 第21章：Ingressの基本と、2026年の注意点⚠️🌐🧭

この章は「**外からHTTP/HTTPSで入ってきた通信を、どのServiceに流す？**」を、Kubernetes流にスッキリ整理する回です😊✨
そして2026年は **Ingressまわりの“事情”が超重要** なので、そこもちゃんと押さえます⚠️

---

## 1) まず結論：Ingressは「ルール表」📄、実際に捌くのは「Ingress Controller」🚦

* **Ingress**：
  「`example.com/api` は `api-service`、`example.com/` は `web-service` に流す」みたいな **HTTPルーティングのルール** を書くKubernetesのAPIオブジェクト📄✨ ([Kubernetes][1])
* **Ingress Controller**：
  そのルール表（Ingress）を見て、実際にプロキシしてくれる **実行役** 🚦
  これがクラスタにいないと、Ingressを書いても何も起きません🫠 ([Kubernetes][2])

イメージ図（超ざっくり）👇

* 🌍 クライアント → 🚪（入口）Ingress Controller → 🧭（ルール）Ingress → 🧷 Service → 📦 Pod

---

## 2) Serviceだけじゃダメ？Ingressを使う理由💡

Serviceにも公開方法があるよね？って話、めっちゃ大事です🙂

* **Service: LoadBalancer**

  * 1サービスごとに外部IP/LBが必要になりがち💸
  * “入口”が増えやすい（運用が散らかりがち）🌀
* **Ingress**

  * 入口を1つ（または少数）にまとめて、**Host/Pathで振り分け** できる🎯
  * **TLS終端（HTTPS）** や **仮想ホスト** もやりやすい🔒 ([Kubernetes][1])

つまりIngressは、**「入口をまとめて交通整理する」** ための仕組みです🚥✨

---

## 3) 2026年の超重要注意点⚠️：Ingress自体は安定だけど“凍結”🍧

Kubernetes公式ドキュメントでは、Ingressについてこういう立ち位置になっています👇

* ✅ Ingress APIは **GA（安定）** で、Kubernetesから消す予定はない
* ⚠️ でも **Ingress APIは“凍結”されていて、新しい進化は基本しない**
* 👉 Kubernetesとしては **Gateway API推奨** の流れ ([Kubernetes][1])

この章でIngressを学ぶ価値はまだ全然あります🙆‍♂️
ただし2026年は特に「どのControllerを使うか」が運命を分けます😇😈

---

## 4) 2026年の超重要注意点⚠️：Ingress NGINXが“引退”🪦

多くの学習記事で出てくる **Ingress NGINX** は、公式に「引退」が明言されています⚠️

* **2026年3月まで**：ベストエフォート保守
* **それ以降**：リリースなし／バグ修正なし／脆弱性修正なし ([GitHub][3])
* 既存の導入が“すぐ壊れる”わけではないけど、放置すると危険性が増える、という強い警告も出ています ([Kubernetes][4])

さらに、Ingress NGINXのREADMEでも「すでに開発されていないので、新規導入するならGateway API実装を探してね」と明記されています ([GitHub][3])

✅ ここでの学び方（おすすめ）

* **Ingressの概念・YAML・トラブルシュートは学ぶ**（超重要🔥）
* ただし本番の入口に何を使うかは、**Ingress NGINX前提で固めない**（2026は特に）⚠️

---

## 5) Ingressを“誰に処理させるか”を決める：IngressClass🎫

Ingressは「どのControllerが担当するか」を指定できます。

* `spec.ingressClassName: nginx` みたいに書く✍️
* これで **複数Controller混在** も可能（チーム別など）🧩 ([Kubernetes][2])

---

## 実習💪✨：Ingressで「/a と /b を振り分け」してみる🚥

> 目的：Ingressの“ルール”が **Serviceに振り分ける** 感覚をつかむ🎯
> テストはローカルで `curl` します🧪

---

## 0) 作業用Namespaceを作る📁

```bash
kubectl create namespace ing-demo
```

---

## 1) 2つの“返事するだけ”アプリを動かす📦📦

ここでは軽量な `hashicorp/http-echo` を使って、A/Bの返事を作ります🙂

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: echo-a
  namespace: ing-demo
spec:
  replicas: 1
  selector:
    matchLabels: { app: echo-a }
  template:
    metadata:
      labels: { app: echo-a }
    spec:
      containers:
        - name: app
          image: hashicorp/http-echo:1.0
          args: ["-text=Hello from A 👋"]
          ports:
            - containerPort: 5678
---
apiVersion: v1
kind: Service
metadata:
  name: echo-a
  namespace: ing-demo
spec:
  selector: { app: echo-a }
  ports:
    - port: 80
      targetPort: 5678
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: echo-b
  namespace: ing-demo
spec:
  replicas: 1
  selector:
    matchLabels: { app: echo-b }
  template:
    metadata:
      labels: { app: echo-b }
    spec:
      containers:
        - name: app
          image: hashicorp/http-echo:1.0
          args: ["-text=Hello from B ✨"]
          ports:
            - containerPort: 5678
---
apiVersion: v1
kind: Service
metadata:
  name: echo-b
  namespace: ing-demo
spec:
  selector: { app: echo-b }
  ports:
    - port: 80
      targetPort: 5678
```

適用👇

```bash
kubectl apply -f echo-ab.yaml
kubectl -n ing-demo get pod,svc
```

---

## 2) Ingress Controllerを入れる🚦（学習用）

IngressはControllerがいないと動かないので、Controllerを入れます。([Kubernetes][2])

ここでは例として「Ingressの学習で有名」なIngress NGINXを使いますが、**2026年3月以降の本番利用は要注意** という前提で “概念学習に寄せます”⚠️ ([Kubernetes][4])

（クラスタがローカルでも動きやすい “cloud” 用のマニフェスト例）

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.14.2/deploy/static/provider/cloud/deploy.yaml
kubectl -n ingress-nginx get pod,svc
```

`ingress-nginx-controller` が `Running` になったらOKです✅

---

## 3) Ingress（ルール表）を書く📄🧭

Hostが `demo.local` のときに👇

* `/a` → `echo-a`
* `/b` → `echo-b`

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: demo-ing
  namespace: ing-demo
spec:
  ingressClassName: nginx
  rules:
    - host: demo.local
      http:
        paths:
          - path: /a
            pathType: Prefix
            backend:
              service:
                name: echo-a
                port:
                  number: 80
          - path: /b
            pathType: Prefix
            backend:
              service:
                name: echo-b
                port:
                  number: 80
```

適用👇

```bash
kubectl apply -f ingress.yaml
kubectl -n ing-demo get ingress
kubectl -n ing-demo describe ingress demo-ing
```

---

## 4) 動作確認🧪（Hostヘッダでテストする）

ローカルだと外部IPが用意されないことがあるので、ControllerのServiceをポートフォワードして確実に試します🎯

```bash
kubectl -n ingress-nginx port-forward svc/ingress-nginx-controller 8080:80
```

別ターミナル（PowerShellでもOK）で👇

```bash
curl -H "Host: demo.local" http://localhost:8080/a
curl -H "Host: demo.local" http://localhost:8080/b
```

* `/a` → `Hello from A 👋`
* `/b` → `Hello from B ✨`

が返ってきたら勝ちです🎉🎉🎉

---

## “詰まったらここ”🧯：Ingressトラブルシュートの型🧠

## A) Ingressは作れた？📄

```bash
kubectl -n ing-demo get ingress
kubectl -n ing-demo describe ingress demo-ing
```

**イベント欄** に「classが無い」「controllerが無い」系が出てたら、まずController側を疑う👀

## B) Controllerは動いてる？🚦

```bash
kubectl -n ingress-nginx get pod,svc
kubectl -n ingress-nginx logs deploy/ingress-nginx-controller --tail=200
```

## C) Serviceの先にPodがいる？🧷📦

```bash
kubectl -n ing-demo get svc,ep
kubectl -n ing-demo get pod -o wide
```

* Serviceの`Endpoints`が空だと、**selector/label不一致** が多いです😇

---

## 設計ミニTips🧩✨（超入門でも効くやつ）

## 1) ルールは“アプリ単位”で分けると管理が楽📁

* Ingressが巨大1枚になると、変更が怖くなる😱
* まずは **1アプリ=1Ingress** くらいが扱いやすいです🙂

## 2) annotation地獄は避ける（Controller乗り換えが地獄化）🌀

* IngressはControllerごとに「独自annotation」が多いです
* 使えば便利だけど、**依存が濃くなる** → 乗り換えが辛い🥲
* 2026年は特に「入口の乗り換え」が現実の話なので、最小から！⚠️ ([Kubernetes][4])

---

## 2026チェック：自分のクラスタがIngress NGINX依存か確認🔎

本番運用者向けの確認コマンドとして、公式ステートメントでも言及されています👇 ([Kubernetes][4])

```bash
kubectl get pods --all-namespaces --selector app.kubernetes.io/name=ingress-nginx
```

出たら「入口がそれ」かもしれないので、計画的に移行を検討🧠

---

## まとめ🎁

* Ingressは **HTTP/HTTPSのルール表** 📄
* 動かすには **Ingress Controllerが必須** 🚦 ([Kubernetes][2])
* 2026の重要ポイント：

  * Ingress APIは安定だけど凍結、今後の推奨はGateway API寄り ([Kubernetes][1])
  * Ingress NGINXは **2026年3月で引退**（以降リリース/修正なし）⚠️ ([Kubernetes][4])

次の第22章は、まさにこの流れを受けた **Gateway API**（GA以降の本命）に入ります🚪✨ ([Kubernetes][5])

[1]: https://kubernetes.io/docs/concepts/services-networking/ingress/ "Ingress | Kubernetes"
[2]: https://kubernetes.io/docs/concepts/services-networking/ingress-controllers/ "Ingress Controllers | Kubernetes"
[3]: https://github.com/kubernetes/ingress-nginx "GitHub - kubernetes/ingress-nginx: Ingress NGINX Controller for Kubernetes"
[4]: https://kubernetes.io/blog/2026/01/29/ingress-nginx-statement/ "Ingress NGINX: Statement from the Kubernetes Steering and Security Response Committees | Kubernetes"
[5]: https://kubernetes.io/blog/2025/11/06/gateway-api-v1-4/ "Gateway API 1.4: New Features | Kubernetes"
