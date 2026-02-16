
import os

images = [
    # File 49: docs/cap_ts_study_016.md
    {
        "file": "docs/cap_ts_study_016.md",
        "filename": "cap_ts_study_016_voting_box.png",
        "description": "Voting Box",
        "prompt": "**Theme**: Quorum Voting Box<br><br>**Labels to Render**:<br>- N: \"Copies (N) 📦\"<br>- W: \"Write Votes (W) ✍️\"<br>- R: \"Read Votes (R) 👀\"<br><br>**Visual Details**:<br>1. Core Concept: Voting for success.<br>2. Metaphor: A ballot box. There are N copies inside. Hands are casting votes labeled W (Write) or R (Read).<br>3. Action: Voting.<br>4. Layout: Scene focus.",
        "insertion_marker": "## 16.1 クォーラムってなに？（超ざっくり）🧠💡"
    },
    {
        "file": "docs/cap_ts_study_016.md",
        "filename": "cap_ts_study_016_nwr_definitions.png",
        "description": "N/W/R Definitions",
        "prompt": "**Theme**: N W R Definitions<br><br>**Labels to Render**:<br>- N: \"3 Replicas\"<br>- W: \"2 Writes (Success)\"<br>- R: \"2 Reads (Answer)\"<br><br>**Visual Details**:<br>1. Core Concept: Visualizing the variables.<br>2. Metaphor: Three distinct zones.<br>   - N: Three server towers.<br>   - W: Two checkmarks.<br>   - R: Two magnifying glasses.<br>3. Action: Static definition.<br>4. Layout: Horizontal row.",
        "insertion_marker": "## 16.2 N / W / R って何？🔤📌"
    },
    {
        "file": "docs/cap_ts_study_016.md",
        "filename": "cap_ts_study_016_overlap_nodes.png",
        "description": "Overlap Nodes",
        "prompt": "**Theme**: Quorum Overlap<br><br>**Labels to Render**:<br>- Write Set: \"A, B\"<br>- Read Set: \"B, C\"<br>- Overlap: \"Node B (Latest) ✨\"<br><br>**Visual Details**:<br>1. Core Concept: Intersection ensures consistency.<br>2. Metaphor: Venn diagram style overlap. Node A and B are in the Write circle. Node B and C are in the Read circle. Node B is highlighted as the overlap.<br>3. Action: Intersection.<br>4. Layout: Venn diagram.",
        "insertion_marker": "## 16.4 3ノードでイメージしよう（N=3）🧑‍🤝‍🧑🧑‍🤝‍🧑🧑‍🤝‍🧑"
    },
    {
        "file": "docs/cap_ts_study_016.md",
        "filename": "cap_ts_study_016_case_a_majority.png",
        "description": "Case A Majority",
        "prompt": "**Theme**: Quorum Majority Balance<br><br>**Labels to Render**:<br>- Left: \"Speed ⚡\"<br>- Right: \"Consistency ✅\"<br>- Center: \"Balanced (Majority)\"<br><br>**Visual Details**:<br>1. Core Concept: Balanced approach.<br>2. Metaphor: A balance scale. Speed and Consistency are balanced perfectly.<br>3. Action: Balancing.<br>4. Layout: Centered object.",
        "insertion_marker": "### ✅ Case A（W=2, R=2）＝「多数決で一致を取りに行く」🗳️✅"
    },
    {
        "file": "docs/cap_ts_study_016.md",
        "filename": "cap_ts_study_016_case_b_speed.png",
        "description": "Case B Speed",
        "prompt": "**Theme**: Speed Priority Risk<br><br>**Labels to Render**:<br>- Runner: \"Fast (W=1) ⚡\"<br>- Obstacle: \"Stale Data 🕰️\"<br>- Result: \"Trip! 💥\"<br><br>**Visual Details**:<br>1. Core Concept: Fast but risky.<br>2. Metaphor: A runner sprinting fast but tripping over a stone labeled \"Stale Data\".<br>3. Action: Tripping.<br>4. Layout: Action scene.",
        "insertion_marker": "### ⚡ Case B（W=1, R=1）＝「速さ優先」⚡😆"
    },
    {
        "file": "docs/cap_ts_study_016.md",
        "filename": "cap_ts_study_016_case_c_strict.png",
        "description": "Case C Strict",
        "prompt": "**Theme**: Strict Quorum Fragility<br><br>**Labels to Render**:<br>- Fortress: \"W=3 (Strict)\"<br>- Gate: \"Closed 🚫\"<br>- Reason: \"1 Node Down 💀\"<br><br>**Visual Details**:<br>1. Core Concept: Strong but fragile.<br>2. Metaphor: A strong fortress with a closed gate. One of the three guard towers has collapsed, preventing the gate from opening.<br>3. Action: Blocking.<br>4. Layout: Scene.",
        "insertion_marker": "### 💥 Case C（W=3）＝「全員一致」🧱😇"
    },
    {
        "file": "docs/cap_ts_study_016.md",
        "filename": "cap_ts_study_016_misconception_magic.png",
        "description": "Misconception Magic",
        "prompt": "**Theme**: Quorum Misconception<br><br>**Labels to Render**:<br>- Hat: \"Quorum Magic? 🎩\"<br>- Rabbit: \"Latest Data?\"<br>- Monster: \"Conflict! 😈\"<br><br>**Visual Details**:<br>1. Core Concept: Quorum is not magic.<br>2. Metaphor: A magician's hat. Instead of just a cute rabbit (Latest Data), a scary conflict monster is also popping out.<br>3. Action: Surprise.<br>4. Layout: Close-up.",
        "insertion_marker": "### 勘違い①：クォーラム＝「必ず最新が見える魔法」ではない🪄❌"
    },

    # File 50: docs/cap_ts_study_017.md
    {
        "file": "docs/cap_ts_study_017.md",
        "filename": "cap_ts_study_017_stale_read_concept.png",
        "description": "Stale Read Concept",
        "prompt": "**Theme**: Stale Read Experience<br><br>**Labels to Render**:<br>- Screen: \"Stock: 10 (Old) 📱\"<br>- DB: \"Stock: 9 (New) 🗃️\"<br>- User: \"Huh? 🤔\"<br><br>**Visual Details**:<br>1. Core Concept: User sees old data.<br>2. Metaphor: A user looking at a smartphone screen showing \"10\". Behind them, the database clearly shows \"9\".<br>3. Action: Confusion.<br>4. Layout: Scene.",
        "insertion_marker": "## 17.1 「古い読み取り」ってなに？😵‍💫📖"
    },
    {
        "file": "docs/cap_ts_study_017.md",
        "filename": "cap_ts_study_017_causes_lag.png",
        "description": "Causes of Lag",
        "prompt": "**Theme**: Causes of Stale Reads<br><br>**Labels to Render**:<br>- 1: \"Replication Lag 🐢\"<br>- 2: \"Cache (Ice) 🧊\"<br>- 3: \"Distributed Read 🧭\"<br><br>**Visual Details**:<br>1. Core Concept: Three main causes.<br>2. Metaphor: Three icons.<br>   - A slow turtle (Lag).<br>   - An ice cube (Cache).<br>   - A compass pointing to different servers (Distributed).<br>3. Action: Static display.<br>4. Layout: Horizontal row.",
        "insertion_marker": "## 17.2 どうして起きるの？（超ざっくり）🧠🔍"
    },
    {
        "file": "docs/cap_ts_study_017.md",
        "filename": "cap_ts_study_017_tech_primary_after_update.png",
        "description": "Tech 1 Primary",
        "prompt": "**Theme**: Read Primary After Update<br><br>**Labels to Render**:<br>- Action: \"Update! ✍️\"<br>- Router: \"Go to Primary (5s) 👑\"<br>- Path: \"To Replica (Later) 🪞\"<br><br>**Visual Details**:<br>1. Core Concept: Routing logic.<br>2. Metaphor: A traffic director (Router) pointing a user to the King (Primary) immediately after they updated something. A timer shows \"5s\".<br>3. Action: Directing.<br>4. Layout: Flow.",
        "insertion_marker": "### ✅ テク1：更新直後だけ Primary を読む（いちばん効く）👑📌"
    },
    {
        "file": "docs/cap_ts_study_017.md",
        "filename": "cap_ts_study_017_tech_read_repair.png",
        "description": "Tech 3 Read Repair",
        "prompt": "**Theme**: Read Repair<br><br>**Labels to Render**:<br>- Replica: \"Old Data 🏚️\"<br>- Reader: \"Fixing... 🔧\"<br>- Result: \"New Data ✨\"<br><br>**Visual Details**:<br>1. Core Concept: Fixing while reading.<br>2. Metaphor: A reader noticing a broken/old part of the Replica and using a wrench to fix it immediately.<br>3. Action: Repairing.<br>4. Layout: Action scene.",
        "insertion_marker": "### ✅ テク3：Read Repair（読んだついでに古いReplicaを直す）🩹📚"
    },
    {
        "file": "docs/cap_ts_study_017.md",
        "filename": "cap_ts_study_017_lab_architecture.png",
        "description": "Lab Architecture",
        "prompt": "**Theme**: Lab Architecture<br><br>**Labels to Render**:<br>- API: \"API\"<br>- Log: \"Events (JSONL)\"<br>- Worker: \"Worker (Delayed) 🐢\"<br>- Replica: \"Replica JSON\"<br><br>**Visual Details**:<br>1. Core Concept: Lab setup.<br>2. Metaphor: Architecture diagram. API writes to Primary and Event Log. Worker reads Log with delay and writes to Replica.<br>3. Action: Flow.<br>4. Layout: Diagram.",
        "insertion_marker": "### 17.4.1 まずは“遅いReplica”を用意する🐢🪞"
    },
    {
        "file": "docs/cap_ts_study_017.md",
        "filename": "cap_ts_study_017_force_primary_map.png",
        "description": "Force Primary Map",
        "prompt": "**Theme**: Force Primary Logic<br><br>**Labels to Render**:<br>- Map: \"User ID -> Until Time\"<br>- Clock: \"Now < Until?\"<br>- Yes: \"Primary 👑\"<br>- No: \"Replica 🪞\"<br><br>**Visual Details**:<br>1. Core Concept: Time-based routing.<br>2. Metaphor: A logic gate. Checking a map entry against a clock to decide the path.<br>3. Action: Decision.<br>4. Layout: Flowchart.",
        "insertion_marker": "### 17.5.2 次に改善を体験（autoにする）👑✨"
    },
    {
        "file": "docs/cap_ts_study_017.md",
        "filename": "cap_ts_study_017_use_cases.png",
        "description": "Use Cases",
        "prompt": "**Theme**: Use Case Separation<br><br>**Labels to Render**:<br>- Profile: \"Primary (My Edit) 👑\"<br>- Feed: \"Replica (Others' Post) 🪞\"<br><br>**Visual Details**:<br>1. Core Concept: Different needs.<br>2. Metaphor: Split screen.<br>   - Left: User editing their profile (Primary).<br>   - Right: User scrolling a news feed (Replica).<br>3. Action: Usage.<br>4. Layout: Split view.",
        "insertion_marker": "## 17.7 いつこの手を使う？（適用条件まとめ）🤖✅"
    },

    # File 51: docs/cap_ts_study_018.md
    {
        "file": "docs/cap_ts_study_018.md",
        "filename": "cap_ts_study_018_stale_cache_truck.png",
        "description": "Stale Cache Truck",
        "prompt": "**Theme**: Stale Cache Delivery<br><br>**Labels to Render**:<br>- Truck: \"Cache Express (Fast) 🚚\"<br>- Cargo: \"Old News (Stock: 10) 📰\"<br>- Press: \"DB (Stock: 9) 🖨️\"<br><br>**Visual Details**:<br>1. Core Concept: Fast delivery of old data.<br>2. Metaphor: A fast delivery truck delivering an old newspaper. The printing press (DB) has the new edition but it's slower.<br>3. Action: Delivery.<br>4. Layout: Scene.",
        "insertion_marker": "### 2.1 よくある悲劇ストーリー📖💥"
    },
    {
        "file": "docs/cap_ts_study_018.md",
        "filename": "cap_ts_study_018_cache_terms_icons.png",
        "description": "Cache Terms",
        "prompt": "**Theme**: Cache Terminology Icons<br><br>**Labels to Render**:<br>- Hit: \"Hit 🎯\"<br>- Miss: \"Miss 🕳️\"<br>- TTL: \"TTL ⏳\"<br>- Invalidate: \"Delete 🗑️\"<br><br>**Visual Details**:<br>1. Core Concept: Visualizing terms.<br>2. Metaphor: Four icons.<br>   - Hit: Dartboard bullseye.<br>   - Miss: Empty box.<br>   - TTL: Hourglass.<br>   - Invalidate: Trash can.<br>3. Action: Static icons.<br>4. Layout: Row.",
        "insertion_marker": "## 3. キャッシュの基本用語ミニ辞典📖🐣"
    },
    {
        "file": "docs/cap_ts_study_018.md",
        "filename": "cap_ts_study_018_ttl_shelf.png",
        "description": "TTL Shelf",
        "prompt": "**Theme**: TTL Shelf Life<br><br>**Labels to Render**:<br>- Item: \"Data\"<br>- Clock: \"Expires in 10s\"<br>- Bin: \"Expired 🗑️\"<br><br>**Visual Details**:<br>1. Core Concept: Expiration.<br>2. Metaphor: A supermarket shelf. Items have clocks attached. When the clock hits zero, the item falls into a bin.<br>3. Action: Falling.<br>4. Layout: Scene.",
        "insertion_marker": "### 5.1 `cache.ts`（TTLキャッシュ本体）🧠🧊"
    },
    {
        "file": "docs/cap_ts_study_018.md",
        "filename": "cap_ts_study_018_cache_aside_pattern.png",
        "description": "Cache Aside",
        "prompt": "**Theme**: Cache-Aside Pattern<br><br>**Labels to Render**:<br>- App: \"Do you have it?\"<br>- Cache: \"No (Miss) 🙅\"<br>- DB: \"Here it is (Slow) 🐢\"<br><br>**Visual Details**:<br>1. Core Concept: Lookup flow.<br>2. Metaphor: A character (App) asking a fast robot (Cache). Robot says no. App goes to a slow library (DB).<br>3. Action: Interaction.<br>4. Layout: Scene.",
        "insertion_marker": "## 7. 実装：API（キャッシュありGET、キャッシュ放置のPOST）😈🧊"
    },
    {
        "file": "docs/cap_ts_study_018.md",
        "filename": "cap_ts_study_018_invalidation_button.png",
        "description": "Invalidation Button",
        "prompt": "**Theme**: Cache Invalidation<br><br>**Labels to Render**:<br>- Action: \"Update DB ✍️\"<br>- Button: \"Delete Cache 🔴\"<br>- Result: \"Clean ✨\"<br><br>**Visual Details**:<br>1. Core Concept: Delete on update.<br>2. Metaphor: A hand pressing a big red \"Delete Cache\" button immediately after writing to the DB.<br>3. Action: Pressing button.<br>4. Layout: Close-up.",
        "insertion_marker": "## 9. 改善①：更新したら“そのキーだけ消す”🗑️✅"
    },
    {
        "file": "docs/cap_ts_study_018.md",
        "filename": "cap_ts_study_018_cache_stampede.png",
        "description": "Cache Stampede",
        "prompt": "**Theme**: Cache Stampede<br><br>**Labels to Render**:<br>- Dam: \"TTL Expired 💥\"<br>- Flood: \"Requests 🌊\"<br>- DB: \"Help! 😱\"<br><br>**Visual Details**:<br>1. Core Concept: Thundering herd on expiry.<br>2. Metaphor: A dam breaking (TTL expiry) and a flood of water (requests) rushing towards a small hut (DB).<br>3. Action: Flooding.<br>4. Layout: Scene.",
        "insertion_marker": "### 11.1 キャッシュスタンピード（雪崩）❄️💥"
    },

    # File 52: docs/cap_ts_study_019.md
    {
        "file": "docs/cap_ts_study_019.md",
        "filename": "cap_ts_study_019_lost_update_painters.png",
        "description": "Lost Update Painters",
        "prompt": "**Theme**: Lost Update Painters<br><br>**Labels to Render**:<br>- Painter A: \"Paint 11 🔴\"<br>- Painter B: \"Paint 11 🔵\"<br>- Wall: \"Just 11 (Not 12) 🎨\"<br><br>**Visual Details**:<br>1. Core Concept: Overwrite conflict.<br>2. Metaphor: Two painters painting the number \"11\" on the same spot at the same time, covering each other. The result is just \"11\", not \"12\".<br>3. Action: Painting.<br>4. Layout: Action scene.",
        "insertion_marker": "## 19.2 なぜ「上書き」が危ないの？😱🧨（lost update 体験）"
    },
    {
        "file": "docs/cap_ts_study_019.md",
        "filename": "cap_ts_study_019_commutativity_blocks.png",
        "description": "Commutativity Blocks",
        "prompt": "**Theme**: Commutativity<br><br>**Labels to Render**:<br>- Order 1: \"A + B\"<br>- Order 2: \"B + A\"<br>- Result: \"Same Height 🧱\"<br><br>**Visual Details**:<br>1. Core Concept: Order independence.<br>2. Metaphor: Stacking blocks. Red then Blue equals Blue then Red in total height.<br>3. Action: Stacking.<br>4. Layout: Side by side.",
        "insertion_marker": "## 19.3 「加算」にすると何が嬉しい？🎁✨（競合に強い）"
    },
    {
        "file": "docs/cap_ts_study_019.md",
        "filename": "cap_ts_study_019_counter_levels.png",
        "description": "Counter Levels",
        "prompt": "**Theme**: Counter Implementation Levels<br><br>**Labels to Render**:<br>- Lvl A: \"DB Atomic 🔒\"<br>- Lvl B: \"Delta Event 📨\"<br>- Lvl C: \"G-Counter 🧲\"<br><br>**Visual Details**:<br>1. Core Concept: Three approaches.<br>2. Metaphor: Three tiers.<br>   - A: A safe with a lock.<br>   - B: A mailbox receiving letters.<br>   - C: Multiple magnets merging.<br>3. Action: Static display.<br>4. Layout: Steps.",
        "insertion_marker": "## 19.4 カウンタ設計：3つのレベル感 🧩📚"
    },
    {
        "file": "docs/cap_ts_study_019.md",
        "filename": "cap_ts_study_019_bad_overwrite.png",
        "description": "Bad Overwrite",
        "prompt": "**Theme**: Bad Overwrite API<br><br>**Labels to Render**:<br>- Robot: \"Erase & Write ✏️\"<br>- Old Data: \"Gone 💨\"<br>- Status: \"Dangerous ☠️\"<br><br>**Visual Details**:<br>1. Core Concept: Destructive update.<br>2. Metaphor: A robot erasing a whiteboard and writing a new number, ignoring what was there before.<br>3. Action: Erasing.<br>4. Layout: Scene.",
        "insertion_marker": "### ② まず悪い例：上書きAPI（消えるやつ）😱"
    },
    {
        "file": "docs/cap_ts_study_019.md",
        "filename": "cap_ts_study_019_good_delta.png",
        "description": "Good Delta",
        "prompt": "**Theme**: Good Delta API<br><br>**Labels to Render**:<br>- Robot: \"Add Ticket 🎫\"<br>- Queue: \"+1, +1, +1\"<br>- Status: \"Safe ✅\"<br><br>**Visual Details**:<br>1. Core Concept: Additive update.<br>2. Metaphor: A robot dropping a \"+1\" ticket into a queue. No erasing happens.<br>3. Action: Dropping ticket.<br>4. Layout: Scene.",
        "insertion_marker": "### ③ 良い例：APIは「+1イベント」を積む 📨➕"
    },
    {
        "file": "docs/cap_ts_study_019.md",
        "filename": "cap_ts_study_019_duplicate_pitfall.png",
        "description": "Duplicate Pitfall",
        "prompt": "**Theme**: Duplicate Event Pitfall<br><br>**Labels to Render**:<br>- Mailbox: \"2 Letters (Same)\"<br>- Worker: \"Counted Twice! 😱\"<br>- Result: \"+2 (Wrong) ❌\"<br><br>**Visual Details**:<br>1. Core Concept: Double counting.<br>2. Metaphor: A mailbox with two identical \"+1\" letters. A worker adds both to the total, causing an error.<br>3. Action: Counting.<br>4. Layout: Cause and effect.",
        "insertion_marker": "### 落とし穴1：デルタは強いけど「重複」には弱い 📨🌀"
    },

    # File 53: docs/cap_ts_study_020.md
    {
        "file": "docs/cap_ts_study_020.md",
        "filename": "cap_ts_study_020_lost_update_tags.png",
        "description": "Lost Update Tags",
        "prompt": "**Theme**: Lost Update Tags<br><br>**Labels to Render**:<br>- User A: \"Stick SALE 🏷️\"<br>- User B: \"Stick GIFT 🎁\"<br>- Result: \"SALE Covered 🙈\"<br><br>**Visual Details**:<br>1. Core Concept: Overwrite hides data.<br>2. Metaphor: A board where User A sticks a \"SALE\" tag, and User B immediately sticks a \"GIFT\" tag *over* it, hiding the first one.<br>3. Action: Covering.<br>4. Layout: Action scene.",
        "insertion_marker": "### 事故①：片方の変更が消える（Lost Update）🫥💥"
    },
    {
        "file": "docs/cap_ts_study_020.md",
        "filename": "cap_ts_study_020_three_brothers.png",
        "description": "Three Brothers",
        "prompt": "**Theme**: Set History Event Icons<br><br>**Labels to Render**:<br>- Set: \"Basket 🧺\"<br>- History: \"Scroll 📜\"<br>- Event: \"Megaphone 📣\"<br><br>**Visual Details**:<br>1. Core Concept: Three data models.<br>2. Metaphor: Three icons.<br>   - Set: A basket of unique items.<br>   - History: A chronological scroll.<br>   - Event: A megaphone announcing facts.<br>3. Action: Static display.<br>4. Layout: Row.",
        "insertion_marker": "## 20.3 合体しやすい3兄弟：集合・履歴・イベント👭✨"
    },
    {
        "file": "docs/cap_ts_study_020.md",
        "filename": "cap_ts_study_020_append_log.png",
        "description": "Append Log",
        "prompt": "**Theme**: Append Only Log<br><br>**Labels to Render**:<br>- Pen: \"Writing New Line ✍️\"<br>- Scroll: \"History (Ink) 🖋️\"<br>- Action: \"No Eraser 🚫\"<br><br>**Visual Details**:<br>1. Core Concept: Immutability.<br>2. Metaphor: A pen writing a new line at the bottom of a long scroll. The previous lines are permanent ink.<br>3. Action: Writing.<br>4. Layout: Close-up.",
        "insertion_marker": "### 20.5.3 イベントを「追記で保存」する（JSONL）📝📚"
    },
    {
        "file": "docs/cap_ts_study_020.md",
        "filename": "cap_ts_study_020_set_merge.png",
        "description": "Set Merge",
        "prompt": "**Theme**: Set Merge<br><br>**Labels to Render**:<br>- Set A: \"{SALE}\"<br>- Set B: \"{GIFT}\"<br>- Merged: \"{SALE, GIFT} 🎉\"<br><br>**Visual Details**:<br>1. Core Concept: Lossless combination.<br>2. Metaphor: Two partial puzzle pieces coming together to form a complete picture containing both elements.<br>3. Action: Merging.<br>4. Layout: Process flow.",
        "insertion_marker": "### 集合は「合体」できる🧺"
    },
    {
        "file": "docs/cap_ts_study_020.md",
        "filename": "cap_ts_study_020_event_stacking.png",
        "description": "Event Stacking",
        "prompt": "**Theme**: Event Stacking<br><br>**Labels to Render**:<br>- Block 1: \"Event 1\"<br>- Block 2: \"Event 2\"<br>- Tower: \"State 🏗️\"<br><br>**Visual Details**:<br>1. Core Concept: Accumulation.<br>2. Metaphor: Stacking LEGO blocks to build a tower. Adding a new block increases the height without destroying the base.<br>3. Action: Stacking.<br>4. Layout: Vertical stack.",
        "insertion_marker": "### イベントは「足し算」できる📣"
    },
    {
        "file": "docs/cap_ts_study_020.md",
        "filename": "cap_ts_study_020_reverse_order.png",
        "description": "Reverse Order",
        "prompt": "**Theme**: Out of Order Events<br><br>**Labels to Render**:<br>- 1st: \"Shipped 🚚\"<br>- 2nd: \"Ordered 🛒\"<br>- Worker: \"Huh? 🤔\"<br><br>**Visual Details**:<br>1. Core Concept: Causality violation.<br>2. Metaphor: A timeline where the \"Shipped\" truck arrives before the \"Ordered\" cart. A worker looks puzzled.<br>3. Action: Confusion.<br>4. Layout: Timeline.",
        "insertion_marker": "## 20.8 よくある落とし穴（でも今は気にしすぎなくてOK）😵‍💫⚠️"
    },

    # File 54: docs/cap_ts_study_021.md
    {
        "file": "docs/cap_ts_study_021.md",
        "filename": "cap_ts_study_021_conflict_crash.png",
        "description": "Conflict Crash",
        "prompt": "**Theme**: Conflict Crash<br><br>**Labels to Render**:<br>- Car A: \"Update A\"<br>- Car B: \"Update B\"<br>- Intersection: \"Crash! 💥\"<br><br>**Visual Details**:<br>1. Core Concept: Simultaneous collision.<br>2. Metaphor: Two cars crashing at an intersection because the traffic lights failed (both green).<br>3. Action: Crash.<br>4. Layout: Action scene.",
        "insertion_marker": "## 21.2 競合ってなに？（超ざっくり）🧠🔀"
    },
    {
        "file": "docs/cap_ts_study_021.md",
        "filename": "cap_ts_study_021_double_apply.png",
        "description": "Double Apply",
        "prompt": "**Theme**: Double Apply<br><br>**Labels to Render**:<br>- Stamp: \"+10 Points\"<br>- Card: \"+20 (Stamped Twice) 😱\"<br>- Machine: \"Malfunction ⚙️\"<br><br>**Visual Details**:<br>1. Core Concept: Repeated application.<br>2. Metaphor: A stamp machine malfunctioning and stamping \"+10\" twice on the same point card.<br>3. Action: Stamping.<br>4. Layout: Close-up.",
        "insertion_marker": "### B) 二重反映（Double Apply）📨📨➡️💥"
    },
    {
        "file": "docs/cap_ts_study_021.md",
        "filename": "cap_ts_study_021_cancel_leak.png",
        "description": "Cancel Leak",
        "prompt": "**Theme**: Cancel Leak<br><br>**Labels to Render**:<br>- Letter: \"Cancel Order ✉️\"<br>- Hole: \"Lost 🕳️\"<br>- Manager: \"Shipping it! 📦\"<br><br>**Visual Details**:<br>1. Core Concept: Lost message.<br>2. Metaphor: A \"Cancel\" letter falling into a hole in the floor before reaching the Manager, who is happily shipping the item.<br>3. Action: Falling.<br>4. Layout: Scene.",
        "insertion_marker": "### C) 取り消し漏れ（Cancel Leak）🧨🕳️"
    },
    {
        "file": "docs/cap_ts_study_021.md",
        "filename": "cap_ts_study_021_sleep_trap.png",
        "description": "Sleep Trap",
        "prompt": "**Theme**: Sleep Trap<br><br>**Labels to Render**:<br>- Action 1: \"Read 📖\"<br>- Action 2: \"Sleep zzz 😴\"<br>- Action 3: \"Write (Conflict) ✍️\"<br><br>**Visual Details**:<br>1. Core Concept: Delay causing conflict.<br>2. Metaphor: A person reading a book, falling asleep, then waking up and writing in it, unaware the page was changed by someone else while they slept.<br>3. Action: Sequence.<br>4. Layout: Storyboard.",
        "insertion_marker": "## 21.5 実装①：わざと壊れる「ナイーブ在庫リポジトリ」🧨"
    },
    {
        "file": "docs/cap_ts_study_021.md",
        "filename": "cap_ts_study_021_flaky_test.png",
        "description": "Flaky Test",
        "prompt": "**Theme**: Flaky Test<br><br>**Labels to Render**:<br>- Machine: \"Test Runner\"<br>- Reel 1: \"PASS ✅\"<br>- Reel 2: \"FAIL ❌\"<br>- Reel 3: \"PASS ✅\"<br><br>**Visual Details**:<br>1. Core Concept: Unpredictability.<br>2. Metaphor: A slot machine spinning. It shows a mix of PASS and FAIL icons.<br>3. Action: Spinning.<br>4. Layout: Object focus.",
        "insertion_marker": "### 実行してみる🎮"
    },
    {
        "file": "docs/cap_ts_study_021.md",
        "filename": "cap_ts_study_021_barrier_race.png",
        "description": "Barrier Race",
        "prompt": "**Theme**: Deterministic Barrier<br><br>**Labels to Render**:<br>- Gate: \"Barrier 🚧\"<br>- Horses: \"Requests 🐎🐎\"<br>- Action: \"Wait for All\"<br><br>**Visual Details**:<br>1. Core Concept: Synchronization.<br>2. Metaphor: A starting gate at a horse race. All horses (requests) are held until the gate opens, ensuring they start processing together.<br>3. Action: Waiting.<br>4. Layout: Scene.",
        "insertion_marker": "## 21.8 “毎回” 壊れるようにする（再現性を作る）🎯✨"
    },

    # File 55: docs/cap_ts_study_022.md
    {
        "file": "docs/cap_ts_study_022.md",
        "filename": "cap_ts_study_022_lww_clock_skew.png",
        "description": "LWW Clock Skew",
        "prompt": "**Theme**: Clock Skew LWW<br><br>**Labels to Render**:<br>- Clock A: \"12:00 (Fast) 🕰️\"<br>- Clock B: \"11:59 (Slow) 🕰️\"<br>- Judge: \"A Wins! 🏆\"<br><br>**Visual Details**:<br>1. Core Concept: Time inaccuracy.<br>2. Metaphor: Two clocks. Clock A is old but fast (ahead of time). Clock B is new but slow. The judge picks A just because the time is greater.<br>3. Action: Judging.<br>4. Layout: Comparison.",
        "insertion_marker": "## A. LWW（Last-Write-Wins）🕒👑"
    },
    {
        "file": "docs/cap_ts_study_022.md",
        "filename": "cap_ts_study_022_domain_rule_guard.png",
        "description": "Domain Rule Guard",
        "prompt": "**Theme**: Domain Rule Guard<br><br>**Labels to Render**:<br>- Truck: \"Shipped 🚚\"<br>- Zone: \"Cancelled 🚫\"<br>- Guard: \"Stop! Rule Violation 🛡️\"<br><br>**Visual Details**:<br>1. Core Concept: Logic protection.<br>2. Metaphor: A guard rail or gate labeled \"Rule\" blocking a truck labeled \"Shipped\" from entering a zone labeled \"Cancelled\".<br>3. Action: Blocking.<br>4. Layout: Scene.",
        "insertion_marker": "## B. ドメインルール（業務ルールで決める）📜🧱"
    },
    {
        "file": "docs/cap_ts_study_022.md",
        "filename": "cap_ts_study_022_merge_puzzle.png",
        "description": "Merge Puzzle",
        "prompt": "**Theme**: Data Merge<br><br>**Labels to Render**:<br>- Piece A: \"Update A\"<br>- Piece B: \"Update B\"<br>- Result: \"Complete Picture 🧩\"<br><br>**Visual Details**:<br>1. Core Concept: Combination.<br>2. Metaphor: Two puzzle pieces coming together to form a whole picture. They fit perfectly.<br>3. Action: Connecting.<br>4. Layout: Close-up.",
        "insertion_marker": "## C. マージ（複数の更新を“合成”する）🧩🧲"
    },
    {
        "file": "docs/cap_ts_study_022.md",
        "filename": "cap_ts_study_022_selection_checklist.png",
        "description": "Selection Checklist",
        "prompt": "**Theme**: Selection Checklist<br><br>**Labels to Render**:<br>- List: \"Choice\"<br>- Item 1: \"Money? -> Rule 💸\"<br>- Item 2: \"Settings? -> LWW ⚙️\"<br><br>**Visual Details**:<br>1. Core Concept: Decision aid.<br>2. Metaphor: A clipboard with a checklist. A pen is checking off items based on the questions.<br>3. Action: Checking.<br>4. Layout: Object focus.",
        "insertion_marker": "# 4) どれを選ぶ？判断チェックリスト ✅📋"
    },
    {
        "file": "docs/cap_ts_study_022.md",
        "filename": "cap_ts_study_022_lww_vs_rule.png",
        "description": "LWW vs Rule",
        "prompt": "**Theme**: LWW vs Rule<br><br>**Labels to Render**:<br>- LWW: \"Broken Vase 💥\"<br>- Rule: \"Safe Vase 🛡️\"<br><br>**Visual Details**:<br>1. Core Concept: Safety comparison.<br>2. Metaphor: Split screen.<br>   - Left (LWW): A broken vase (accidental loss).<br>   - Right (Rule): A pristine vase protected by a glass case.<br>3. Action: Contrast.<br>4. Layout: Split view.",
        "insertion_marker": "## 5-1. まずは型を作る 🧱✨"
    },
    {
        "file": "docs/cap_ts_study_022.md",
        "filename": "cap_ts_study_022_discard_pitfall.png",
        "description": "Discard Pitfall",
        "prompt": "**Theme**: Discard Pitfall<br><br>**Labels to Render**:<br>- Detective: \"Investigation 🕵️‍♀️\"<br>- Bin: \"Empty (Deleted)\"<br>- Clue: \"Missing ❓\"<br><br>**Visual Details**:<br>1. Core Concept: Losing evidence.<br>2. Metaphor: A detective looking for clues but finding an empty trash can because the losing update was deleted.<br>3. Action: Searching.<br>4. Layout: Scene.",
        "insertion_marker": "# 7) よくある落とし穴ワースト5 😵‍💫⚠️"
    }
]

def get_next_id(plan_file):
    try:
        with open(plan_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if len(lines) < 3:
                return 1
            last_line = lines[-1].strip()
            if not last_line:
                return 1
            parts = last_line.split('|')
            if len(parts) > 1:
                try:
                    return int(parts[1].strip()) + 1
                except ValueError:
                    return 1
            return 1
    except FileNotFoundError:
        return 1

def append_to_plan(plan_file, images, start_id):
    with open(plan_file, 'a', encoding='utf-8') as f:
        current_id = start_id
        for img in images:
            row = f"| {current_id} | {os.path.basename(img['file'])} | {img['filename']} | ./picture/{img['filename']} | {img['prompt']} | {img['insertion_marker']} |\n"
            f.write(row)
            current_id += 1

def update_markdown_files(images):
    for img in images:
        filepath = img['file']
        insertion_marker = img['insertion_marker']
        image_tag = f"![{img['description']}](./picture/{img['filename']})\n\n"

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            if insertion_marker in content:
                # Check if image is already there to avoid duplicates
                if img['filename'] in content:
                    print(f"Skipping {img['filename']} in {filepath} (already exists)")
                    continue

                # Insert after the marker
                new_content = content.replace(insertion_marker, insertion_marker + "\n\n" + image_tag)

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Inserted {img['filename']} into {filepath}")
            else:
                print(f"Warning: Insertion marker '{insertion_marker}' not found in {filepath}")
        except FileNotFoundError:
            print(f"Error: File {filepath} not found")

if __name__ == "__main__":
    plan_file = "docs/picture/image_generation_plan.md"
    start_id = get_next_id(plan_file)
    print(f"Starting ID: {start_id}")

    append_to_plan(plan_file, images, start_id)
    update_markdown_files(images)
    print("Done!")
