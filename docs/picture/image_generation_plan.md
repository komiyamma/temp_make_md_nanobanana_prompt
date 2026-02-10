# Image Generation Plan
| ID | Target MD File Name | Proposed Image Filename | Relative Link Path | Prompt | Insertion Point |
|---|---|---|---|---|---|
| 0 | test_study_md.md | test_study_aaa_bbb.png | ./picture/test_study_aaa_bbb.png | A screenshot of the Hidemaru Editor "Key Assignment" (キー割り当て) dialog. The "User Menu" or "Macro" section is visible. A key combination like "Ctrl+@" or "Ctrl+Shift+G" is selected, and the file `HmGoogleGemini.mac` is assigned to it. The focus is on showing the association between the key and the macro file. Clean technical style. | After the paragraph ending with `なんらかのキー割り当てをするのを推奨します。`. |
| 1 | react_index.md | react_index_hero_roadmap.png | ./picture/react_index_hero_roadmap.png | **Theme**: React v19 and TypeScript Learning Journey

**Labels to Render**:
- React: "React v19"
- TypeScript: "TypeScript"
- Goal: "完全習得"

**Visual Details**:
1. Core Concept: A clear, exciting path or roadmap.
2. Metaphor: A winding path going up a mountain or through a futuristic city, with checkpoints.
3. Action: The path starts simple and gets more advanced, but looks achievable.
4. Layout: Wide aspect ratio, path flowing from bottom-left to top-right. | # 挫折しないReact v19入門：TS完全対応【290章】ロードマップ |
| 1 | react_index.md | react_index_component_architecture.png | ./picture/react_index_component_architecture.png | **Theme**: Component-based Architecture

**Labels to Render**:
- Parent: "親パーツ"
- Child: "子パーツ"
- Data: "データ (Props)"

**Visual Details**:
1. Core Concept: UI is built from nested components.
2. Metaphor: Building blocks or a tree structure.
3. Action: An arrow labeled "Props" flowing down from Parent to Child.
4. Layout: Hierarchical tree structure, clean and simple. | ## 🎁 **Module 3: Props（型付きデータの受け渡し） (21〜30章)** |
| 1 | react_index.md | react_index_state_management_evolution.png | ./picture/react_index_state_management_evolution.png | **Theme**: Evolution of State Management

**Labels to Render**:
- Level 1: "useState"
- Level 2: "useContext"
- Level 3: "Zustand"

**Visual Details**:
1. Core Concept: Scaling state management from local to global.
2. Metaphor: Small bucket (useState) -> Water tower (Context) -> Distribution center (Zustand).
3. Action: Showing capacity/complexity handling increasing.
4. Layout: Three distinct stages side-by-side or steps. | ## 🐻 **Module 19: グローバルステート管理の決定版 (Zustand) (171〜180章)** |
| 2 | react_study_001.md | react_study_001_declarative_vs_imperative.png | ./picture/react_study_001_declarative_vs_imperative.png | **Theme**: Declarative vs Imperative Programming Analogy

**Labels to Render**:
- Imperative: "命令的 (How)"
- Declarative: "宣言的 (What)"
- Action 1: "Step 1, Step 2, Step 3..."
- Action 2: "Please make this!"

**Visual Details**:
1. Core Concept: Contrast between giving instructions and describing the result.
2. Metaphor: Left side: A person reading a long recipe (Imperative). Right side: A person showing a photo of the finished dish (Declarative).
3. Action: Left is busy/complex. Right is simple/direct.
4. Layout: Split comparison. Left (Gray/Complex), Right (Colorful/Simple). | ## まずは直感でOK：宣言的 vs 命令的 🤔➡️😊 |
| 2 | react_study_001.md | react_study_001_virtual_dom_diff.png | ./picture/react_study_001_virtual_dom_diff.png | **Theme**: React Virtual DOM Diffing

**Labels to Render**:
- Real DOM: "ブラウザ (Real DOM)"
- Virtual DOM: "React (Virtual DOM)"
- Diff: "差分 (Diff)"

**Visual Details**:
1. Core Concept: React compares new state with old state and updates only what changed.
2. Metaphor: Spot the difference game. Two blueprint layers overlaying.
3. Action: A magnifying glass highlighting a single changing element (e.g., a button changing color), while the rest is static.
4. Layout: Left to Right flow. Old Virtual DOM -> New Virtual DOM -> Patch to Real DOM. | ## Reactのざっくり仕組み 🧠⚙️ |
| 2 | react_study_001.md | react_study_001_jsx_concept.png | ./picture/react_study_001_jsx_concept.png | **Theme**: JSX: JavaScript + HTML

**Labels to Render**:
- JS: "JavaScript (Logic)"
- HTML: "HTML (Structure)"
- Result: "JSX"

**Visual Details**:
1. Core Concept: Fusion of Logic and Structure.
2. Metaphor: Two puzzle pieces locking together or a blender mixing them.
3. Action: JS gear and HTML tag merging into a React Component block.
4. Layout: Equation style: A + B = C. | ## JSXってなに？🧩（さわりだけ） |
| 2 | react_study_001.md | react_study_001_state_ui_sync.png | ./picture/react_study_001_state_ui_sync.png | **Theme**: State driving UI updates

**Labels to Render**:
- State: "State (データ)"
- UI: "UI (見た目)"
- Sync: "自動更新"

**Visual Details**:
1. Core Concept: Data changes automatically reflect on screen.
2. Metaphor: A puppet master (State) controlling a puppet (UI), or a reflection in a mirror.
3. Action: When the data (e.g., a counter number) changes, the UI updates instantly.
4. Layout: Top to Bottom or Side by Side connection. | ## “状態（State）” が変わると、画面も変わる 🌗 |
| 3 | react_study_002.md | react_study_002_component_reusability.png | ./picture/react_study_002_component_reusability.png | **Theme**: Component Reusability

**Labels to Render**:
- Component: "部品 (Component)"
- Usage 1: "画面A"
- Usage 2: "画面B"

**Visual Details**:
1. Core Concept: Write once, use everywhere.
2. Metaphor: A rubber stamp (Component) creating multiple identical impressions (Instances) on different papers (Screens). Or Lego blocks.
3. Action: Stamping the same "Button" or "Card" design onto two different layouts.
4. Layout: Central "Master" component, arrows pointing to usages. | ## コンポーネントだから“増えても怖くない”🧱🧱🧱 |
| 3 | react_study_002.md | react_study_002_dynamic_ui_usecase.png | ./picture/react_study_002_dynamic_ui_usecase.png | **Theme**: When to use React?

**Labels to Render**:
- Dynamic: "React (動的・複雑)"
- Static: "HTML (静的・シンプル)"

**Visual Details**:
1. Core Concept: React excels at complex, changing interfaces.
2. Metaphor: A high-tech dashboard (React) vs a printed poster (Static HTML).
3. Action: The dashboard has graphs moving and lights blinking. The poster is still.
4. Layout: Split comparison. | ## Reactがうれしい場面 💡 |
| 3 | react_study_002.md | react_study_002_team_development.png | ./picture/react_study_002_team_development.png | **Theme**: Efficient Team Development with Components

**Labels to Render**:
- Dev A: "Aさん (Header担当)"
- Dev B: "Bさん (Main担当)"
- Combine: "合体！"

**Visual Details**:
1. Core Concept: Parallel development without conflict.
2. Metaphor: Two people building different parts of a model kit, then snapping them together perfectly.
3. Action: Dev A holds the Header block, Dev B holds the Content block. They fit together.
4. Layout: Side by side developers, arrows merging to the center app. | ## チーム開発で光る✨ “読みやすさ＆変更の強さ” |
| 4 | react_study_003.md | react_study_003_props_injection.png | ./picture/react_study_003_props_injection.png | **Theme**: Props Injection Mechanism

**Labels to Render**:
- Props: "Props (name, emoji)"
- Component: "ProfileCard"
- UI: "完成したカード"

**Visual Details**:
1. Core Concept: Data + Template = UI.
2. Metaphor: A factory machine or a mold.
3. Action: Inputs (Strings/Emoji) go into the top of the component box, and a rendered HTML card comes out the bottom.
4. Layout: Vertical flow. Input -> Process -> Output. | ### 1) `ProfileCard.tsx` を新規作成 ✍️ |
| 4 | react_study_003.md | react_study_003_smart_vs_dumb.png | ./picture/react_study_003_smart_vs_dumb.png | **Theme**: Presentational vs Stateful Components

**Labels to Render**:
- Presentational: "見た目だけ (Card)"
- Stateful: "機能持ち (Counter)"
- Combined: "組み合わせ"

**Visual Details**:
1. Core Concept: Separation of concerns.
2. Metaphor: A beautiful frame (Presentational) holding a clock mechanism (Stateful). Or a mannequin vs a robot.
3. Action: The frame is static/styled. The clock mechanism is moving/ticking.
4. Layout: Split comparison and then combination. | ## “状態を持つ部品”と“見た目だけの部品” 🧠👀 |
| 4 | react_study_003.md | react_study_003_monolith_vs_modular.png | ./picture/react_study_003_monolith_vs_modular.png | **Theme**: Monolithic vs Modular Component Structure

**Labels to Render**:
- NG: "巨大コンポーネント (Monolith)"
- OK: "分割された部品 (Modular)"

**Visual Details**:
1. Core Concept: Maintainability through splitting.
2. Metaphor: A tangled ball of yarn (NG) vs neatly rolled balls of different colors (OK). Or a messy room vs organized drawers.
3. Action: The tangled one looks hard to use. The organized one looks easy to pick from.
4. Layout: Split comparison. | ## よくあるNG & その直し方 🙅‍♀️➡️🙆‍♀️ |
