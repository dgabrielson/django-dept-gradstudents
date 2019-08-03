from __future__ import print_function, unicode_literals

import datetime
import operator
from functools import reduce

# from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db.models.query import QuerySet

from .choices import MSC_PROGRAM_CHOICES, PHD_PROGRAM_CHOICES

"""
Graduate Students models
"""

# from decimal import Decimal

#######################################################################
#######################################################################
#######################################################################


class BaseCustomQuerySet(QuerySet):
    """
    Custom QuerySet.
    """

    def active(self):
        """
        Returns only the active items in this queryset
        """
        return self.filter(active=True)

    def search(self, *criteria):
        """
        Magic search for objects.
        This is heavily modelled after the way the Django Admin handles
        search queries.
        See: django.contrib.admin.views.main.py:ChangeList.get_query_set
        """
        if not hasattr(self, "search_fields"):
            raise ImproperlyConfigured(
                "No search fields.  Provide a "
                "search_fields attribute on the QuerySet."
            )

        if len(criteria) == 0:
            assert False, "Supply search criteria"

        terms = [str(c) for c in criteria]
        if len(terms) == 1:
            terms = terms[0].split()

        def construct_search(field_name):
            if field_name.startswith("^"):
                return "%s__istartswith" % field_name[1:]
            elif field_name.startswith("="):
                return "%s__iexact" % field_name[1:]
            elif field_name.startswith("@"):
                return "%s__search" % field_name[1:]
            else:
                return "%s__icontains" % field_name

        qs = self.filter(active=True)
        orm_lookups = [
            construct_search(str(search_field)) for search_field in self.search_fields
        ]
        for bit in terms:
            or_queries = [models.Q(**{orm_lookup: bit}) for orm_lookup in orm_lookups]
            qs = qs.filter(reduce(operator.or_, or_queries))
            if field_name.startswith("^"):
                return "%s__istartswith" % field_name[1:]
            elif field_name.startswith("="):
                return "%s__iexact" % field_name[1:]
            elif field_name.startswith("@"):
                return "%s__search" % field_name[1:]
            else:
                return "%s__icontains" % field_name

        qs = self.filter(active=True)
        orm_lookups = [
            construct_search(str(search_field)) for search_field in self.search_fields
        ]
        for bit in terms:
            or_queries = [models.Q(**{orm_lookup: bit}) for orm_lookup in orm_lookups]
            qs = qs.filter(reduce(operator.or_, or_queries))

        return qs.distinct()


#######################################################################
#######################################################################
#######################################################################


class GraduateStudentQuerySet(BaseCustomQuerySet):
    """
    Custom query set for GraduateStudent objects.

    Provides the following custom methods:
    * active
    * phd_filter
    * msc_filter
    * alumni_filter
    * graduates

    """

    def active(self, status="S"):
        qs = self.filter(active=True)
        if status is not None:
            qs = qs.filter(status=status)
        return qs

    def phd_filter(self, status="S"):
        qs = self.active(status=status)
        qs = qs.filter(program__in=[e[0] for e in PHD_PROGRAM_CHOICES])
        return qs

    def msc_filter(self, status="S"):
        qs = self.active(status=status)
        qs = qs.filter(program__in=[e[0] for e in MSC_PROGRAM_CHOICES])
        return qs

    def in_range(self, date_range, grad_date_adjustment=0):
        """
        Case 1: student start date in date range
        Case 2: student graduation date (confirmed) in date range
        Case 3: student has graduated but was in program entirely interior to
                the date range:
                - student started before end date AND
                - has confirmed graduation date after start date.
        Case 4: student has not graduated (no date), is current student, AND
                started before the end of the date range.
        Case 5: student has not graduated (tentative but unconfirmed date) AND
                started before the end of the date range.
        Case 6: student has graduated (confirmed) and program is entirely exterior
                to the date range. (Like Case 3, but opposite relation of ranges.)

        TODO: consider doing this with exclude statements instead.  It may be
        more readable / maintainable.

        Cases 3 and 6 need to be adjusted/modified to deal with students
        "near" graduation.
        """
        grad_adj = datetime.timedelta(days=grad_date_adjustment)
        return self.filter(
            Q(start_date__range=date_range)
            | Q(
                graduation_date__range=[
                    date_range[0] + grad_adj,
                    date_range[1] + grad_adj,
                ],
                graduation_date_confirmed=True,
            )
            | Q(
                start_date__lte=date_range[1],
                graduation_date__gte=date_range[0] + grad_adj,
                graduation_date_confirmed=True,
            )
            | Q(start_date__lte=date_range[1], graduation_date__isnull=True, status="S")
            | Q(
                start_date__lte=date_range[1],
                graduation_date__isnull=False,
                graduation_date_confirmed=False,
                status="S",
            )
            | Q(
                start_date__lte=date_range[0],
                graduation_date__gte=date_range[1] + grad_adj,
                graduation_date_confirmed=True,
            )
        ).distinct()

    def alumni_filter(self):
        """
        Filters only students who have graduated, sets ordering
        by graduation_date (most recent graduates first).
        """
        return self.filter(status__exact="G").order_by("-graduation_date")

    def graduates(self, date_range, confirmed_only=True):
        """
        Returns any graduates in the given date range
        """
        qs = self.filter(active=True, status__in=["S", "G"])
        qs = qs.filter(graduation_date__range=date_range)
        if confirmed_only:
            qs = qs.filter(graduation_date_confirmed=True)
        return qs


#######################################################################


class FundingSourceQuerySet(BaseCustomQuerySet):
    """
    Custom QuerySet for FundingSource objects.
    """


#######################################################################


class FundingQuerySet(BaseCustomQuerySet):
    """
    Custom QuerySet for Funding objects.
    """

    def in_range(self, date_range):
        """
        Returns any funding instance that occurs within the given date range.
        """
        qs = self.active()
        qs = qs.filter(
            Q(start_date__range=date_range)
            | Q(end_date__range=date_range)
            | Q(start_date__lte=date_range[1], end_date__gte=date_range[0])
        ).distinct()
        # This last one is the edge case of a funding instance which is
        # entirely outside of the given date range.
        return qs

    def sum(self):
        """
        Return the sum of all amounts in the current QuerySet.
        WARNING: Be extremely cautious using this function in combination
        with the in_range() filter: It will almost certainly double
        count over consecutive ranges.
        This can be done using the (more expensive) sum_for_range() method.
        """
        return sum(self.values_list("amount", flat=True))

    def sum_for_range(self, date_range):
        """
        Return the sum of all amounts in the current QuerySet; but only
        over the given date range.
        """
        return sum((f.for_range(date_range) for f in self.in_range(date_range)))

    def earliest_start_date(self):
        """
        Return the earliest start date in the current QuerySet.
        """
        return self.earliest("start_date").start_date

    def latest_end_date(self):
        """
        Return the lastest start or end date in the current QuerySet.
        (If the latest funding was a one off, this will be a start date,
        not an end date.)
        """
        start = self.latest("start_date").end_date
        end = self.exclude(end_date=None).latest("end_date").end_date
        return max([start, end])


#######################################################################


class MilestoneTypeQuerySet(BaseCustomQuerySet):
    """
    Custom QuerySet for MilestoneType objects.
    """


#######################################################################


class MilestoneQuerySet(BaseCustomQuerySet):
    """
    Custom QuerySet for Milestone objects.
    """


#######################################################################


class PaperworkQuerySet(BaseCustomQuerySet):
    """
    Custom QuerySet for Paperwork objects.
    """

    def filter_for_user(self, user):
        """
        Access check -- check user permissions, ownership, etc.
        """
        # todo: consider guardian here...
        if user.has_perm("graduate_students.change_graduatestudent"):
            return self
        else:
            return self.none()

    def get_for_user(self, user, **kwargs):
        """
        Restrict by user access.
        """
        qs = self.filter_for_user(user)
        return qs.get(**kwargs)


#######################################################################
