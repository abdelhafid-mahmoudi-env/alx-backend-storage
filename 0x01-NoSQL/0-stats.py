#!/usr/bin/python3
import sys
import signal
import re

# Initialize variables
total_size = 0
status_counts = {200: 0, 301: 0, 400: 0, 401: 0, 403: 0, 404: 0, 405: 0, 500: 0}
line_count = 0

# Signal handler for interrupt (CTRL + C)
def handle_interrupt(sig, frame):
    print_stats()
    sys.exit(0)

# Function to parse each line and update metrics
def parse_line(line):
    global total_size, status_counts, line_count
    
    line = line.strip()
    match = re.match(r'^(\d+\.\d+\.\d+\.\d+) - \[.+\] "GET /projects/260 HTTP/1\.1" (\d+) (\d+)$', line)
    if match:
        status_code = int(match.group(2))
        file_size = int(match.group(3))
        
        total_size += file_size
        if status_code in status_counts:
            status_counts[status_code] += 1
        
        line_count += 1
        
        if line_count % 10 == 0:
            print_stats()

# Function to print current statistics
def print_stats():
    global total_size, status_counts
    print(f"File size: {total_size}")
    for code in sorted(status_counts.keys()):
        if status_counts[code] > 0:
            print(f"{code}: {status_counts[code]}")

# Register signal handler
signal.signal(signal.SIGINT, handle_interrupt)

# Main loop to process stdin
try:
    for line in sys.stdin:
        parse_line(line)
except KeyboardInterrupt:
    handle_interrupt(signal.SIGINT, None)
