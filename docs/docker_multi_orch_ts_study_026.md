# 第26章：SecurityContext（root回避・読み取り専用）🧷🛡️

この章は「**Podの中のプロセス権限**」をちゃんと縛って、**“やられにくいコンテナ”**にする回です😎✨
（やることはシンプル！でも効果はデカい！💥）

---

## 1) まず結論：最低限の“守りセット”🧰🔒

![5 Security Context Flags](./picture/docker_multi_orch_ts_study_026_security_pillars.png)

「とりあえずこれ入れとけば事故りにくい」基本セットはコレです👇
（公式ドキュメントと、PSSの考え方に沿ったやつ）([Kubernetes][1])

* **runAsNonRoot: true**（root禁止）🧑‍🚫👑
* **allowPrivilegeEscalation: false**（権限の“昇格”禁止）🚫⬆️
  ※ただし **privileged** や **CAP_SYS_ADMIN** を付けると実質 true 扱いになるケースがあるので、そもそも付けないのが吉😇([Kubernetes][1])
* **capabilities.drop: ["ALL"]**（余計な力を全部捨てる）🗑️💪([cheatsheetseries.owasp.org][2])
* **readOnlyRootFilesystem: true**（ルートFSを読み取り専用）📚🔒([Kubernetes][1])
* **seccompProfile: RuntimeDefault**（危険なシステムコールを絞る）🧯
  ※PSSのRestricted側の“今どき”感にも合います([Kubernetes][3])

この章では特に **「root回避」＋「読み取り専用」**を、手を動かして体に入れます💪🔥

---

## 2) “rootで動く”と何がマズいの？😇➡️😈

![Root vs Non-Root Blast Radius](./picture/docker_multi_orch_ts_study_026_root_vs_nonroot.png)

コンテナって、放っておくと **root（UID 0）で動く**ことが多いです。
もしアプリが侵入されたとき、rootだと「できること」が増えすぎて、被害がデカくなりがちです💣
なので **最小権限**（Least Privilege）が基本方針になります。([Docker][4])

---

## 3) SecurityContextって何者？（超ざっくり）🧠🗺️

![Pod vs Container Context Scope](./picture/docker_multi_orch_ts_study_026_context_scope.png)

SecurityContextは **Pod / Container がOSに対してどう振る舞うか**を決める設定です。
ユーザーID、特権、ファイル権限、ケーパビリティ、読み取り専用…などを縛れます。([Kubernetes][1])

ポイントは2つ👇

* **Pod全体にかける securityContext**（例：fsGroup など）🏠
* **Containerごとにかける securityContext**（例：runAsNonRoot、readOnlyRootFilesystem）📦

この章は **コンテナ側の縛り**が主役です🎯

---

## 4) ハンズオン①：まず「rootで動いてる」を目で見る👀💥

## 4-1) まず“危険寄り”のマニフェスト（わざと）😈

（※アプリ名は何でもOK。ここでは例として api を使います）

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
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
        - name: api
          image: your-registry/your-api:latest
          ports:
            - containerPort: 3000
```

適用：

```bash
kubectl apply -f 26-unsafe.yaml
kubectl get pod -l app=api
```

## 4-2) Podの中でユーザー確認（たいてい root）👑

```bash
kubectl exec -it deploy/api -- id
```

出力に **uid=0(root)** が見えたら「はい、rootで動いてます」🙋‍♂️

---

## 5) ハンズオン②：runAsNonRoot を入れて “root禁止”🚫👑

## 5-1) まずはコンテナに「root禁止」だけ足す

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
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
        - name: api
          image: your-registry/your-api:latest
          ports:
            - containerPort: 3000
          securityContext:
            runAsNonRoot: true
```

適用：

```bash
kubectl apply -f 26-nonroot.yaml
kubectl get pod -l app=api
kubectl describe pod -l app=api
```

## 5-2) ここで“よくある失敗”😇💥

もしイメージが root 前提だと、Podが起動せずに怒られます。
「runAsNonRoot なのに root で動こうとしてるじゃん！」って止めてくれる挙動です👍([Kubernetes][3])

**対処は2択：**

* **Dockerfileで非rootユーザーに切り替える**（おすすめ）🐳✅
* **Kubernetes側で runAsUser を指定する**（“そのUIDが成立する”前提が必要）🎛️

---

## 6) ハンズオン③：Dockerfileで “最初から非root” にする🐳🧑‍🔧

Node.js の公式イメージは、非rootユーザー（例：node, UID 1000）を持ってることが多いけど、**デフォルトでそれを使うとは限りません**。なので Dockerfile で明示しちゃうのが安全です。([GitHub][5])

例（ざっくり）👇

```dockerfile
FROM node:24-bookworm-slim

WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev

COPY . .

## ここが大事：非rootで動かす
USER node

EXPOSE 3000
CMD ["node", "dist/index.js"]
```

ビルド＆プッシュ（例）：

```bash
docker build -t your-registry/your-api:nonroot .
docker push your-registry/your-api:nonroot
```

マニフェスト側も image を差し替え：

```yaml
image: your-registry/your-api:nonroot
securityContext:
  runAsNonRoot: true
```

再適用後に確認：

```bash
kubectl exec -it deploy/api -- id
```

rootじゃないUIDになってたら勝ちです🎉

---

## 7) ハンズオン④：readOnlyRootFilesystem を入れて“改ざん耐性”📚🔒

![Read-Only Root + Writable /tmp](./picture/docker_multi_orch_ts_study_026_readonly_fs.png)

次は「**コンテナのルート領域を書き換え不可**」にします。
攻撃者が侵入しても、ファイル落としたり改変したりしにくくなります🧱([Kubernetes][1])

## 7-1) そのまま入れる（まず失敗を味わう）😈➡️😵

```yaml
securityContext:
  runAsNonRoot: true
  readOnlyRootFilesystem: true
```

適用：

```bash
kubectl apply -f 26-readonly.yaml
kubectl get pod -l app=api
kubectl logs -l app=api --tail=50
```

## 7-2) ありがちなエラー原因：/tmp に書けない🫠

アプリやライブラリが **/tmp** や **キャッシュ**に書こうとして失敗します。
readOnlyにすると「ルート側の /tmp も書けない」ので当然コケます💥

## 7-3) 解決：/tmp を emptyDir で“書ける島”にする🏝️✍️

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
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
      volumes:
        - name: tmp
          emptyDir: {}
      containers:
        - name: api
          image: your-registry/your-api:nonroot
          ports:
            - containerPort: 3000
          volumeMounts:
            - name: tmp
              mountPath: /tmp
          securityContext:
            runAsNonRoot: true
            readOnlyRootFilesystem: true
```

これで「ルートは読取専用、/tmp だけ書ける」になります✌️😎

---

## 8) 仕上げ：さらに“勝ち筋”に寄せる（推奨セット）🏆🛡️

![Privilege Escalation Prevention](./picture/docker_multi_orch_ts_study_026_escalation_prevention.png)

ここまで来たら、同時に入れちゃうと強いです💪
（PSS Restricted の“考え方”に寄せる感じ）([Kubernetes][3])

```yaml
securityContext:
  runAsNonRoot: true
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop: ["ALL"]
  seccompProfile:
    type: RuntimeDefault
```

補足：allowPrivilegeEscalation は「親より強くなるの禁止」だけど、そもそも privileged や危険capを付けてたら話が崩れるので、**付けない設計**が大事です😇([Kubernetes][1])

---

## 9) “動かなくなった！”ときの切り分けテンプレ🥋🧯

![The Hardening Troubleshooting Loop](./picture/docker_multi_orch_ts_study_026_troubleshooting_loop.png)

困ったらこの順で見ればOKです（ほぼ勝てます）😎✨

1. Podのイベントを見る

   ```bash
   kubectl describe pod -l app=api
   ```

2. ログを見る

   ```bash
   kubectl logs -l app=api --tail=100
   ```

3. 典型パターン別に直す

   * **runAsNonRootで起動拒否** → Dockerfileで USER を切る / runAsUser を検討([Medium][6])
   * **Read-only file system** → 書き込み先を洗い出して emptyDir をマウント
   * **権限不足（Permission denied）** → volumeの所有/グループ（fsGroup）を検討（Pod側securityContextが効く場面）([Kubernetes][1])

---

## 10) 一歩先：Pod Security Standards / Admission とつながる話🚪🧱

今やった “縛り” は、クラスタ側で **「このnamespaceはこの厳しさでいく」**みたいに強制する流れ（Pod Security Admission）と相性がいいです。([Kubernetes][7])

つまり、チームや将来の自分が増えても
「誰かが雑に privileged で出しちゃった…😇」みたいな事故を減らせます✅

---

## 11) AIで楽するポイント🤖✨（貼るだけで強くなる）

* エラー文を貼って：
  「このエラーの原因候補を3つ。まず確認すべき kubectl コマンドも出して」🔍
* マニフェストを貼って：
  「PSS Restricted寄せにしたい。足りない securityContext を追加して」🛡️
* ログを貼って：
  「readOnlyRootFilesystem で壊れてる。どのパスに書いてそう？」🧭

※ただしAIは **権限まわりを盛りがち**なので、「capabilitiesは最小？」「privileged入ってない？」を毎回チェックすると安定です😎✅

---

## 12) チェックリスト（提出前に10秒で見るやつ）📝✅

* [ ] runAsNonRoot: true になってる？🧑‍🚫👑
* [ ] allowPrivilegeEscalation: false になってる？🚫⬆️
* [ ] capabilities.drop: ["ALL"] になってる？🗑️
* [ ] readOnlyRootFilesystem: true になってる？📚🔒
* [ ] /tmp など必要な書込先は emptyDir で確保した？🏝️✍️
* [ ] seccompProfile: RuntimeDefault 入れた？🧯

---

次の章（第27章）は「観測性の入口（イベント・ログ・メトリクス）」なので、今回の **“壊したときに何が起きるか”** をログで追えるようになると、学習の気持ちよさが一気に上がりますよ〜😆📊

[1]: https://kubernetes.io/docs/tasks/configure-pod-container/security-context/?utm_source=chatgpt.com "Configure a Security Context for a Pod or Container"
[2]: https://cheatsheetseries.owasp.org/cheatsheets/Kubernetes_Security_Cheat_Sheet.html?utm_source=chatgpt.com "Kubernetes Security - OWASP Cheat Sheet Series"
[3]: https://kubernetes.io/docs/concepts/security/pod-security-standards/?utm_source=chatgpt.com "Pod Security Standards"
[4]: https://www.docker.com/blog/understanding-the-docker-user-instruction/?utm_source=chatgpt.com "Understanding the Docker USER Instruction"
[5]: https://github.com/nodejs/docker-node/blob/master/docs/BestPractices.md?utm_source=chatgpt.com "docker-node/docs/BestPractices.md at main"
[6]: https://medium.com/%40mughal.asim/kubernetes-security-contexts-series-part-3-running-containers-as-non-root-0b7ebd54636c?utm_source=chatgpt.com "Running Containers as Non-Root"
[7]: https://kubernetes.io/docs/concepts/security/pod-security-admission/?utm_source=chatgpt.com "Pod Security Admission"
