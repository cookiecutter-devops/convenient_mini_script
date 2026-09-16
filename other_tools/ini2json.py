#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser
import json
import os

"""
INI文件转换为JSON文件
"""



if len(sys.argv) < 2:
    print("Usage: %s <ini_file>" % sys.argv[0])
    sys.exit(1)

ini_file = sys.argv[1]
if not os.path.isfile(ini_file):
    print("File not found: %s" % ini_file)
    sys.exit(1)

conf = ConfigParser.ConfigParser()
conf.optionxform = str  # preserve case of keys
conf.read(ini_file)

result = []
for section in conf.sections():
    for key, value in conf.items(section, raw=True):
        result.append({'section': section, 'key': key, 'value': value})

# print(json.dumps(result))
print(json.dumps(result, indent=2, ensure_ascii=False))
