#!/usr/bin/env python3

import argparse
from math import log
from pathlib import Path
from numpy.core.fromnumeric import mean, std
from numpy.lib.function_base import median
    
BAR_LENGTH_MAX = 80
STATS = {}
DEBUG = False

def parse_args():
    parser = argparse.ArgumentParser(description='Use log scaling (default) for identifying '
        'an encrypted file. All bars should be maxed and relative std. dev. close to 1. '
        'Change the scaling (several can be combined) for other views.')
    parser.add_argument('input_file_name', type=Path)
    parser.add_argument('--scale', nargs='*', choices=['log', 'max', 'minmax'], 
                        default=['log'],
                        help='Choose one or more scaling options '
                             'to be applied in the specified order')
    parser.add_argument('--debug', action='store_true')

    return parser.parse_args()


def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


# Log scale a list of values, avoiding divide-by-zero errors
def scaleLog(scale_list):
    # Shift all values to >= 1 so log does not produce negatives
    if any([x < 1 for x in scale_list]):
        scale_list = [x + 1 for x in scale_list]

    scale_list = [log(x) for x in scale_list]

    return scale_list


# Scale a list of values so the smallest value is 0.0
# and the largest value is 1.0
# Returns a list of floats
def scaleMinMax(scale_list):
    minimum = min(scale_list)
    scale_list = [x - minimum for x in scale_list]
    maximum = max(scale_list)

    if maximum == 0:
        return scale_list

    scale_list = [x / maximum for x in scale_list]

    return scale_list


# Scale a list of values so the largest value is 1.0
# Returns a list of floats
def scaleMax(scale_list):
    maximum = max(scale_list)

    if maximum == 0:
        return scale_list

    scale_list = [x / maximum for x in scale_list]

    return scale_list


# Scale the data using one or more techniques provided in the
# scale_methods list (applied in the order they appear)
def scaleData(scale_list, scale_methods):
    for method in scale_methods:
        debug_print(scale_list)
        if method == 'log':
            scale_list = scaleLog(scale_list)
            print('Log scaled')
        elif method == 'max':
            scale_list = scaleMax(scale_list)
            print('Max scaled')
        elif method == 'minmax':
            scale_list = scaleMinMax(scale_list)
            print('MinMax scaled')
    
    # Always scaleMax so the data is in the range [0.0, 1.0]
    debug_print(scale_list)
    scale_list = scaleMax(scale_list)
    print('Max scaled')

    return scale_list


# Calculate statistics
def get_stats(byte_counts):
    STATS['min'] = min(byte_counts)
    STATS['max'] = max(byte_counts)
    STATS['mean'] = mean(byte_counts)
    STATS['stddev'] = std(byte_counts)
    STATS['rel. stddev'] = 100 * std(byte_counts) / mean(byte_counts)
    STATS['median'] = median(byte_counts)


def print_stats():
    print('Statistics:')

    for stat, val in STATS.items():
        print('\t{}:  {}'.format(stat, val))

    print()


def main():
    global DEBUG

    args = parse_args()

    if args.debug:
        DEBUG = True

    print(args.input_file_name)

    if not args.input_file_name.exists():
        print('Error: File does not exist')
        return 1

    with args.input_file_name.open(mode='rb') as fd:
        read_data = fd.read()

    print('First 16 bytes:')
    for x in range(0, 16):
        print(format(read_data[x], 'x'), end='')

    print()

    # Update the global stats dictionary and print it
    byte_counts = [read_data.count(x) for x in range(0, 256)]
    get_stats(byte_counts)
    print_stats()

    # Scale the data for printing a histogram
    byte_counts_scaled = scaleData(byte_counts, args.scale)
    debug_print(byte_counts_scaled)
    
    # Scale the 0-1 values to 0-BAR_LENGTH_MAX
    bar_lengths = [round(x * BAR_LENGTH_MAX) for x in byte_counts_scaled]

    # Add 1 to any values with a byte count of at least 1, but natural bar length of 0
    # so we don't have any bars of zero length except for real zeros
    add1 = [count > 0 and bar == 0  for count, bar in zip(byte_counts, bar_lengths)]
    bar_lengths = [bar + 1 if do_add else bar for do_add, bar in zip(add1, bar_lengths)]
    
    print()

    for x in range(0, 256):
        # Print the byte hex ordinal, follow by the decimal count of each byte
        print('{:>4}: {:>10} | '.format(hex(x), byte_counts[x]), end='')

        bar_length = bar_lengths[x]
        width = 6
        debug_print('{:>{width}} | '.format(bar_length, width=width), end='')

        for _ in range(bar_length):
            print('*', end='')
        print(' ' * (BAR_LENGTH_MAX - bar_length), end='')
        print('|')

    return 0


if __name__ == '__main__':
    main()
