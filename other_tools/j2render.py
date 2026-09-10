#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, with_statement, print_function

import os
import sys
import io
import json
import argparse
import logging

logger = logging.getLogger("j2render")


def parse_j2(template_text, **kwargs):
    from jinja2 import Template
    template = Template(template_text)
    return template.render(**kwargs)


def parse_j2_file(template_file, **kwargs):
    with io.open(template_file, 'r', encoding='utf-8') as f:
        return parse_j2(f.read(), **kwargs)


def parse_j2_file_to_file(template_file, output_file, **kwargs):
    with io.open(output_file, 'w', encoding='utf-8') as f:
        f.write(parse_j2_file(template_file, **kwargs))


def _load_yaml(text):
    """
    变量加载
    :param text:
    :return:
    """
    try:
        import yaml
    except ImportError:
        raise RuntimeError(
            "Parsing YAML requires PyYAML. Install it: pip install pyyaml")
    return yaml.safe_load(text)


def load_vars_from_file(path):
    """
    从文件加载变量，支持 .yaml/.yml/.json。
    返回 dict（空文件返回 {}）。
    """
    if not os.path.exists(path):
        raise RuntimeError("Vars file not found: %s" % path)

    with io.open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    ext = os.path.splitext(path)[1].lower()
    if ext == ".json":
        data = json.loads(text) if text.strip() else {}
    elif ext in (".yaml", ".yml"):
        data = _load_yaml(text) or {}
    else:
        # 未知后缀：先试 json，再试 yaml
        try:
            data = json.loads(text) if text.strip() else {}
        except ValueError:
            data = _load_yaml(text) or {}

    if not isinstance(data, dict):
        raise RuntimeError(
            "Vars file %s must contain a mapping (dict), got: %s"
            % (path, type(data).__name__))
    return data


def parse_extra_var(item):
    """
    解析单个 -e 参数，返回 dict。

    支持三种形式（模仿 ansible）：
      1) @file.yaml / @file.json     -> 从文件加载
      2) key=value                   -> 内联单变量
      3) '{"k": "v"}' 或 'k: v'      -> 内联 json/yaml
    另外为了方便，直接给一个存在的文件路径也当作文件处理。
    """
    if isinstance(item, bytes):
        item = item.decode('utf-8')
    # 形式1：@file
    if item.startswith("@"):
        return load_vars_from_file(item[1:])

    # 直接是个存在的文件路径
    if os.path.isfile(item):
        return load_vars_from_file(item)

    # 形式2：key=value（且不像 json/yaml 结构）
    if "=" in item and not item.strip().startswith(("{", "[")):
        key, _, value = item.partition("=")
        key = key.strip()
        value = value.strip()
        # 尝试把 value 解析成 json（数字/布尔/列表等），失败则当字符串
        try:
            value = json.loads(value)
        except ValueError:
            pass
        return {key: value}

    # 形式3：内联 json / yaml
    text = item.strip()
    try:
        data = json.loads(text)
    except ValueError:
        data = _load_yaml(text)

    if not isinstance(data, dict):
        raise RuntimeError("Inline extra-var must be a mapping: %s" % item)
    return data


def build_context(extra_vars_list):
    """
    合并多个 -e 的结果。后面的覆盖前面的（与 ansible 行为一致）。
    """
    context = {}
    for item in extra_vars_list or []:
        data = parse_extra_var(item)
        context.update(data)
    return context


def build_parser():
    parser = argparse.ArgumentParser(
        description="Render a Jinja2 (.j2) template like Ansible 'template'.",
        epilog=(
            "Examples:\n"
            "  j2render.py conf.j2 -e @vars.yaml\n"
            "  j2render.py conf.j2 -e @a.yaml -e @b.json -o out.conf\n"
            "  j2render.py conf.j2 -e name=nginx -e port=8080\n"
            "  j2render.py conf.j2 -e '{\"env\":\"prod\"}'\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("template", help="Path to the .j2 template file")
    parser.add_argument(
        "-e", "--extra-vars", action="append", default=[], metavar="VARS",
        help="Variables: @file.yaml/@file.json, key=value, or inline json/yaml. "
             "Can be used multiple times (later ones override earlier).")
    parser.add_argument(
        "-o", "--output", default=None,
        help="Output file (default: stdout)")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Verbose logging")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s")

    if not os.path.isfile(args.template):
        logger.error("Template file not found: %s", args.template)
        return 2

    try:
        context = build_context(args.extra_vars)
        logger.debug("Render context: %s", context)

        result = parse_j2_file(args.template, **context)

        if args.output:
            with io.open(args.output, 'w', encoding='utf-8') as f:
                f.write(result)
            logger.info("Rendered -> %s", args.output)
        else:
            _write_stdout(result)
        return 0
    except Exception as e:  # noqa: BLE001
        logger.error("%s", e, exc_info=args.verbose)
        return 1


def _write_stdout(text):
    if not text.endswith(u"\n"):
        text = text + u"\n"
    if sys.version_info[0] < 3:
        sys.stdout.write(text.encode('utf-8'))
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    sys.exit(main())
