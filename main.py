import csv
import argparse
from collections import defaultdict
import statistics
import itertools

from prettytable import PrettyTable


def schools(args):
    file_name = f'data/Odata{args.year}.csv'
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
        sortorder=args.sortorder.upper(),
        areaname=args.areaname,
        N=args.N,
        verbose=args.verbose
    )


def to_upper_first_letter(s):
    if not s:
        return s

    return s[0].upper() + s[1:]


def print_top(year, sortby='TOTAL', sortorder='DESC', areaname=None, N=10, verbose=False):
    file_name = f'data/Odata{year}.csv'


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
                column = to_upper_first_letter(column) if to_upper_first_letter(column) in row else column

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

    school_stats_totals = sorted(
        school_stats_totals.items(), key=lambda x: x[1].get(sortby, 0),
        reverse=sortorder == 'DESC'
    )

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


def gender(args):
    print_stats_by(
        grouping='SEXTYPENAME',
        grouping_title='Sex',
        year=args.year,
        sortby=args.sortby.upper(),
        sortorder=args.sortorder.upper(),
        areaname=args.areaname,
        N=args.N,
        verbose=args.verbose
    )

def region(args):
    print_stats_by(
        grouping='REGNAME',
        grouping_title='Region',
        year=args.year,
        sortby=args.sortby.upper(),
        sortorder=args.sortorder.upper(),
        areaname=args.areaname,
        N=args.N,
        verbose=args.verbose
    )

def language(args):
    print_stats_by(
        grouping='ClassLangName',
        grouping_title='Language',
        year=args.year,
        sortby=args.sortby.upper(),
        sortorder=args.sortorder.upper(),
        areaname=args.areaname,
        N=args.N,
        verbose=args.verbose
    )

def print_stats_by(year, grouping='SEXTYPENAME', grouping_title='SEX', sortby='TOTAL', sortorder='DESC', areaname=None, N=10, verbose=False):
    file_name = f'data/Odata{year}.csv'


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
        grouping = grouping.upper()
        columns = [x.upper() for x in columns]

    results = defaultdict(lambda: defaultdict(list))
    
    c = 0
    with open(file_name, newline='') as f:
        reader = csv.DictReader(f, delimiter=';')
        
        for row in reader:
            grouping_value = row[grouping]

            if areaname and areaname not in row['AREANAME']:
                continue

            for column in columns:
                if row[column] != 'null':
                    results[grouping_value][column].append(float(row[column].replace(',','.')))
            
            c += 1

    stats_totals = defaultdict(dict)

    for grouping_value, stats in results.items():
        stats_totals[grouping_value] = {
            k.replace('Ball100', '').replace('BALL100', '').upper(): (round(statistics.mean(v), 2), len(v))
            for k, v in sorted(stats.items(), key=lambda x: x[0])
        }
        all_marks = list(itertools.chain(*list(stats.values())))
        
        if all_marks:
            stats_totals[grouping_value]['TOTAL'] = (round(statistics.mean(all_marks), 2), len(all_marks))

    stats_totals = sorted(
        stats_totals.items(), key=lambda x: x[1].get(sortby, [0, 0])[0],
        reverse=sortorder == 'DESC'
    )

    _columns = [x.replace('Ball100', '').upper() for x in columns]

    table = PrettyTable()
    if verbose:
        table.field_names = ['#', grouping_title] + [x.replace('Ball100', '').upper() for x in columns] + ['MEAN SCORE']
    else:
        table.field_names = ["#", grouping_title, sortby, "MEAN SCORE"]

    table.align[grouping_title] = 'l'

    for number, (grouping_value, gender_stats_total) in enumerate(stats_totals[:N], start=1):
        if verbose:
            table.add_row([number, grouping_value] + [f'{gender_stats_total.get(x, [0.0, 0])[0]} ({gender_stats_total.get(x, [0.0, 0])[1]})' for x in _columns] + [f'{gender_stats_total["TOTAL"][0]} ({gender_stats_total["TOTAL"][1]})'])
        else:
            table.add_row([number, grouping_value, f'{gender_stats_total[sortby][0]} ({gender_stats_total[sortby][1]})', f'{gender_stats_total["TOTAL"][0]} ({gender_stats_total["TOTAL"][1]})'])

    print(f'Stats for {year}. Analysed {c} records')
    print(table)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Schools')

    subparsers = parser.add_subparsers(help='sub-command help')

    parser_schools = subparsers.add_parser('schools', help='schools')
    parser_schools.add_argument('--year', type=int, help='Year', default=2020)
    parser_schools.add_argument('--areaname', type=str, help='AREANAME')
    parser_schools.set_defaults(func=schools)

    parser_top = subparsers.add_parser('top', help='top')
    parser_top.add_argument('--year', type=int, help='Year', default=2020)
    parser_top.add_argument('--areaname', type=str, help='AREANAME')
    parser_top.add_argument('--sortby', type=str, help='Field to sort by', default='TOTAL')
    parser_top.add_argument('--sortorder', type=str, help='Sorting order', default='DESC')
    parser_top.add_argument('-N', type=int, help='Top N schools')
    parser_top.add_argument('--verbose', help='Verbose output', const=True, nargs='?', default=False)
    parser_top.set_defaults(func=top)

    parser_gender = subparsers.add_parser('gender', help='gender')
    parser_gender.add_argument('--year', type=int, help='Year', default=2020)
    parser_gender.add_argument('--sortby', type=str, help='Field to sort by', default='TOTAL')
    parser_gender.add_argument('--sortorder', type=str, help='Sorting order', default='DESC')
    parser_gender.add_argument('--areaname', type=str, help='AREANAME')
    parser_gender.add_argument('-N', type=int, help='Top N schools')
    parser_gender.add_argument('--verbose', help='Verbose output', const=True, nargs='?', default=False)
    parser_gender.set_defaults(func=gender)

    parser_region = subparsers.add_parser('region', help='region')
    parser_region.add_argument('--year', type=int, help='Year', default=2020)
    parser_region.add_argument('--sortby', type=str, help='Field to sort by', default='TOTAL')
    parser_region.add_argument('--sortorder', type=str, help='Sorting order', default='DESC')
    parser_region.add_argument('--areaname', type=str, help='AREANAME')
    parser_region.add_argument('-N', type=int, help='Top N schools')
    parser_region.add_argument('--verbose', help='Verbose output', const=True, nargs='?', default=False)
    parser_region.set_defaults(func=region)

    parser_language = subparsers.add_parser('language', help='language')
    parser_language.add_argument('--year', type=int, help='Year', default=2020)
    parser_language.add_argument('--sortby', type=str, help='Field to sort by', default='TOTAL')
    parser_language.add_argument('--sortorder', type=str, help='Sorting order', default='DESC')
    parser_language.add_argument('--areaname', type=str, help='AREANAME')
    parser_language.add_argument('-N', type=int, help='Top N schools')
    parser_language.add_argument('--verbose', help='Verbose output', const=True, nargs='?', default=False)
    parser_language.set_defaults(func=language)

    args = parser.parse_args()
    args.func(args)
