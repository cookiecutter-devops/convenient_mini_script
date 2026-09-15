#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import pymysql
import sys
import paramiko
import argparse
import configparser
from concurrent.futures import ThreadPoolExecutor,as_completed

"""
ssh工具类,多线程执行ssh命令,获取返回结果,并打印出来
参数:
    hosts: 服务器列表,每个元素为(ip,user,password)
    cmd: 要执行的命令
    timeout: 超时时间
    workers: 并发数
    quiet: 是否静默模式

示例：
python ssh_tool.py --hosts=192.168.1.1,192.168.1.2 --cmd=ls --timeout=10 --workers=2 --quiet
"""
config_file=os.path.expanduser("~/bin/config_ssh.ini")
def load_db_config():
    config=configparser.ConfigParser()
    config.read(config_file)
    try:
        return {
                'host':config.get('database','host'),
                'user':config.get('database','user'),
                'password':config.get('database','password'),
                'database':config.get('database','database'),
                'charset':config.get('database','charset')
                }
    except Exception as e:
        print(e)
        sys.exit(1)
def get_ssh_hosts_from_db():
    db_config=load_db_config()
    hosts=[]
    connection=None
    cursor=None
    try:
        connection=pymysql.connect(**db_config)
        cursor=connection.cursor()
        sql="select ip,ssh_user,ssh_password from servers"
        cursor.execute(sql)
        for row in cursor.fetchall():
            hosts.append((row[0],row[1],row[2]))
        connection.close()
        return hosts
    except Exception as e:
        print(e)
        return []
def ssh_exec(host,user,password,cmd,timeout):
    try:
        ssh=paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host,username=user,password=password,timeout=timeout)
        stdin,stdout,stderr=ssh.exec_command(cmd)
        out=stdout.read().decode("utf-8")
        err=stderr.read().decode("utf-8")
        ssh.close()
        return host,out,err,True
    except Exception as e:
        return host,"",str(e),False

def run_on_hosts(hosts,cmd,timeout,workers,quiet):
    if not hosts:
        print("none")
        return
    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_host={
                executor.submit(ssh_exec,ip,user,pwd,cmd,timeout):(ip,user)
                for ip,user,pwd in hosts}
        for future in as_completed(future_to_host):
            ip,user=future_to_host[future]
            try:
                host,out,err,success=future.result()
                if not quiet:
                     print(f"========== {host} (用户: {user}) ==========")
                if success:
                    if out and not quiet:
                        print(out)
                    if err and not quiet:
                        print(f"{err}")
                else:
                    print(f"错误 [{host}]: {err}")
                if not quiet:
                    print()
            except Exception as e:
                print(f"{ip} wrong is{e}")

def parse_args():
    p=argparse.ArgumentParser(description="并发 SSH 工具")
    p.add_argument("--hosts",nargs="+",help="目标 IP 列表")
    p.add_argument("--user",help="SSH 用户名")
    p.add_argument("--password",help="SSH 密码")
    p.add_argument("--cmd",default="df -h",help="命令 (默认 df -h)")
    p.add_argument("--timeout",type=int,default=5,help="超时秒数")
    p.add_argument("--workers",type=int,default=5,help="并发数")
    p.add_argument("--from-db",action="store_true",help="从数据库读取")
    p.add_argument("--quiet",action="store_true",help="quiet moshi")
    return p.parse_args()

def main():
    args=parse_args()
    if args.from_db:
        hosts=get_ssh_hosts_from_db()
        if not hosts:
            print("wuu zh ji")
            sys.exit(1)
        run_on_hosts(hosts,args.cmd,args.timeout,args.workers,args.quiet)
    elif args.hosts:
        if not args.user or not args.password:
            sys.exit(1)
        hosts=[(ip,args.user,args.password) for ip in args.hosts]
        run_on_hosts(hosts,args.cmd,args.timeout,args.workers,args.quiet)
    else:
        print("指定 --hosts 或 --from-db")
        sys.exit(1)

if __name__=="__main__":
    main()
