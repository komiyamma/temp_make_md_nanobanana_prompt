# 第11章：ConfigMapで設定を外出しする🧩

この章は「**コードを書き換えずに設定だけ差し替える**」を、Kubernetes流でサクッと体験する回です 😄✨
（環境ごとの差分に強くなる＝運用っぽさが一気に出ます💪）

---

## この章のゴール🎯

* ConfigMapが「何者」か、ざっくり言える 🗣️
* Node/TSアプリに **ConfigMap（環境変数 or ファイル）** を注入できる 🔌
* **更新したときの挙動**（勝手に変わる / 変わらない）を体験できる 🔁
* “設計超入門”として、**どれをConfigMapにして、どれは別にするか**が判断できる 🧠

---

## 1) ConfigMapってなに？📦（一言で）

![ConfigMap Concept](./picture/docker_multi_orch_ts_study_011_01_configmap_concept.png)

ConfigMapは、**「秘密じゃない設定」をキーと値で持つ入れ物**です 🧺
Podはそれを **環境変数**・**コマンド引数**・**設定ファイル（Volume）** として使えます。([Kubernetes][1])

⚠️ 逆に、**秘密情報（パスワード等）**には向きません。秘密はSecretへ、が鉄則です 🔐([Kubernetes][1])

さらに現実的な制約👇

* ConfigMapは巨大データ置き場じゃない（**上限 1MiB**）📏([Kubernetes][1])
* 文字列は `data`、バイナリは `binaryData` に入れられるよ 🧾🧱([Kubernetes][1])

---

## 2) 「設定を外出し」すると何が嬉しい？🌱

![Externalizing Configuration](./picture/docker_multi_orch_ts_study_011_02_external_config.png)

たとえばこんな設定、コードにベタ書きしてると詰みやすいです 😇💥

* ログレベル（devはdebug、prodはinfo）🪵
* 機能フラグ（新機能ON/OFF）🚩
* APIの挨拶文 / 表示名 / タイムアウト ⏱️
* 外部サービスのURL（ただし秘密は入れない！）🌐

ConfigMapにすると、

* **イメージは同じ**のまま、環境差だけ変えられる 🧊➡️🔥
* 設定変更で、**再ビルド不要**になってスピードUP ⚡
* 「設定ミスった」時も、差し戻しがラク 😌🔙

---

## 3) ハンズオン🧪：Node/TS APIにConfigMapを刺す🔌

![Injection Methods](./picture/docker_multi_orch_ts_study_011_03_injection_methods.png)

ここでは、次の2つを同時にやります👇

* **環境変数で刺す**（シンプルでよく使う）🌟
* **ファイルで刺す**（設定ファイル派に強い）📄

> 重要：ConfigMapは “Linuxの `/etc` 的なもの” と思うとイメージしやすいです 🐧📁([Kubernetes][2])

---

## 3-1) Node/TS側：設定を読むコード（最小）🍔

ポイントは「**envがあればenv優先**、なければ **ファイル**、それもなければ **デフォルト**」です ✅

```ts
// src/config.ts
import fs from "node:fs";

type AppConfig = {
  greeting: string;
  logLevel: "debug" | "info" | "warn" | "error";
  featureNewEndpoint: boolean;
};

function readJson(path: string): Partial<AppConfig> {
  try {
    return JSON.parse(fs.readFileSync(path, "utf8"));
  } catch {
    return {};
  }
}

export function loadConfig(): AppConfig {
  const fileCfg = readJson("/app/config/app-config.json");

  const greeting = process.env.GREETING ?? fileCfg.greeting ?? "Hello 👋";
  const logLevel = (process.env.LOG_LEVEL ?? fileCfg.logLevel ?? "info") as AppConfig["logLevel"];
  const featureNewEndpoint =
    (process.env.FEATURE_NEW_ENDPOINT ?? String(fileCfg.featureNewEndpoint ?? false)) === "true";

  return { greeting, logLevel, featureNewEndpoint };
}
```

で、エンドポイントは「毎回読む」方式（学習用に分かりやすい）👇
※本番はキャッシュ＋リロードとかにするけど、まずはこれでOKです 😄

```ts
// src/app.ts (例)
import express from "express";
import { loadConfig } from "./config";

const app = express();

app.get("/hello", (_req, res) => {
  const cfg = loadConfig();
  res.json({
    greeting: cfg.greeting,
    logLevel: cfg.logLevel,
    featureNewEndpoint: cfg.featureNewEndpoint,
  });
});

export default app;
```

---

## 3-2) ConfigMapを作る（env用・ファイル用を分ける）✂️📦

**なぜ分けるの？🤔**
ConfigMapのキーは `- _ .` など色々OKですが([Kubernetes][1])、環境変数名には向かない文字もあるので（例：`app-config.json`）
**env用はenv用、ファイル用はファイル用**にしておくと事故りにくいです 🧯

## (A) env用 ConfigMap（文字列のキー/値）🌿

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: demo-api-env
data:
  GREETING: "こんにちは from ConfigMap 👋"
  LOG_LEVEL: "debug"
  FEATURE_NEW_ENDPOINT: "true"
```

## (B) ファイル用 ConfigMap（設定ファイルを1枚入れる）📄

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: demo-api-file
data:
  app-config.json: |
    {
      "greeting": "こんにちは from JSON 📄✨",
      "logLevel": "info",
      "featureNewEndpoint": false
    }
```

---

## 3-3) Deploymentに注入する（envFrom + volume）🚀

* envは `envFrom` でまとめて注入（楽ちん）🧺
* ファイルは volumeで `/app/config` にマウント 📁

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-api
spec:
  replicas: 1
  selector:
    matchLabels:
      app: demo-api
  template:
    metadata:
      labels:
        app: demo-api
    spec:
      containers:
        - name: api
          image: your-registry/demo-api:1.0.0
          ports:
            - containerPort: 3000

          # ✅ env注入（まとめて）
          envFrom:
            - configMapRef:
                name: demo-api-env

          # ✅ ファイル注入（/app/config/app-config.json）
          volumeMounts:
            - name: app-config
              mountPath: /app/config
              readOnly: true

      volumes:
        - name: app-config
          configMap:
            name: demo-api-file
            items:
              - key: app-config.json
                path: app-config.json
```

適用はまとめて👇（ファイル分割してOK）

```bash
kubectl apply -f demo-api-env.yaml
kubectl apply -f demo-api-file.yaml
kubectl apply -f demo-api-deploy.yaml
```

---

## 3-4) 動作確認👀（ポートフォワードでOK）

```bash
kubectl port-forward deploy/demo-api 8080:3000
```

PowerShellなら👇（どっちでもOK）

```powershell
Invoke-RestMethod http://localhost:8080/hello
```

結果の `greeting` や `featureNewEndpoint` が ConfigMap由来になってたら勝ちです 🎉✨

---

## 4) ここが超大事🔥：ConfigMap更新は「どこまで自動」？🔁

結論👇（ここテストでめっちゃ出るやつです📝）

## 4-1) env（環境変数）で読んでる場合🌿

![Env Update Trap](./picture/docker_multi_orch_ts_study_011_04_env_update_trap.png)

**ConfigMapを更新しても、環境変数は自動で更新されません。Pod再起動が必要です。**([Kubernetes][1])

つまり👇

* ✅ ConfigMapを更新
* ❌ でもコンテナ内の `process.env` は変わらない
* ✅ 反映させるには **ロールアウト再起動**（またはPod再作成）

```bash
kubectl rollout restart deploy/demo-api
```

---

## 4-2) ファイル（Volumeマウント）で読んでる場合📄

![Volume Update Lag](./picture/docker_multi_orch_ts_study_011_05_volume_update_lag.png)

ConfigMapをVolumeで使ってると、**反映は「いずれ」されます**（即時じゃない）⏳
kubeletが周期的に同期して、遅延は最大で「同期周期＋キャッシュ遅延」みたいな世界です。([Kubernetes][1])

さらに、**すぐ反映させたい時**は、Podのアノテーション更新で即時リフレッシュを促せます。([Kubernetes][2])

（例：PowerShellで“今だ！”って印を付ける）👇

```powershell
$pod = (kubectl get pod -l app=demo-api -o jsonpath="{.items[0].metadata.name}")
kubectl annotate pod $pod config-refresh=(Get-Date -Format o) --overwrite
```

---

## 4-3) 罠⚠️：subPathを使うと更新されない😇💥

![SubPath Trap](./picture/docker_multi_orch_ts_study_011_06_subpath_trap.png)

ConfigMapを **subPath** でマウントしてると、**更新が届きません**。([Kubernetes][1])
「設定を差し替えたい！」目的なら subPath は避けるのが無難です 🙅‍♂️

---

## 5) “設計超入門”ポイント🧠：何をConfigMapに入れる？

## 入れてOK（だいたい安全）✅

* ログレベル、フラグ、表示文言、URL（公開して問題ないもの）🪵🚩🗣️🌐
* “環境差があるけど秘密じゃない”設定 🌱

## 入れない（Secretや別の仕組みへ）❌🔐

* パスワード、APIキー、トークン
  ConfigMapは秘密を守る仕組みじゃないです。([Kubernetes][1])

## “大きい設定ファイル”も注意⚠️

ConfigMapは **1MiB制限**があるので([Kubernetes][1])、巨大JSONをドカンはやめようね…！📦💦

---

## 6) 便利機能：immutable ConfigMap（固める）🧊

![Immutable ConfigMap](./picture/docker_multi_orch_ts_study_011_07_immutable_config.png)

ConfigMapには `immutable` を付けて「**作ったら変更禁止**」にできます（v1.19〜）🧊🔒([Kubernetes][1])

用途はこんな感じ👇

* 「勝手に設定が変わって事故る」を防ぐ 🧯
* 更新を“差し替え方式（新しいConfigMap名に切替）”に寄せられる 🔁

イメージ：

* `demo-api-env-v1` を作る
* `Deployment` がそれを参照
* 変更したい時は `demo-api-env-v2` を作って参照を切替
  → “変更履歴”が残って強い 💪📜

---

## 7) トラブルシュート道場🥋🧯（困ったらここ）

## (A) Podが起動しない / 変なエラーになる😵

まずはこれ👇（最強セット）

```bash
kubectl get pod -l app=demo-api
kubectl describe pod -l app=demo-api
kubectl logs -l app=demo-api --tail=200
```

「ConfigMapが存在しない」「キーがない」系は `describe` の Events に出がちです 🔎

※ConfigMap参照は `optional` にできて、存在しない場合に空扱いにする等も可能です。([Kubernetes][2])

---

## (B) 変更したのに反映されない😇

* envで読んでる → **再起動必要**（rollout restart）([Kubernetes][1])
* volumeで読んでる → **少し待つ** or **Podアノテーション更新**([Kubernetes][2])
* subPath使ってる → **更新来ない**([Kubernetes][1])

---

## (C) ConfigMapの作り方が分からない📦

`kubectl create configmap` で **ファイル/ディレクトリ/リテラル**から作れます。([Kubernetes][3])
ただし学習と運用の両面で、最終的には **YAMLで管理（apply）** が扱いやすいです 🧠📄

---

## 8) AIで楽するコツ🤖✨（Copilot/Codex向け）

使えるプロンプト例👇（貼ってOK）

* 「このDeploymentにConfigMapをenvFromで注入して、キー不足時はoptionalにして」🧩✅
* 「ConfigMapをファイルとして `/app/config/app-config.json` にマウントするYAMLを作って」📄📁
* 「ConfigMap更新がenvに反映されない理由を、超初心者向けに3行で」🧠📝
* 「subPathを使うと更新されないケースがある？対策もセットで教えて」⚠️🛡️

---

## 9) 小テスト📝（サクッと確認）

1. ConfigMapは何を入れる箱？🔐はOK？
2. envで注入した値は、ConfigMap更新で自動更新される？
3. Volumeマウントは更新される？どれくらい遅れることがある？
4. subPathを使うと何が起きる？

---

## まとめ🎉

* ConfigMapは **秘密じゃない設定**を外出しする箱 📦([Kubernetes][1])
* env注入は **更新されない** → 反映は再起動 🔁([Kubernetes][1])
* volume注入は **いずれ更新される**（遅延あり）⏳([Kubernetes][1])
* subPathは **更新が届かない罠** ⚠️([Kubernetes][1])
* 迷ったら「秘密はSecret」「ConfigはConfigMap」で分離！🔐✅([Kubernetes][1])

---

次の章（Secret）に行く前に、もしよければ👇
「この章のハンズオン用に、今使ってるデモAPIのDeployment/ServiceのYAML（貼れる範囲でOK）」を出してくれたら、**そのまま“あなたの構成に合わせて”ConfigMap注入パッチ**を作りますよ 💪😄

[1]: https://kubernetes.io/docs/concepts/configuration/configmap/ "ConfigMaps | Kubernetes"
[2]: https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod-configmap/ "Configure a Pod to Use a ConfigMap | Kubernetes"
[3]: https://kubernetes.io/docs/reference/kubectl/generated/kubectl_create/kubectl_create_configmap/ "kubectl create configmap | Kubernetes"
