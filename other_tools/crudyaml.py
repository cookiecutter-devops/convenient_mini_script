#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import argparse
import errno
import io
import json
import os
import sys
import yaml
from collections import OrderedDict

try:
    text_type = unicode
except NameError:
    text_type = str

'''
python crudyaml.py /etc/bingo/bingo.yaml get databases
python crudyaml.py /etc/bingo/bingo.yaml set databases.nova "dm://nova:Aa123456@172.16.131.11:25236"
'''


class OrderedLoader(yaml.SafeLoader):
    pass


class OrderedDumper(yaml.SafeDumper):
    pass


def ordered_mapping(loader, node):
    loader.flatten_mapping(node)
    return OrderedDict(loader.construct_pairs(node))


def represent_ordered_dict(dumper, data):
    return dumper.represent_dict(data.items())


OrderedLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    ordered_mapping
)

OrderedDumper.add_representer(
    OrderedDict,
    represent_ordered_dict
)


def write_stdout(value):
    if not isinstance(value, text_type):
        value = value.decode("utf-8")

    sys.stdout.write(value + u"\n")


def write_stderr(value):
    if not isinstance(value, text_type):
        value = value.decode("utf-8")

    sys.stderr.write(value + u"\n")


def json_to_yaml(data):
    result = yaml.dump(data, Dumper=OrderedDumper, allow_unicode=True, default_flow_style=False)
    if not isinstance(result, text_type):
        result = result.decode("utf-8")

    return result


def parse_value(value):
    try:
        return yaml.load(value, Loader=OrderedLoader)
    except yaml.YAMLError:
        return value


class JsonHandler(object):

    def __init__(self, data):
        self.data = data or OrderedDict()

    def dump(self):
        return json.dumps(self.data, indent=2, ensure_ascii=False)

    def load(self, data):
        self.data = json.loads(data)

    def _get_parent(self, key, create=False):
        parts = key.split(".")

        if len(parts) == 1:
            return self.data, parts[0]

        current = self.data

        for part in parts[:-1]:
            if part not in current:
                if not create:
                    return None, parts[-1]

                current[part] = OrderedDict()

            if not isinstance(current[part], dict):
                raise TypeError("error must dict type".format(part))

            current = current[part]

        return current, parts[-1]

    def get_value(self, key):
        data = self.data

        for part in key.split("."):
            if not isinstance(data, dict) or part not in data:
                return None

            data = data[part]

        return data

    def set_value(self, key, value):
        parent, last_key = self._get_parent(key, create=True)
        if parent is None:
            raise KeyError(key)

        parent[last_key] = value
        return value

    def delete_key(self, key):
        parent, last_key = self._get_parent(key, create=False)

        if parent is None or last_key not in parent:
            return None

        return parent.pop(last_key)

    def get_all_keys(self):
        return list(self.data.keys())

    def get_all_values(self):
        return list(self.data.values())

    def get_all_items(self):
        return list(self.data.items())


def parse_args():
    parser = argparse.ArgumentParser(description="YAML CRUD tool")
    parser.add_argument("yaml_file", type=str, help="Path to the YAML file")
    parser.add_argument("action", choices=["get", "set", "delete", "get_all_keys", "get_all_values", "get_all_items", ],
                        help="Action to perform")
    # 支持：set databases.nova "value"
    parser.add_argument("key", nargs="?", help="Key or nested key, for example databases.nova")
    parser.add_argument("value", nargs="?", help="Value to set")
    # 同时兼容：--key databases.nova --value "value"
    parser.add_argument("--key", dest="key_option", help="Key to use for the action")
    parser.add_argument("--value", dest="value_option", help="Value to use for the action")
    return parser.parse_args()


def load_yaml_file(filename):
    with io.open(filename, "r", encoding="utf-8") as f:
        return yaml.load(f, Loader=OrderedLoader) or OrderedDict()


def save_yaml_file(filename, data):
    content = json_to_yaml(data)
    with io.open(filename, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    args = parse_args()

    key = args.key_option or args.key

    if args.value_option is not None:
        value = args.value_option
    else:
        value = args.value

    if args.action in ("get", "set", "delete") and not key:
        write_stderr(u"错误：该操作需要提供 key")
        return 1

    if args.action == "set" and value is None:
        write_stderr(u"错误: set 操作需要提供 value")
        return 1

    try:
        if not os.path.isfile(args.yaml_file):
            write_stderr(u"文件不存在：{}".format(args.yaml_file))
            return 1

        data = load_yaml_file(args.yaml_file)

        if not isinstance(data, dict):
            write_stderr(u"错误: YAML 顶层结构必须是字典")
            return 1

        json_handler = JsonHandler(data)

        if args.action == "get":
            result = json_handler.get_value(key)

            if result is None:
                write_stderr(u"错误：配置项不存在：{}".format(key))
                return 1

            output = json.dumps(result, ensure_ascii=False, indent=2)

            write_stdout(output)
            return 0

        elif args.action == "set":
            parsed_value = parse_value(value)
            json_handler.set_value(key, parsed_value)
            save_yaml_file(args.yaml_file, json_handler.data)
            return 0

        elif args.action == "delete":
            result = json_handler.delete_key(key)

            if result is None:
                write_stderr(u"错误：配置项不存在：{}".format(key))
                return 1

            save_yaml_file(args.yaml_file, json_handler.data)
            return 0

        elif args.action == "get_all_keys":
            output = json.dumps(json_handler.get_all_keys(), ensure_ascii=False, indent=2)

            write_stdout(output)
            return 0

        elif args.action == "get_all_values":
            output = json.dumps(json_handler.get_all_values(), ensure_ascii=False, indent=2)

            write_stdout(output)
            return 0

        elif args.action == "get_all_items":
            output = json.dumps(json_handler.get_all_items(), ensure_ascii=False, indent=2)

            write_stdout(output)
            return 0

    except IOError as e:
        if getattr(e, "errno", None) == errno.ENOENT:
            write_stderr(u"文件不存在：{}".format(args.yaml_file))
        else:
            write_stderr(u"文件操作失败：{}".format(e))

        return 1

    except yaml.YAMLError as e:
        write_stderr(u"YAML 解析失败：{}".format(e))
        return 1

    except Exception as e:
        write_stderr(u"操作失败：{}".format(e))
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
