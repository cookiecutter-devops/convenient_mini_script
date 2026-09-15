#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import yaml

"""
合并多个yaml文件,将相同key的值合并到一个列表中
"""


def merge(files, output):
    result = {}

    for filename in files:
        with open(filename, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        for key, value in data.items():
            if key not in result:
                result[key] = value
                continue

            old = result[key]
            if not isinstance(old, list):
                old = [old]

            if isinstance(value, list):
                old.extend(value)
            else:
                old.append(value)

            result[key] = old

    with open(output, "w", encoding="utf-8") as f:
        yaml.safe_dump(result,f,allow_unicode=True,default_flow_style=False,sort_keys=False)

    print("Merged {} files -> {}".format(len(files), output))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge multiple YAML files")
    parser.add_argument( "files", nargs="+", help="Input YAML files, the last argument is output file" )
    args = parser.parse_args()

    merge(args.files[:-1], args.files[-1])
