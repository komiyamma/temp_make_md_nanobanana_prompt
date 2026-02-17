# 第26章：VS Code の Dev Containers で“開発環境ごと固定”🧰🐳

この章は、ひとことで言うと **「プロジェクト専用の開発PCを、ボタン1つで召喚する」** 回です😆✨

![Dev Container Concept](./picture/docker_runtime_fix_ts_study_026_01_concept.png)

Nodeの版・ツール・拡張機能まで、ぜんぶ「このリポジトリに紐づく」状態にできます🔒

Dev Containers は、フォルダ（=プロジェクト）を **“コンテナの中で開く”** 開発スタイルを作れます。VS Code の機能（補完・デバッグ・ターミナルなど）を、コンテナ内の環境でそのまま使えるのが強みです🧠⚡ ([Visual Studio Code][1])

---

## この章のゴール🎯✨

* ✅ 「このリポジトリはこのNodeで開発する」が **VS Codeごと固定**できる🟢
* ✅ 拡張機能（ESLint / Prettier / AI系など）も **プロジェクトに紐づけて自動セット**できる🧩
* ✅ 新しいPCでも「開くだけで同じ開発環境」になって、事故が減る🧯

---

## なんで嬉しいの？（よくある地獄が消える）💥➡️🫧

* 😵「PCに入ってるNodeが違う」→ **関係なくなる**
* 😵「拡張機能の入れ忘れでLintが動かない」→ **自動で入る**
* 😵「環境構築メモが古い」→ **設定がリポジトリに残る**
* 😵「新メンバーが初日から詰まる」→ **“開く”だけで揃う**

Dev Containers は “フォルダに devcontainer 設定があるなら、それに従ってコンテナを用意する” という考え方です📦 ([Visual Studio Code][1])

---

## Dev Containers のざっくり仕組み🍱🧠

![Host vs Container Mechanism](./picture/docker_runtime_fix_ts_study_026_02_mechanism.png)

* 🧑‍💻 VS Code はいつも通り起動
* 🐳 でも、**コードの実行・依存インストール・拡張機能の動作**はコンテナ側
* 📁 ローカルのフォルダは、コンテナにマウントされて編集できる

つまり **「エディタは普段通り」＋「中身は別PC（コンテナ）」** みたいな感覚です😄 ([Visual Studio Code][1])

---

## 最短5分：動くところまで行こう🚀（まずは“最小”でOK）

### 1) Dev Containers 拡張を入れる🧩

マーケットプレイスの **Dev Containers**（拡張）を入れます。([marketplace.visualstudio.com][2])

---

### 2) `.devcontainer/devcontainer.json` を作る📁✨

![devcontainer.json Anatomy](./picture/docker_runtime_fix_ts_study_026_03_config_anatomy.png)

プロジェクト直下に `.devcontainer` フォルダを作って、`devcontainer.json` を置きます。

```json
{
  "name": "node-ts-dev",
  "image": "node:24-bookworm-slim",
  "postCreateCommand": "npm ci"
}
```

* `"image"`：このプロジェクトの“開発PC”の土台（ここでNode版が固定される）🧱
* `"postCreateCommand"`：コンテナ初回作成後に走るコマンド（依存を揃える）📦

  * Dev Containers には、作成タイミングで動くコマンド群（`postCreateCommand` など）が用意されています🛠️ ([devcontainers.github.io][3])

> ちなみに Node のリリース状態は公式で確認できます（例：v24 Active LTS / v25 Current など）🟢 ([nodejs.org][4])
> （この章では “どう固定するか” が主役なので、まずはここだけでOK👌）

---

### 3) 「コンテナで開く」▶️🐳

![Reopen in Container](./picture/docker_runtime_fix_ts_study_026_04_reopen_action.png)

VS Code のコマンドパレット（Ctrl+Shift+P）から、だいたい次の系統を選びます：

* 🐳 **Dev Containers: Reopen in Container**（または近い名前）

すると、コンテナが作られて “その中” に入ります🏠✨ ([Visual Studio Code][1])

---

### 4) 固定できてるかチェック✅🔍

コンテナ内ターミナルで：

```bash
node -v
npm -v
```

これで **「PCに何が入ってるか」じゃなくて「devcontainerが決めた環境」** が使われてるのを確認できます😄

---

## 便利オプション：ここから“快適”にする😆🛠️

最小で動いたら、次は快適化です✨
Dev Containers の設定は公式の devcontainer.json 仕様で整理されています。([devcontainers.github.io][3])

---

### ① ポート転送を自動化📡（3000/5173/…）

フロントやAPIを起動するとき、毎回ポート設定で迷いがちなので固定します🔒

```json
{
  "name": "node-ts-dev",
  "image": "node:24-bookworm-slim",
  "forwardPorts": [3000, 5173],
  "postCreateCommand": "npm ci"
}
```

`forwardPorts` は “常に転送するポート” を指定できます📌 ([devcontainers.github.io][3])

---

### ② 拡張機能も「プロジェクトに紐づけて自動インストール」🧩✨

![Auto Extensions](./picture/docker_runtime_fix_ts_study_026_05_auto_extensions.png)

ESLint / Prettier / AI系（Copilot など）を「毎回入れる」のはダルいので、ここに置きます💪

```json
{
  "name": "node-ts-dev",
  "image": "node:24-bookworm-slim",
  "postCreateCommand": "npm ci",
  "customizations": {
    "vscode": {
      "extensions": [
        "dbaeumer.vscode-eslint",
        "esbenp.prettier-vscode",
        "github.copilot"
      ]
    }
  }
}
```

`customizations.vscode.extensions` の考え方は、コミュニティ/解説でもよく整理されています📚 ([Zenn][5])
（「拡張機能IDを並べる」だけでOK👍）

---

### ③ node_modules を“ホストに作らない”作戦💣➡️🧼

![Node Modules Mount](./picture/docker_runtime_fix_ts_study_026_06_mount_strategy.png)

Dev Containers は基本「作業フォルダをマウント」するので、何も考えず `npm i` すると **ホスト側に `node_modules` が生まれる** ことがあります😇
嫌な場合は、`node_modules` を **named volume** に逃がすのが定番です🏃‍♂️💨

```json
{
  "name": "node-ts-dev",
  "image": "node:24-bookworm-slim",
  "postCreateCommand": "npm ci",
  "mounts": [
    "source=node_modules,target=${containerWorkspaceFolder}/node_modules,type=volume"
  ]
}
```

`mounts` は Docker の `--mount` と同じ形式で書けます🧷 ([devcontainers.github.io][3])

---

## Windowsで詰まりやすいポイント（ここだけ先に潰す）🪟🧯

### ✅ Docker Desktop × WSL2 の基本だけ

Docker Desktop は WSL2 バックエンドを使うのが今の主流で、WSLのバージョンが古いと不調が出やすいです⚠️
Docker 側も「WSLは新しめ推奨」「WSL Integration の設定」などを案内しています。([Docker Documentation][6])

チェック例：

```bash
wsl.exe -l -v
```

---

## “壊れたとき”の復旧コマンド🧯🔁

* 🔁 設定変えたのに反映されない → **Rebuild**

  * **Dev Containers: Rebuild Container**（系のコマンド）
* 🧹 なんか変…全部やり直したい → **Remove / Reopen**

  * **Dev Containers: Reopen in Container** で再作成

（devcontainer の変更は「コンテナ作り直し」が必要なことが多いです💡）

---

## 章末ミニチャレンジ🎮✨（やると一気に定着）

1. ✅ `forwardPorts` を入れて、開発サーバを起動→ブラウザで確認📡
2. ✅ `customizations.vscode.extensions` に ESLint/Prettier/AI系を入れて、コンテナ内で動くのを確認🧩
3. ✅ `mounts` で `node_modules` を volume 化して、ホストに増えないか確認🧼

---

## まとめ🎁✨

Dev Containers を使うと、**Node/ツール/拡張機能まで含めた「開発環境そのもの」をリポジトリに固定**できます🧰🐳
そしてこれは「個人開発でもチームでも効く」やつです💪🔥 ([marketplace.visualstudio.com][2])

次の第27章で `.devcontainer/devcontainer.json` をもう少しちゃんと“型”にして、ワンクリック起動を完成させよう😆📦

[1]: https://code.visualstudio.com/docs/devcontainers/containers "Developing inside a Container"
[2]: https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers "
        Dev Containers - Visual Studio Marketplace
    "
[3]: https://devcontainers.github.io/implementors/json_reference/ "Dev Container metadata reference"
[4]: https://nodejs.org/en/about/previous-releases?utm_source=chatgpt.com "Node.js Releases"
[5]: https://zenn.dev/enlog/articles/efadffc0bfc86b?utm_source=chatgpt.com "devcontainer.jsonの書き方と主要なプロパティ"
[6]: https://docs.docker.com/desktop/features/wsl/ "WSL | Docker Docs"
