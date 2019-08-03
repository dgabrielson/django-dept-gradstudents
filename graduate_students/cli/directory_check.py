"""
Synchronize the list of graduate students with graduate student
directory entries.
"""
from __future__ import print_function, unicode_literals

from datetime import timedelta

from directory.models import DirectoryEntry, EntryType
from django.utils.timezone import now
from people.models import Person

from .. import conf
from ..models import GraduateStudent

#############################################################

DJANGO_COMMAND = "main"
HELP_TEXT = __doc__.strip()
USE_ARGPARSE = True
OPTION_LIST = (
    (
        ["--auto"],
        dict(
            action="store_true",
            help="Automatically create and deactivate directory entries.",
        ),
    ),
)

#############################################################
#############################################################


def directory_deactivate(entry, verbosity):
    """
    Deactivate directory entry.
    """
    entry.active = False
    if verbosity > 0:
        print("** Deactivated directory entry: {}".format(entry))
    entry.save()


#############################################################


def directory_create_or_activate(entry_type, person, verbosity):
    entry, flag = DirectoryEntry.objects.get_or_create(person=person, type=entry_type)
    if not flag and not entry.active:
        entry.active = True
        entry.save()
        if verbosity > 0:
            print("** Reactivated directory entry: {}".format(entry))
    if flag and verbosity > 0:
        print("** Created directory entry: {}".format(entry))


#############################################################


def main(options, args):
    """
    options and args are not used.
    """
    verbosity = int(options["verbosity"])
    auto = options["auto"]
    if verbosity > 2:
        print(
            "directory:typefilter_list: {}".format(
                conf.get("directory:typefilter_list")
            )
        )
    if conf.get("directory:typefilter_list") is None:
        print(
            """Invalid configuration settings.

You will need to set, at a minimum:
    "directory:typefilter_list" - a list of
        ["directory-slug", "graduatestudent-object-filter-name"] pairs.
        Useful filter names are: "active", "phd_filter", and "msc_filter".

You may also want to set:
    "directory:graduation_date_cutoff" [default: 35 (days)]
        -- the number of days *before* the graduation date to remove
           graduate students from the directory.
    "directory:defense_date_grace" [default: 14 (days)]
        -- the number of days *after* the defense, if any...

    When BOTH of these settings are None, then logic is based
    on deactivating on the first day of the semester which
    contains the graduation date.
"""
        )
        return

    graduation_date_cutoff = conf.get("directory:graduation_date_cutoff")
    defense_date_grace = conf.get("directory:defense_date_grace")
    semester_method = (graduation_date_cutoff is None) and (defense_date_grace is None)
    for typeslug, filter in conf.get("directory:typefilter_list"):
        filter_f = getattr(GraduateStudent.objects, filter)

        # This is the list of graduate students that **should be** on the directory
        gradstudent_list = filter_f()

        if semester_method:
            from classes.models import Semester

            this_term = Semester.objects.get_current()
            this_term_start, this_term_finish = this_term.get_start_finish_dates()
            # exclude graduations before this term started:
            gradstudent_list = gradstudent_list.exclude(
                graduation_date_confirmed=True, graduation_date__lte=this_term_start
            )
            # exclude anybody with a confirmed graduation in this term:
            gradstudent_list = gradstudent_list.exclude(
                graduation_date_confirmed=True,
                graduation_date__gte=this_term_start,
                graduation_date__lte=this_term_finish,
            )
            if now().date() > this_term_finish:
                next_term = this_term.get_next()
                next_term_start, next_term_finish = this_term.get_start_finish_dates()
                # also exclude anybody confirmed graduating in the next term.
                gradstudent_list = gradstudent_list.exclude(
                    graduation_date_confirmed=True,
                    graduation_date__gte=this_term_finish,
                    graduation_date__lte=next_term_finish,
                )

        else:
            # These won't both be true:
            if graduation_date_cutoff is None:
                graduation_date_cutoff = 0
            if defense_date_grace is None:
                defense_date_grace = 0
            cutoff = now() + timedelta(days=graduation_date_cutoff)
            grace = now() + timedelta(days=-defense_date_grace)
            gradstudent_list = gradstudent_list.exclude(defense_date__lte=grace)
            gradstudent_list = gradstudent_list.exclude(
                graduation_date_confirmed=True, graduation_date__lte=cutoff
            )

        gradstudent_list = gradstudent_list.exclude(start_date__gt=now())
        # ensure that both the grad student record and the person record are active.
        gradstudent_list = gradstudent_list.filter(active=True, person__active=True)

        gradstudent_pks = set(gradstudent_list.values_list("person_id", flat=True))

        entry_type = EntryType.objects.active().get(slug=typeslug)

        # This is the list of **currrent** directory entries.
        directory_list = DirectoryEntry.objects.active().filter(type=entry_type)
        directory_pks = set(directory_list.values_list("person_id", flat=True))

        remove_pks = directory_pks.difference(gradstudent_pks)
        add_pks = gradstudent_pks.difference(directory_pks)

        for entry in directory_list.filter(person__in=remove_pks):
            if auto:
                directory_deactivate(entry, verbosity)
            else:
                print("Update directory: remove {0} {1}".format(entry_type, entry))

        for gradstudent in gradstudent_list.filter(person__in=add_pks):
            gradstudent.person.add_flag_by_name("directory")
            if auto:
                directory_create_or_activate(entry_type, gradstudent.person, verbosity)
            else:
                print("Update directory: add {0} {1}".format(entry_type, gradstudent))


#############################################################
