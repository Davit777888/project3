#!/usr/bin/env python3
import hashlib
import argparse
from termcolor import colored
from concurrent.futures import ThreadPoolExecutor



def parse_arguments():
    parser = argparse.ArgumentParser(description='Hash cracking tool for authorized pentesting')
    parser.add_argument('-H', '--hash', required=True, help='Hash to crack')
    parser.add_argument('-t', '--hash-type', required=True,
                        choices=['md5', 'sha1', 'sha256', 'sha512', 'ntlm'],
                        help='Type of hash to crack')
    parser.add_argument('-w', '--wordlist', required=True, help='Path to wordlist file')
    parser.add_argument('-T', '--threads', type=int, default=4,
                        help='Number of threads to use (default: 4)')
    return parser.parse_args()


def load_wordlist(wordlist_path):
    try:
        with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(colored(f"[!] Wordlist file {wordlist_path} not found", 'red'))
        exit(1)


def hash_string(string, algorithm):
    h = hashlib.new(algorithm)
    h.update(string.encode('utf-8'))
    return h.hexdigest()


def crack_hash(args, wordlist_chunk):
    for word in wordlist_chunk:
        hashed_word = hash_string(word, args.hash_type)
        if hashed_word == args.hash:
            print(colored(f"\n[+] CRACKED: {args.hash} -> {word}", 'green'))
            exit(0)
        print(colored(f"[-] Trying: {word}", 'red'), end='\r')


def main():
    args = parse_arguments()
    wordlist = load_wordlist(args.wordlist)

    print(colored(f"\n[•] Starting hash cracker", 'cyan'))
    print(colored(f"[•] Hash type: {args.hash_type.upper()}", 'cyan'))
    print(colored(f"[•] Wordlist: {args.wordlist}", 'cyan'))
    print(colored(f"[•] Threads: {args.threads}", 'cyan'))

    chunk_size = len(wordlist) // args.threads
    chunks = [wordlist[i:i + chunk_size] for i in range(0, len(wordlist), chunk_size)]

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        for chunk in chunks:
            executor.submit(crack_hash, args, chunk)

    print(colored("\n[!] Failed to crack the hash", 'red'))


if __name__ == "__main__":
    main()
