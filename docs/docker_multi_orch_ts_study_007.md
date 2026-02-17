# 第07章：PodでNode/TS APIを動かす🍔🐳☸️

この章はとにかく **「1 Podで動いた！🎉」** まで一直線です。
（次の第8章で Deployment にして「落ちても戻る🛟」へ進化させます）

---

## この章でできるようになること🎯

* Pod（= いちばん小さい実行単位）で **Node/TypeScript APIを起動**できる🍔
* `kubectl get/describe/logs/exec` で **生存確認＆原因調査**できる🔎
* `kubectl port-forward` で **手元PCからアクセス**できる🌐 ([Kubernetes][1])
* “よくある詰まり”の **最短直し方**が分かる🧯

---

## まずは超重要な前提（この章の地雷だけ回避💣）

![localhost_vs_0000_trap](./picture/docker_multi_orch_ts_study_007_localhost_vs_0000_trap.png)

Podで動かすWebサーバーは、**コンテナ内で `0.0.0.0` にバインド**してないと外から繋がりません🙅‍♂️
「ローカルでは動くのに、K8sだと繋がらない」No.1原因です🥲

---

## 0) 今日の環境メモ（2026年の“今”）🗓️✨

* Kubernetes の最新パッチは **v1.35.1（2026-02-10）** ([Kubernetes][2])
* ローカル学習だと kind は **v0.31.0 でデフォルトKubernetes 1.35.0** ([GitHub][3])
* minikube の最新は **v1.38.0（2026-01-28）** ([minikube][4])
* Node は **v24 が Active LTS**（安定枠） ([nodejs.org][5])
* TypeScript は **5.9系が安定版**、6.0はBeta情報あり（学習は安定版推奨） ([GitHub][6])

---

## 1) “動かす対象”のAPI（すでにイメージがあるなら読み飛ばしOK✅）

ここでは最小のAPIを用意します🍔
エンドポイントは2つだけ：

* `GET /health` → `ok`
* `GET /hello` → `hello from pod`

## 1-1) `src/index.ts`（最小のExpress API）🧩

```ts
import express from "express";

const app = express();

app.get("/health", (_req, res) => res.status(200).send("ok"));
app.get("/hello", (_req, res) => res.status(200).send("hello from pod"));

const port = Number(process.env.PORT ?? 3000);

// ⭐超重要：0.0.0.0 で待ち受ける（これがないとPod外から繋がりにくい）
app.listen(port, "0.0.0.0", () => {
  console.log(`listening on http://0.0.0.0:${port}`);
});
```

## 1-2) `Dockerfile`（学習用：分かりやすさ優先）🐳

```dockerfile
## build
FROM node:24-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY tsconfig.json ./
COPY src ./src
RUN npm run build

## runtime
FROM node:24-alpine
WORKDIR /app
ENV NODE_ENV=production
COPY --from=build /app/package*.json ./
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

> ここまでが “アプリ側”。次は “Kubernetes側” に入ります☸️✨

---

## 2) イメージをクラスタに「届ける」📦🚚（第6章の復習ミニ）

Podは **ノード（複数）それぞれがイメージを取る**世界です🌍
ローカル学習では、だいたい次のどっちかでOK：

## A. kind の場合：`kind load docker-image` が楽ちん🚀

公式にもこの手順が載っています ([Kind][7])

```bash
## 例：ローカルでビルド
docker build -t ts-api:0.1.0 .

## kindクラスタへ読み込み（クラスタ名があるなら --name も）
kind load docker-image ts-api:0.1.0
```

## B. minikube の場合：`minikube image load` が定番🧳

（コマンド体系として `minikube image ...` が用意されています） ([minikube][8])

```bash
docker build -t ts-api:0.1.0 .
minikube image load ts-api:0.1.0
```

> もちろん「レジストリにpushしてpull」でもOKです👍（本番は基本それ）

---

## 3) Podマニフェストを書く📄✍️（この章の主役）

![pod_anatomy_simple](./picture/docker_multi_orch_ts_study_007_pod_anatomy_simple.png)

ファイル名：`pod-ts-api.yaml`

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: ts-api-pod
  labels:
    app: ts-api
spec:
  containers:
    - name: api
      image: ts-api:0.1.0
      imagePullPolicy: IfNotPresent
      ports:
        - containerPort: 3000
      env:
        - name: PORT
          value: "3000"
        - name: NODE_ENV
          value: "production"
```

## ここで覚えるポイント🧠✨

* `kind: Pod` は **“生身の1体”**（増やす・入れ替えるのは次章）🧍
* `labels` は次に Service/Deployment で効いてくる名札🏷️
* `imagePullPolicy: IfNotPresent` はローカル学習で便利（引っ張り失敗を減らす）🧯

---

## 4) 起動して「動いた！」まで行く🎉

## 4-1) apply（投入！）🚀

```bash
kubectl apply -f pod-ts-api.yaml
```

## 4-2) 状態を見る（まず get）👀

![kubectl_get_vs_describe](./picture/docker_multi_orch_ts_study_007_kubectl_get_vs_describe.png)

```bash
kubectl get pod -w
```

* `Running` になったら第一関門突破🥳
* `ImagePullBackOff` とか出たら、次の「詰まり集」へ🧯

## 4-3) 詳細を見る（困ったら describe）🔎

```bash
kubectl describe pod ts-api-pod
```

> 「何が起きてる？」はだいたい describe に書いてあります📘

---

## 5) ログを見る📜（Podの心の声）

![kubectl_logs_concept](./picture/docker_multi_orch_ts_study_007_kubectl_logs_concept.png)

```bash
kubectl logs ts-api-pod
```

追いかけたいなら follow（いわゆる tail）🧵
`kubectl logs -f` は公式リファレンスにもあります ([Kubernetes][9])

```bash
kubectl logs -f ts-api-pod
```

---

## 6) Podの中に入って確認する🕵️‍♂️（exec）

![kubectl_exec_teleport](./picture/docker_multi_orch_ts_study_007_kubectl_exec_teleport.png)

```bash
kubectl exec -it ts-api-pod -- sh
```

中でこんな感じにチェックできます✅

```sh
## 環境変数
echo $PORT

## ローカル疎通（コンテナ内）
wget -qO- http://localhost:3000/health
```

---

## 7) 手元PCからアクセスする🌐（port-forward）

![kubectl_port_forward_tunnel](./picture/docker_multi_orch_ts_study_007_kubectl_port_forward_tunnel.png)

Pod に対してポート転送します🚪
コマンド仕様は公式の `kubectl port-forward` に載っています ([Kubernetes][1])

```bash
kubectl port-forward pod/ts-api-pod 3000:3000
```

ブラウザでアクセス🎉

* `http://localhost:3000/health`
* `http://localhost:3000/hello`

---

## 8) わざと壊して「Podの限界」も体感😈➡️😇

Podは “1体” なので、アプリが落ちると再起動はしますが、**運用として強い形ではない**です（次章で進化）🛟

簡単な実験：

1. `PORT` を変な値にする（例：文字列）
2. apply
3. `kubectl get pod` で `RESTARTS` が増えるのを見る👀

```bash
kubectl get pod
kubectl describe pod ts-api-pod
kubectl logs -f ts-api-pod
```

---

## 9) よくある詰まり集🧯（最短で抜ける）

## A) `ImagePullBackOff` / `ErrImagePull` 📦💥

原因あるある：

* タグ間違い（`0.1.0` が `0.1.O` とか）😇
* ローカルイメージをクラスタに読み込んでない（kind/minikube）😅
* レジストリがprivateで認証できてない🔐

対処：

* kind → `kind load docker-image ...` ([Kind][7])
* minikube → `minikube image load ...` ([minikube][8])
* まず `kubectl describe pod ...` の Events を見る👀

## B) `CrashLoopBackOff` 🔁💀

![crash_loop_back_off](./picture/docker_multi_orch_ts_study_007_crash_loop_back_off.png)

対処：

* `kubectl logs -f ts-api-pod` ([Kubernetes][9])
* アプリが「0.0.0.0 で待ち受けてるか」を確認✅（最重要）

## C) `port-forward` はできたのに繋がらない🌐❌

原因：

* アプリが `localhost` バインドになってる

対処：

* Nodeの listen を `"0.0.0.0"` にする（この章の地雷回避）💣➡️✅

## D) `Pending` のまま🕰️

対処：

* `kubectl describe pod ...` の `Events` を見る
  （リソース不足、ノードの準備不足などが見える👀）

---

## 10) できたかチェック✅（セルフテスト）

* [ ] `kubectl get pod` で `Running` を見た👀
* [ ] `kubectl logs` で “listening...” を見た📜 ([Kubernetes][9])
* [ ] `kubectl port-forward` で `/health` が `ok` になった🌐 ([Kubernetes][1])
* [ ] `kubectl exec` で Pod の中から `localhost` 疎通した🕵️‍♂️

---

## 🤖 AIで楽するポイント（この章）✨

* YAMLを書いたらAIにこう聞く：
  「このPod、起動しない可能性あるところを3つ指摘して。**Eventsで確認する場所**もセットで」🔎
* `kubectl describe` の出力を貼って：
  「この Events の読み方を、**原因→確認→対処**で短くまとめて」🧯

---

## 次の章へのつながり🔗✨

Podで「動いた！」は達成🎉
でも Pod は “生身の1体” なので、次は **Deployment** で **落ちても戻る🛟＆増やせる📈** に進化します！

（第8章でやること：replicas / rollout / “Podを消して復活を見る” 😈➡️😇）

[1]: https://kubernetes.io/docs/reference/kubectl/generated/kubectl_port-forward/?utm_source=chatgpt.com "kubectl port-forward"
[2]: https://kubernetes.io/releases/?utm_source=chatgpt.com "Releases"
[3]: https://github.com/kubernetes-sigs/kind/releases?utm_source=chatgpt.com "Releases · kubernetes-sigs/kind"
[4]: https://minikube.sigs.k8s.io/?utm_source=chatgpt.com "Welcome! | minikube"
[5]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[6]: https://github.com/microsoft/typescript/releases?utm_source=chatgpt.com "Releases · microsoft/TypeScript"
[7]: https://kind.sigs.k8s.io/docs/user/quick-start/?utm_source=chatgpt.com "Quick Start - kind - Kubernetes"
[8]: https://minikube.sigs.k8s.io/docs/commands/image/?utm_source=chatgpt.com "minikube image - Kubernetes"
[9]: https://kubernetes.io/docs/reference/kubectl/generated/kubectl_logs/?utm_source=chatgpt.com "kubectl logs"
