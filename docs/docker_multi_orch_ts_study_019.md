# 第19章：永続化（PV / PVC / StorageClass）💾🪴

「Podは消える🫥」「でもデータは残したい😇」——ここを解決するのが **PV / PVC / StorageClass** です。
この章は、次の第20章（StatefulSetでDB系🗃️）に入る前の“土台づくり”だよ〜！✨

---

## この章でできるようになること ✅🎯

* PV / PVC / StorageClass の役割を、**図がなくても説明できる** 🧠✨ ([Kubernetes][1])
* **PVCを作るだけでPVが自動で生える（Dynamic Provisioning）** を体験する 🌱➡️🌳 ([Kubernetes][2])
* Podを消しても、**ファイルが残ってる！** を自分の手で確認する 🥳
* ありがちな詰まり（PVCがPending😇、Podが起動しない😇）を **describeで切り分け** できる 🔎

---

## 1) まず“超ざっくり世界観”🗺️✨（駐車場たとえ🚗）

![PV/PVC Parking Metaphor](./picture/docker_multi_orch_ts_study_019_parking_metaphor.png)

* **PV**：クラスタに存在する“駐車場（実体）”🚗🅿️
  → 管理者が作るか、仕組みで自動作成される ([Kubernetes][1])
* **PVC**：ユーザーが出す“駐車券（この条件の場所ほしい）”🎫
  → 「容量◯Gi」「アクセスモード」など条件を書く ([Kubernetes][1])
* **StorageClass**：駐車場の“作り方テンプレ（種類）”🏗️
  → どのprovisioner（作成係）で、どんなパラメータで作るか ([Kubernetes][2])

イメージはこれ👇

* Pod 📦 → （使いたい！）→ PVC 🎫 → （束縛/Bind）→ PV 🅿️ → （実体）→ ストレージ💾
* StorageClass 🏗️ → （自動作成係）→ PV 🅿️ が“勝手に生える”🌱

---

## 2) 2026ストレージ事情の“ここだけ”メモ 🧠⚠️

![Dynamic Provisioning Magic](./picture/docker_multi_orch_ts_study_019_dynamic_provisioning.png)

* **Dynamic Provisioning** は「PVCを作ったらストレージが自動で用意される」仕組み。手でPVを量産しなくてOK👌 ([Kubernetes][2])

![WaitForFirstConsumer Logic](./picture/docker_multi_orch_ts_study_019_wait_for_first_consumer.png)

* **StorageClassの`volumeBindingMode: WaitForFirstConsumer`** は超重要！
  PVの確保/バインドを“Podがどこに置かれるか”が決まるまで待てる（ゾーン/トポロジ系の事故が減る）⏳🧭 ([Kubernetes][3])
* “ローカル（ノードのディスク）”系は便利だけど、**マルチノードでは置き場所（ノード）が大事**。
  `hostPath`は特に「単一ノード向け」扱いの注意があるよ⚠️ ([Kubernetes][1])

---

## 3) ハンズオン①：PVC→Pod→書き込み→Pod削除→復活🥳💾

## 3-1. まず、クラスタにStorageClassがあるか確認👀

（最初に“ある前提”で進めないのがコツ！）

```bash
kubectl get sc
```

* `standard` とか `local-path` とかが見えたらOK🙆‍♂️
* もし **default** なStorageClassがあるなら、PVC側で `storageClassName` を省略しても自動で補われることが多いよ🧠 ([Kubernetes][4])

> ここで `sc` が0件だったら、後ろの「kind向けプランB」へGO👉

---

## 3-2. PVC（駐車券🎫）を作る

`chapter19-pvc.yaml` を作って貼り付け👇

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: chapter19-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

適用！

```bash
kubectl apply -f chapter19-pvc.yaml
kubectl get pvc
```

* `STATUS` が `Bound` になったら最高🎉
* この時点で **PVが自動作成されてる** ことが多い（Dynamic Provisioning）🌱 ([Kubernetes][2])

PVも見てみよ👇

```bash
kubectl get pv
```

---

## 3-3. PodからPVCをマウントして、ファイルを書く📝

`chapter19-pod.yaml` を作って貼り付け👇

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: chapter19-writer
spec:
  containers:
    - name: writer
      image: busybox:1.36
      command: ["sh", "-c", "echo hello-pv > /data/hello.txt && sleep 3600"]
      volumeMounts:
        - name: data
          mountPath: /data
  volumes:
    - name: data
      persistentVolumeClaim:
        claimName: chapter19-pvc
```

適用＆確認👇

```bash
kubectl apply -f chapter19-pod.yaml
kubectl get pod
kubectl exec -it chapter19-writer -- cat /data/hello.txt
```

`hello- pv` が出たら成功〜！🥳🎉

---

## 3-4. Podを消して作り直す（データ残ってる？）🫣➡️😇

![Data Persistence across Restarts](./picture/docker_multi_orch_ts_study_019_pod_restart_data.png)

まず消す👇

```bash
kubectl delete pod chapter19-writer
kubectl get pod
```

もう一回作る👇

```bash
kubectl apply -f chapter19-pod.yaml
kubectl exec -it chapter19-writer -- cat /data/hello.txt
```

**同じファイルが残ってたら勝ち🏆💾**
これが「Podは消えてもデータは残る」感覚だよ〜！ ([Kubernetes][1])

---

## 4) “アクセスモード”でハマらないための最低限🧠🧷

![Access Modes Explained](./picture/docker_multi_orch_ts_study_019_access_modes.png)

PVCでよく使うやつ👇（雰囲気だけでOK！）

* `ReadWriteOnce (RWO)`：基本これ。**1つのノードに読み書きでマウント**（クラスタによって細部が違うこともあるけど、最初はこの理解でOK） ([Kubernetes][1])
* `ReadWriteMany (RWX)`：複数ノードから同時マウントできるタイプ（NFSみたいな仕組みが必要なことが多い）
* `ReadWriteOncePod (RWOP)`：さらに厳しめ。「1 Podだけ」に近い制約で安全側に寄せるやつ🛡️ ([Kubernetes][1])

⚠️超大事：
アクセスモードは“読み取り専用を強制する”みたいな万能ロックじゃないよ。仕組み上の注意もあるので、過信しないのが吉🙏 ([Kubernetes][1])

---

## 5) トラブルシュート道場🥋（PVCがPendingのとき）

## 5-1. まずこれだけやればいい👍

```bash
kubectl describe pvc chapter19-pvc
kubectl get sc
kubectl get pv
```

## 5-2. ありがち原因トップ3 😇

![Pending PVC Diagnosis](./picture/docker_multi_orch_ts_study_019_pvc_pending_reasons.png)

1. **StorageClassが無い / defaultが無い**
   → PVCが「どこに作っていいか分からん…」で止まる🫠
2. **容量やaccessModesが合うPVが存在しない（手動PV運用のとき）**
   → 条件一致がなくてずっと待つ⏳ ([Kubernetes][1])
3. **トポロジ問題（マルチゾーンやローカルストレージ）**
   → `WaitForFirstConsumer` が効くケースが多い！🧭 ([Kubernetes][3])

---

## 6) kindでStorageClassが無い場合の“プランB”🛠️（ローカル学習用）

まずは `kubectl get sc` を必ず確認ね👀
もし0件だったら、ローカル学習では **Rancher の Local Path Provisioner** が定番ルートのひとつだよ🚀
（各ノードのローカル領域に `hostPath` / `local` のPVを“自動で”作ってくれるタイプ） ([GitHub][5])

インストール例（READMEのStable）👇

```bash
kubectl apply -f https://raw.githubusercontent.com/rancher/local-path-provisioner/v0.0.34/deploy/local-path-storage.yaml
kubectl get sc
```

入ったら、さっきのハンズオン①をそのまま再実行すればOK🙆‍♂️
（このProvisionerは“ローカルストレージを簡単に使う”ための仕組みだよ） ([GitHub][5])

---

## 7) minikubeの補足メモ（動きが分かると気持ちいい😆）

minikube は `hostPath` 系PVを扱えて、永続化されるディレクトリの例も案内されてるよ📁
また、よりマルチノード向きのアドオン（CSI hostpath driver）にも触れてる🧩 ([minikube][6])

---

## 8) AI（Copilot/Codex）に手伝わせるおすすめプロンプト🤖✨

* 「このPVCがPendingなんだけど、`kubectl describe pvc` の出力から原因候補を3つ、優先度順で出して」🔎
* 「このStorageClassの`volumeBindingMode`って何？“初心者向けのたとえ”で説明して」🧠
* 「Deploymentでレプリカ増やしたらRWOで詰まりそう？どう設計すると安全？」🧯

---

## 9) まとめ🎉

* **PV＝実体🅿️ / PVC＝要求🎫 / StorageClass＝自動生成テンプレ🏗️** ([Kubernetes][1])
* **Dynamic Provisioning** があると「PVC作るだけ」でだいぶラク😇 ([Kubernetes][2])
* マルチノードになるほど **`WaitForFirstConsumer`** が効いてくる🧭 ([Kubernetes][3])
* 次章のStatefulSetで「DBらしさ🗃️」を出すために、ここは絶対押さえる価値アリ💪

---

次（第20章）では、この永続化を“DB運用っぽく”進化させて **StatefulSet** に入るよ〜！🧱🗃️✨

[1]: https://kubernetes.io/docs/concepts/storage/persistent-volumes/ "Persistent Volumes | Kubernetes"
[2]: https://kubernetes.io/docs/concepts/storage/dynamic-provisioning/ "Dynamic Volume Provisioning | Kubernetes"
[3]: https://kubernetes.io/docs/concepts/storage/storage-classes/ "Storage Classes | Kubernetes"
[4]: https://kubernetes.io/docs/tasks/administer-cluster/change-default-storage-class/ "Change the default StorageClass | Kubernetes"
[5]: https://github.com/rancher/local-path-provisioner "GitHub - rancher/local-path-provisioner: Dynamically provisioning persistent local storage with Kubernetes"
[6]: https://minikube.sigs.k8s.io/docs/handbook/persistent_volumes/ "Persistent Volumes | minikube"
