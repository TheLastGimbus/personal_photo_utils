import argparse
import os
from datetime import datetime
from pathlib import Path

prs = argparse.ArgumentParser()
prs.add_argument('format', type=str, help=
"""
Format of date in file name (without extension). See: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes

Can also be:
- 'signal' => 'signal-%Y-%m-%d-%H%M%S' (cuts off rest)
- 'screenshot' =>'Screenshot_%Y%m%d-%H%M%S' (cuts off rest)
""")
prs.add_argument('--recursive', '-r', action='store_true')
prs.add_argument('--path', '-p', help="Input dir to fix", type=str, default='.')

args = prs.parse_args()


def main():
    name_preprocess = lambda name: name
    if args.format == 'signal':
        args.format = 'signal-%Y-%m-%d-%H%M%S'
        name_preprocess = lambda name: name[:24]
    elif args.format == 'screenshot':
        args.format = 'Screenshot_%Y%m%d-%H%M%S'
        name_preprocess = lambda name: name[:26]

    files = [x for x in Path(args.path).glob('**/*' if args.recursive else '*') if x.is_file()]
    for file in files:
        try:
            date = datetime.strptime(name_preprocess(file.stem), args.format)
        except ValueError:
            continue
        print(file, date)
        os.utime(file, (date.timestamp(), date.timestamp()))


if __name__ == '__main__':
    main()
