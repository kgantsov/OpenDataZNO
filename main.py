import csv
import argparse
from collections import defaultdict
import statistics
import itertools

from prettytable import PrettyTable


def schools(args):
    file_name = f'data/Odata{args.year}_utf8.csv'
    s = set()

    with open(file_name, newline='') as f:
        reader = csv.DictReader(f, delimiter=';')
        
        for row in reader:
            school_name = row['EONAME']
            if args.areaname in row['AREANAME']:
                s.add(school_name)
        
    for school_name in s:
        print(school_name)


def top(args):
    print_top(
        year=args.year,
        sortby=args.sortby.upper(),
        areaname=args.areaname,
        N=args.N,
        verbose=args.verbose
    )


def print_top(year, sortby='TOTAL', areaname=None, N=10, verbose=False):
    file_name = f'data/Odata{year}_utf8.csv'


    columns = [
        'UkrBall100',
        'histBall100',
        'mathBall100',
        'physBall100',
        'chemBall100',
        'bioBall100',
        'geoBall100',
        'engBall100',
        'fraBall100',
        'deuBall100',
        'spaBall100'
    ]

    if year == 2017:
        columns = [x.upper() for x in columns]

    school_results = defaultdict(lambda: defaultdict(list))
    

    with open(file_name, newline='') as f:
        reader = csv.DictReader(f, delimiter=';')
        
        for row in reader:
            school_name = row['EONAME']

            if areaname and areaname not in row['AREANAME']:
                continue

            for column in columns:
                if row[column] != 'null':
                    school_results[school_name][column].append(float(row[column].replace(',','.')))

    school_stats_totals = defaultdict(dict)

    for school_name, school_stats in school_results.items():
        school_stats_totals[school_name] = {
            k.replace('Ball100', '').upper(): round(statistics.mean(v), 2)
            for k, v in sorted(school_stats.items(), key=lambda x: x[0])
        }
        all_marks = list(itertools.chain(*list(school_stats.values())))
        
        if all_marks:
            school_stats_totals[school_name]['TOTAL'] = round(statistics.mean(all_marks), 2)

    school_stats_totals = sorted(school_stats_totals.items(), key=lambda x: x[1].get(sortby, 0), reverse=True)

    _columns = [x.replace('Ball100', '').upper() for x in columns] + ['TOTAL']

    for number, (school_name, school_stats_total) in enumerate(school_stats_totals[:N], start=1):
        if verbose:
            print(f'{number}. {school_name}. Year:{year}')
            
            table = PrettyTable()
            table.field_names = _columns
            table.add_row([school_stats_total.get(x, 0.0) for x in _columns])
            
            print(table)
            print()
        else:
            print(f'{number}. Stats for {school_name} IN {year} TOTAL MEAN SCORE: {school_stats_total["TOTAL"]}')
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Schools')

    subparsers = parser.add_subparsers(help='sub-command help')

    parser_schools = subparsers.add_parser('schools', help='schools')
    parser_schools.add_argument('--year', type=int, help='Year')
    parser_schools.add_argument('--areaname', type=str, help='AREANAME')
    parser_schools.set_defaults(func=schools)

    parser_top = subparsers.add_parser('top', help='top')
    parser_top.add_argument('--year', type=int, help='Year')
    parser_top.add_argument('--areaname', type=str, help='AREANAME')
    parser_top.add_argument('--sortby', type=str, help='Field to sort by', default='TOTAL')
    parser_top.add_argument('-N', type=int, help='Top N schools')
    parser_top.add_argument('--verbose', help='Verbose output', const=True, nargs='?', default=False)
    parser_top.set_defaults(func=top)

    args = parser.parse_args()
    args.func(args)
