from __future__ import print_function, unicode_literals

from ..choices import PROGRAM_CHOICES
from ..models import GraduateStudent as Model
from . import print_object

#######################################################################

HELP_TEXT = "Change program for a single graduate student"
DJANGO_COMMAND = "main"
USE_ARGPARSE = True
OPTION_LIST = (
    (
        ["graduatestudent_pk"],
        {"help": "The primary key of the graduate student to change"},
    ),
    (["program_code"], {"help": "The program code to change to.  Use ? to list codes"}),
)

#######################################################################

#######################################################################


def print_program_codes():
    print("Available programs are:")
    for code, desc in PROGRAM_CHOICES:
        print('* "{}" {}'.format(code, desc))


#######################################################################


def main(options, args):

    pk = options["graduatestudent_pk"]
    program = options["program_code"]

    if program not in [p[0] for p in PROGRAM_CHOICES]:
        print("Not a valid program code")
        print_program_codes()
        return

    obj = Model.objects.get(pk=pk)
    obj.program = program
    obj.save()
    print_object(obj)


#######################################################################
