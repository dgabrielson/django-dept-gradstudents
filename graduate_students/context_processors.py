from __future__ import print_function, unicode_literals

import datetime

from django.conf import settings

# APPLICATION SETTINGS
from . import conf
from .models import GraduateStudent

"""
Graduate Student context processor.
Returns upcoming graduates.
"""

TIMESPAN = conf.get("upcoming_grads_days")


def upcoming_graduates(request):
    today = datetime.date.today()
    ref_date = datetime.date(today.year, today.month, 1)
    range_ = [ref_date, ref_date + datetime.timedelta(days=TIMESPAN)]

    return {"upcoming_graduates": GraduateStudent.objects.graduates(range_)}


#
