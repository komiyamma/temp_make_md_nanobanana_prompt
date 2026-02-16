import json
import subprocess
import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tools/execute_plan.py <json_list_file>")
        sys.exit(1)

    json_list_file = sys.argv[1]
    with open(json_list_file, 'r') as f:
        data = json.load(f)

    # Ensure data is a list
    if not isinstance(data, list):
        print("Error: JSON file must contain a list of objects.")
        sys.exit(1)

    for item in data:
        # Create temp payload
        temp_payload = 'temp_payload.json'
        with open(temp_payload, 'w') as f:
            json.dump(item, f)

        # Call append_image_plan.py
        cmd = ["python3", "tools/append_image_plan.py", "--from-json", temp_payload]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Error appending {item.get('proposed_filename', 'unknown')}:")
            print(result.stderr)
        else:
            print(f"Successfully appended {item.get('proposed_filename', 'unknown')}")
            print(result.stdout)

        # Remove temp payload
        if os.path.exists(temp_payload):
            os.remove(temp_payload)

if __name__ == "__main__":
    main()
