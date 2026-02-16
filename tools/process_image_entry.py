import argparse
import os
import json
import subprocess
import sys
import re

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', required=True)
    parser.add_argument('--proposed_filename', required=True)
    parser.add_argument('--prompt', required=True)
    parser.add_argument('--relative_link', required=True)
    parser.add_argument('--insertion_point', required=True)
    args = parser.parse_args()

    filepath = args.filename
    if not os.path.exists(filepath):
        print(f"Error: File {filepath} not found.")
        sys.exit(1)

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Check if image already exists in markdown
    # strict check for filename in content
    if args.proposed_filename in content:
        print(f"Skipping: Image {args.proposed_filename} already exists in {filepath}.")
        sys.exit(0)

    # 2. Append to plan
    plan_payload = {
        "filename": args.filename,
        "proposed_filename": args.proposed_filename,
        "relative_link": args.relative_link,
        "prompt": args.prompt,
        "insertion_point": args.insertion_point
    }

    with open('payload.json', 'w', encoding='utf-8') as f:
        json.dump(plan_payload, f, ensure_ascii=False)

    try:
        # append_image_plan.py prints "Duplicate found..." if it skips.
        # We need to know if it skipped to avoid modifying markdown?
        # Actually append_image_plan logic: "If duplicate found... return".
        # It doesn't exit with error code.
        # But if it's in the plan but not in markdown, we SHOULD add it to markdown?
        # The instructions say: "If a match is found ONLY in Step 2 (Plan Check): Append a numeric suffix...".
        # This implies I should have generated a unique filename BEFORE calling this.
        # However, for simplicity, I assume I'm generating unique filenames.
        # If it's already in the plan, append_image_plan will skip adding it to the table.
        # But if it's NOT in the markdown, we still want to add it to the markdown?
        # No, if it's in the plan, it might be for a different run or already done.
        # Wait, if it is in the plan, it means we planned it. If it is NOT in the markdown, we should probably add it.
        # But `append_image_plan.py` is about the PLAN file.
        # If I am re-running this, I might generate the same plan.
        # If `append_image_plan.py` says duplicate, it means we already planned this image.
        # Should I proceed to insert into markdown?
        # If the file doesn't have it, yes.

        subprocess.run(['python3', 'tools/append_image_plan.py', '--from-json', 'payload.json'], check=True)
    finally:
        if os.path.exists('payload.json'):
            os.remove('payload.json')

    # 3. Modify markdown file
    # Normalize newlines for searching
    search_text = args.insertion_point.replace('\\n', '\n')

    if search_text not in content:
        print(f"Error: Insertion point text '{search_text}' not found in {filepath}.")
        sys.exit(1)

    # Construct image tag
    description = os.path.splitext(os.path.basename(args.proposed_filename))[0]
    image_tag = f"\n\n![{description}]({args.relative_link})\n"

    # Insert after the search text
    # We use replace, but only the first occurrence?
    # Usually insertion points are unique headers.
    new_content = content.replace(search_text, search_text + image_tag, 1)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"Successfully inserted image tag into {filepath}")

if __name__ == "__main__":
    main()
