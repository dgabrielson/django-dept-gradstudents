from __future__ import print_function, unicode_literals

from django.utils.timezone import now

from ..models import GraduateStudent

#######################################################################

HELP_TEXT = "Run time based updates for graduate students"
USE_ARGPARSE = True
DJANGO_COMMAND = "main"
OPTION_LIST = ()

#######################################################################

#######################################################################


def main(options, args):
    verbosity = int(options["verbosity"])
    # current students who need to become graduates:
    gradstudent_list = GraduateStudent.objects.active().filter(
        graduation_date__lte=now(), graduation_date_confirmed=True
    )
    for gradstudent in gradstudent_list:
        if verbosity > 2:
            print("Considering for graduation", gradstudent)
        gradstudent.status = "G"  # graduated.
        gradstudent.clean()  # person flag changes.
        gradstudent.save()
        if verbosity > 0:
            print(
                "{0} ({1}) {2}".format(
                    gradstudent,
                    gradstudent.get_program_display(),
                    gradstudent.get_status_display(),
                )
            )
    gradstudent_list = GraduateStudent.objects.active(status="S")
    for gradstudent in gradstudent_list:
        if verbosity > 2:
            print("Cross-checking current student", gradstudent)
        if "gradstudent" not in gradstudent.person.flags.active().slugs():
            gradstudent.person.add_flag_by_name("gradstudent")
            if verbosity > 0:
                print(gradstudent, "added missing gradstudent flag!")
        if not gradstudent.person.username:
            print(
                gradstudent,
                "has no username; email:",
                gradstudent.person.email,
                "person_id:",
                gradstudent.person_id,
            )


#######################################################################
