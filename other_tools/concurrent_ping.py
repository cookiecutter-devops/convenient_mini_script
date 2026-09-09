#!/usr/bin/env python3
import subprocess
from concurrent.futures import ThreadPoolExecutor

def ping_ip(ip):
    try:
        result=subprocess.run(
                ['ping','-c','1','-W','1',ip],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
                )
        return ip,result.returncode==0
    except Exception as e:
        return ip,False

def main():
     ips=['8.8.8.8','1.1.1.1','192.168.1.1','10.0.0.1']
     with ThreadPoolExecutor(max_workers=5) as executor:
         results=executor.map(ping_ip,ips)

     for ip,online in results:
        status='success' if online else 'lose'
        print(f"{ip}-{status}")

if __name__ == "__main__":
    main()
