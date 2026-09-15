#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JSON路径查询工具

example:
data.json
{
  "name": "bingo",
  "databases": {
    "nova": {
      "host": "127.0.0.1",
      "port": 25236
    },
    "neutron": {
      "host": "127.0.0.2"
    }
  },
  "users": [
    {
      "name": "tom",
      "age": 18
    },
    {
      "name": "jack",
      "age": 20
    }
  ]
}

python3 json-path.py data.json /name
python3 json-path.py data.json /databases/nova/host
python3 json-path.py data.json /users/0/name
"""

import json
import sys

def query(data, path):
    parts = path.strip('/').split('/')
    current = data
    for part in parts:
        if not part:
            continue
        if isinstance(current, dict):
            current = current.get(part)
        elif isinstance(current, list):
            try:
                current = current[int(part)]
            except (ValueError, IndexError):
                return None
        else:
            return None
        if current is None:
            return None
    return current

if __name__ == "__main__":
    data = json.load(open(sys.argv[1]))
    path = sys.argv[2] if len(sys.argv) > 2 else "/"
    result = query(data, path)
    print(json.dumps(result, indent=2, ensure_ascii=False) if result else "null")
