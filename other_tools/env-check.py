#!/usr/bin/env python3
import sys
import platform

# '''
# 检查环境信息
# '''
# def check_environment():
#     info = {
#         "python": sys.version,
#         "platform": platform.platform(),
#         "arch": platform.architecture(),
#         "cpu_count": platform.cpu_count(),
#         "hostname": platform.node(),
#     }
#     return info

# if __name__ == "__main__":
#     for k, v in check_environment().items():
#         print(f"{k}: {v}")




import subprocess, sys, shutil

def check_tools():
    tools = ['python', 'node', 'npm', 'git', 'docker', 'curl', 'make', 'jq']
    for tool in tools:
        path = shutil.which(tool)
        if path:
            try:
                version = subprocess.run([tool, '--version'], capture_output=True, text=True, timeout=5)
                print(f'  {tool}: {version.stdout.strip()[:30]}')
            except:
                print(f'  {tool}: found at {path}')
        else:
            print(f'  {tool}: NOT FOUND')

if __name__=='__main__':
    print('Environment Check:')
    check_tools()
