#!/usr/bin/env python3
import re
import argparse
import hashlib
from termcolor import colored

HASH_PATTERNS = {
    'MD5': r'^[a-f0-9]{32}$',
    'SHA-1': r'^[a-f0-9]{40}$',
    'SHA-256': r'^[a-f0-9]{64}$',
    'SHA-512': r'^[a-f0-9]{128}$',
    'bcrypt': r'^\$2[aby]\$\d+\$[./A-Za-z0-9]{53}$',
    'NTLM': r'^[a-f0-9]{32}$',
    'MySQL': r'^[a-f0-9]{40}$',
    'CRC32': r'^[a-f0-9]{8}$'
}


def parse_arguments():
    parser = argparse.ArgumentParser(description='Hash identifier tool')
    parser.add_argument('hash', help='Hash to analyze')
    parser.add_argument('-g', '--generate', help='Generate hash from string (specify algorithm)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    return parser.parse_args()


def identify_hash(hash_string, verbose=False):
    results = []
    for hash_type, pattern in HASH_PATTERNS.items():
        if re.match(pattern, hash_string, re.IGNORECASE):
            results.append(hash_type)

    if verbose:
        print(colored("\n[•] Detailed hash analysis:", 'cyan'))
        print(f"Hash length: {len(hash_string)} characters")
        print(f"Characters: {'Hex only' if re.match(r'^[a-f0-9]+$', hash_string, re.IGNORECASE) else 'Mixed'}")

    if results:
        print(colored(f"\n[+] Possible hash types:", 'green'))
        for res in results:
            print(f"- {res}")
    else:
        print(colored("\n[!] Failed to identify hash type", 'red'))


def generate_hash(text, algorithm):
    algorithm = algorithm.lower()
    if algorithm not in hashlib.algorithms_available:
        print(colored(f"[!] Algorithm {algorithm} not supported", 'red'))
        print(colored(f"Available algorithms: {', '.join(hashlib.algorithms_available)}", 'yellow'))
        return

    try:
        h = hashlib.new(algorithm)
        h.update(text.encode('utf-8'))
        print(colored(f"\n[+] {algorithm} hash for '{text}':", 'green'))
        print(h.hexdigest())
    except Exception as e:
        print(colored(f"[!] Hash generation error: {str(e)}", 'red'))


def main():
    args = parse_arguments()
    if args.generate:
        generate_hash(args.hash, args.generate)
    else:
        identify_hash(args.hash, args.verbose)


if __name__ == "__main__":
    main()
