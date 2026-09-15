#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
正则表达式测试工具
"""
import re
import sys

def test_regex(pattern, text):
    matches = re.findall(pattern, text)
    return {"pattern": pattern, "matches": matches, "count": len(matches)}

if __name__ == "__main__":
    result = test_regex(sys.argv[1], sys.argv[2])
    print(f"Pattern: {result['pattern']}")
    print(f"Matches: {result['count']}")
    for m in result["matches"]:
        print(f"  - {m}")
