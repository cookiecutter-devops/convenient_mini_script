#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
哈希工具
"""
import hashlib
import sys
import os


def hash_file(filepath):
    """计算文件哈希值"""
    with open(filepath, 'rb') as f:
        content = f.read()
        return hashlib.md5(content).hexdigest()


def compute_hash(filepath, algorithm='sha256'):
    """计算文件哈希值"""
    h = hashlib.new(algorithm)
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


if __name__=='__main__':
    filepath = sys.argv[1]
    algo = sys.argv[2] if len(sys.argv)>2 else 'sha256'
    result = compute_hash(filepath, algo)
    size = os.path.getsize(filepath)
    print(f'{algo}({filepath}) = {result}')
    print(f'File size: {size:,} bytes')
