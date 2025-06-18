# !/usr/bin/env python3
import requests
import argparse
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin
from termcolor import colored


def parse_arguments():
    parser = argparse.ArgumentParser(description='Web server directory enumeration tool')
    parser.add_argument('-u', '--url', required=True, help='Target URL (e.g., http://example.com)')
    parser.add_argument('-w', '--wordlist', required=True, help='Path to directory wordlist file')
    parser.add_argument('-t', '--threads', type=int, default=10, help='Number of threads (default: 10)')
    parser.add_argument('-e', '--extensions', help='File extensions to check (comma-separated, e.g., php,html)')
    return parser.parse_args()


def load_wordlist(wordlist_file, extensions=None):
    try:
        with open(wordlist_file, 'r') as f:
            words = [line.strip() for line in f if line.strip()]

        if extensions:
            extensions = extensions.split(',')
            extended_words = []
            for word in words:
                extended_words.append(word)
                for ext in extensions:
                    extended_words.append(f"{word}.{ext}")
            return extended_words
        return words
    except FileNotFoundError:
        print(colored(f"[!] Wordlist file {wordlist_file} not found", 'red'))
        exit(1)


def check_directory(url, directory):
    try:
        target_url = urljoin(url, directory)
        response = requests.get(target_url, timeout=5)

        if response.status_code == 200:
            print(colored(f"[+] Found: {target_url} (Code: {response.status_code})", 'green'))
        elif response.status_code in [301, 302, 303, 307, 308]:
            print(colored(
                f"[→] Redirect: {target_url} → {response.headers.get('Location', '?')} (Code: {response.status_code})",
                'yellow'))
        elif response.status_code == 403:
            print(colored(f"[!] Forbidden: {target_url} (Code: {response.status_code})", 'red'))
        elif response.status_code == 401:
            print(colored(f"[!] Unauthorized: {target_url} (Code: {response.status_code})", 'blue'))

    except requests.exceptions.RequestException as e:
        print(colored(f"[x] Error checking {directory}: {str(e)}", 'red'))


def main():
    args = parse_arguments()

    target_url = args.url if args.url.endswith('/') else args.url + '/'

    print(colored(f"\n[•] Starting directory enumeration for {target_url}", 'cyan'))
    print(colored(f"[•] Using wordlist: {args.wordlist}", 'cyan'))
    print(colored(f"[•] Threads: {args.threads}", 'cyan'))
    if args.extensions:
        print(colored(f"[•] Checking extensions: {args.extensions}", 'cyan'))

    directories = load_wordlist(args.wordlist, args.extensions)

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        for directory in directories:
            executor.submit(check_directory, target_url, directory)

    print(colored("\n[•] Enumeration completed!", 'cyan'))


if __name__ == "__main__":
    main()
