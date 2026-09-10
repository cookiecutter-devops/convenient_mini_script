#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
批量渲染 Jinja2 模板

pip install "Jinja2==3.0.3" "PyYAML==5.4.1"


python3.6 render_templates.py \
    --template-dir services \
    --vars-file ../kolla/ansible/group_vars/all.yml \
    --output-dir output \
    --force

'''

import argparse
import os
import sys
import tempfile
from pathlib import Path

import yaml
from jinja2 import (
    Environment,
    FileSystemLoader,
    StrictUndefined,
    TemplateError,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="批量渲染 Jinja2 模板"
    )

    parser.add_argument("-t", "--template-dir", required=True)
    parser.add_argument("-v", "--vars-file", required=True)
    parser.add_argument("-o", "--output-dir", required=True)

    parser.add_argument(
        "-p",
        "--pattern",
        default="**/*.j2",
        help="模板匹配模式，默认：**/*.j2",
    )

    parser.add_argument(
        "--template-suffix",
        default=".j2",
        help="模板后缀，默认：.j2",
    )

    parser.add_argument(
        "--output-suffix",
        default="",
        help="输出文件追加后缀",
    )

    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="文件编码，默认：utf-8",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="覆盖已有文件",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只预览，不写文件",
    )

    parser.add_argument(
        "--strict",
        action="store_true",
        help="变量不存在时直接报错",
    )

    parser.add_argument(
        "--keep-suffix",
        action="store_true",
        help="保留模板后缀",
    )

    return parser.parse_args()


def load_variables(path, encoding):
    if not os.path.isfile(path):
        raise RuntimeError("变量文件不存在：{}".format(path))

    try:
        with open(path, "r", encoding=encoding) as file_obj:
            data = yaml.safe_load(file_obj)
    except yaml.YAMLError as exc:
        raise RuntimeError(
            "YAML 文件格式错误：{}\n{}".format(path, exc)
        )

    if data is None:
        return {}

    if not isinstance(data, dict):
        raise RuntimeError(
            "变量文件顶层必须是字典：{}".format(path)
        )

    return data


def build_output_path(
    template_path,
    template_dir,
    output_dir,
    template_suffix,
    output_suffix,
    keep_suffix,
):
    relative_path = template_path.relative_to(template_dir)

    if not keep_suffix:
        if not relative_path.name.endswith(template_suffix):
            raise RuntimeError(
                "模板文件后缀不正确：{}".format(template_path)
            )

        output_name = relative_path.name[:-len(template_suffix)]
        relative_path = relative_path.with_name(output_name)

    if output_suffix:
        relative_path = relative_path.with_name(
            relative_path.name + output_suffix
        )

    return output_dir / relative_path


def atomic_write(path, content, encoding):
    if not path.parent.exists():
        path.parent.mkdir(parents=True)

    fd, temp_name = tempfile.mkstemp(
        prefix=".{0}.".format(path.name),
        dir=str(path.parent),
        text=True,
    )

    try:
        with os.fdopen(
            fd,
            "w",
            encoding=encoding,
            newline="",
        ) as file_obj:
            file_obj.write(content)
            file_obj.flush()
            os.fsync(file_obj.fileno())

        os.replace(temp_name, str(path))

    except Exception:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise


def render_templates(args):
    template_dir = Path(args.template_dir).resolve()
    output_dir = Path(args.output_dir).resolve()
    vars_file = Path(args.vars_file).resolve()

    if not template_dir.is_dir():
        raise RuntimeError(
            "模板目录不存在：{}".format(template_dir)
        )

    variables = load_variables(
        str(vars_file),
        args.encoding,
    )

    environment_options = {
        "loader": FileSystemLoader(str(template_dir)),
        "autoescape": False,
        "keep_trailing_newline": True,
    }

    if args.strict:
        environment_options["undefined"] = StrictUndefined

    environment = Environment(**environment_options)

    template_files = sorted(
        path
        for path in template_dir.glob(args.pattern)
        if path.is_file()
    )

    if not template_files:
        print(
            "未找到模板文件：{} / {}".format(
                template_dir,
                args.pattern,
            ),
            file=sys.stderr,
        )
        return 0

    count = 0

    for template_path in template_files:
        relative_path = template_path.relative_to(template_dir)
        template_name = relative_path.as_posix()

        output_path = build_output_path(
            template_path,
            template_dir,
            output_dir,
            args.template_suffix,
            args.output_suffix,
            args.keep_suffix,
        )

        print(
            "{} -> {}".format(
                template_path,
                output_path,
            )
        )

        if output_path.exists() and not args.force:
            raise RuntimeError(
                "输出文件已存在，如需覆盖请使用 --force：{}".format(
                    output_path
                )
            )

        try:
            template = environment.get_template(template_name)
            rendered = template.render(**variables)
        except TemplateError as exc:
            raise RuntimeError(
                "渲染模板失败：{}\n{}".format(
                    template_path,
                    exc,
                )
            )

        if not args.dry_run:
            atomic_write(
                output_path,
                rendered,
                args.encoding,
            )

        count += 1

    if args.dry_run:
        print("预览完成，共处理 {} 个模板".format(count))
    else:
        print("生成完成，共处理 {} 个模板".format(count))

    return 0


def main():
    args = parse_args()
    return render_templates(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RuntimeError as exc:
        print("错误：{}".format(exc), file=sys.stderr)
        sys.exit(1)
