import argparse
import json
import os
import sys

def main():
    parser = argparse.ArgumentParser(description='Append an image plan to the markdown table.')
    parser.add_argument('--from-json', required=True, help='Path to the JSON payload file.')
    args = parser.parse_args()

    with open(args.from_json, 'r', encoding='utf-8') as f:
        payload = json.load(f)

    # Validate payload
    required_keys = ['filename', 'proposed_filename', 'relative_link', 'prompt', 'insertion_point']
    for key in required_keys:
        if key not in payload:
            print(f"Error: Missing key '{key}' in payload.")
            sys.exit(1)

    plan_file = 'docs/picture/image_generation_plan.md'

    # Check if plan file exists, if not create it with header
    if not os.path.exists(plan_file):
        os.makedirs(os.path.dirname(plan_file), exist_ok=True)
        with open(plan_file, 'w', encoding='utf-8') as f:
            f.write('| ID | File Name | Proposed Image Filename | Relative Link Path | Prompt | Insertion Point |\n')
            f.write('|---|---|---|---|---|---|\n')

    # Read existing lines to determine next ID
    with open(plan_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    last_id = 0
    for line in reversed(lines):
        line = line.strip()
        if not line.startswith('|'):
            continue
        parts = [p.strip() for p in line.split('|')]
        # Filter empty strings from split
        parts = [p for p in parts if p]

        if len(parts) >= 1 and parts[0].isdigit():
            last_id = int(parts[0])
            break

    next_id = last_id + 1

    # Format fields
    filename = payload['filename']
    proposed_filename = payload['proposed_filename']
    relative_link = payload['relative_link']
    # Convert newlines to <br> for prompt
    prompt = payload['prompt'].replace('\n', '<br>')
    insertion_point = payload['insertion_point'].replace('\n', ' ') # Flatten insertion point just in case

    # Construct new row
    new_row = f"| {next_id} | {filename} | {proposed_filename} | {relative_link} | {prompt} | {insertion_point} |\n"

    # Append to file
    with open(plan_file, 'a', encoding='utf-8') as f:
        f.write(new_row)

    print(f"Successfully appended plan ID {next_id} for {filename}")

if __name__ == '__main__':
    main()
