#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import subprocess
import sys

"""
git 工具函数
"""


def run_git(args, cwd=None):
    """执行 git 命令，返回 (返回码, stdout, stderr)。"""
    try:
        process = subprocess.Popen(
            ["git"] + args,
            cwd=cwd or os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        stdout, stderr = process.communicate()

        return (process.returncode, stdout.strip(), stderr.strip())
    except OSError as e:
        return -1, "", "Git is not installed or not in PATH: {}".format(e)


def status_summary(repo_path=None):
    """获取简洁的仓库状态摘要。"""
    code, output, error = run_git(["status", "--short"], repo_path)
    if code != 0:
        return "Error: {}".format(error)

    if not output:
        return "Clean working tree"

    staged = []
    unstaged = []
    untracked = []

    for line in output.splitlines():
        if len(line) < 2:
            continue

        if line.startswith("??"):
            untracked.append(line)
        else:
            if line[0] != " ":
                staged.append(line)
            if line[1] != " ":
                unstaged.append(line)

    result = []

    if staged:
        result.append("{} staged change(s)".format(len(staged)))

    if unstaged:
        result.append("{} unstaged change(s)".format(len(unstaged)))

    if untracked:
        result.append("{} untracked file(s)".format(len(untracked)))

    return ", ".join(result) or "Clean working tree"


def batch_commit(repo_path, pattern, message):
    """批量提交匹配模式的文件。"""
    code, _, error = run_git(["add", pattern], repo_path)

    if code != 0:
        print("Failed to stage: {}".format(error), file=sys.stderr)
        return False

    code, output, error = run_git(["diff", "--cached", "--name-only"], repo_path)

    if code != 0:
        print("Failed to check staged files: {}".format(error), file=sys.stderr)
        return False

    if not output:
        print("No files matched pattern: {}".format(pattern))
        return False

    code, _, error = run_git(["commit", "-m", message], repo_path)

    if code != 0:
        print("Commit failed: {}".format(error), file=sys.stderr)
        return False

    print("Committed {} file(s)".format(len(output.splitlines())))
    return True


def list_branches(repo_path=None):
    """列出所有本地分支。"""
    code, output, _ = run_git(["branch"], repo_path)

    if code != 0:
        return []

    return [line.strip() for line in output.splitlines() if line.strip()]


def cleanup_merged_branches(repo_path=None, target_branch="main", dry_run=True):
    """清理已合并到目标分支的本地分支。"""
    run_git(["fetch", "--prune"], repo_path)

    code, output, error = run_git(["branch", "--merged", target_branch], repo_path)

    if code != 0:
        print("Error: {}".format(error), file=sys.stderr)
        return []

    branches = []

    for line in output.splitlines():
        line = line.strip()

        if not line:
            continue

        # 删除当前分支前的 "* " 标记
        branch = line.lstrip("* ").strip()

        if branch != target_branch:
            branches.append(branch)

    if dry_run:
        for branch in branches:
            print("  [DRY RUN] Would delete: {}".format(branch))
    else:
        for branch in branches:
            code, _, error = run_git(["branch", "-d", branch], repo_path)

            if code == 0:
                print("  Deleted: {}".format(branch))
            else:
                print( "  Failed to delete {}: {}".format( branch, error ), file=sys.stderr )

    return branches


def commit_stats(repo_path=None, author=None):
    """获取提交统计信息。"""
    args = ["shortlog", "-sn", "--no-merges"]

    if author:
        args.extend(["--author", author])

    code, output, _ = run_git(args, repo_path)

    if code != 0:
        return {}

    stats = {}

    for line in output.splitlines():
        line = line.strip()

        if not line:
            continue

        parts = line.split(None, 1)

        if len(parts) == 2:
            try:
                stats[parts[1].strip()] = int(parts[0])
            except ValueError:
                continue

    return stats


def main():
    if len(sys.argv) < 2:
        print("Usage: python git_utils.py <command> [args]")
        print("Commands: status, branches, cleanup, stats")
        return 1

    command = sys.argv[1]

    if command == "status":
        print(status_summary())

    elif command == "branches":
        for branch in list_branches():
            print(branch)

    elif command == "cleanup":
        dry_run = "--execute" not in sys.argv
        branches = cleanup_merged_branches(dry_run=dry_run)

        if dry_run and branches:
            print( "\nAdd --execute to actually delete {} branch(es)".format( len(branches) ) )

    elif command == "stats":
        stats = commit_stats()

        for author, count in sorted(
                stats.items(),
                key=lambda item: item[1],
                reverse=True):
            print("{:5d}  {}".format(count, author))

    else:
        print("Unknown command: {}".format(command))
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
