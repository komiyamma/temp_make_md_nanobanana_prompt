# 第06章：イメージを“クラスタに届ける”（レジストリ基礎）📦🚚

この章は一言でいうと…
**「Kubernetesは“どのノードで動くか分からない”👉だからイメージは“どのノードでも取れる状態”にしておく」**を体に染み込ませる回です😎✨

（ちなみに本日時点のKubernetes最新は **v1.35.1（2026-02-10）** です。）([Kubernetes][1])
ローカル学習でよく使う **kind v0.31.0** はデフォルトKubernetesが **1.35.0** になっています。([GitHub][2])
**minikube v1.38.0（2026-01-28）** も現役です。([minikube][3])

---

## この章でできるようになること ✅🎯

* 「なんでレジストリが要るの？」を説明できる🤔➡️😌
* **タグ設計**（`latest`依存を減らす）を自分のルールで決められる🏷️✨
* 3つの“届け方”を使い分けできる🚚

  1. **レジストリへpush**（本番もこれ）🌍
  2. **kindへload**（最速ローカル学習）⚡
  3. **minikubeへload / docker-env**（ローカル学習）🧪

---

## 1) そもそも：なぜ「クラスタに届ける」必要があるの？🧠🗺️

![why_registry_needed](./picture/docker_multi_orch_ts_study_006_why_registry_needed.png)

Kubernetesは、Podを起動するときに
**「じゃあこのPod、どのノードで動かす？」**を毎回判断します🎲

* あるPodは **Node A** に置かれるかも
* 次の再起動では **Node B** に置かれるかも
* スケールしたら **Node C** にも増えるかも

つまり **各ノードが自分でイメージをpullできないと詰む**わけです😇💥
（Docker/Composeの「同じマシン内で完結」と発想が違うところ！）

---

## 2) レジストリ超入門：レジストリは“配達センター”📦🏬

![registry_delivery_center](./picture/docker_multi_orch_ts_study_006_registry_delivery_center.png)

レジストリはざっくり言うと：

* 🏭 **イメージ置き場**（みんなが取りに来る倉庫）
* 🚚 **配達ルート**（各ノードがpullして持ってくる）

代表例（覚え方だけでOK🙆‍♂️）

* Docker Hub
* GitHub Container Registry（GHCR）
* 各クラウドのレジストリ（ECR/GAR/ACRなど）

この章ではまず「**push/pullの流れ**」を理解して、次章以降で「認証（Secret）」に進むのが気持ちいいです🔐✨

---

## 3) タグ設計：`latest`に頼りすぎない🏷️⚠️

## ✅ まず覚える“事故パターン”

![latest_tag_trap](./picture/docker_multi_orch_ts_study_006_latest_tag_trap.png)

* `latest` を使う
* いつの間にか中身が変わる
* でもPod側は「同じ名前だし…」で**古いのを掴む/違うノードで違う中身**になる
* 地獄👹

しかもKubernetesは、タグが `:latest`（またはタグ省略）のとき **`imagePullPolicy: Always` が適用されます**（=毎回レジストリへ確認に行く）([Kubernetes][4])
ローカル学習で `latest` を雑に使うと「pullしに行って失敗」しがちです😇

## ✅ おすすめのタグ方針（学習用でも強い）

![tagging_strategies](./picture/docker_multi_orch_ts_study_006_tagging_strategies.png)

* まずは **SemVer**：`0.1.0`, `0.1.1` みたいに積む📈
* もしくは **Gitの短いSHA**：`sha-1a2b3c4` みたいに一意にする🧬

例：

* `ghcr.io/<user>/todo-api:0.1.0`
* `ghcr.io/<user>/todo-api:sha-1a2b3c4`

さらに強くしたい人は、**digest固定**（`@sha256:...`）が最強です🔒（“同名で中身が変わる”を物理的に防げる）

---

## 4) ハンズオン：Node/TS APIを「配達可能なイメージ」にする🍔📦

ここでは「**distを作って、実行だけを載せる**」のがシンプルで強いです💪✨
（Nodeは **v24がActive LTS** になっています。）([nodejs.org][5])

## 4-1) Dockerfile（例：超ベーシックな2段ビルド）🧱

```dockerfile
## build stage
FROM node:24-alpine AS build
WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

## runtime stage
FROM node:24-alpine
WORKDIR /app

ENV NODE_ENV=production

COPY package*.json ./
RUN npm ci --omit=dev

COPY --from=build /app/dist ./dist

EXPOSE 3000
CMD ["node", "dist/index.js"]
```

💡ポイント

* `npm ci`：lockfile通りに固定されやすい✅
* 実行側は `--omit=dev` で軽くする🪶

## 4-2) ビルド＆ローカル起動（PowerShell想定）🛠️

```powershell
docker build -t todo-api:0.1.0 .
docker run --rm -p 3000:3000 todo-api:0.1.0
```

---

## 5) 3つの“届け方”🚚✨（本番⇄ローカルを行き来できるように）

![delivery_methods_3_ways](./picture/docker_multi_orch_ts_study_006_delivery_methods_3_ways.png)

## A) いちばん正攻法：レジストリにpushして、K8sがpullする🌍📦

**本番でもそのまま使える**のが最大のメリットです👍

ざっくり流れ：

1. `docker tag` でレジストリ名を付ける
2. `docker push`
3. Deploymentの `image:` をその名前にする

（例）

```powershell
docker tag todo-api:0.1.0 ghcr.io/<user>/todo-api:0.1.0
docker push ghcr.io/<user>/todo-api:0.1.0
```

Deployment側：

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
        - name: todo-api
          image: ghcr.io/<user>/todo-api:0.1.0
          ports:
            - containerPort: 3000
```

---

## B) ローカル最速：kind に “load” する⚡📥

kindは **ローカルのDockerイメージをクラスタノードへ直接ロード**できます。([kind.sigs.k8s.io][6])

```powershell
kind load docker-image todo-api:0.1.0
```

✅いいところ

* レジストリ不要で爆速💨
* 「今作ったイメージをすぐ試す」に強い💪

⚠️注意

* これは**ローカル学習の近道**。本番の流れ（push/pull）も別で必ずやると強いです😎

---

## C) minikube：image load / docker-env を使う🧪📦

## C-1) `minikube image load`（素直で分かりやすい）

minikubeには **イメージをクラスタへロードするコマンド**が用意されています。([minikube][7])

```powershell
minikube image load todo-api:0.1.0
```

## C-2) もう一つ：`docker-env`（“minikube内のDocker”でビルドする）

minikubeは、ターミナルのDocker先を「minikube内」に切り替える方法も公式で案内しています（PowerShell例あり）。([minikube][8])

```powershell
& minikube -p minikube docker-env --shell powershell | Invoke-Expression
docker build -t todo-api:0.1.0 .
```

この方法だと「作った瞬間にクラスタから見える」状態になりやすいです⚡
ただし、**`imagePullPolicy: Always` のままだとネットへpullしに行って失敗**しがちなので、公式も注意しています。([minikube][8])

---

## 6) よくある詰まりポイント集😵‍💫➡️😄（ここだけ見ればだいたい勝てる）

## 😭「ちゃんとビルドしたのにK8sが古いの使ってる気がする」

* タグが同じ（例：`0.1.0`のまま）で中身だけ変えた
  👉 **タグを上げる**（`0.1.1`）か、digest固定を検討🔒

## 😭「ローカルで作ったのにpull失敗する」

![image_pull_policy_logic](./picture/docker_multi_orch_ts_study_006_image_pull_policy_logic.png)

* `imagePullPolicy: Always` になってる可能性高い
  👉 ローカル検証では `IfNotPresent` / `Never` を意識する（特にminikube docker-env）([Kubernetes][4])

## 😭「ARM/AMDで動かない…」

* 開発PCと実行環境のCPUアーキが違うと起きます🌀
  👉 **buildxで`--platform`** を付けてマルチプラットフォーム化するとラクです。([Docker Documentation][9])
  （学習では後回しでOKだけど、将来いきなり効いてきます💥）

---

## 7) AIで楽するポイント🤖✨（この章と相性いいやつ）

* Dockerfileを貼って：
  「**このDockerfile、軽量化できる？セキュリティ的に直す点ある？**」🔍🧠
* 失敗ログ（`kubectl describe` / `kubectl events` / `pod logs`）を貼って：
  「**原因候補を3つ、優先順で。確認コマンドも一緒に**」🧯📋
* タグ設計について：
  「**個人開発で破綻しないタグ運用を提案して。SemVer派/sha派の両方**」🏷️✨

---

## 8) ミニ課題（15〜30分）🧪⏱️

1. `todo-api:0.1.0` をビルドしてローカル起動✅
2. kind を使ってるなら `kind load docker-image` で動かす✅([kind.sigs.k8s.io][6])
3. minikube を使ってるなら `minikube image load` で動かす✅([minikube][7])
4. 仕上げにタグを `0.1.1` に上げて、「更新したのが反映される」まで確認🎉

---

次の章（7章）では、この“届いたイメージ”を **Podとして動かす**ところに入ります🍔🚀
必要なら、この章のハンズオンを **kind版 / minikube版** で「完全に同じ成果」になるように手順をもう一段かみ砕いて書きますよ😄👍

[1]: https://kubernetes.io/releases/?utm_source=chatgpt.com "Releases"
[2]: https://github.com/kubernetes-sigs/kind/releases?utm_source=chatgpt.com "Releases · kubernetes-sigs/kind"
[3]: https://minikube.sigs.k8s.io/?utm_source=chatgpt.com "Welcome! | minikube"
[4]: https://kubernetes.io/ja/docs/concepts/configuration/overview/?utm_source=chatgpt.com "設定のベストプラクティス"
[5]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[6]: https://kind.sigs.k8s.io/docs/user/quick-start/?utm_source=chatgpt.com "Quick Start - kind - Kubernetes"
[7]: https://minikube.sigs.k8s.io/docs/commands/image/ "image | minikube"
[8]: https://minikube.sigs.k8s.io/docs/handbook/pushing/ "Pushing images | minikube"
[9]: https://docs.docker.com/build/building/multi-platform/?utm_source=chatgpt.com "Multi-platform builds"
