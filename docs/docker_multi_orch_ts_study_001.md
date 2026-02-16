# 第01章：Kubernetesって何を解決するの？🤔☸️

## この章でできるようになること 🎯✨

* 「Docker/Composeで十分な場面」と「Kubernetesが必要になる場面」を言い分けられる😎
* Kubernetesの“強み3点セット”を説明できる（自動回復🛟・スケール📈・宣言型📄）
* “クラスタの世界”を頭の中に地図として置ける🗺️🧠

---

## まず結論：Kubernetesは「複数マシン運用の面倒」を肩代わりする仕組み 💪😇

Docker/Composeは **基本「1台のマシン（または1台として扱える環境）」** をいい感じに動かすのが得意🐳✨
一方 Kubernetes は **「複数マシン（クラスタ）」でアプリを安全に動かし続ける** のが得意☸️🔥

2026年2月時点では、Kubernetesの最新パッチは **v1.35.1（2026-02-10）** です。([Kubernetes][1])

---

## 1) Docker/Composeで “だんだん辛くなる瞬間” 😵‍💫🧨

イメージしやすい「あるある」を先に並べるね👇

## あるある①：落ちたら人が直す（夜中に起きる）🌙📟

* アプリが落ちた
* 再起動する
* ついでにログ見る
* また落ちる
  → **人間が運用ループに組み込まれる** 😭

## あるある②：台数を増やした瞬間に “配線” が地獄 🧵🕸️

* どのマシンで動いてる？
* どのIPに向ける？（IP変わる）
* ロードバランサどうする？
* 設定配るのどうする？
  → **複数台になると、接続・配置・更新が急に難易度UP** 🚀💥

## あるある③：更新が怖い（止めたくないのに止まる）😨🔄

* 新バージョン出したい
* でも途中で落ちたら？
* どこまで反映されたか分からない
  → “安全に更新する仕組み” が欲しくなる😵

---

## 2) Kubernetesが解決する「3つの大きな問題」🛠️☸️

## ✅ (1) 自動回復（Self-Healing）🛟✨

「落ちたら起きる」を **仕組みでやる**

* Podが死んだら作り直す
* 望む数（replicas）を保つ
  → “夜中に起きる率”が減る😴💤

## ✅ (2) 安全な更新（Rolling Update & Rollback）🔄🧯

いきなり全部入れ替えずに、少しずつ更新

* 少しずつ新しいPodを増やす
* ダメなら戻す
  → “更新＝事故”になりにくい🚧➡️✅

## ✅ (3) 宣言型（Declarative）📄🧠

「こういう状態であってほしい」を書くと、Kubernetesが合わせにいく😇

* 例：「APIを3つ動かして」「この設定で」「このポートで」
  → 命令（手順）じゃなくて、**理想状態（ゴール）** を渡す感じ🎯

---

## 3) たった1つだけ覚える “Kubernetesの心臓” ❤️‍🔥

## 「現在の状態」→「望む状態」へ寄せ続ける（調整ループ）🔁⚙️

Kubernetesは、ざっくり言うとこれをずっとやってる👇

* あなた：**「こうなっててほしい」**（マニフェスト📄）
* Kubernetes：**「いまこうなってる」**（現状👀）
* Kubernetes：差分を見て、足りない分を作る／多い分を消す🧹

この発想があるから、

* 落ちても戻る🛟
* 台数増減できる📈
* 更新を段階的にできる🔄
  …が成立するよ！

---

## 4) “クラスタの世界”を3行でつかむ 🗺️👥

ここは次章で詳しくやるけど、今は雰囲気だけ👇

* **クラスタ**：複数マシン（ノード）が集まった1つの運用単位🏢
* **Pod**：動く最小単位（コンテナを包んだカプセルみたいなやつ）📦
* **コントローラ**：Podを増やしたり戻したりする担当（自動回復の主役）👮‍♂️

---

## 5) 10分ミニ体験： “Kubernetesっぽさ” を味見する 😋☸️

まだ深掘りしない。**「あ、こういう感じなんだ」** だけ掴もう🫶

## 体験A：クラスタができたら勝ち 🏁✨

ローカル学習では **kind** か **minikube** が定番。

* kind は v0.31.0 が **Kubernetes 1.35.0 をデフォルト** にしています。([GitHub][2])
* minikube は **v1.38.0（2026-01-28）** が最新リリースとして案内されています。([minikube][3])

## 体験B：「望む状態」を書いたら、勝手に合わせるのを見る 👀🔁

例として「Webを2つ動かしたい」を宣言してみる（イメージでOK）👇

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hello-web
spec:
  replicas: 2
  selector:
    matchLabels:
      app: hello-web
  template:
    metadata:
      labels:
        app: hello-web
    spec:
      containers:
        - name: web
          image: nginx:stable
          ports:
            - containerPort: 80
```

これを適用したあとに、雰囲気だけでいいので👇をやると「自動」を体感できる😆

```powershell
kubectl get pods
kubectl delete pod <どれか1つ>
kubectl get pods
```

* 1個消したのに、**また2個に戻ろうとする**（＝望む状態へ寄せる）🛟🔁
  ここで「Kubernetesの旨味」が体に入る🍜✨

> まだ `kubectl` の細かい操作は次章以降でちゃんとやるよ⌨️😊

---

## 6) 2026年の “軽い注意点メモ” ⚠️📌（今は知ってるだけでOK）

「入口（外部公開）」周りは、今ちょうど流れが変わってる🌊

* **Ingress NGINX** は **2026年3月までベストエフォート保守 → 以後リリース/修正/脆弱性対応なし** の方針が告知されています。([Kubernetes][4])
* 代替の本命として **Gateway API v1.4.0 がGA** として紹介されています。([Kubernetes][5])

この教材でも、後半は **Gateway API寄りの考え方** を前提に進めるのが安全だよ🛡️🚪

---

## 7) AIの使いどころ（第1章ver）🤖✨

ここはガチで効くやつだけ👇

* マニフェストを貼って
  「このYAMLが“望む状態”として言ってることを、日本語で3行で説明して」🗣️
* `kubectl get/describe` の出力を貼って
  「原因候補を3つ。切り分け順に並べて」🔎🧭
* ただし！
  **最終判断は “kubectl describe / logs / events” 側の事実で確定** ね🧠✅

---

## 8) 章末チェック（3分）📝✅

言えたら勝ち🎉

* Docker/Composeは何が得意？🐳
* Kubernetesは何が得意？☸️
* 「宣言型」って何？📄
* Kubernetesの心臓は何？（現在→望むへ寄せる）🔁

---

## 9) 次章予告 👀✨

次は「クラスタの登場人物（Control Plane / Node / Pod）」を、迷子にならない順番で整理するよ🗺️👥
**“どこで何が起きてるか” が分かると、Kubernetesが急に優しくなる** ☺️☸️

[1]: https://kubernetes.io/releases/?utm_source=chatgpt.com "Releases"
[2]: https://github.com/kubernetes-sigs/kind/releases?utm_source=chatgpt.com "Releases · kubernetes-sigs/kind"
[3]: https://minikube.sigs.k8s.io/?utm_source=chatgpt.com "Welcome! | minikube"
[4]: https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/?utm_source=chatgpt.com "Ingress NGINX Retirement: What You Need to Know"
[5]: https://kubernetes.io/blog/2025/11/06/gateway-api-v1-4/?utm_source=chatgpt.com "Gateway API 1.4: New Features"
