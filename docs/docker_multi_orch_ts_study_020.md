# 第20章：StatefulSet入門（DB系の扱い方）🧱🗃️

まず“今どき情報”を1行で👇
**2026-02-13（日本時間）時点**で、Kubernetes の最新は **v1.35.1（2026-02-10）**です。([Kubernetes][1])（パッチは定期的に出るので、学習中も「小刻みに上げる」意識が大事👍([Kubernetes][2])）

---

## 0. 今日のゴール 🎯✨

この章を終えると、こういう感覚が身につきます👇

* 「Deploymentじゃダメで、StatefulSetが必要なケース」が言える🧠
* **“名前が固定” “DNSが固定” “ストレージが固定”** の3点セットを体で理解する💪
* 学習用ミニDB（っぽいもの）を **StatefulSet + PVC** で動かして、**再起動してもデータが残る**のを確認できる💾✅

---

## 1. StatefulSetって何者？（超ざっくり）🤔🧠

![StatefulSet Identity Components](./picture/docker_multi_orch_ts_study_020_identity_trio.png)

一言でいうと👇
**「名札付きで、引っ越しても住所と倉庫が変わらないPodたち」** を扱う仕組みです🏷️🚚

StatefulSetのPodは、次が“固定”になります：

1. **名前が固定**：`web-0`, `web-1` みたいに“番号付き”で決まる🔢
2. **ネットワークIDが固定**：PodごとのDNS名が作れる📮
3. **ストレージが固定**：PodごとにPVC（ディスク）が“紐づく”💾

この「固定3点セット」が、DB系（順序や同一性が大事）で効きます🗃️✨
Kubernetes公式も「StatefulSet Podは ordinal + stable network identity + stable storage のアイデンティティを持つ」と説明しています。([Kubernetes][3])

---

## 2. Deployment と StatefulSet の使い分け ⚖️🙂

![Stateless vs Stateful Comparison](./picture/docker_multi_orch_ts_study_020_deployment_vs_statefulset.png)

* **Deployment**：どのPodでも同じ。入れ替えてもOK。スケールも雑に増減OK🍔🍟
* **StatefulSet**：**“あのPod（0番）であること”**に意味がある。順序や名前やディスクが大事🧱🗃️

迷ったらこの質問👇

* 「Podが入れ替わっても平気？」→平気なら Deployment 寄り
* 「“この子（0番）”じゃないと困る？ それ専用ディスクが要る？」→ StatefulSet 寄り

---

## 3. StatefulSetで絶対セットになりがちなやつ 👇🧩

![Essential Components for StatefulSet](./picture/docker_multi_orch_ts_study_020_headless_and_templates.png)

## ✅ Headless Service（超重要）📡

StatefulSetは **Headless Service が必要**（PodのネットワークIDのため）って公式が明言してます。([Kubernetes][3])
Headless Service は `clusterIP: None` のやつです🫥

## ✅ volumeClaimTemplates（PodごとのPVC自動作成）💾

`volumeClaimTemplates` を書くと、PodごとにPVCが生えます🌱
このとき **消しても（StatefulSet削除/スケールダウンしても）基本、ボリュームは消えない**のが原則です（データ安全重視）。([Kubernetes][3])

---

## 4. ハンズオン：学習用ミニDB（っぽい）を StatefulSet で動かす 🧪🗃️

ここでは「DBそのもの」じゃなくて、**“データが残る＆Podの名前が固定”**が一発で分かる教材用構成にします🎓✨
（公式チュートリアルでも、作成・削除・スケール・更新の基本をこの流れで学びます👍）([Kubernetes][4])

---

## 4-1. まずストレージの前提チェック（1分）👀💾

PVCが自動で作られるには、**StorageClass** が必要なことが多いです🧱
PVCに `storageClassName` を書かなければ、**デフォルトStorageClassが使われます**。([Kubernetes][5])

コマンド（出るのが理想👇）

```bash
kubectl get sc
```

* `default` が付いたStorageClassが1つある → だいたいOK🙆‍♂️
* ない / PVCがずっとPending → 後半の「詰まりポイント」へ🚧

---

## 4-2. マニフェストを作る（Headless Service + StatefulSet）🧾✨

ファイル名例：`statefulset-mini.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: mini
  labels:
    app: mini
spec:
  clusterIP: None   # ← Headless Service
  selector:
    app: mini
  ports:
    - name: http
      port: 80
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mini
spec:
  serviceName: "mini"          # ← 上のHeadless Service名
  replicas: 3
  selector:
    matchLabels:
      app: mini
  template:
    metadata:
      labels:
        app: mini
    spec:
      terminationGracePeriodSeconds: 10
      containers:
        - name: web
          image: registry.k8s.io/nginx-slim:0.24
          ports:
            - containerPort: 80
              name: http
          volumeMounts:
            - name: data
              mountPath: /usr/share/nginx/html
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 256Mi
```

ポイント解説（ここが肝🧠✨）

* `clusterIP: None` → PodごとのDNSを作るための土台📮([Kubernetes][3])
* `volumeClaimTemplates` → PodごとにPVCが生える💾([Kubernetes][3])
* `ReadWriteOnce` は学習用の簡単ルート

  * なお公式は本番用途なら **ReadWriteOncePod 推奨**（状況次第だけど知っておくと強い）([Kubernetes][3])

適用👇

```bash
kubectl apply -f statefulset-mini.yaml
```

---

## 4-3. “固定されてる感”を観察する 👀🔍

Pod名を見る👇

```bash
kubectl get pod -l app=mini
```

たぶんこうなります👇

* `mini-0`
* `mini-1`
* `mini-2`

PVCも見る👇（Podごとに作られてるはず）

```bash
kubectl get pvc -l app=mini
```

> 「Podごとに専用ディスクが付いてる」＝StatefulSetっぽさMAX💾✨

---

## 4-4. “それぞれ別のデータが残る”を作る 🧪📝

各Podに「自分専用のHTML」を書き込みます（= ミニDBっぽい）😄

```bash
kubectl exec mini-0 -- sh -c 'echo "<h1>mini-0 data</h1>" > /usr/share/nginx/html/index.html'
kubectl exec mini-1 -- sh -c 'echo "<h1>mini-1 data</h1>" > /usr/share/nginx/html/index.html'
kubectl exec mini-2 -- sh -c 'echo "<h1>mini-2 data</h1>" > /usr/share/nginx/html/index.html'
```

表示確認は、いったん **port-forward** が簡単です🚪
（1つずつ見て「中身が違う！」を味わう🍽️）

```bash
kubectl port-forward pod/mini-0 8080:80
```

ブラウザで `http://localhost:8080` → `mini-0 data` が出ればOK🎉

同様に `mini-1` / `mini-2` も確認してみてね🙂

---

## 4-5. ここが本番：Podを消しても“同じ名前＆同じデータ”が戻る 😈➡️😇

![Persistence across Pod Recreation](./picture/docker_multi_orch_ts_study_020_sticky_identity.png)

Podを1個消します👇

```bash
kubectl delete pod mini-1
```

しばらくして👇

```bash
kubectl get pod -l app=mini
```

* `mini-1` が **また作られて戻ってくる**（番号が同じ）🏷️
* さらに `mini-1` を port-forward してみると、**前に書いたデータが残ってる**はず💾✨

これがStatefulSetの「名札＋倉庫」パワーです🧱🗃️
（そして、スケールダウンや削除でボリュームが自動削除されないのが基本、という注意点もここに繋がります⚠️）([Kubernetes][3])

---

## 5. 更新（アップデート）の考え方：StatefulSetは“慎重派”🔄🧠

![Ordered Rolling Update](./picture/docker_multi_orch_ts_study_020_rolling_update.png)

StatefulSetのRollingUpdateは、基本 **大きい番号→小さい番号**の順に、1個ずつ更新します。([Kubernetes][6])
さらに **partition** を使うと「カナリア（試し更新）」もできます🐤([Kubernetes][6])

## 5-1. “カナリア更新”のイメージ 🐤➡️🦅

例：`partition: 2` にすると

* `mini-2` だけ新しい版
* `mini-0` と `mini-1` は古い版のまま
  …みたいな段階更新ができます。([Kubernetes][6])

## 5-2. 2026の新しめトピック：maxUnavailable（beta）🆕

Kubernetes v1.35 では、StatefulSetの更新中に **同時に落ちていいPod数**を調整する `maxUnavailable` が **beta** として使えます（デフォルト1）。([Kubernetes][6])
※初心者のうちは「へーそういうのあるんだ」くらいでOK🙆‍♂️

---

## 6. “DBをStatefulSetで扱う”ときの設計メモ（超入門）🧠🗒️

![DB Cluster Architecture](./picture/docker_multi_orch_ts_study_020_db_design_memo.png)

DB系で大事になりがちな観点を、やさしくまとめます👇

* **順序が大事**：起動順・停止順が事故を左右する（StatefulSetは順序の概念を持つ）🧯
* **ストレージが主役**：Podよりディスクが偉いことが多い💾👑
* **消すのが怖い**：だからデフォで「スケールダウンしてもボリューム残す」思想🪴([Kubernetes][3])
* **ネットワークも主役**：固定DNSで“特定の子”に話しかけたい📮([Kubernetes][3])

---

## 7. よくある詰まりポイント集 🚧🧰

## 7-1. PVCがずっと Pending 😵‍💫

だいたいこれ👇

* StorageClassがない
* デフォルトStorageClassがない
* 動的プロビジョニングが効いてない

「PVCに `storageClassName` がないなら、デフォルトStorageClassが使われる」ので、まずそこを確認します👀([Kubernetes][5])

---

## 7-2. “ローカルストレージ系”の2026注意点（さらっと）⚠️🛡️

開発用のクラスタで使われがちな **Rancher Local Path Provisioner** に、**CVE-2025-62878（CVSS 10.0）**の脆弱性が出て、**v0.0.34で修正**されています。([GitHub][7])
「自分のクラスタがそれ使ってるっぽい」なら、最新版に追従してね🙏（本番は特に）

---

## 8. AI（Copilot/Codex）に頼ると爆速になるポイント 🤖⚡

そのまま投げてOKな“指示文”例👇

* 「このStatefulSetマニフェスト、初心者が踏みがちな罠を3つ指摘して。理由も」🧠
* 「DeploymentとStatefulSetの判断基準を、ToDo API + DBの例で説明して」🗂️
* 「PVCがPendingのとき、kubectlで確認する順番をチェックリスト化して」✅

---

## 9. ミニ課題（やると定着🔥）🎒

1. `replicas: 5` に増やす → `mini-3`, `mini-4` が増えるのを確認👀
2. `mini-4` にだけデータを書いて、`mini-4` を消して、戻っても残るか確認💾
3. Headless Service のDNS名を想像してみる（例：`mini-0.mini.default.svc.cluster.local`）📮([Kubernetes][3])

---

## まとめ 🧾✨

* StatefulSetは「**名前・DNS・ストレージが固定**」なPodを扱う仕組み🏷️📮💾([Kubernetes][3])
* **Headless Service + volumeClaimTemplates** がセットになりがち🧩([Kubernetes][3])
* スケールダウン/削除しても **ボリュームは基本残る**（安全優先）🪴([Kubernetes][3])
* v1.35では更新の制御（maxUnavailableなど）も進化中🆕([Kubernetes][6])

---

次の章（21章）では、外から入れる話（Ingress/Gateway）に行くので、その前に「Statefulな子は特別扱いするんだな〜」って感覚ができてれば完璧です☸️🚪✨

[1]: https://kubernetes.io/releases/?utm_source=chatgpt.com "Releases"
[2]: https://kubernetes.io/releases/patch-releases/?utm_source=chatgpt.com "Patch Releases"
[3]: https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/ "StatefulSets | Kubernetes"
[4]: https://kubernetes.io/docs/tutorials/stateful-application/basic-stateful-set/?utm_source=chatgpt.com "StatefulSet Basics"
[5]: https://kubernetes.io/docs/concepts/storage/storage-classes/ "Storage Classes | Kubernetes"
[6]: https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/?utm_source=chatgpt.com "StatefulSets"
[7]: https://github.com/advisories/GHSA-jr3w-9vfr-c746?utm_source=chatgpt.com "Local Path Provisioner vulnerable to Path Traversal via ..."
