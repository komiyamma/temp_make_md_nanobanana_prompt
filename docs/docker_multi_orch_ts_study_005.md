# 第05章：マニフェスト入門（YAMLの読み方と“宣言型”）📄✨

この章は **「Kubernetesの設計図＝マニフェスト（YAML）」を、読めて・少し書けて・安全に適用できる** ようになる回です😊
コマンド暗記よりも **“読み方の型”** を先に作るよ〜！🧠🔧

---

## この章でできるようになること ✅🎯

* YAMLを見て「何のリソースで、何がしたいか」をざっくり読める 👀✨
* `apiVersion / kind / metadata / spec` の4点セットを理解する 📦
* `kubectl apply` で作成・更新できる（＝宣言型の入口）🚪
* `kubectl diff` と `--dry-run=client` で **事故らず** 変更できる 🧯
* `kubectl explain` で「このフィールド何？」を自力で調べられる 🔎

---

## まず「宣言型」ってなに？🤔🧾

![imperative_vs_declarative](./picture/docker_multi_orch_ts_study_005_imperative_vs_declarative.png)

Kubernetesはざっくりこういう世界観です👇

* **命令型**：「今すぐこれをやって！」（手順を指示）🗣️
* **宣言型**：「こういう状態にしておいて！」（理想の状態を宣言）🧙‍♂️✨

マニフェストは後者。
つまり **“理想の完成図（desired state）” を書く** → Kubernetesが **現実を寄せてくる** って感じです💪

この「理想を宣言する」思想がKubernetesのど真ん中です。
マニフェストの必須フィールドとして `apiVersion / kind / metadata / spec` が挙げられてます。([Kubernetes][1])

---

## YAMLミニ基礎（ここでコケるの、だいたいこれ）🥲🧱

## 1) インデントが命（基本はスペース）🫠

![yaml_indentation_rule](./picture/docker_multi_orch_ts_study_005_yaml_indentation_rule.png)

* YAMLは **インデントで構造が決まる**
* 同じ階層はインデントを揃える（タブは避けるのが安全）⚠️

## 2) 配列（リスト）は `-` で始まる 📌

例：`containers` は配列なので `-` が出ます。

## 3) 文字列のクォートは「困ったら付ける」🧷

コロン `:` や `{}` や `#` が混ざると誤解されがちなので、**怪しい文字列はクォート**すると安心😌

---

## Kubernetesマニフェストの“4大パーツ”🧩

![manifest_4_parts](./picture/docker_multi_orch_ts_study_005_manifest_4_parts.png)

マニフェストを見たら、まずこれを探す！👇

1. `apiVersion`：どのAPIグループ/バージョン？🧬
2. `kind`：何の種類？（Pod / Service / Deployment…）📦
3. `metadata`：名前・ラベル・namespaceなど名札🏷️
4. `spec`：理想の状態（何をどう動かすか）🧠

この4つは公式にも「必要なフィールド」としてまとめられてます。([Kubernetes][1])

> 逆にいうと、最初は `spec` の細部がわからなくてもOK！
> 「kind と metadata.name と spec の雰囲気」が読めれば勝ちです🎉

---

## 重要：`status` は基本 “書かない” 🙅‍♂️📛

![spec_vs_status](./picture/docker_multi_orch_ts_study_005_spec_vs_status.png)

`kubectl get -o yaml` で出したYAMLには `status` が出てきたりします。
でも `status` は **クラスタ側が記録する“結果”** なので、基本は触りません✋

---

## まずは1個、手で作ってみよう（超ミニPod）🐣🚀

## 0) 作業用フォルダとファイル📁

ファイル名は例：`05-hello-pod.yaml`

## 1) マニフェストを書く ✍️

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hello-pod
  labels:
    app: hello
spec:
  containers:
    - name: hello
      image: node:24-alpine
      ports:
        - containerPort: 3000
      command: ["node"]
      args:
        - "-e"
        - "require('http').createServer((req,res)=>{res.end('hello k8s');}).listen(3000)"
```

* `kind: Pod` → Podを作るよ！📦
* `metadata.name` → 名前は `hello-pod` 🏷️
* `spec.containers[]` → コンテナの配列（ここで `-` が出る）📌
* `image: node:24-alpine` → Node 24 は Active LTS 扱い（2026-02時点）🟢([nodejs.org][2])

---

## 2) “事故らない”チェック（dry-run）🧯✅

![kubectl_dry_run_safety](./picture/docker_multi_orch_ts_study_005_kubectl_dry_run_safety.png)

いきなり適用せず、まず **クライアント側でdry-run** します。

```bash
kubectl apply --dry-run=client -f 05-hello-pod.yaml
```

`--dry-run=client` は「実際には送らず、送る予定の内容をプレビューできる」系の用途として案内されています。([Kubernetes][3])

さらに出力も見たいなら：

```bash
kubectl apply --dry-run=client -f 05-hello-pod.yaml -o yaml
```

---

## 3) 差分も見ておく（diff）🧠🔍

「いまのクラスタ」と「ファイル」の差分を見ます。

```bash
kubectl diff -f 05-hello-pod.yaml
```

`kubectl diff` は差分がある/ないで終了コードも変わります（CIで便利）🧪([Kubernetes][4])

---

## 4) いよいよ適用（apply）🚀

```bash
kubectl apply -f 05-hello-pod.yaml
```

`apply` は「存在しなければ作成、あれば更新」という流れで動きます。([Kubernetes][5])

確認！

```bash
kubectl get pod hello-pod -o wide
kubectl logs hello-pod
```

ポートフォワードしてブラウザ/HTTPで確認もできます📡

```bash
kubectl port-forward pod/hello-pod 3000:3000
```

別ターミナルで：

```bash
curl http://localhost:3000
```

---

## 5) “宣言型っぽさ” を体験しよう（更新してapply）🔁✨

![kubectl_diff_apply_loop](./picture/docker_multi_orch_ts_study_005_kubectl_diff_apply_loop.png)

`hello k8s` の文字を変えてみて👇

```yaml
- "require('http').createServer((req,res)=>{res.end('hello manifest!!');}).listen(3000)"
```

そしてもう一回：

```bash
kubectl diff -f 05-hello-pod.yaml
kubectl apply -f 05-hello-pod.yaml
kubectl logs hello-pod
```

これが **「完成図を更新 → 現実が追従」** の体験です😎

---

## 「このフィールド何…？」を解決する最強コマンド🔎💪

## `kubectl explain`

マニフェストはフィールド名が多くて迷子になります😵‍💫
そんな時に **公式の“構造説明”をその場で引ける** のがこれ！

```bash
kubectl explain pod
kubectl explain pod.spec
kubectl explain pod.spec.containers
kubectl explain pod.spec.containers.ports
```

`kubectl explain` はサーバが提供する OpenAPI 情報からフィールド構造を説明してくれます。([Kubernetes][6])

---

## よくあるミス集（最短で直す）🧯🛠️

## A) `mapping values are not allowed...`（だいたいコロン周り）😇

* 文字列に `:` が混ざってる → クォートで囲う
* インデントがズレてる → 近い行のスペースを確認

## B) `spec: containers: ...` の階層ミス（インデント）🫠

* `containers` が `spec` の下にいない
* `- name:` の位置がずれてる

## C) “配列なのに `-` がない” 🙃

* `containers` や `ports` は配列になりがち
* `-` を忘れると別構造として解釈される

---

## AIで楽するポイント（でも丸投げしない🤖🧠）

AIは **「整形」「説明」「ミス探し」** が得意です💪✨
おすすめの使い方👇

## 1) YAML読解係にする📖

「このYAMLがやってることを日本語で3行で」
「kindごとに目的を箇条書きで」📝

## 2) “よくあるミス”検知係にする🧯

* `kubectl apply` のエラー全文
* 問題のYAML

を貼って「原因候補3つ＋直し方」で出してもらう👍

## 3) でも最後に自分で確認する✅

AIはフィールド名を **それっぽく** 作ることがあるので、最後に

* `kubectl explain ...` で存在確認 🔎([Kubernetes][6])
* `kubectl apply --dry-run=client ...` で安全確認 🧯([Kubernetes][3])

この2枚ガードが超おすすめです💯

---

## ミニ課題（10〜15分）⏱️🎒

## 課題1：ラベルを増やす🏷️

`metadata.labels` に `tier: demo` を追加して、`diff → apply` してみよう！

## 課題2：ポートをわざと壊して直す😈➡️😇

`containerPort: 3000` を `containerPort: "3000"`（文字列）にしてみる
→ `dry-run` や `apply` でどう怒られるか見る
→ 元に戻す

## 課題3：`kubectl explain` で “自力で調べる”🔍

`kubectl explain pod.spec` を見て
「containers以外にどんな項目があるか」眺めてみる👀([Kubernetes][6])

---

## 片付け（消すのも大事）🧹

```bash
kubectl delete -f 05-hello-pod.yaml
```

---

## まとめ🎉

* マニフェストは **理想の状態を宣言する設計図** 🧾✨
* まずは `apiVersion / kind / metadata / spec` を読む癖！([Kubernetes][1])
* 変更は **dry-run → diff → apply** の順で安全運転🧯🚦([Kubernetes][3])
* わからないフィールドは **kubectl explain** で殴る🔎💥([Kubernetes][6])

次の章（6章）では、マルチノード前提で **「イメージをクラスタに届ける」** が主役になります📦🚚
マニフェストが読めるようになると、そこがめちゃスムーズになりますよ〜！😄

[1]: https://kubernetes.io/docs/concepts/overview/working-with-objects/?utm_source=chatgpt.com "Objects In Kubernetes"
[2]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[3]: https://kubernetes.io/docs/reference/kubectl/conventions/?utm_source=chatgpt.com "kubectl Usage Conventions"
[4]: https://kubernetes.io/docs/reference/kubectl/generated/kubectl_diff/?utm_source=chatgpt.com "kubectl diff"
[5]: https://kubernetes.io/docs/reference/kubectl/generated/kubectl_apply/?utm_source=chatgpt.com "kubectl apply"
[6]: https://kubernetes.io/docs/reference/kubectl/generated/kubectl_explain/?utm_source=chatgpt.com "kubectl explain"
