import os

PLAN_FILE = "docs/picture/image_generation_plan.md"

def fix_plan_file():
    if not os.path.exists(PLAN_FILE):
        print(f"{PLAN_FILE} not found.")
        return

    with open(PLAN_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    header_lines = [
        "# Image Generation Plan\n",
        "| ID | Target MD File Name | Proposed Image Filename | Relative Link Path | Prompt | Insertion Point |\n",
        "|---|---|---|---|---|---|\n"
    ]

    new_lines = []
    # Keep the first occurrence of the header block
    header_found = False

    # Simple state machine
    # 0: seeking first header
    # 1: found first header, now seeking content

    # Or simpler: Just keep the first 3 lines if they match the header, and filter out any subsequent lines that match the header lines.

    # Let's trust the content structure:
    # We want to keep lines[0], lines[1], lines[2].
    # And filter out any lines > 2 that match lines[0], lines[1], or lines[2].

    if len(lines) < 3:
        print("File too short to fix.")
        return

    # Assuming the file starts with the header (even if duplicated)
    # The first 3 lines *should* be the header.
    new_lines.extend(lines[:3])

    for i in range(3, len(lines)):
        line = lines[i]
        if line in header_lines:
            continue
        new_lines.append(line)

    with open(PLAN_FILE, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print(f"Fixed {PLAN_FILE}. Removed duplicate headers.")

if __name__ == "__main__":
    fix_plan_file()
