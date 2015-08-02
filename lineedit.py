#!/usr/bin/python

"""

Read README.md for more information.


TODO
----

TODO Option to not add a destline if the same line is already in the file.

TODO Option to create a backup of the original file.

TODO Replace using regex backreference.

TODO Explain all -f and -p options.
"""


import os, sys
import argparse
import codecs
import logging
import re
import difflib

args = None
logger = None

def UnsupportedCondition(Exception): pass

def read_lines(filename):
    logger.debug(u'Reading file `%s`.', filename)
    lines=[]
    lineending=os.linesep

    with codecs.open(filename, 'r', 'utf-8') as fp:
        for c,line in enumerate(fp):
            if c == 0:
                if line.endswith('\r\n'):
                    lineending='\r\n'
                elif line.endswith('\r'):
                    lineending='\r'
                elif line.endswith('\n'):
                    lineending='\n'
                else:
                    logger.debug('No line-ending is found. Using OS default.')
                logger.debug('Using %s as line-neding for the file.', repr(lineending))

            lines.append(line.strip())

    logger.debug(u'Read %s lines.', len(lines))
    if not args.v:
        logger.info(u'Read file `%s`, total %s line(s), using %s as line-ending.', filename, len(lines), repr(lineending))

    fp.close()

    return lines,lineending

def parse_args():

    parser = argparse.ArgumentParser(
        description='LineEdit: A tool to quickly automate config file editing.',
        epilog='Exit codes are as follows:\n-1 = There was an error.\n0 = There was a match and it was replaces.\n 1 = No match was found. Nothing is replaced.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument('file',
        help='Source file: file path which should be edited (should be a textfile).')
    parser.add_argument('sourceline',
        type=unicode,
        help='Source line: line to search for using one of the method described in -f option.')
    parser.add_argument('destline',
        type=unicode,
        help='Destination line: the line which will be added or will replace source line using methods described in -p options. If `-p comment` is used, this string will be the comment characher.')


    parser.add_argument('-f',
        choices=['starts','regex','exact','ends'],
        default='exact',
        help='Find source position using one of the methods.')


    parser.add_argument('-n',
        action='store_true',
        help='Do the action only if source line is not found.')


    parser.add_argument('-p',
        choices=['replace','above','below','end','begin','comment','delete'],
        default='replace',
        help='Destination position: At which position should the destination line be added/replaces.')


    parser.add_argument('-m', '--max',
        default=1,
        help='Maximum number of matches. If more matches are found, no changes '
            'will take place.')
    parser.add_argument('-y',
        action='store_true',
        help='Yes, make changes to the file. Otherwise only show line numbers '
        'which will be changes.')

    parser.add_argument('-v',
        action='store_true',
        help='Output more debug information.')
    parser.add_argument('-l', '--long-diff',
        action='store_true',
        help='Show whole file with changes, not useful if the source file is long.')
    parser.add_argument('--create',
        action='store_true',
        help='Create the output file if source file does not exists. Useful if you want to append something to a (new) file.')

    try:
        args = parser.parse_args()
    except Exception as e:
        parser.print_help()
        sys.exit(-1)

    return args

def main():

    outputbuffer = []

    try:
        inputbuffer,lineending = read_lines(args.file)
    except IOError:
        if not args.create:
            logger.error(u'File `%s` is not found, please check the location. Use `--create` option to continue. Aborting...', args.file)
            sys.exit(-1)
        else:
            logger.warning(u'File `%s` will be created if needed, because it is not found.', args.file)
            inputbuffer,lineending = [], os.linesep


    if args.n:
        if not args.p in ['begin','end']:
            logger.error('When using `-n` option, the destination line can only be added at the beginning or at the end. Aborting...')
            sys.exit(-1)
    if args.p == 'comment':
        if len(args.destline.strip()) == 0:
            logger.error('Comment character cannot be empty.')
            sys.exit(-1)
        elif args.destline not in ['#', '//', ';', '--', '# ', '// ', '; ', '-- ',]:
            logger.warning('You are using `%s` as a comment character. This is a bit unusual.', args.destline)

    logger.info("Using `%s` matching, destination position is `%s`.", args.f, args.p)

    # Create regex to match source line.
    if args.f == 'starts':
        SOURCE_MATCH = r'^' + re.escape(args.sourceline)
    elif args.f == 'ends':
        SOURCE_MATCH = re.escape(args.sourceline) + r'$'
    elif args.f == 'exact':
        SOURCE_MATCH = r'^' + re.escape(args.sourceline) + r'$'
    elif args.f == 'regex':
        SOURCE_MATCH = args.sourceline
    else:
        raise UnsupportedCondition(u'Source finding using `{}` is not supported.' % args.f)

    RE_SOURCE_MATCH = re.compile(SOURCE_MATCH, re.U)
    logger.debug('Matching regex pattern for source line `%s`.', RE_SOURCE_MATCH.pattern)

    # Find source line and do the right action.
    matches_found = 0
    args.destline = args.destline.replace('\\t', '\t')
    for c,sourceline in enumerate(inputbuffer):
        if RE_SOURCE_MATCH.match(sourceline):
            logger.info('Found a match at line %s, matched string: `%s`.', c+1, sourceline)
            matches_found += 1
            if args.p == 'replace':
                outputbuffer.append(args.destline)
            elif args.p == 'comment':
                outputbuffer.append(args.destline + sourceline)
            elif args.p == 'above':
                outputbuffer.append(args.destline)
                outputbuffer.append(sourceline)
            elif args.p == 'below':
                outputbuffer.append(sourceline)
                outputbuffer.append(args.destline)
            elif args.p == 'begin':
                outputbuffer.insert(0,args.destline)
                outputbuffer.append(sourceline)
            elif args.p == 'end':
                outputbuffer.append(sourceline)
            elif args.p == 'delete':
                pass
            else:
                raise UnsupportedCondition(u'Destination position using `{}` is not supported.' % args.p)

        else:
            outputbuffer.append(sourceline)


    if args.max < matches_found:
        logger.error('Found %s matche(s), only %s change is allowed. Change that using `-m` option. Aborting.', matches_found, args.max)
        sys.exit(-1)


    if args.n and matches_found > 0:
        logger.info('`-n` flag is used, but there was a match found. No change needed.')
        sys.exit(0)
    elif args.n and matches_found == 0:
        if args.p == 'begin':
            outputbuffer.insert(0,args.destline)
        elif args.p == 'end':
            outputbuffer.append(args.destline)
    else:
        # Add a dest line at the end of the buffer if there was match and
        # position was 'end'
        if args.p == 'end' and matches_found > 0:
            outputbuffer.append(args.destline)


    if matches_found > 0 or args.n and matches_found == 0:
        logger.info('The result will be as follows, line starting with `> -` is removed and starting with `> +` is added:')
        for line in difflib.ndiff(inputbuffer, outputbuffer):
            if args.long_diff: # Show all lines
                if not line.startswith('?'):
                    logger.info('> %s',line)
            elif line.startswith('+') or line.startswith('-'): # Show only added/removed lines
                    logger.info('> %s',line)

        if args.y:
            if not os.access(args.file, os.W_OK):
                logger.error('Cannot write to `%s`, please make sure you have access.', args.file)
                sys.exit(-1)

            logger.info('Updating `%s` with new edits.', args.file)

            with codecs.open(args.file,'w','utf-8') as fp:
                fp.write(lineending.join(outputbuffer))
            fp.close()

        else:
            logger.warning('No changes written, please use `-y` option update the file. Aborting.')
            sys.exit(1)

    else:
        logger.warning('No matches found and nothing is replaced. Aborting.')
        sys.exit(1)


def configure_logger():

    logging.basicConfig(format=u'%(message)s',)
    logger = logging.getLogger('lineedit')

    # Source: http://stackoverflow.com/a/1336640/638504
    def add_colors_to_logger(fn):

        # add methods we need to the class
        def new(*args):
            levelno = args[1].levelno
            if(levelno>=50):
                color = '\x1b[31mERROR: ' # red
            elif(levelno>=40):
                color = '\x1b[31mERROR: ' # red
            elif(levelno>=30):
                color = '\x1b[33mWARNING: ' # yellow
            elif(levelno>=20): # info
                color = '\x1b[0m' # normal/grey
                # color = '\x1b[32m' # green
            elif(levelno>=10): # debug
                color = '\x1b[0m' # normal/grey
                # color = '\x1b[35m' # pink
            else:
                color = '\x1b[0m' # normal
            args[1].msg = str(color) + str(args[1].msg) +  '\x1b[0m'  # normal
            #print "after"
            return fn(*args)
        return new

    logging.StreamHandler.emit = add_colors_to_logger(logging.StreamHandler.emit)

    return logger

if __name__ == '__main__':
    try:
        logger = configure_logger()
        args = parse_args()
        logger.setLevel('DEBUG') if args.v else logger.setLevel('INFO')
        main()

    except UnsupportedCondition as e:
        print("")
        print(u'A fatal error occured: \n\n\t' + e.message)
        print("")
        sys.exit(-1)

    except:
        raise



