---
description: Generate an image generation plan for a range of Markdown files based on their content analysis.
---

// turbo-all
1.  **Parse Arguments**:
    - You will receive an argument string like `1-20`. Parse this to get the `start_id` and `end_id`.

2.  **Iterate and Analyze**:
    - For each `current_id` from `start_id` to `end_id`:
        a.  **Extract Context**:
            - **Option A (Preferred): Use Script with File Output**:
                - Run the following command. **CRITICAL**: Use the `--output` argument to avoid terminal encoding issues.
                  ```powershell
                  python .\prepare_analysis_context.py --id <current_id> --report-path ".\Markdown File Categorization Report.md" --root-dir ".\docs" --output temp_context_<current_id>.json
                  ```
                - Read the generated `temp_context_<current_id>.json` file.
            - **Option B (Fallback): Direct Read**:
                - If the script fails or JSON is invalid, read `Markdown File Categorization Report.md` to find the filename for the `<current_id>`.
                - Then, directly read the Markdown file content using `view_file` or `cat`.

        b.  **Analyze Content**:
            - Review the content (from JSON `text_preview` or direct Markdown read).
            - **Goal**: Identify sections in the text where an explanatory image (diagram, flowchart, screenshot) would be beneficial.
            - **Constraint**: Do NOT propose an image if there is already an image nearby (check `existing_images` and the text context).
            - **Constraint**: If content is empty or very short, you may skip.

        c.  **Formulate Plan**:
            - If a need for an image is found:
                - **Group**: Extract from JSON `group` or the Report.
                - **Filename Construction**:
                    - Get the last part of the directory name from `group` (e.g., `other_soft/hm_activeperl` -> `hm_activeperl`).
                    - Construct the base: `cnt_<last_part>`.
                    - Append a detailed description with at least 2 English words: e.g., `_split_number`.
                    - Final: `cnt_<last_part>_<description>.png`.
                - **Global Uniqueness Check (ABSOLUTE RULE)**:
                    - **Step 1: Check Existing Images in Current Markdown**:
                        - Parse the Markdown content to find ALL `![](...)` or `<img src="...">` tags.
                        - Extract the filenames from the `src` or path attributes (e.g., `cnt_foo_bar.png`).
                        - **CRITICAL CONSTRAINT**: The proposed filename must NOT match ANY filename already present in the Markdown file. 
                        - **Action on Match**: If the exact filename (e.g., `cnt_foo.png`) is ALREADY present in the Markdown file's image tags, **SKIP ONLY this specific image proposal**. Do NOT append a suffix. Assume the image is already implemented. Do NOT stop analyzing the rest of the file.
                    - **Step 2: Check Existing Plans**:
                        - Read `./picture/image_generation_plan.md` to gather ALL existing `Proposed Image Filename` entries (from the entire file, not just this session).
                        - **Constraint**: Ensure your new `<proposed_image_filename>` matches NONE of the existing filenames in the plan.
                    - **Resolution**:
                        - If a match is found in **Step 1 (Markdown Check)**: **DISCARD** this specific image proposal entirely (do not add to plan).
                        - If a match is found ONLY in **Step 2 (Plan Check)**: Append a numeric suffix or change the description to make it unique.
                - **Prompt**: Write a "thoroughly detailed image generation prompt" describing the visual elements, style, and content of the image.
                - **Relative Link**: Construct the relative path: `./<group>/<proposed_image_filename>`.

        d.  **Append to Plan**:
            - **Duplicate Check (Concept)**:
                - Check if there is already a row for the `<current_id>` with a similar concept to avoid redundant entries for the same ID.
                - If a similar entry exists for this ID, **SKIP** appending.
            - **Safe Append**:
                - If no duplicate concept is found:
                - Use `write_to_file` to *overwrite* the file with the **Full Previous Content + New Row**.
                - (Note: `write_to_file` does not support append mode, so reading first then writing back is required).
                - Format: `| <current_id> | <filename> | <group> | <proposed_image_filename> | <relative_link> | <prompt> | <insertion_point> |`

        e.  **Modify Markdown File**:
            - **Action**: Insert the image tag into the source Markdown file.
            - **Tag**: `![<description>](<relative_link>)`
            - **Method**:
                - Identify a unique line of text *before* or *after* your desired insertion point.
                - Use `replace_file_content` to replace `Target Text` with `Target Text + \n + Image Tag`.
                - **CRITICAL**: Do NOT replace the `Target Text` with *just* the Image Tag. You must KEEP the `Target Text` in the replacement.
                - **Goal**: Place the image tag exactly where described in `<insertion_point>`.
                - **Constraint**: Do NOT use `div`, `class`, `attr`, or `edge` attributes. Just a simple Markdown image link `![]()`.
                - **Verification**: Ensure the file is updated and no original content is missing. THIS IS MANDATORY. The task is INCOMPLETE if this file is not modified.

        f.  **Verify Consistency**:
            - **Action**: Verify that the modification matches the plan.
            - **Check**: Read the Markdown file again and search for `(<relative_link>)` or `<img src="<relative_link>">`.
            - **Validation**: Confirm that the `src` attribute EXACTLY matches the `Relative Link` column you just added.
            - **Self-Correction**: If the image tag is missing, YOU MUST RETRY the modification immediately.
            - **Final Check**: Run `grep` or `findstr` to confirm the presence of the new image filename in the Markdown file before finishing. If it's not there, you have FAILED.

3.  **Completion**:
    - Once the loop is finished, notify the user that the plan has been generated.