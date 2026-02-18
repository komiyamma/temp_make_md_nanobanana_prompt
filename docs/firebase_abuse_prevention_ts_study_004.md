# 第04章：reCAPTCHA Enterprise って何？いつ使う？🏢🔐

この章は「**reCAPTCHA v3で始めたけど、運用が本気になってきた**」ときに迷いがちな **Enterprise** を、ちゃんと“判断できる”ようになる回です🙂✨
（ミニアプリ題材：メモ＋画像＋AI整形📝📷🤖）

---

## 1) まず結論：Enterprise は「運用で勝つためのreCAPTCHA」🏁🧠

**reCAPTCHA Enterprise** は、ユーザー操作のリスクを **0.0〜1.0（0.1刻み）**で評価して、そのスコアが **しきい値（app risk threshold）以上**ならOK、未満ならNG…という感じで、App Checkが判定します🧿📊
そして **デフォルトのしきい値は 0.5 推奨**です。([Firebase][1])

さらに、トークンの **TTL（有効期間）**も運用に合わせて調整できます（**30分〜7日**、デフォルトは **1時間**が妥当と明記）。短くすると安全だけど、再判定が増えて遅延・クォータ・コストに効いてきます⚖️([Firebase][1])

---

## 2) v3 と Enterprise の違い（超ざっくり）🔎✨

![v3 vs Enterprise](./picture/firebase_abuse_prevention_ts_study_004_01_v3_vs_enterprise.png)

イメージで掴むと早いです👇

* **v3**：まずはこれでOKなことが多い。しきい値0.5推奨。TTLのデフォルトは **1日**。([Firebase][2])
* **Enterprise**：**より運用前提**（設定・監視・スコア段階・課金まわり）。しきい値0.5推奨。TTLのデフォルトは **1時間**。([Firebase][1])

そして大きい差がこれ👇

* **スコア段階（granularity）**
  Essentialsが4段階、Standard/Enterpriseが11段階…みたいに“細かく運用できる度”が違います📈([Google Cloud Documentation][3])
* **無料枠と課金**
  reCAPTCHAは「月10,000 assessmentsまで無料（組織単位）」があり、Enterpriseはそれを超えると **1,000 assessments あたり $1**という形が明記されています💸([Google Cloud Documentation][3])

---

## 3) 「いつEnterpriseにする？」判断基準🧭🧿

![Decision Compass](./picture/firebase_abuse_prevention_ts_study_004_02_decision_compass.png)

### ✅ Enterpriseが“向いてる”サイン

* Bot対策を「**ちゃんと運用**」したい（監視→調整→再監視）👀🔁
* しきい値を **0.1刻みでチューニング**したい（人間を弾きすぎた/緩すぎたの微調整）🎛️([Firebase][1])
* コスト事故が怖い機能がある（とくに **AI** やアップロード系）😱💸

  * 例：AI整形ボタンは、App Checkで守るのが強く推奨されています。([Firebase][4])
* （ちょい上級）「**使い回し対策**」など強化の流れも見据えたい♻️🚫

  * 例：AI系の本番チェックリストでは replay protection に備えた設定も推奨されています。([Firebase][4])

### ❌ v3のままで様子見でいいサイン

* まだβ〜小規模で、まずは **体験と速度**が大事🏃‍♂️💨
* しきい値はデフォルト0.5で十分そう🙂
* 余計なコストの芽を増やしたくない🌱

---

## 4) 超重要：Billingをつける前の「しきい値の制限」🧯

![Billing Unlock](./picture/firebase_abuse_prevention_ts_study_004_03_billing_gate.png)

Enterpriseは、**請求アカウントを紐付ける前**だと、使えるスコア段階が限定されます（例：0.1/0.3/0.7/0.9 など）＆App Check側で設定できるしきい値も制限されます。([Firebase][1])

さらに、Billing追加後には **自動のセキュリティレビューが走る**とも書かれています。([Firebase][1])
なので「最初からEnterpriseでガチ運用するつもり」なら、この仕様は早めに知っておくと安心です🙂👍

---

## 読む📖（この章で押さえるポイント）

1. Enterpriseは **スコア（0.0〜1.0）としきい値（推奨0.5）**で判定する🧿([Firebase][1])
2. **TTLは30分〜7日**。短いほど安全だけど、遅延・クォータ・コストに効く⚖️([Firebase][1])
3. 無料枠10,000 assessments/月（組織単位）＋超過課金の形を把握する💸([Google Cloud Documentation][3])

---

## 手を動かす🛠️（Enterprise導入の最短ルート）

## A. Console側（設定）🧰

![Console Setup Steps](./picture/firebase_abuse_prevention_ts_study_004_04_setup_checklist.png)

1. reCAPTCHA Enterprise API を有効化（促されたらON）✅([Firebase][1])
2. **Website-type key** を作成し、ドメインを登録🌐
3. **「Use checkbox challenge」を選ばない**（ここハマりがち！）🚫☑️([Firebase][1])
4. Firebase Console の App Check で、対象Webアプリに **site key** を登録🧿([Firebase][1])
5. （任意）TTLを確認：最初はデフォルト1時間でOK、短くしすぎ注意⏳([Firebase][1])
6. （任意）しきい値：まずは **0.5**で開始🎛️([Firebase][1])

## B. アプリ側（コード）⚛️

![Code Structure](./picture/firebase_abuse_prevention_ts_study_004_05_code_structure.png)

`services/firebase.ts` みたいな“1箇所”に寄せるのがコツです📦✨

```ts
// services/firebase.ts
import { initializeApp } from "firebase/app";
import {
  initializeAppCheck,
  ReCaptchaEnterpriseProvider,
} from "firebase/app-check";

const firebaseConfig = {
  // いつものやつ（省略）
};

export const app = initializeApp(firebaseConfig);

// ✅ App Check は「Firestore/Storage/AI Logic を触る前」に初期化！
export const appCheck = initializeAppCheck(app, {
  provider: new ReCaptchaEnterpriseProvider(import.meta.env.VITE_RECAPTCHA_SITE_KEY),
  isTokenAutoRefreshEnabled: true, // ← これONにしないと更新されないので要注意
});
```

ポイント👇

* **site key は公開キー**（フロントに置く前提のやつ）です🔑
* `isTokenAutoRefreshEnabled: true` は、公式のv3手順でも「自動更新は明示的にON」って強調されています🧠([Firebase][2])
* 先にメトリクス監視→あとで強制、の順が安全です👀（いきなり強制はUX事故りがち😇）([Firebase][2])

---

## ミニ課題📝（判断基準づくり）

あなたのアプリ（メモ＋画像＋AI整形）を想定して、次を1枚メモに書いてください✍️✨

1. **Enterpriseにしたい理由**を2つ（例：AIコスト、Bot被害、運用でしきい値調整したい…）
2. **しきい値0.5から動かす条件**を1つ（例：正規ユーザーが弾かれたら下げる…等）
3. **TTLを短くする条件**を1つ（例：攻撃が来たときだけ短縮…等）([Firebase][1])

---

## チェック✅（この章を抜ける条件）

* 「Enterpriseは **運用前提**」って、自分の言葉で説明できる🙂
* TTLを短くすると **安全↑ / 遅延・クォータ・コスト↑**になり得るのが腹落ちしてる⚖️([Firebase][1])
* Billingなしだと **しきい値やスコア段階が制限される**のを理解した🧯([Firebase][1])
* AI整形ボタンは **App Checkで守るのが強く推奨**される理由がわかる🤖🧿([Firebase][4])

---

## つまずきポイント集（先回りで潰す😎🧯）

* **ドメイン登録ミス**：`localhost` や本番ドメイン入れ忘れでハマる🌐💥
* **checkbox challenge を選んでしまう**：Enterpriseキー作成時に要注意🚫☑️([Firebase][1])
* **しきい値を上げすぎる**：Botは減るけど、ユーザーも消える😇（まず0.5）([Firebase][1])
* **TTL短すぎ**：安全だけど、再判定が増えて遅延・クォータ・コストに刺さる⏳💸([Firebase][1])
* **AIは特に守る**：AIは“守り＋監視＋制限”が超大事（本番チェックリストでもApp Check推奨）🤖🧿([Firebase][4])

---

## おまけ：AIで判断と実装を速くする🚀🤖

![AI & Remote Config](./picture/firebase_abuse_prevention_ts_study_004_06_ai_integration.png)

* 「Enterpriseにするか」迷ったら、AIに **判断材料の洗い出し**をさせるのが強いです🧠✨
* さらにAI機能側は、**Remote Configで“モデル名などをアプリ更新なしで変えられる”**のが推奨されていて、運用と相性が良いです🎛️([Firebase][4])
* そしてAI Logicには **ユーザー単位のリクエスト制限（デフォルト100 RPM）**があるので、App Checkとセットで「破産しない設計」に寄せられます💸🧯([Firebase][5])

---

次の章（第5章）で、いよいよReact側に App Check を組み込む流れに入ると「守りが効いてる感」が一気に出て楽しいです😆🧿🔥

[1]: https://firebase.google.com/docs/app-check/web/recaptcha-enterprise-provider "Get started using App Check with reCAPTCHA Enterprise in web apps  |  Firebase App Check"
[2]: https://firebase.google.com/docs/app-check/web/recaptcha-provider?utm_source=chatgpt.com "Get started using App Check with reCAPTCHA v3 in web apps"
[3]: https://docs.cloud.google.com/recaptcha/docs/compare-tiers "Compare features between reCAPTCHA tiers  |  Google Cloud Documentation"
[4]: https://firebase.google.com/docs/ai-logic/production-checklist "Production checklist for using Firebase AI Logic  |  Firebase AI Logic"
[5]: https://firebase.google.com/docs/ai-logic/faq-and-troubleshooting "FAQ and troubleshooting  |  Firebase AI Logic"
