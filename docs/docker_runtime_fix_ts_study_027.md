# 第27章：`.devcontainer/devcontainer.json` 最小を置く📁✨

この章は「**ワンクリックで“いつもの開発環境”が立ち上がる**」状態を作る回です😆🧰
やることはシンプルで、**`.devcontainer/devcontainer.json` を1枚置くだけ**です👍

---

![One-Click Environment Setup](./picture/docker_runtime_fix_ts_study_027_01_one_click_setup.png)

#### 1) ゴール🎯✨

* VS Codeでフォルダを開いて
  👉 **Dev Containers: Reopen in Container** を押すだけで
  ✅ Node/TS入りのコンテナが起動して、そこで開発できるようになる！📦🐳
  （`devcontainer.json` はプロジェクト配下の `.devcontainer/devcontainer.json` か、ルート直下の `.devcontainer.json` に置けます）([Visual Studio Code][1])

---

![Project File Structure](./picture/docker_runtime_fix_ts_study_027_02_file_structure.png)

#### 2) まず「最低限の配置」を作る🧱📁

こんな感じにします👇（Dockerfile は前の章までで作ってある想定）

```text
myapp/
  Dockerfile
  package.json
  package-lock.json
  src/
    index.ts
  .devcontainer/
    devcontainer.json
```

---

![Config Anatomy (Context)](./picture/docker_runtime_fix_ts_study_027_03_config_anatomy.png)

#### 3) **最小 devcontainer.json（Dockerfile を使う版）**✅✨

ここがこの章の本体です👇

```json
{
  "name": "node-ts",
  "build": {
    "dockerfile": "../Dockerfile",
    "context": ".."
  }
}
```

ポイントは2つだけ！🧠✨

* `"build.dockerfile"` は **devcontainer.json から見た相対パス**です。([devcontainers.github.io][2])
  だから `.devcontainer/devcontainer.json` からルートの `Dockerfile` を指すなら `../Dockerfile` ✅
* `"build.context"` は **Docker build の作業ディレクトリ**です。デフォルトは `"."`（つまり `.devcontainer/`）なんだけど、これだと `package.json` が見えなくて詰みやすいです💥
  なので **`"context": ".."` を付けるのが事故りにくい**です。([devcontainers.github.io][2])

> ここ、初心者が一番ハマる場所です😇
> 「Dockerfile は見つかったのに、COPY が失敗する / package.json が無いって言われる」系は、だいたい context が原因！

---

![VS Code Launch Action](./picture/docker_runtime_fix_ts_study_027_04_vscode_launch.png)

#### 4) VS Code で起動する手順（最短ルート）🏃‍♂️💨

1. プロジェクトを VS Code で開く📂
2. コマンドパレット（F1）で
   **Dev Containers: Reopen in Container** を実行🚪🐳
3. あとは待つだけ（初回はビルドが走る）🔧✨
4. 左下に「リモートっぽい表示」が出て、コンテナに入れてたら成功🎉
   （拡張やツールが “コンテナ内” に入って動くのが Dev Containers の強みです）([marketplace.visualstudio.com][3])

> もしまだコンテナに入ってない状態なら、**Dev Containers: Open Folder in Container...** でもOKです。([Visual Studio Code][1])

---

#### 5) 「最小」から1歩だけ便利にする👣✨（おすすめ）

最小で動いたら、次はこれを足すと幸せになりやすいです😊💡

![Auto Extensions Installation](./picture/docker_runtime_fix_ts_study_027_05_auto_extensions.png)

##### A. ESLint など “拡張” を自動インストール🧩⬇️

```json
{
  "name": "node-ts",
  "build": { "dockerfile": "../Dockerfile", "context": ".." },
  "customizations": {
    "vscode": {
      "extensions": [
        "dbaeumer.vscode-eslint"
      ]
    }
  }
}
```

VS Code の公式ドキュメントにもこの形で例が載ってます。([Visual Studio Code][1])

![Post Create Command](./picture/docker_runtime_fix_ts_study_027_06_post_create_command.png)

##### B. 初回だけ `npm ci` まで自動で走らせる📦⚡

```json
{
  "name": "node-ts",
  "build": { "dockerfile": "../Dockerfile", "context": ".." },
  "postCreateCommand": "npm ci"
}
```

* `.devcontainer` の中身を変えたら **Rebuild が必要**です。([Visual Studio Code][1])
* `postCreateCommand` は「**コンテナ作成後に1回だけ**」走るので、依存インストールと相性がいいです👍（`npm install` みたいな用途が想定されています）([Visual Studio Code][1])

---

![Context Pitfall](./picture/docker_runtime_fix_ts_study_027_07_context_pitfall.png)

#### 6) よくある詰まりポイント🧯💥（最短で直す）

##### ❶ `COPY package.json` が失敗する / ファイルが無いと言われる

👉 **`"build.context": ".."` を付ける**（これが9割）([devcontainers.github.io][2])

##### ❷ 設定変えたのに反映されない

👉 **Dev Containers: Rebuild Container**（設定変更は自動反映されない設計です）([Visual Studio Code][1])

##### ❸ ワークスペースのマウント位置を変えたい

👉 `workspaceMount` / `workspaceFolder` を使います（自動マウント挙動を上書きできる）([Visual Studio Code][4])

---

#### 7) AIに投げると爆速になるやつ🤖⚡（コピペでOK）

* **最小 devcontainer.json をあなたの Dockerfile に合わせて作らせる**

  * 「`.devcontainer/devcontainer.json` を最小で作って。Dockerfile はプロジェクトルートにある。ハマりやすい `build.context` も正しく入れて」

* **エラー貼って原因を特定させる**

  * 「Dev Containers のビルドログを貼るので、原因と直し方を “最短手順” で出して。直すべきのは devcontainer.json / Dockerfile のどれ？」

* **拡張セットを提案させる（Node/TS向け）**

  * 「Node+TypeScriptで最低限入れると嬉しい VS Code 拡張を devcontainer.json の `customizations` で提案して。理由も1行で」

---

#### 8) この章の“できた判定”✅🎉

* `.devcontainer/devcontainer.json` がある
* **Reopen in Container** で開ける([Visual Studio Code][1])
* そして “次回以降も同じ環境” が再現できる😆🔁

---

次の章（第28章）で、Windows での安定運用（WSL2 / Docker Desktop まわり）に入ると、**「なぜか動かない」系が激減**します🪟🐧🔥

[1]: https://code.visualstudio.com/docs/devcontainers/create-dev-container "Create a Dev Container"
[2]: https://devcontainers.github.io/implementors/json_reference/ "Dev Container metadata reference"
[3]: https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers "
        Dev Containers - Visual Studio Marketplace
    "
[4]: https://code.visualstudio.com/remote/advancedcontainers/change-default-source-mount "Change the default source code mount"
