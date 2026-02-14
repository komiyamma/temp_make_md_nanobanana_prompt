import sys
import os

PLAN_FILE = 'docs/picture/image_generation_plan.md'

def get_next_id():
    if not os.path.exists(PLAN_FILE):
        return 1
    with open(PLAN_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Filter for table rows (lines starting with | and containing |)
    table_lines = [l for l in lines if l.strip().startswith('|') and '|' in l]

    if len(table_lines) < 2:
        # Only header or nothing
        return 1

    last_line = table_lines[-1]
    try:
        parts = [p.strip() for p in last_line.split('|')]
        # parts[0] is usually empty string if line starts with |
        # parts[1] should be ID
        if len(parts) > 1 and parts[1].isdigit():
             return int(parts[1]) + 1
        return 1
    except Exception:
        return 1

def main():
    if len(sys.argv) < 5:
        print("Usage: python3 process_image_plans.py <markdown_file> <image_filename> <anchor_text> <insertion_mode>")
        sys.exit(1)

    markdown_file = sys.argv[1]
    image_filename = sys.argv[2]
    anchor_text = sys.argv[3]
    insertion_mode = sys.argv[4]

    # Read prompt from stdin
    prompt = sys.stdin.read().strip()
    if not prompt:
        print("ERROR: No prompt provided via stdin.")
        sys.exit(1)

    # Check Plan File Uniqueness
    if os.path.exists(PLAN_FILE):
        with open(PLAN_FILE, 'r', encoding='utf-8') as f:
            plan_content = f.read()
            if image_filename in plan_content:
                print(f"SKIP: Image {image_filename} already in plan.")
                sys.exit(0)

    # Check Markdown File
    if not os.path.exists(markdown_file):
        print(f"ERROR: File {markdown_file} not found.")
        sys.exit(1)

    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()

    if image_filename in content:
        print(f"SKIP: Image {image_filename} already in {markdown_file}.")
        sys.exit(0)

    if anchor_text not in content:
        print(f"ERROR: Anchor '{anchor_text}' not found in {markdown_file}.")
        sys.exit(1)

    if content.count(anchor_text) > 1:
        print(f"ERROR: Anchor '{anchor_text}' appears {content.count(anchor_text)} times in {markdown_file}. Must be unique.")
        sys.exit(1)

    # Update Markdown
    image_tag = f"![{image_filename}](./picture/{image_filename})"
    new_content = ""

    if insertion_mode == 'before':
        new_content = content.replace(anchor_text, f"{image_tag}\n\n{anchor_text}")
    elif insertion_mode == 'after':
        new_content = content.replace(anchor_text, f"{anchor_text}\n\n{image_tag}")
    else:
         print(f"ERROR: Invalid insertion mode '{insertion_mode}'. Use 'before' or 'after'.")
         sys.exit(1)

    with open(markdown_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    # Append to Plan
    next_id = get_next_id()
    relative_link = f"./picture/{image_filename}"
    formatted_prompt = prompt.replace('\n', '<br>').replace('|', r'\|')

    row = f"| {next_id} | {os.path.basename(markdown_file)} | {image_filename} | {relative_link} | {formatted_prompt} | {anchor_text} |\n"

    with open(PLAN_FILE, 'a', encoding='utf-8') as f:
        # Check if file ends with newline
        if os.path.exists(PLAN_FILE) and os.path.getsize(PLAN_FILE) > 0:
             with open(PLAN_FILE, 'rb') as f_rb:
                 try:
                     f_rb.seek(-1, os.SEEK_END)
                     if f_rb.read(1) != b'\n':
                         f.write('\n')
                 except OSError:
                     pass
        f.write(row)

    print(f"SUCCESS: Added {image_filename} to plan and updated {markdown_file}")

if __name__ == "__main__":
    main()
