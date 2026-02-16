import argparse
import os
import re
import json

def get_next_id_and_check_duplicate(filepath, proposed_filename):
    if not os.path.exists(filepath):
        return 1, False

    last_id = 0
    duplicate_found = False

    # Sanitize proposed_filename for comparison with file content which is sanitized
    sanitized_filename = proposed_filename.replace('|', r'\|') if proposed_filename else ''

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if not line.startswith('|'):
                continue

            # Skip separator line like |---|---|
            if '---' in line:
                continue

            parts = [p.strip() for p in line.split('|')]
            if len(parts) > 1:
                try:
                    # parts[0] is empty string before first |, parts[1] is ID
                    current_id = int(parts[1])
                    if current_id > last_id:
                        last_id = current_id
                except ValueError:
                    continue

            if len(parts) > 3:
                existing_filename = parts[3].strip()
                if existing_filename == sanitized_filename:
                    duplicate_found = True

    return last_id + 1, duplicate_found

def append_row(filepath, filename, proposed_filename, relative_link, prompt, insertion_point):
    next_id, duplicate_found = get_next_id_and_check_duplicate(filepath, proposed_filename)

    if duplicate_found:
        print(f"Duplicate found: {proposed_filename}. Skipping append.")
        return

    # Sanitize inputs for markdown table
    if filename:
        filename = filename.replace('|', r'\|')
    if proposed_filename:
        proposed_filename = proposed_filename.replace('|', r'\|')
    if relative_link:
        relative_link = relative_link.replace('|', r'\|')

    if prompt:
        prompt = prompt.replace('\n', '<br>').replace('|', r'\|')
    if insertion_point:
        insertion_point = insertion_point.replace('\n', ' ').replace('|', r'\|')

    row = f"| {next_id} | {filename} | {proposed_filename} | {relative_link} | {prompt} | {insertion_point} |\n"

    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(row)

    print(f"Appended ID {next_id}: {proposed_filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Append image plan row.')
    parser.add_argument('--filename', help='Markdown filename')
    parser.add_argument('--proposed_filename', help='Proposed image filename')
    parser.add_argument('--relative_link', help='Relative link path')
    parser.add_argument('--prompt', help='Image generation prompt')
    parser.add_argument('--insertion_point', help='Insertion point text')
    parser.add_argument('--from-json', help='Load arguments from a JSON file')
    parser.add_argument('--plan-file', help='Path to plan file', default='docs/picture/image_generation_plan.md')

    args = parser.parse_args()

    plan_file = args.plan_file

    if args.from_json:
        with open(args.from_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
            append_row(plan_file,
                       data.get('filename', ''),
                       data.get('proposed_filename', ''),
                       data.get('relative_link', ''),
                       data.get('prompt', ''),
                       data.get('insertion_point', ''))
    else:
        if not all([args.filename, args.proposed_filename, args.relative_link, args.prompt, args.insertion_point]):
             parser.error("All arguments are required unless --from-json is used.")

        append_row(plan_file, args.filename, args.proposed_filename, args.relative_link, args.prompt, args.insertion_point)
