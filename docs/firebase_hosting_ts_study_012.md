# 第12章：キャッシュ基礎（速くするけど壊さない）⚡🧠

この章では、**Firebase Hosting を爆速にしつつ「更新したのに反映されない😇」事故を減らす**ための、いちばん大事な“考え方→設定→検証”をまとめます🚀

---

## 1) キャッシュって何が起きてるの？（2階建てで考える）🏢🏢

キャッシュはざっくり **2か所**にあります👇

* **ブラウザキャッシュ**（あなたのPCのChromeが持つ）🧠
* **CDNキャッシュ**（世界中の中継地点が持つ）🌍⚡
  Firebase Hosting は **グローバルCDNで静的ファイルを自動キャッシュ**し、**再デプロイするとCDN側のキャッシュはクリア**されます🧹✨ ([Firebase][1])

ただし注意！⚠️
**Functions / Cloud Run みたいな“動的”は、CDNに基本キャッシュされません**（URLの中身が人や入力で変わるから）([Firebase][1])
→ 動的をCDNにキャッシュしたいなら、後半の「おまけ」も見てね🙂

---

## 2) Cache-Control をざっくり理解しよう📦

キャッシュの挙動は、基本 **`Cache-Control` ヘッダー**で決まります📌 ([Firebase][1])

よく出るやつだけ覚えればOK！🙆‍♂️

* `public`：CDNもブラウザもキャッシュしていいよ🙆‍♀️ ([Firebase][1])
* `private`：ブラウザだけキャッシュしてね（CDNはダメ）🙅‍♀️
  ※Firebase Hosting は動的コンテンツに **デフォルト `private`** を付けがち ([Firebase][1])
* `max-age=秒`：ブラウザが「何秒まで古くてもOKか」⏱️ ([Firebase][1])
* `s-maxage=秒`：CDNなど共有キャッシュ用の寿命（`max-age`より優先）🌍⏱️ ([Firebase][1])
* `no-cache`：**保存はしてもいいけど、使う前に“更新確認(再検証)”してね**🔁
* `no-store`：**保存しないで**🗑️（超安全だけど遅くなりやすい）
* `immutable`：このファイルは変わらない前提でOK（主に“ハッシュ付き”ファイル向け）🧊

---

## 3) React + Hosting の「壊れない定番」ルール🍣✨

ここが最重要！💥
React(Viteなど)のビルドは、JS/CSSがだいたい **ファイル名にハッシュ**（例: `app.a1b2c3.js`）が付きます。
この“ハッシュ付き資産”は **1年キャッシュ**してOK🙆‍♂️（ファイル名が変わる＝別物だから）

一方で…

* `index.html`（またはSPAの入口HTML）を長期キャッシュ ❌
  → **古いHTMLが残る**
  → そのHTMLが **古いJSを参照**
  → もう存在しないJSを取りに行って **404 / 真っ白** 😇

なので、基本方針はこう👇

* **HTML（SPA入口）**：短命 or 再検証（`no-cache` など）🔁
* **ハッシュ付きのJS/CSS/画像/フォント**：長期キャッシュ（`public, max-age=31536000, immutable`）🚀
* **サービスワーカー `sw.js` があるなら**：短命（更新しやすくする）🧯

---

## 4) `firebase.json` でキャッシュを設定する🧾🛠️

Firebase Hosting は `firebase.json` の **`hosting.headers`** でレスポンスヘッダーを付けられます✍️ ([Firebase][2])
しかも **ルールは上から順に評価される**（順番が大事）📌 ([Firebase][2])
さらに重要：**ヘッダーのマッチングは rewrites より先に行われます**（SPAの /about などは “/about でマッチ” する）🧠 ([Firebase][2])

---

## 4-1) まずはコピペでOKな“鉄板セット”🥇

> 目的：SPAのどのURLでもHTMLは更新確認、資産は長期キャッシュ✅

```json
{
  "hosting": {
    "public": "dist",
    "ignore": ["firebase.json", "**/.*", "**/node_modules/**"],

    "headers": [
      {
        "source": "**",
        "headers": [
          { "key": "Cache-Control", "value": "no-cache" }
        ]
      },
      {
        "source": "**/*.@(js|css|png|jpg|jpeg|gif|svg|webp|ico|woff|woff2|ttf|otf|map)",
        "headers": [
          { "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }
        ]
      },
      {
        "source": "/sw.js",
        "headers": [
          { "key": "Cache-Control", "value": "no-cache" }
        ]
      }
    ]
  }
}
```

ポイント解説🧠✨

* `source: "**"` で **全部をいったん no-cache**（SPAの `/about` みたいなURLにも効かせたい）
* その後に、拡張子で **資産だけ長期キャッシュに上書き**（順番が命）📌 ([Firebase][2])
* `sw.js` は更新トラブルの温床になりがちなので、短命に寄せる🧯

> 💡 もし `dist` じゃなくて `build` などなら `public` だけ合わせてね！

---

## 5) 手を動かす：キャッシュを“見える化”して安全確認🔎👀

## 手順①：いまのヘッダーを確認する（変更前）🧪

1. 公開URLを Chrome で開く🌐
2. DevTools（F12）→ **Network** タブ📡
3. `index.html`（Doc）をクリック → **Headers** → `Cache-Control` を見る👀
4. JSやCSSファイルも同じく `Cache-Control` を見る👀

> ここで「今はこうなってる」をスクショ📸しておくと、あとで勝てます🏆

---

## 手順②：`firebase.json` に headers を入れる✍️

上の“鉄板セット”を入れて保存🧾

---

## 手順③：Preview Channel にデプロイして試す（安全運転）🚦

本番をいきなり触らず、プレビューで確認しよう🙂

```bash
firebase hosting:channel:deploy cache-lab
```

---

## 手順④：変更後のヘッダーを確認する✅

* `index.html` / SPAのURL（例 `/about`）
  → `Cache-Control: no-cache` になってる？🔁
* JS/CSS/画像
  → `public, max-age=31536000, immutable` になってる？🚀

---

## 手順⑤：更新がちゃんと反映されるかテストする🔁✨

1. CSSの色をちょっと変える🎨
2. build → デプロイ
3. **シークレットモード禁止！** 普通のタブで更新して、反映されるか確認😆

---

## 6) ミニ課題✍️🎯（10分）

次の3つを、**自分の言葉で1行ずつ**説明してね🙂

1. HTMLを長期キャッシュすると何が起きる？😇
2. ハッシュ付きJS/CSSを長期キャッシュしていい理由は？🧊
3. `no-cache` と `no-store` の違いは？🧠

---

## 7) チェック✅（できたら勝ち！）

* [ ] `/about` みたいな直叩きでも `Cache-Control: no-cache` が効いてる🔁
* [ ] JS/CSS/画像が `max-age=31536000` になってる🚀
* [ ] 再デプロイ後、通常更新で変更が反映される✨
* [ ] “真っ白”や “古いJS 404” が起きない🙂

---

## 8) よくある事故と回避術🧯

## 事故①：更新したのに反映されない（HTMLが古い）😇

→ HTMLは `no-cache`（再検証）にするのが安全🛡️

## 事故②：404 がしばらく直らない😵

Firebase Hosting は **存在しないURLの 404 をCDNが最大10分キャッシュ**することがあります🕙 ([Firebase][1])
→ 404作った/直した直後は「最大10分待つ」か「URL変えて確認」もあり

## 事故③：SPAなのに /about だけ挙動が違う🤔

ヘッダーのマッチは **rewrites より前**なので、`/index.html` だけに設定しても `/about` には当たりません⚠️ ([Firebase][2])
→ だからこの章の例は `source: "**"` を使ってるよ👍

---

## 9) AI活用コーナー🤖✨（キャッシュ事故を“AIレビュー”で減らす）

## 9-1) Gemini CLI で「firebase.json のキャッシュ設計」をレビューしてもらう🧠

Firebase は **Gemini CLI 向けの拡張**も用意しています（Firebase専用の知識を足しやすい）([Firebase][3])
たとえばこう聞く👇

* 「React(Vite)の dist 構成で、壊れない Cache-Control を firebase.json の headers で提案して。SPAのルート直叩きも考慮してね」🤖
* 「`no-cache` と `no-store` の違いを、Hosting運用の観点で説明して」🧠

## 9-2) MCP server で “Firebaseの状況込み” で相談しやすくする🧩

Firebase には **Firebase MCP server** があって、AIツールが Firebase プロジェクトやコードベースと連携しやすくなります🧩 ([Firebase][4])
→ “このプロジェクトの `firebase.json` を見た上で提案して” がやりやすくなるイメージ✨

さらに、公式の **AI prompt catalog**（定型プロンプト集）もあります📚 ([Firebase][5])
→ キャッシュ方針のチェックリスト生成とか、相性いいです✅

## 9-3) Firebase AI Logic は「リリース前チェック自動化」にも繋がる🤖✅

直接キャッシュを速くする機能ではないけど、**“リリース前チェック”をAIで型化**する流れに繋げられます🧾
なお、Firebase AI Logic のドキュメント上では **Gemini 2.0 Flash / Flash-Lite が 2026-03-31 にretire予定**という注意が出ています（モデル選びの更新が必要）([Firebase][6])

---

## おまけ：Functions / Cloud Run を Hosting から呼ぶときのキャッシュ感覚🧠⚙️

動的はデフォルトでCDNキャッシュされにくいけど、**キャッシュしたいなら `Cache-Control: public` を返す**のが基本です📌 ([Firebase][1])
また、**キャッシュは GET/HEAD だけ**とか、`Vary` や `__session` cookie の扱いなど注意点もあります🍪🧠 ([Firebase][1])
（ここは第19章の “Functions/Cloud Run” でガッツリやると気持ちいいやつ！🔥）

---

次は、あなたの今の構成に合わせて **`public`（dist/build）や assets のパス**を微調整した“あなた専用 firebase.json”にして、**Preview Channel で事故ゼロ確認**まで一気にやろう😆🚀

[1]: https://firebase.google.com/docs/hosting/manage-cache "Manage cache behavior  |  Firebase Hosting"
[2]: https://firebase.google.com/docs/hosting/full-config "Configure Hosting behavior  |  Firebase Hosting"
[3]: https://firebase.google.com/docs/ai-assistance/gcli-extension?utm_source=chatgpt.com "Firebase extension for the Gemini CLI"
[4]: https://firebase.google.com/docs/ai-assistance/mcp-server?utm_source=chatgpt.com "Firebase MCP server | Develop with AI assistance - Google"
[5]: https://firebase.google.com/docs/ai-assistance/prompt-catalog?utm_source=chatgpt.com "AI prompt catalog for Firebase | Develop with AI assistance"
[6]: https://firebase.google.com/docs/ai-logic?utm_source=chatgpt.com "Gemini API using Firebase AI Logic - Google"
