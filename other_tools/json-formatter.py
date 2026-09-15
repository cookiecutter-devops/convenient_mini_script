#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys

def format_json(input_str, indent=2):
    try:
        parsed = json.loads(input_str)
        return json.dumps(parsed, indent=indent, ensure_ascii=False)
    except json.JSONDecodeError as e:
        return f"Error: {e}"

if __name__ == "__main__":
    data = sys.stdin.read() if not sys.argv[1:] else open(sys.argv[1]).read()
    print(format_json(data))




# import json, sys

# def format_json_file(path):
#     with open(path, 'r', encoding='utf-8') as f:
#         data = json.load(f)
#     with open(path, 'w', encoding='utf-8') as f:
#         json.dump(data, f, ensure_ascii=False, indent=2)
#     print(f"Formatted: {path}")

# if __name__ == '__main__':
#     for p in sys.argv[1:]:
#         format_json_file(p)



# import json
# import sys

# def format_json(filepath, indent=2):
#     with open(filepath, 'r', encoding='utf-8') as f:
#         data = json.load(f)
#     with open(filepath, 'w', encoding='utf-8') as f:
#         json.dump(data, f, indent=indent, ensure_ascii=False)

# if __name__ == '__main__':
#     if len(sys.argv) < 2:
#         print("用法: python json-formatter.py <文件路径> [缩进空格数]")
#         sys.exit(1)
#     indent = int(sys.argv[2]) if len(sys.argv) > 2 else 2
#     format_json(sys.argv[1], indent)
