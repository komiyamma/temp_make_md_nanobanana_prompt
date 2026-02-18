# 第04章：`firebase.json` 超入門（出すもの／無視するもの）🧾

この章では、Firebase Hostingの設定ファイル `firebase.json` を「怖くない存在」にします😆
今日の主役はこの2つ👇

* `public`：**どのフォルダを“公開物”として出すか** 📦
* `ignore`：**出したくないものを“デプロイ対象から外す”** 🧹

---

## 読む 📚👀

## 1) `firebase.json` って何者？🧐

`firebase.json` は、Firebaseの各サービス設定をまとめる“プロジェクトの設定ファイル”です。Hosting を初期化すると、プロジェクト直下に `firebase.json` と `.firebaserc` が作られます。([Firebase][1])

そして Hosting ではまず、「どのファイルをデプロイする？」を `public` と `ignore` で決めます。([Firebase][2])

---

## 2) `public` は「デプロイするフォルダ」📦➡️🌐

`public` は **必須**。ここで指定したフォルダの中身が Hosting にアップされます。([Firebase][2])

例：デフォルトはこう👇（`public` フォルダを出す）

```json
{
  "hosting": {
    "public": "public"
  }
}
```

でも、React/Vite だと “ビルド成果物” が `dist` だったりしますよね？
その場合はこうします👇（例：`dist/app` を出す）([Firebase][2])

```json
{
  "hosting": {
    "public": "dist/app"
  }
}
```

📝 コツ

* **`public` は「ソースコード置き場」じゃない**です🙅‍♂️
  ここは **ビルド後に生成される成果物フォルダ** を指すのが基本です（例：`dist` / `build` / `out` など）✨

---

## 3) `ignore` は「デプロイしないもの」🧹🛑

`ignore` は **任意**。でも、ほぼ必須級に大事です😇
ここに書いたパターンに一致するファイルは、デプロイ時に無視されます。([Firebase][2])

デフォルトはだいたいこう👇（超よく見るやつ）

```json
{
  "hosting": {
    "public": "public",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ]
  }
}
```

それぞれの意味、めちゃ大事なので噛み砕きます👇 ([Firebase][2])

* `"firebase.json"`
  → うっかり公開物フォルダに入っても **設定ファイルは出さない** 🧾🚫
* `"**/.*"`
  → `.git` や `.env` みたいな **ドットから始まる隠し系** を出さない 🕵️‍♂️🚫
* `"**/node_modules/**"`
  → 依存パッケージは **巨大＆公開に不要** なので出さない 📦💥

✅ 重要ポイント
Hosting のパターンは **glob（グロブ）** で、`.gitignore` っぽい書き方です。([Firebase][2])

---

## 4) 「出すもの／無視するもの」判断の超シンプル基準 🧠✨

迷ったらこれ👇

* ✅ 出す：**ブラウザが読むもの**（`index.html` / `assets/*` / `favicon` / `manifest` など）🌐
* ❌ 出さない：**開発用・秘密・巨大**（`node_modules` / `.env` / `.git` / 元ソース / テストデータ）🔐🧨

---

## 手を動かす 🛠️🔥

## Step 1：ビルド成果物フォルダを確認する 👀📁

まず、あなたのReactアプリでビルドしたときに「どのフォルダができるか」を確認します。

例（よくある確認のしかた）👇

* `npm run build` を実行
* 生成されたフォルダを探す（`dist` / `build` など）
* その中に `index.html` があるか確認 ✅

---

## Step 2：`firebase.json` の `public` を合わせる 🔧🎯

`public` を **ビルド成果物のフォルダ名** に合わせます。

例：成果物が `dist` の場合👇

```json
{
  "hosting": {
    "public": "dist",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ]
  }
}
```

---

## Step 3：デプロイ前のセルフチェック ✅🧪

デプロイで事故りやすいのはだいたいここです😅

* `public` で指定したフォルダが **存在する** ✅
* その中に `index.html` が **いる** ✅
* `node_modules` や `.env` みたいなものが **紛れ込んでない** ✅

---

## ミニ課題 ✍️😺

1. 自分のプロジェクトで、ビルド成果物フォルダ（例：`dist` or `build`）を1行でメモ📝
2. `firebase.json` の `public` をそこに合わせる🔧
3. 「なぜ `node_modules` は無視する？」を一言で✍️

   * 例：「デカいし、公開に不要だから」📦🚫

---

## チェック ✅🎉

* `public` が「ビルド成果物フォルダ」を指している ✅
* `ignore` が「秘密・巨大・開発用」を弾いている ✅
* `firebase.json` を見ても“怖くない”気持ちになった ✅😎

---

## よくあるハマりどころ集 🧯😵‍💫

* **`public` をソース（例：`src`）にしてしまう**
  → 画面が出ない／変なものが公開される あるある🙈
* **ビルドせずにデプロイする**
  → 古い成果物が出る／空フォルダ出して詰む 😭
* **`.well-known` が必要なのに `**/.*` で弾いてしまう**
  → 例：`/.well-known/assetlinks.json` 系で困ることがあります（ドット始まり扱い）。その場合は `ignore` を見直すのが近道です🧩([GitHub][3])

---

## AIで“詰まり”を秒速で潰す 🤖🧯

## 1) Firebase MCP server を使うと「設定の確認」が速い 🧩⚡

Firebase公式の **Firebase MCP server** を使うと、Antigravity や Gemini CLI などのAIツールが、Firebaseプロジェクトを“道具として操作”しやすくなります。([Firebase][4])

たとえば Gemini CLI 側は、Firebase拡張の導入が推奨されてます。([Firebase][4])
（中では `npx -y firebase-tools@latest mcp` を使う構成が案内されています）([Firebase][4])

🗣️ AIに投げると強い質問例（そのままコピペでOK）👇

* 「このリポジトリのビルド成果物フォルダはどれ？ `firebase.json` の `public` を最適化して」
* 「`ignore` で弾くべき“危険ファイル”が混ざってないかチェックして」
* 「今の `firebase.json` の意図を初心者向けに説明して」

---

## 2) Gemini in Firebase でコンソール上の相談もできる 🧯💬

Firebase コンソールには **Gemini in Firebase**（AIアシスタント）があります。まず有効化して使えます。([Firebase][5])
「Hosting の設定、ここが不安…」みたいな相談を、コンソールから投げられるのが便利です🙌

---

## まとめ 🏁✨

* `public` は「ビルド成果物フォルダ」📦
* `ignore` は「秘密・巨大・開発用を弾く」🧹🔐
* AI（MCP / Gemini）を使うと、設定レビューと原因切り分けが一気に速くなる 🤖⚡([Firebase][4])

---

次の第5章（SPAルーティングでリロード404を直す🔁）に進む前に、もしよければ今の `firebase.json` の **hosting 部分だけ**ここに貼ってくれたら、事故りにくい形に“超初心者向けに整形”して返すよ😆🛠️

[1]: https://firebase.google.com/docs/hosting/quickstart?utm_source=chatgpt.com "Get started with Firebase Hosting"
[2]: https://firebase.google.com/docs/hosting/full-config "Configure Hosting behavior  |  Firebase Hosting"
[3]: https://github.com/firebase/firebase-tools/issues/7685?utm_source=chatgpt.com "Firebase hosting issues with assetlinks.json #7685"
[4]: https://firebase.google.com/docs/ai-assistance/mcp-server "Firebase MCP server  |  Develop with AI assistance"
[5]: https://firebase.google.com/docs/ai-assistance/gemini-in-firebase/set-up-gemini?utm_source=chatgpt.com "Set up Gemini in Firebase - Google"
