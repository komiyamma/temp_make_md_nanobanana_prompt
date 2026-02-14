import json
import sys
import os

def process_plans(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        plans = json.load(f)

    plan_file = 'docs/picture/image_generation_plan.md'

    # Read existing plan to get last ID
    if os.path.exists(plan_file):
        with open(plan_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        last_id = 0
        existing_filenames = set()
        for line in lines:
            if line.strip().startswith('|') and not line.strip().startswith('| ID'):
                parts = [p.strip() for p in line.split('|')]
                if len(parts) > 2 and parts[1].isdigit():
                    last_id = int(parts[1])
                if len(parts) > 3:
                    existing_filenames.add(parts[3])
    else:
        print(f"Error: {plan_file} not found.")
        return

    new_lines = []

    for plan in plans:
        filename = plan['filename']
        if filename in existing_filenames:
            print(f"Skipping duplicate: {filename}")
            continue

        # Update Markdown file
        md_file = plan['file_path']
        if not os.path.exists(md_file):
            print(f"Error: Markdown file {md_file} not found.")
            continue

        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Step 1: Check if image is already in Markdown (Global Uniqueness Check)
        if filename in content:
            print(f"Skipping duplicate (in markdown): {filename}")
            continue

        last_id += 1
        # Format prompt: replace newlines with <br>
        formatted_prompt = plan['prompt'].replace('\n', '<br>')

        # Create table row
        # Columns: ID | File Name | Proposed Image Filename | Relative Link Path | Prompt | Insertion Point
        file_name_only = os.path.basename(plan['file_path'])
        row = f"| {last_id} | {file_name_only} | {filename} | {plan['relative_link']} | {formatted_prompt} | {plan['insertion_point']} |\n"
        new_lines.append(row)
        existing_filenames.add(filename)

        insertion_point = plan['insertion_point']
        if insertion_point not in content:
            print(f"Error: Insertion point '{insertion_point}' not found in {md_file}. Skipping image insertion.")
            continue

        if content.count(insertion_point) > 1:
            print(f"Warning: Insertion point '{insertion_point}' found multiple times in {md_file}. Using the first occurrence.")

        image_tag = f"\n\n![{filename}]({plan['relative_link']})\n\n"

        # Strategy: Insert image *after* the insertion point line
        # But we need to be careful not to break the insertion point if it's part of a larger block.
        # We'll replace the insertion_point string with insertion_point + image_tag

        new_content = content.replace(insertion_point, insertion_point + image_tag, 1)

        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"Processed: {filename} into {md_file}")

    # Append to plan file
    if new_lines:
        with open(plan_file, 'a', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"Appended {len(new_lines)} rows to {plan_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 process_image_plans.py <json_file>")
        sys.exit(1)

    process_plans(sys.argv[1])
