from __future__ import print_function, unicode_literals

from ..models import GraduateStudent as Model
from . import print_object

#######################################################################

HELP_TEXT = "Get detail on a graduate student record"
USE_ARGPARSE = True
DJANGO_COMMAND = "main"
OPTION_LIST = (
    (["pk"], {"nargs": "+", "help": "Primary key(s) to output details for"}),
)
ARGS_USAGE = "pk [pk [...]]"

#######################################################################

M2M_FIELDS = []
RELATED_ONLY = None  # Specify a list or None; None means introspect for related
RELATED_EXCLUDE = ["funding_set"]  # any related fields to skip

#######################################################################


def main(options, args):
    args = options["pk"]
    for pk in args:
        # get the object
        obj = Model.objects.get(pk=pk)
        print_object(obj)
        # m2m fields:
        for field in M2M_FIELDS:
            print(
                "\t"
                + field
                + "\t"
                + ", ".join([str(o) for o in getattr(obj, field).all()])
            )
        if RELATED_ONLY is None:
            related_sets = [attr for attr in dir(obj) if attr.endswith("_set")]
        else:
            related_sets = RELATED_ONLY
        for attr in related_sets:
            if attr in RELATED_EXCLUDE:
                continue
            related = getattr(obj, attr)
            for rel_obj in related.all():
                print_object(rel_obj)
        print()


#######################################################################
