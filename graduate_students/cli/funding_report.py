#!/usr/bin/env python
from __future__ import print_function, unicode_literals

import datetime
import os
import sys
from pprint import pprint

from graduate_students.utils import make_funding_spreadsheet
from spreadsheet import SUPPORTED_FORMATS

"""
generate a funding report for graduate students
"""

##############################################################################


def setup_django(settings_file):
    def real_path_of_file(filename):
        if filename.endswith(".pyc"):
            fn = os.path.abspath(filename[:-1])
        else:
            fn = os.path.abspath(filename)

        while os.path.islink(fn):
            fn = os.path.abspath(os.readlink(fn))

        return os.path.dirname(fn)

    sys.path.insert(0, real_path_of_file(settings_file))
    os.environ["DJANGO_SETTINGS_MODULE"] = os.path.splitext(
        os.path.basename(settings_file)
    )[0]


setup_django("../../gradstudents_demo_site/settings.py")

##############################################################################
# DJANGO IMPORTS:


def main(start_string, end_string, format_):
    start_date = datetime.datetime.strptime(start_string, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_string, "%Y-%m-%d").date()

    return make_funding_spreadsheet(start_date, end_date, format_)


if __name__ == "__main__":
    usage = """usage: %prog [options] start_date end_date
    
    start_date and end_date are in the format YYYY-MM-DD
    """
    parser = optparse.OptionParser(usage=usage)

    parser.add_option(
        "-f",
        "--format",
        dest="format",
        help="Specifiy the output format.  One of: %s." % ", ".join(SUPPORTED_FORMATS),
    )

    parser.add_option(
        "-o",
        "--outfile",
        dest="outfile",
        help="Specifiy the output filename.  If this is not given, the spreadsheet will be dumped to stdout.",
    )

    (options, args) = parser.parse_args()

    if len(args) != 2:
        print("You must specify a start_date and end_date.")
        sys.exit(1)

    start_date, end_date = args

    format_ = options.format
    if not format_ and options.outfile:
        format_ = os.path.splitext(options.outfile)[-1].lstrip(".")
    if not format_:
        format_ = "csv"

    data = main(start_date, end_date, format_)

    fp = open(options.outfile, "wb") if options.outfile else sys.stdout
    fp.write(data)

#
