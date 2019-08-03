"""
Generate a list of graduate student records.
"""
#######################################################################
from __future__ import print_function, unicode_literals

from ..models import GraduateStudent as Model
from . import resolve_lookup

HELP_TEXT = __doc__.strip()
USE_ARGPARSE = True
DJANGO_COMMAND = "main"
OPTION_LIST = (
    (
        ["--all"],
        dict(action="store_true", help="List all records, not just current ones"),
    ),
    (
        ["-f", "--fields"],
        dict(
            dest="field_list",
            help='Specify a comma delimited list of fields to include, e.g., -f "get_primary_net_iface.mac_address,room"',
        ),
    ),
)

#######################################################################

#######################################################################


def main(options, args):
    qs = Model.objects.all()
    if not options["all"]:
        qs = qs.active()
    for item in qs:

        value_list = [resolve_lookup(item, "pk"), "{}".format(item)]
        if options["field_list"]:
            for field in options["field_list"].split(","):
                value_list.append(resolve_lookup(item, field))
        print("\t".join(value_list))


#######################################################################
