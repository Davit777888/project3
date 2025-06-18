#!/usr/bin/env python3
import requests
import argparse
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
from termcolor import colored


def parse_arguments():
  
    parser = argparse.ArgumentParser(description='Subdomain discovery tool')
    parser.add_argument('-d', '--domain', required=True, help='Target domain (e.g., example.com)')
    parser.add_argument('-w', '--wordlist', required=True, help='Path to subdomain wordlist file')
    parser.add_argument('-t', '--threads', type=int, default=10, help='Number of threads (default: 10)')
    parser.add_argument('-o', '--output', help='Output file to save results')
    return parser.parse_args()


def load_wordlist(wordlist_file):

    try:
        with open(wordlist_file, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(colored(f"[!] Wordlist file {wordlist_file} not found", 'red'))
        exit(1)


def check_subdomain(subdomain, domain, output_file=None):

    url = f"http://{subdomain}.{domain}"
    try:
        response = requests.get(url, timeout=5, allow_redirects=False)

        if response.status_code == 200:
            result = f"[+] Found: {url} (Code: {response.status_code})"
            print(colored(result, 'green'))
            if output_file:
                with open(output_file, 'a') as f:
                    f.write(f"{url}\n")
        elif response.status_code in [301, 302, 303, 307, 308]:
            result = f"[→] Redirect: {url} → {response.headers.get('Location', '?')} (Code: {response.status_code})"
            print(colored(result, 'yellow'))
        elif response.status_code == 403:
            result = f"[!] Forbidden: {url} (Code: {response.status_code})"
            print(colored(result, 'red'))
        elif response.status_code == 401:
            result = f"[!] Unauthorized: {url} (Code: {response.status_code})"
            print(colored(result, 'blue'))

    except requests.exceptions.RequestException:
        pass  # Silently skip failed connections


def main():

    args = parse_arguments()

    # Validate domain format
    if not args.domain.startswith(('http://', 'https://')):
        domain = args.domain
    else:
        domain = urlparse(args.domain).netloc

    print(colored(f"\n[•] Starting subdomain discovery for {domain}", 'cyan'))
    print(colored(f"[•] Using wordlist: {args.wordlist}", 'cyan'))
    print(colored(f"[•] Threads: {args.threads}", 'cyan'))
    if args.output:
        print(colored(f"[•] Saving results to: {args.output}", 'cyan'))

    subdomains = load_wordlist(args.wordlist)

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        for subdomain in subdomains:
            executor.submit(check_subdomain, subdomain, domain, args.output)

    print(colored("\n[•] Discovery completed!", 'cyan'))


if __name__ == "__main__":
    main()
