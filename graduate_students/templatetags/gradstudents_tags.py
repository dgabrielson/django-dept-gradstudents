#######################
from __future__ import print_function, unicode_literals

from django import template

from ..models import GraduateStudent

#######################

#####################################################################

register = template.Library()

#####################################################################


@register.filter
def get_graduate_students(person_qs, status=None):
    """
    Get a queryset of graduate students from a queryset of
    supervisors.
    """
    if status is None:
        status = "S"  # current students

    supervisor_values = person_qs.values_list("supervisor", flat=True)
    grad_qs = GraduateStudent.objects.active(status=status)
    return grad_qs.filter(pk__in=supervisor_values)


#####################################################################
