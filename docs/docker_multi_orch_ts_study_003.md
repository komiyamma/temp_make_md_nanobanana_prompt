# 第03章：ローカルで“擬似マルチノード”クラスタを作る🏗️🖥️☸️

この章でやるのはシンプルです👇
**1台のWindows PCの中に「ノードが複数あるKubernetesクラスタ」を作って、ノード一覧を見て、Podをばら撒いて“分散してる感”を目で確認**します👀✨

ちなみに本日時点のKubernetes最新は **v1.35.1（2026-02-10）** です。([Kubernetes][1])
（ローカル学習ツール側は、内部で使うK8sバージョンが少しズレることがあるので“ズレる前提”でOK👌）

---

## ゴール🎯✅

次の3つができたら勝ちです🏆

1. **kind** または **minikube** で **ノード3台（control-plane 1 + worker 2）** のクラスタを作れる
2. `kubectl get nodes` でノードが複数見える
3. Podを増やして `kubectl get pods -o wide` を見ると **Podが複数ノードに分散**しているのが分かる

---

![Kind vs Minikube](./picture/docker_multi_orch_ts_study_003_04_kind_vs_minikube.png)

## まず選ぶ：kind と minikube どっち？🤔🧭

![Kind Architecture](./picture/docker_multi_orch_ts_study_003_01_kind_architecture.png)

## kind（おすすめ）🐳⚡

* ノードが **Dockerコンテナとして作られる**ので軽い✨ ([GitHub][2])
* “擬似マルチノード”が作りやすい
* 現行の kind v0.31.0 は **Kubernetes 1.35.0 をデフォルト**にしてます([GitHub][3])（最新版K8sに近いのが嬉しい）

## minikube（機能いろいろ）⛏️🧰

* ローカルK8sの定番。**Windowsでも winget で入れられる** ([minikube][4])
* マルチノードも公式チュートリアルあり ([minikube][5])
* ただしマルチノード時は **ボリューム周りに注意点**がある（後述）([minikube][5])

迷ったら：**とりあえず kind** → 余裕が出たら minikube も触る、が楽です😄👍

---

![Kubectl Connection](./picture/docker_multi_orch_ts_study_003_05_kubectl_connection.png)

## kubectl だけ先に入れておく🧪⌨️

Kubernetesを触る“リモコン”が `kubectl` です🎮
**kubectlはクラスタと「±1マイナーバージョン」範囲で合わせるのが安全**ってルールがあります（例：v1.35のkubectlは v1.34～v1.36 のcontrol planeと会話できる）([Kubernetes][6])

---

## ルートA：kindで擬似マルチノードを作る🐳🏗️（推し）

## A-1) kind をインストール🧩

* kindは **v0.31.0** が最新リリースとして案内されています([GitHub][3])
* Windowsではいくつか入れ方があります（wingetや手動など）

例：wingetで入る環境ならこれが楽です👇（※Windows標準のパッケージ管理）

```powershell
winget install -e --id Kubernetes.kind
```

（wingetでのkind配布自体は環境差があるので、うまくいかなければ「GitHub Releasesからkind.exeを置く」ルートに切替でOKです🔁）

インストールできたか確認👇

```powershell
kind version
kubectl version --client
```

---

![3-Node Cluster](./picture/docker_multi_orch_ts_study_003_02_3_node_cluster.png)

## A-2) 3ノード構成の設定ファイルを作る🧾✨

`kind` は設定ファイルでノード構成を書けます（公式ドキュメントに設定例あり）([kind.sigs.k8s.io][7])

VS Codeで `kind-3nodes.yaml` を作って👇

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
  - role: worker
  - role: worker
```

---

![Scale Action](./picture/docker_multi_orch_ts_study_003_06_scale_action.png)

## A-3) クラスタ作成！🚀

```powershell
kind create cluster --name k3 --config kind-3nodes.yaml
```

ノードが3つ見えたら成功🎉

```powershell
kubectl get nodes -o wide
```

ここで「おぉ…ノードが複数ある…」を味わってください😆✨

---

![Pod Dispersion](./picture/docker_multi_orch_ts_study_003_03_pod_dispersion.png)

## A-4) Podをばら撒いて“分散”を確認👀📦

まず適当なDeploymentを作って👇

```powershell
kubectl create deployment demo-web --image=nginx:stable
```

レプリカを増やして👇

```powershell
kubectl scale deployment demo-web --replicas=6
```

どのノードに載ったかを見る👇

```powershell
kubectl get pods -o wide
```

**同じノードに偏ることもある**けど、何度か増減したり作り直したりすると分散が見えます🔁🙂
（「スケジューラが空いてる場所に置く」って感覚を掴めればOK👌）

---

## A-5) お片付け🧹

```powershell
kind delete cluster --name k3
```

---

## ルートB：minikubeで擬似マルチノードを作る⛏️🏗️

## B-1) minikube をインストール📦

minikube最新は **v1.38.0（2026-01-28）** と案内されています([minikube][8])
Windowsは `winget` で入れられます([minikube][4])

```powershell
winget install Kubernetes.minikube
```

---

## B-2) Dockerドライバでマルチノード起動🐳

minikubeはDockerドライバがあります（要件の説明あり）([minikube][9])

```powershell
minikube start -p mk3 --driver=docker --nodes=3
```

確認👇

```powershell
kubectl get nodes -o wide
```

---

## B-3) 注意点⚠️（マルチノード時のVolume）

minikubeの公式チュートリアルに **「デフォルトのhost-path provisionerはマルチノードをサポートしない」** という注意が明記されています([minikube][5])
この章ではまず「ノード/Pod/分散」が目的なので、Volumeは深追いしなくてOKです🙆‍♂️
（Volumeは後の章で“ちゃんとしたやり方”をやると気持ちいいです🧠✨）

---

## B-4) お片付け🧹

```powershell
minikube delete -p mk3
```

---

![Context Switch](./picture/docker_multi_orch_ts_study_003_07_context_switch.png)

## つまづきポイント集🆘😵‍💫（最短で復帰するやつ）

## 1) `kubectl` が違うクラスタを見てるっぽい🤨

コンテキスト一覧を見る👇

```powershell
kubectl config get-contexts
```

kindなら（例）👇

```powershell
kubectl config use-context kind-k3
```

minikubeなら（例）👇

```powershell
kubectl config use-context mk3
```

---

## 2) ノードが増えない／起動が重い🐌

* ノード増やす＝PCリソースを追加で食います🍚💻
* `--nodes=3` がキツかったら、まず `--nodes=2` でもOK🙆‍♂️

---

## 3) minikubeのDockerドライバ関連で詰まる🐳🔧

Dockerドライバの要件と注意がまとまってます（WSL利用時の注意も含む）([minikube][9])
困ったらログを出して、AIに貼ると復帰が速いです🤖✨

---

## AIで楽するコツ🤖✨（この章専用）

* kindのYAMLを貼って：
  「**control-plane 1 + worker 2** になってる？余計な設定ない？初心者向けに改善して」
* `kubectl get pods -o wide` の結果を貼って：
  「どのノードに偏ってる？なぜ起きる？次に試す操作を3つ」
* エラー全文を貼って：
  「原因候補を3つ→確認コマンド→直し方 の順で出して」

“AIの回答をそのまま信じる”じゃなく、**コマンドを自分で打って確かめる**のが最強です💪😄

---

## 章末ミニ演習🎓🧪（10分）

1. 3ノードクラスタを作る（kind推奨）
2. `nginx` を `replicas=9` にする
3. `kubectl get pods -o wide` を眺めて、**Podが複数ノードに散ってる**のをスクショ📸
4. 最後に削除🧹（kind delete / minikube delete）

---

次の章（第4章）では、このクラスタに対して **kubectlの基本コマンド10連発**をやって、「困ったらコレ！」の型を作っていきます⌨️🧰✨

[1]: https://kubernetes.io/releases/?utm_source=chatgpt.com "Releases - Kubernetes"
[2]: https://github.com/kubernetes-sigs/kind/blob/main/README.md?utm_source=chatgpt.com "README.md - kubernetes-sigs/kind"
[3]: https://github.com/kubernetes-sigs/kind/releases?utm_source=chatgpt.com "Releases · kubernetes-sigs/kind"
[4]: https://minikube.sigs.k8s.io/docs/start/?utm_source=chatgpt.com "minikube start - Kubernetes"
[5]: https://minikube.sigs.k8s.io/docs/tutorials/multi_node/?utm_source=chatgpt.com "Using Multi-Node Clusters - Minikube - Kubernetes"
[6]: https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/?utm_source=chatgpt.com "Install and Set Up kubectl on Windows"
[7]: https://kind.sigs.k8s.io/docs/user/configuration/?utm_source=chatgpt.com "kind – Configuration - Kubernetes"
[8]: https://minikube.sigs.k8s.io/?utm_source=chatgpt.com "Welcome! | minikube"
[9]: https://minikube.sigs.k8s.io/docs/drivers/docker/?utm_source=chatgpt.com "docker - Minikube - Kubernetes"
