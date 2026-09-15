#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import argparse

def load_env(file_path):
    env_vars = {}
    with open(file_path, 'r') as file:
        for line in file:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                env_vars[key] = value
    return env_vars


def render_yaml(env_vars, yaml_file_path):
    with open(yaml_file_path, 'r') as file:
        content = file.read()

    for key, value in env_vars.items():
        content = re.sub(r'\{\{\s*' + re.escape(key) + r'\s*\}\}', value, content)

    with open(yaml_file_path, 'w') as file:
        file.write(content)


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('env_file_path', help='Path to the environment file')
    parser.add_argument('yaml_file_paths', nargs='+', help='Paths to the YAML files')
    return parser.parse_args()


if __name__ == "__main__":
    args = arg_parser()
    env_file_path = args.env_file_path
    yaml_file_paths = args.yaml_file_paths

    env_vars = load_env(env_file_path)

    for yaml_file_path in yaml_file_paths:
        render_yaml(env_vars, yaml_file_path)
