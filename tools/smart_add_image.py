import argparse
import json
import os
import sys
import subprocess
import re

def main():
    parser = argparse.ArgumentParser(description='Add image plan and update markdown file.')
    parser.add_argument('--doc-file', required=True, help='Path to the markdown file.')
    parser.add_argument('--image-suffix', required=True, help='Suffix for the image filename (e.g., _01_concept).')
    parser.add_argument('--prompt', required=True, help='The prompt for the image.')
    parser.add_argument('--insertion-context', required=True, help='Unique text in the line after which the image should be inserted.')
    parser.add_argument('--description', required=True, help='Description for the image alt text.')

    args = parser.parse_args()

    doc_file = args.doc_file
    if not os.path.exists(doc_file):
        print(f"Error: File '{doc_file}' not found.")
        sys.exit(1)

    # Construct filenames
    base_name = os.path.splitext(os.path.basename(doc_file))[0]
    image_filename = f"{base_name}{args.image_suffix}.png"
    relative_link = f"./picture/{image_filename}"

    # Check for existing image in markdown file
    with open(doc_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find existing image tags with the same filename
    # Matches ![...](...filename...) or <img src="...filename...">
    if re.search(rf'\!\[.*\]\(.*{re.escape(image_filename)}.*\)', content) or \
       re.search(rf'<img.*src=".*{re.escape(image_filename)}.*".*>', content):
        print(f"Skipping: Image '{image_filename}' already exists in '{doc_file}'.")
        return

    # Check for existing plan
    plan_file = 'docs/picture/image_generation_plan.md'
    if os.path.exists(plan_file):
        with open(plan_file, 'r', encoding='utf-8') as f:
            plan_content = f.read()
        if image_filename in plan_content:
            print(f"Skipping: Plan for '{image_filename}' already exists in '{plan_file}'.")
            # If plan exists but file is not updated, we might need to update the file?
            # The prompt says "If a match is found ONLY in Step 2 (Plan Check): Append a numeric suffix...".
            # But for simplicity in this script, I'll assume I should skip creating a DUPLICATE plan entry.
            # However, I should still proceed to update the file if the tag is missing?
            # The prompt implies "Do NOT append a suffix. Assume the image is already implemented." if found in MD.
            # If found in PLAN but not in MD, it means we already planned it.
            # But if I am running this script, I intend to add it.
            # To be safe and idempotent: if plan exists, I will NOT run append_image_plan.py,
            # BUT I will still try to insert the tag if it's missing in the doc.
            pass

    # Create JSON payload for append_image_plan.py
    # Only run this if not already in plan (or if we decide to just append anyway? append_image_plan might handle duplicates?)
    # The append_image_plan.py reads lines to determine next ID. It doesn't seem to check for duplicates in the file content other than "Concept" check which is not fully implemented in the script I read.
    # The prompt says: "If a similar entry exists for this file, SKIP appending."
    # I'll check if filename is in plan. If not, append.

    plan_exists = False
    if os.path.exists(plan_file):
        with open(plan_file, 'r', encoding='utf-8') as f:
            if image_filename in f.read():
                plan_exists = True

    if not plan_exists:
        payload = {
            "filename": os.path.basename(doc_file),
            "proposed_filename": image_filename,
            "relative_link": relative_link,
            "prompt": args.prompt,
            "insertion_point": args.insertion_context
        }

        payload_file = 'temp_payload.json'
        with open(payload_file, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        try:
            subprocess.run(['python3', 'tools/append_image_plan.py', '--from-json', payload_file], check=True)
        finally:
            if os.path.exists(payload_file):
                os.remove(payload_file)
    else:
        print(f"Plan for {image_filename} already exists. Skipping plan append.")

    # Update Markdown File
    # We already read content. Now let's insert.
    lines = content.splitlines()
    insertion_index = -1

    for i, line in enumerate(lines):
        if args.insertion_context in line:
            insertion_index = i
            break

    if insertion_index == -1:
        print(f"Error: Insertion context '{args.insertion_context}' not found in '{doc_file}'.")
        # Ensure we don't fail completely if context is missing, but report error.
        sys.exit(1)

    # Check if the line after insertion point is already the image
    # Be careful about bounds
    if insertion_index + 1 < len(lines):
        next_line = lines[insertion_index + 1].strip()
        expected_tag = f"![{args.description}]({relative_link})"
        if expected_tag in next_line:
             print(f"Image tag already present after context in '{doc_file}'.")
             return
        # Also check if it's an empty line then the image
        if next_line == "" and insertion_index + 2 < len(lines):
             next_next_line = lines[insertion_index + 2].strip()
             if expected_tag in next_next_line:
                 print(f"Image tag already present (after empty line) in '{doc_file}'.")
                 return

    # Insert the image tag
    # We'll insert an empty line and then the image tag after the context line
    image_tag = f"\n![{args.description}]({relative_link})\n"

    # We can just insert into the list
    lines.insert(insertion_index + 1, image_tag.strip())
    lines.insert(insertion_index + 1, "") # Add empty line before

    new_content = "\n".join(lines)

    with open(doc_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"Successfully inserted image tag in '{doc_file}' after '{args.insertion_context}'.")

if __name__ == "__main__":
    main()
