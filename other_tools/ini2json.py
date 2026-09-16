#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from __future__ import print_function
# import sys
# try:
#     import ConfigParser
# except ImportError:
#     import configparser as ConfigParser
# import json
# import os

# """
# INI文件转换为JSON文件
# """



# if len(sys.argv) < 2:
#     print("Usage: %s <ini_file>" % sys.argv[0])
#     sys.exit(1)

# ini_file = sys.argv[1]
# if not os.path.isfile(ini_file):
#     print("File not found: %s" % ini_file)
#     sys.exit(1)

# conf = ConfigParser.ConfigParser()
# conf.optionxform = str  # preserve case of keys
# conf.read(ini_file)

# result = []
# for section in conf.sections():
#     for key, value in conf.items(section, raw=True):
#         result.append({'section': section, 'key': key, 'value': value})

# # print(json.dumps(result))
# print(json.dumps(result, indent=2, ensure_ascii=False))

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import json
import os

try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser


def ini_to_json(filename):
    if not os.path.isfile(filename):
        raise IOError("File not found: {}".format(filename))

    config = ConfigParser.ConfigParser()
    config.optionxform = str  # 保留 key 原始大小写

    with open(filename, "r") as f:
        config.readfp(f)       # Python 2.7 / Python 3 均支持

    return [
        {
            "section": section,
            "key": key,
            "value": value
        }
        for section in config.sections()
        for key, value in config.items(section, raw=True)
    ]


def main():
    parser = argparse.ArgumentParser( description="Convert INI file to JSON" )
    parser.add_argument("ini_file", help="INI file path")
    args = parser.parse_args()

    try:
        result = ini_to_json(args.ini_file)
        print(json.dumps( result, indent=2, ensure_ascii=False ))
    except (IOError, ConfigParser.Error) as e:
        print("Error: {}".format(e))
        return 1

    return 0


if __name__ == "__main__":
    main()
