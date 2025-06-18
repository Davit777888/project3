#!/usr/bin/env python3
import re
import argparse
from collections import defaultdict, Counter
from datetime import datetime


def parse_arguments():

    parser = argparse.ArgumentParser(description='Log file analyzer')
    parser.add_argument('logfile', help='Path to log file')
    parser.add_argument('-t', '--time-range', nargs=2,
                        metavar=('START', 'END'),
                        help='Time range (format: "YYYY-MM-DD HH:MM:SS")')
    parser.add_argument('-l', '--level',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Filter by log level')
    parser.add_argument('-i', '--ip', help='Filter by IP address')
    parser.add_argument('-s', '--search', help='Search for specific text')
    parser.add_argument('-o', '--output', help='Output file for results')
    parser.add_argument('-c', '--count', action='store_true',
                        help='Show count statistics')
    return parser.parse_args()


def parse_log_line(line):

    log_pattern = r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (?P<level>\w+) (?P<message>.+)'
    match = re.match(log_pattern, line)
    if match:
        return match.groupdict()
    return None


def filter_logs(log_entries, args):

    filtered = []
    for entry in log_entries:
        if not entry:
            continue

        if args.time_range:
            log_time = datetime.strptime(entry['timestamp'], '%Y-%m-%d %H:%M:%S')
            start = datetime.strptime(args.time_range[0], '%Y-%m-%d %H:%M:%S')
            end = datetime.strptime(args.time_range[1], '%Y-%m-%d %H:%M:%S')
            if not (start <= log_time <= end):
                continue

        if args.level and entry['level'] != args.level:
            continue

        if args.ip and args.ip not in entry['message']:
            continue

        if args.search and args.search.lower() not in entry['message'].lower():
            continue

        filtered.append(entry)
    return filtered


def analyze_logs(log_entries):

    stats = {
        'level_counts': Counter(),
        'hourly_counts': defaultdict(int),
        'common_messages': Counter()
    }

    for entry in log_entries:
        if not entry:
            continue

        stats['level_counts'][entry['level']] += 1

        hour = datetime.strptime(entry['timestamp'], '%Y-%m-%d %H:%M:%S').hour
        stats['hourly_counts'][hour] += 1

        message = entry['message'][:50]
        stats['common_messages'][message] += 1

    return stats


def main():

    args = parse_arguments()

    try:
        with open(args.logfile, 'r') as f:
            log_entries = [parse_log_line(line.strip()) for line in f]
    except FileNotFoundError:
        print(f"Error: Log file {args.logfile} not found")
        return

    filtered_entries = filter_logs(log_entries, args)

    if args.count:
        stats = analyze_logs(filtered_entries)
        print("\nLog Statistics:")
        print(f"Total entries: {len(filtered_entries)}")
        print("\nLog Levels:")
        for level, count in stats['level_counts'].items():
            print(f"{level}: {count}")

        print("\nHourly Distribution:")
        for hour in sorted(stats['hourly_counts']):
            print(f"{hour:02}:00 - {stats['hourly_counts'][hour]} entries")

        print("\nMost Common Messages:")
        for msg, count in stats['common_messages'].most_common(5):
            print(f"{count}x: {msg}...")
    else:
        print("\nFiltered Log Entries:")
        for entry in filtered_entries:
            print(f"{entry['timestamp']} {entry['level']} {entry['message']}")

    if args.output:
        with open(args.output, 'w') as f:
            for entry in filtered_entries:
                f.write(f"{entry['timestamp']} {entry['level']} {entry['message']}\n")
        print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()
