# 第30章：本番ロードマップ（マネージドK8s・アップグレード・GitOps）🗺️🏁🚀

この章は「ローカルで動いた！」から一歩進んで、**“本番で長く安全に運用するには何を決める？”**をまるっと掴む回だよ〜💪✨
ゴールはこれ👇

* 本番に行く前に、**何をマネージドに任せるべきか**判断できる🤝🏢
* **アップグレードを怖がらない設計**（順番・頻度・チェック項目）が作れる🔄🧠
* **GitOps（Gitが正）**で、デプロイと設定変更を安定させる道筋がわかる📌🌿
* 「次の1手」が決まる（AKS/EKS/GKE、GitOpsツール、環境分け、運用ルール）👣🔥

---

## 0) 2026年の前提：いま“本番設計”で気にするニュース🗞️👀

* Kubernetesの最新は **v1.35.1（2026-02-10）**。同日に1.34系もパッチ更新あり。([Kubernetes][1])
* v1.35系は **2026-12-28にmaintenance mode、EOLは2027-02-28** と明記されてる（＝サポート期限は読める）。([Kubernetes][2])
* **Ingress NGINX** は **2026年3月までベストエフォート保守 → その後はリリース/修正/脆弱性対応なし** の方針が公式に告知済み。([Kubernetes][3])
* 代替ルートの本命として **Gateway API v1.4.0 がGA**。([Kubernetes][4])
* **Helm 4** はリリース済み。さらに **Helm v3は猶予付きサポート（バグ修正〜2026-07-08、セキュリティ修正〜2026-11-11）** と期限が出てる。([Helm][5])
* GitOps側は **Argo CD v3.0系列が 2026-02-02 にEOL**（v3.1+へ移行推奨）。([GitHub][6])
* さらに GitHub上では **Argo CD v3.3.0 が “Latest”** として出ている。([GitHub][6])

ここまでで言いたいことは超シンプル👇
**「本番」は “アップグレード前提の世界” なので、寿命・乗り換え・自動化を最初から設計に入れる」**ってこと！🧠🔄✨

---

## 1) まず結論：「本番クラスタは自作しない」寄りが主流😇➡️🏢

本番で一番コワいのは、アプリが落ちることだけじゃなくて…
**クラスタ側（制御プレーン）が壊れて復旧できない**とか、**アップグレードで詰む**とか、そういう「土台崩壊」なんだよね🫠💥

だから本番はだいたいこうなる👇

* **Control Plane（API Server/etcd等）**は、マネージドに任せる🤝
* 自分たちは **ワークロード（Deployment/Service…）と運用ルール**に集中する💪
* アップグレードは「やらない」じゃなくて「**安全にやる仕組み**」を作る🔄🧯

このとき候補になりやすいのが、
Microsoft のAKS / Amazon Web Services のEKS / Google のGKE みたいな “マネージドKubernetes” だよ〜☁️☸️✨

---

## 2) 本番ロードマップの全体像（ざっくり地図）🗺️

「やること多すぎ！」って見えるけど、実は **3本柱** に分解するとスッキリ😋🧩

1. **環境を分ける**（最低でも staging / prod）🏗️🏭
2. **変更を運ぶ仕組み**（GitOpsで “Gitが正”）📌🌿
3. **アップグレードを習慣化**（順番・頻度・互換性チェック）🔄📅

---

## 3) 環境分け：最小は「staging / prod」＋「分け方のルール」🏗️🧠

まず現実的な最小形👇

* staging（検証）🧪
* prod（本番）🔥

分け方は2案あるよ👇（どっちも正解！）

## A案：クラスタを分ける（強い）🏢🏢

* 事故の巻き込みが減る🛡️
* 料金は増えがち💸

## B案：1クラスタで Namespace を分ける（軽い）📁

* 安い・早い💰⚡
* RBAC/NetworkPolicyをちゃんとしないと混ざる😵‍💫

最初は **B案→慣れたらA案** が多いよ〜👍✨

---

## 4) 入口（外部公開）戦略：Ingressは“今後の選択”が重要⚠️🚪

2026年はここが超大事👇

* **Ingress NGINXは2026年3月以降、更新が止まる方針**（=本番で“長期利用”は危険寄り）([Kubernetes][3])
* **Gateway APIはGA**で、今後の“標準の入口”として期待が高い([Kubernetes][4])

なので本番ロードマップ的にはこう考えるとラク👇

* 既にIngress運用してるなら：**代替（Gateway系 or 各社LB）へ移行計画を作る**📆🚚
* これから本番設計するなら：**Gateway API前提**で検討する🚪✨

---

## 5) アップグレード戦略：怖がるより「設計で勝つ」🔄🧠🛡️

## 5-1) “いつ出るか”を知る（頻度を見積もる）📅

Kubernetesは **年3回くらいのペース**でリリースが進むよ、って公式に説明されてるよ。([Kubernetes][7])
さらにAPIの非推奨も「約4ヶ月ごとに新リリース」前提で語られてる。([Kubernetes][8])

つまり本番は👇
**「気づいたら古い」じゃなく「定期メンテ」前提**が自然なんだ🧰✨

## 5-2) サポート期限を“数字で”読む📌

たとえば v1.35 は、**EOLが2027-02-28**って明記されてる。([Kubernetes][2])
こういうのを見ると、「いつまでに上げるべきか」が計画になるよ📆✅

## 5-3) “順番”はルールがある（バージョンスキュー）📏

Kubernetesには **Version Skew Policy** があって、
「コンポーネント間でどれくらいバージョン差が許されるか」が定義されてる。([Kubernetes][9])

ざっくり運用の鉄則は👇

* **Control Plane → Node（kubelet）→ アドオン** の順が基本
* 一気に飛ばさず、互換性を守りながら上げる

kubeadmのアップグレード手順でも「Control Planeは1台ずつ」みたいな考え方が出てくるよ。([Kubernetes][10])

マネージドでも、考え方は同じ！
たとえばEKSは「アップグレード戦略を計画して実行する」ことを“Best Practices”としてまとめてる。([AWS Documentation][11])
GKEもコントロールプレーン/ノードのアップグレード（自動/手動）を前提にドキュメントがある。([Google Cloud Documentation][12])

---

## 6) GitOps：本番の“変更作業”を安定させる魔法📌🪄

## 6-1) GitOpsって何？（超ざっくり）😋

* **Gitに書かれてる状態が正解（Source of Truth）**📌
* クラスタ側のツールが **Gitを見に行って（Pull）** 差分を同期する🔁
* 手でkubectl applyしまくるより、事故りにくい🧯✨

## 6-2) ツール候補：Argo CD と Flux 🧰

* Argo CD はGitHub上で v3.3.0 が最新として扱われている([GitHub][6])
  そして v3.0系列はEOL済み扱い（2026-02-02で終了）だから、古い系列は避けたい。([GitHub][6])
* Fluxも継続的にアップデートされていて、v2.7+のアップグレード手順やAPI移行が強調されてる（Git上のマニフェストを移行しよう、みたいな話）。([GitHub][13])

**初心者のおすすめ**はこう👇

* まずは **Argo CDで“見える化”**（UIで同期状況が分かりやすい）👀✨
* その後、好みでFluxも触る（軽量・Git中心）🪶🌿

---

## 7) ハンズオン：ミニGitOpsで「本番運用ごっこ」🎮🚀

ここから“手を動かす”用の流れ！
（クラウドに行く前に、ローカルで体験しておくと一気に理解が進むよ🔥）

## 7-1) リポジトリ構成（最小）📁

「base（共通）」＋「overlays（環境差分）」が鉄板🍱✨

```text
repo/
  apps/
    api/
      base/
        deployment.yaml
        service.yaml
      overlays/
        staging/
          kustomization.yaml
        prod/
          kustomization.yaml
  clusters/
    staging/
      argocd-app.yaml
    prod/
      argocd-app.yaml
```

ポイント👇

* **prodだけreplicas多め**とか、**prodだけリソース強め**みたいな差をoverlaysに置く🎛️
* 入口（Gateway/Ingress）や証明書は、環境ごとに変えがち🔐🌐

## 7-2) Argo CDを入れる（Helmで）⛵✨

Helm 4が出てるのは追い風（ただしHelm 3のサポート期限も意識ね）。([Helm][5])

例（イメージ）：

```bash
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update

kubectl create namespace argocd

helm install argocd argo/argo-cd -n argocd
```

> 🤖AI活用：`values.yaml` を作るときは「この値は本番で危ない？」ってレビューさせると事故が減るよ✅🧠

## 7-3) Argo CD Application（同期設定）📌

「このパスをこのnamespaceに反映してね」って宣言するやつ！

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: api-staging
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/your-org/your-repo.git
    targetRevision: main
    path: apps/api/overlays/staging
  destination:
    server: https://kubernetes.default.svc
    namespace: staging
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

ここで効くのがGitOpsの強さ👇

* 誰かが手で変えても、**selfHealで戻る**（ドリフト対策）🩹
* 不要リソースも **pruneで掃除**🧹✨

## 7-4) “イメージ更新”の流れ（本番っぽさの核心）🏭🍱

おすすめはこの型👇

1. CI（例：GitHub Actions）でイメージをビルド＆push🧱📦
2. できたタグ（例：git sha）を **GitのマニフェストにPR**で反映🔁
3. PRがマージされたら、Argo CDが検知して反映🚀

「本番はクリックで直接いじらない」方向に寄せると強いよ😎🛡️

---

## 8) 本番で“アップグレード事故”を減らすチェックリスト✅🧯

アップグレードは「作業」じゃなくて「設計」だから、最初からこの観点を持つのが勝ち🏆✨

## 8-1) 互換性チェック（APIの非推奨）📉

KubernetesはリリースごとにAPIの扱いが変わることがあるので、**Deprecation Policy**を理解しておくと安全。([Kubernetes][8])

最低限これ👇

* 「使ってるapiVersionは古くない？」
* 「次のバージョンで消えない？」
* 「CRD（追加リソース）の互換性は？」

## 8-2) アドオン棚卸し（入口・証明書・監視）🧰

* 入口（Ingress/Gateway系）
* 証明書（cert-manager系など）
* DNS（external-dns系）
* 監視（Prometheus系）

ここが古いと、Kubernetesだけ上げても詰む🙃

---

## 9) 2026年の“本番っぽい設計”ミニテンプレ🧩🏗️

最低ラインのおすすめセット👇（小さくても効果デカい💥）

* **Requests/Limits** は全ワークロードに入れる🍰
* **readinessProbe** は必須（サービスにつなげて良いかの判定）✅
* **PodDisruptionBudget**（PDB）で、メンテ時に落ちすぎ防止🛡️
* **RBAC最小権限**（サービスアカウントも分ける）👮
* **NetworkPolicy**（話していい相手だけ）🧱📡
* **stagingで必ずアップグレード検証**（prodに直行しない）🧪➡️🔥

---

## 10) ありがち落とし穴（先に踏み抜きを回避😇）🕳️

* 「とりあえずIngress NGINX」→ **2026年3月以降の更新停止が怖い**⚠️([Kubernetes][3])
* GitOps導入したのに、結局みんながkubectl applyしちゃう → **Gitが正にならない**😵‍💫
* Argo CDを古い系列で止める → **EOLに突っ込む**🧨([GitHub][6])
* アップグレードは“本番だけ”でやる → **検証不足で爆発**💥

---

## 11) 🤖 AIに頼るならこの聞き方が強い（コピペOK）✨

* 「このマニフェスト、本番運用で危ない設定を5つ指摘して。理由と直し方も」🧠✅
* 「次のKubernetesバージョンで非推奨になりそうなapiVersionが含まれてないか確認して」🔍📉
* 「Argo CDでこの構成にするとき、repo構成のおすすめを3案出して。メリデメも」📁🧩
* 「アップグレード手順を“チェックリスト”にして。作業前/作業中/作業後で」🧾🔄

---

## まとめ：この章の“持ち帰り”🎁✨

* 本番は **マネージドK8s + GitOps + 定期アップグレード設計** が超王道☁️☸️📌
* 2026年は **Ingress NGINXの引退**と**Gateway API GA**を意識して入口を決めるのが重要🚪⚠️([Kubernetes][3])
* Helmは **v4登場＆v3に期限**があるので、移行計画も持つと安全⛵📆([Helm][5])
* Argo CDは **v3.0系EOL済み**なので、使うならサポート系列で！🧯([GitHub][6])

---

もし次の一歩として、**「staging/prodをどう分けるか」**と、**「Gateway APIをどの実装（どのコントローラ）で採用するか」**まで含めた“本番ミニ設計図”を、あなたの想定アプリ（API + DBとか）に合わせて作ってあげられるよ📐✨

[1]: https://kubernetes.io/releases/?utm_source=chatgpt.com "Releases"
[2]: https://kubernetes.io/releases/patch-releases/?utm_source=chatgpt.com "Patch Releases"
[3]: https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/?utm_source=chatgpt.com "Ingress NGINX Retirement: What You Need to Know"
[4]: https://kubernetes.io/blog/2025/11/06/gateway-api-v1-4/?utm_source=chatgpt.com "Gateway API 1.4: New Features"
[5]: https://helm.sh/blog/helm-4-released?utm_source=chatgpt.com "Helm 4 Released"
[6]: https://github.com/argoproj/argo-cd/releases?utm_source=chatgpt.com "Releases · argoproj/argo-cd"
[7]: https://kubernetes.io/releases/release/?utm_source=chatgpt.com "Kubernetes Release Cycle"
[8]: https://kubernetes.io/docs/reference/using-api/deprecation-policy/?utm_source=chatgpt.com "Kubernetes Deprecation Policy"
[9]: https://kubernetes.io/releases/version-skew-policy/?utm_source=chatgpt.com "Version Skew Policy"
[10]: https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-upgrade/?utm_source=chatgpt.com "Upgrading kubeadm clusters"
[11]: https://docs.aws.amazon.com/eks/latest/best-practices/cluster-upgrades.html?utm_source=chatgpt.com "Best Practices for Cluster Upgrades - Amazon EKS"
[12]: https://docs.cloud.google.com/kubernetes-engine/docs/how-to/upgrading-a-cluster?utm_source=chatgpt.com "Manually upgrading a cluster or node pool"
[13]: https://github.com/fluxcd/flux2/releases?utm_source=chatgpt.com "Releases · fluxcd/flux2"
