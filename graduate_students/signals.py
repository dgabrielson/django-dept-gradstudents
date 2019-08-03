from __future__ import print_function, unicode_literals

from django.utils.timezone import is_aware, localtime, now

"""
Receiver functions for signals.
"""

################################################################

################################################################


def today(dt=None):
    if dt is None:
        dt = now()
    if is_aware(dt):
        dt = localtime(dt)
    return dt.date()


################################################################


def person_m2m_changed_autocreate_graduatestudent(
    sender, instance, action, reverse, model, pk_set, **kwargs
):
    """
    This could be better, but works for now.
    
    ``action``s:
    * ``post_add`` Create a graduate student record, if one does not exist
        if ``gradstudent`` was one of the flags added.
        
    This *will not* create duplicate graduate students.
    """
    if action == "post_add":
        flag_qs = model.objects.filter(pk__in=pk_set)
        if flag_qs.filter(slug="gradstudent").exists():
            if not instance.graduatestudent_set.all().exists():
                from .models import GraduateStudent

                GraduateStudent.objects.get_or_create(
                    person=instance, defaults={"start_date": today()}
                )


################################################################
