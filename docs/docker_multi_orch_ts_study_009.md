# 第09章：Serviceで“つなぐ”（サービスディスカバリ）🧷🧠✨

この章は、**「PodのIPがコロコロ変わっても、アプリ同士を安定してつなぐ方法」**を身につける回です！😆
Kubernetesの世界だと、**“つなぎ先はIPじゃなくて名前で呼ぶ”**が基本になります📛🔗

> ちなみに本日（2026-02-13）時点のKubernetesは **v1.35.1（2026-02-10リリース）**です。([Kubernetes][1])
> この章の内容（Service / DNS / EndpointSlice）は、まさに現行の中心機能です💪([Kubernetes][2])

---

## 9.1 まず結論：Serviceは「固定の入り口（住所＆電話番号）」📞🏠

Podは落ちたり増えたりして、**IPが変わるのが通常運転**です😇💥
だから **PodのIPに直打ち**すると、すぐ壊れます🫠

そこで登場するのが **Service** です🧷

* **Service**：安定した入口（固定の名前＆仮想IP）📌
* **Pod**：中身（入れ替わること前提）♻️
* **Label / Selector**：どのPodを“中身”として束ねるかの紐づけ🏷️

Kubernetes公式の「Serviceの概念ページ」でも、この思想がど真ん中です。([Kubernetes][2])

---

## 9.2 Serviceディスカバリって何？🤔➡️😎

**Serviceディスカバリ = “サービスを見つける仕組み”**です🧭✨
Kubernetesでは主に **DNS** で見つけます📡

* `db` というServiceを作る
* アプリは `db`（名前）で接続する
* DNSが `db` を解決して、Serviceに到達する

Kubernetesは **ServiceやPodにDNSレコードを作る**仕組みを持っていて、Pod内から「名前で引ける」ようにしてくれます。([Kubernetes][3])

DNS名のルール（ざっくり）👇

* 同じNamespaceなら：`db` だけでOKなことが多い👍
* 別Namespaceなら：`db.<namespace>` や `db.<namespace>.svc.cluster.local` が必要になることがある🌍
  （この仕組み自体がKubernetesの基本仕様です）([Kubernetes][3])

---

## 9.3 Serviceの種類（超ざっくり使い分け）🧰✨

よく使うのはこのへんです👇（名前だけでも覚えれば勝ち🏆）

* **ClusterIP（基本これ）**：クラスタ内部だけの入口🏠
* **NodePort**：各ノードのポートを開けて外から入れる🚪
* **LoadBalancer**：クラウドのLBを使って外から入れる🌩️
* **ExternalName**：外部のDNS名へのエイリアス👻
* **Headless（ClusterIPなし）**：Podを直接見せたい時（Stateful系で多い）🧱

Serviceの公式ドキュメントにまとまっています。([Kubernetes][2])
※ この章はまず **ClusterIP** を主役にします🥳

---

## 9.4 Serviceの裏側：EndpointSliceが“実体の名簿”📇🧠

Serviceは「入口」です。
でも実際にどのPodへ流すかは、**EndpointSlice** が持っています📇✨

ざっくり図にすると👇

* Service（入口）
  → EndpointSlice（名簿）
  → PodIP:Port（本体）

EndpointSliceは **Serviceをスケールさせるための仕組み**として公式に説明されています。([Kubernetes][4])
また、EndpointsからEndpointSliceへ移行が進んでいて、Service周りの新機能はEndpointSliceが前提になっています。([Kubernetes][5])

---

## 9.5 ハンズオン：API → DB（っぽいもの）を“名前で”つなぐ🔗🍔🗄️

ここから手を動かします✋✨
ゴールはこれ👇

* `api` が **`db` という名前**で接続する
* Podが入れ替わっても壊れない
* つながらない時に「どこを見るか」まで分かる

---

## 手順A：Namespaceを作る（迷子防止）🧭📁

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: demo
```

適用👇

```bash
kubectl apply -f namespace.yaml
```

---

## 手順B：DB（今回はPostgreSQL）＋ Service `db` を作る🐘🧷

> ここは「つなぐ練習」なので、DBをDeploymentで置きます🙆‍♂️
> “ちゃんとしたDB運用”は後半（StatefulSetやPVC）でやる想定です🧱💾

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: db
  namespace: demo
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
        - name: postgres
          image: postgres:17
          ports:
            - containerPort: 5432
          env:
            - name: POSTGRES_PASSWORD
              value: postgres
            - name: POSTGRES_USER
              value: postgres
            - name: POSTGRES_DB
              value: appdb
---
apiVersion: v1
kind: Service
metadata:
  name: db
  namespace: demo
spec:
  type: ClusterIP
  selector:
    app: db
  ports:
    - name: postgres
      port: 5432
      targetPort: 5432
```

適用👇

```bash
kubectl apply -f db.yaml
kubectl -n demo get pods,svc
```

ここで **`svc/db` ができていればOK**です🎉

---

## 手順C：API（Node/TS）＋ Service `api` を作る🍔🧷

Nodeは本日（2026-02-13）時点で **v24がActive LTS** です。([nodejs.org][6])
なのでサンプルは Node 24 を基準にします🚀

## ① APIの最小コード（TypeScript）✍️✨

`src/server.ts`

```ts
import express from "express";
import { Client } from "pg";

const app = express();
const port = Number(process.env.PORT ?? "3000");

// Kubernetes Service名でつなぐのがポイント！
const dbHost = process.env.DB_HOST ?? "db";
const dbUser = process.env.DB_USER ?? "postgres";
const dbPass = process.env.DB_PASS ?? "postgres";
const dbName = process.env.DB_NAME ?? "appdb";

function createClient() {
  return new Client({
    host: dbHost,
    user: dbUser,
    password: dbPass,
    database: dbName,
    port: 5432,
  });
}

app.get("/health", (_req, res) => {
  res.json({ ok: true });
});

app.get("/health/db", async (_req, res) => {
  const client = createClient();
  try {
    await client.connect();
    const r = await client.query("SELECT 1 AS ok");
    res.json({ ok: true, db: r.rows[0] });
  } catch (e: any) {
    res.status(500).json({ ok: false, error: String(e?.message ?? e) });
  } finally {
    await client.end().catch(() => {});
  }
});

app.listen(port, () => {
  console.log(`api listening on :${port} (db host: ${dbHost})`);
});
```

`package.json`（最小）

```json
{
  "name": "k8s-service-demo",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "node --watch --enable-source-maps dist/server.js",
    "build": "tsc -p tsconfig.json",
    "start": "node dist/server.js"
  },
  "dependencies": {
    "express": "^4.19.2",
    "pg": "^8.13.0"
  },
  "devDependencies": {
    "typescript": "^5.8.0"
  }
}
```

`tsconfig.json`（最小）

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ES2022",
    "moduleResolution": "Bundler",
    "outDir": "dist",
    "strict": true,
    "esModuleInterop": true
  },
  "include": ["src"]
}
```

## ② Dockerfile（シンプルに）🐳📦

```dockerfile
FROM node:24-slim

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci || npm i

COPY tsconfig.json ./
COPY src ./src

RUN npm run build

ENV PORT=3000
EXPOSE 3000

CMD ["npm", "start"]
```

> ここまで作ったら、いつもの流れでイメージを作って（前章までのやり方でOK）レジストリに置く想定です📦🚚
> （kindなら `kind load docker-image ...` でもOKな構成にできます👍）

## ③ Kubernetesマニフェスト（Deployment + Service）📄🧷

`api.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: demo
spec:
  replicas: 2
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
        - name: api
          image: YOUR_REGISTRY/your-api:1.0.0
          ports:
            - containerPort: 3000
          env:
            - name: PORT
              value: "3000"
            - name: DB_HOST
              value: "db"          # ← Service名で接続！
            - name: DB_USER
              value: "postgres"
            - name: DB_PASS
              value: "postgres"
            - name: DB_NAME
              value: "appdb"
---
apiVersion: v1
kind: Service
metadata:
  name: api
  namespace: demo
spec:
  type: ClusterIP
  selector:
    app: api
  ports:
    - name: http
      port: 3000
      targetPort: 3000
```

適用👇

```bash
kubectl apply -f api.yaml
kubectl -n demo get pods,svc
```

---

## 手順D：つながったか確認する✅🎯

## ① まずログを見る👀🪵

```bash
kubectl -n demo logs deploy/api
```

`db host: db` と出ていれば意図通りです👍

## ② Podの中から `db` が引けるか（DNSチェック）📡🔍

Kubernetes公式でも、DNSトラブルは「クラスタ内から確認する」のが王道です。([Kubernetes][7])

```bash
kubectl -n demo run -it --rm debug --image=busybox:1.36 --restart=Never -- sh
```

中で👇

```sh
nslookup db
nslookup db.demo.svc.cluster.local
```

> もし `nslookup` が無い/動かない感じなら、ネットワーク調査ツール盛り盛りの `netshoot` を使うのも定番です🧰
> （KubernetesでもDockerでもよく使われます）([GitHub][8])

```bash
kubectl -n demo run -it --rm net --image=nicolaka/netshoot --restart=Never -- bash
```

中で👇

```bash
dig db.demo.svc.cluster.local
```

## ③ `api` をローカルから叩く（port-forward）🚇💻

```bash
kubectl -n demo port-forward svc/api 3000:3000
```

別ターミナルで👇

```bash
curl http://localhost:3000/health
curl http://localhost:3000/health/db
```

`/health/db` が `ok: true` なら勝ち🎉🎉🎉

---

## 9.6 つながらない時の“型”🧯🥋（ここが超重要）

Service周りは、だいたい事故パターンが決まってます😎✨
順番に潰せばOK！

---

## パターン1：ServiceのselectorがPodのlabelとズレてる🏷️❌

確認👇

```bash
kubectl -n demo get svc db -o yaml
kubectl -n demo get pods --show-labels
```

**selectorの `app: db`** と、Podの **labelの `app=db`** が一致してないと、Serviceの中身が空になります🫠

---

## パターン2：Serviceに“中身”がいない（EndpointSliceが空）📇❌

確認👇（Service名で絞る）

```bash
kubectl -n demo get endpointslices -l kubernetes.io/service-name=db
kubectl -n demo describe svc db
```

EndpointSliceがServiceのバックエンド（到達先）を表します。([Kubernetes][4])

---

## パターン3：port / targetPort を間違えた🔌😵

ありがち👇

* `port: 5432` なのに `targetPort: 15432` とか
* アプリ側が `DB_HOST=db:5432` じゃなくて変なポートを見てる

確認👇

```bash
kubectl -n demo describe svc db
kubectl -n demo describe pod -l app=db
```

---

## パターン4：Namespaceを間違えた📁😇➡️😱

* `demo` にServiceがあるのに
* `default` のPodから `db` を引いてる

対策：別Namespaceなら **FQDN** を使う（`db.demo.svc.cluster.local`）🌍([Kubernetes][3])

---

## パターン5：DNS自体が壊れてる（CoreDNS）📡💥

Kubernetes公式のDNSデバッグ手順が用意されています。([Kubernetes][7])
まずはこれ👇

* `kubernetes.default` が引けるか（超基本）
* `db.demo.svc.cluster.local` が引けるか（今回の本題）

---

## 9.7 ちいさい課題（5〜15分）📝✨

1. `api` を `replicas: 5` に増やしてみる📈

   * `kubectl -n demo get pods -l app=api -o wide` で増えたの確認👀
2. `db` Podを消してみる😈

   * `kubectl -n demo delete pod -l app=db`
   * IPが変わっても、**Service名 `db` でつながり続ける**のを確認🔁
3. わざと `selector` を壊して「つながらない」を作る🧨

   * そして **describe / endpointslice / nslookup** で復旧する🧯

---

## 9.8 AIに手伝ってもらうコツ🤖🪄（超おすすめ）

* 「このService、selectorとlabel合ってる？合ってないなら具体的にどこ？」🕵️‍♂️
* 「`kubectl describe svc db` の出力貼る→原因候補を3つ＋確認コマンドも」🔍
* 「`api.yaml` を“安全寄りの初学者向け”に整えて（コメント付き）」📝
* 「port/targetPort/コンテナportの関係を図で説明して」🧠📈

※ ただしAIは“それっぽいYAML”を平気で出すので、**必ず `kubectl describe` と `get endpointslices` で裏取り**しましょ✅😎

---

## まとめ🎉

* PodはIPが変わる → **名前で呼ぶ**のが正解📛
* **Service** が「安定した入口」になり、DNSで見つけられる📡([Kubernetes][3])
* 裏側は **EndpointSlice** が名簿を持ってる📇([Kubernetes][4])
* つながらない時は「selector」「EndpointSlice」「DNS」「port」を順に見る🥋🧯

次の章（10章）で、Label/Selector/Namespaceをさらに“整理整頓スキル”として固めると、迷子率が激減します🧹🧭✨

[1]: https://kubernetes.io/releases/?utm_source=chatgpt.com "Releases"
[2]: https://kubernetes.io/docs/concepts/services-networking/service/?utm_source=chatgpt.com "Service"
[3]: https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/?utm_source=chatgpt.com "DNS for Services and Pods"
[4]: https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/?utm_source=chatgpt.com "EndpointSlices"
[5]: https://kubernetes.io/blog/2025/04/24/endpoints-deprecation/?utm_source=chatgpt.com "Continuing the transition from Endpoints to EndpointSlices"
[6]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[7]: https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution/?utm_source=chatgpt.com "Debugging DNS Resolution"
[8]: https://github.com/nicolaka/netshoot?utm_source=chatgpt.com "nicolaka/netshoot: a Docker + Kubernetes network trouble- ..."
