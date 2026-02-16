import argparse
import os
import re
import json

def get_next_id(filepath):
    if not os.path.exists(filepath):
        return 1

    last_id = 0
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

    return last_id + 1

def append_row(filepath, filename, proposed_filename, relative_link, prompt, insertion_point):
    next_id = get_next_id(filepath)

    # Sanitize inputs for markdown table
    # Use double backslash to escape pipe char in replacement string for regex, but here we are using string replace
    # In python string literal, \| is just | unless escaped. But we want literal \| in the output.
    # So we need to write replace('|', r'\|')

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

    args = parser.parse_args()

    plan_file = 'docs/picture/image_generation_plan.md'

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
