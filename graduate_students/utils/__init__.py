from __future__ import print_function, unicode_literals

import datetime
import re
from decimal import Decimal

from spreadsheet import sheetWriter

from .. import conf
from ..cli import resolve_lookup
from ..models import Funding, FundingSource, GraduateStudent

"""
Utilities for the Graduate Students app.

Yo're probably interested in make_funding_spreadsheet()
"""
#######################################################################


EXTRA_FIELDS = conf.get("spreadsheet_extra_fields")

#######################################################################


def funding_table(date_range, graduatestudent_list, source_list):
    """
    Construct the core table of funding for the report.
    """
    funding_list = Funding.objects.in_range(date_range)
    table = []
    for graduate_student in graduatestudent_list:
        row = []
        for source in source_list:
            funding = funding_list.filter(
                graduate_student=graduate_student, source=source
            )
            amounts = [f.for_range(date_range) for f in funding]
            row.append(sum(amounts, Decimal("0.00")))
        table.append(row)
    return table


#######################################################################


def do_augment_table(graduatestudent_list, source_list, table):
    """
    Construct the augmented table for a single group of graduate students.
    """
    headers = [str(source) for source in source_list]
    student_totals = [sum(row) for row in table]
    source_totals = [sum(col) for col in zip(*table)]
    return headers, source_totals, zip(graduatestudent_list, table, student_totals)


#######################################################################


def augmented_table(
    date_range,
    gradstudent_groups,
    source_list,
    final_label="",
    source_total_label="",
    student_total_label="",
):
    """
    Construct the augmented table for the report.

    ``date_range`` is the range for the report.

    The ``gradstudent_groups`` input must be a list of (name, queryset) pairs.
    (The querysets are the students to report for.  If there is more than one
    pair in the list, there will be an extra final line containing grand totals.)

    ``source_list`` is the queryset of FundingSources.

    The various label inputs decorate the tableau.

    The return result is a list of rows, where each row is a list of cells.
    """

    def __make_row(*args):
        """unpacks lists so the row works out"""

        def safe_list(arg):
            if isinstance(arg, list):
                return arg
            return [arg]

        return sum([safe_list(e) for e in args if e is not None], [])

    def __extra_fields(grad):
        """grad can be None, in which case space for fields."""
        if not EXTRA_FIELDS:
            return None
        result = []
        for f in EXTRA_FIELDS:
            if grad is None:
                result.append("")
            else:
                result.append(resolve_lookup(grad, f))
        return result

    def __title_extra_fields(model=GraduateStudent):
        def __title_field_name(model, field):
            m = re.match(r"get_(?P<field>.+)_display", field)
            if m:
                field = m.group("field")
            for f in model._meta.fields:
                if f.name == field:
                    return f.verbose_name.title()
            # something is really wrong if this happens.
            assert False
            return field.title()

        if not EXTRA_FIELDS:
            return None
        result = []
        for f in EXTRA_FIELDS:
            result.append(__title_field_name(model, f))
        return result

    result = []
    result.append(__make_row("Generated on:", datetime.date.today()))
    result.append(__make_row("Start Date:", date_range[0]))
    result.append(__make_row("End Date:", date_range[1]))
    result.append([])

    grand_totals = []
    ST = Decimal("0.0")
    for group_name, graduatestudent_list in gradstudent_groups:
        base_table = funding_table(date_range, graduatestudent_list, source_list)
        headers, totals, table = do_augment_table(
            graduatestudent_list, source_list, base_table
        )

        result.append(
            __make_row(group_name, __title_extra_fields(), student_total_label, headers)
        )

        S = Decimal("0.0")
        for grad, data, total in table:
            result.append(__make_row(str(grad), __extra_fields(grad), total, data))
            S += total
        result.append(__make_row(source_total_label, __extra_fields(None), S, totals))
        result.append([])
        grand_totals.append(totals)
        ST += S

    if len(gradstudent_groups) > 1:
        # grad totals for categories.
        result.append(
            __make_row(
                final_label,
                __extra_fields(None),
                ST,
                [sum(col) for col in zip(*grand_totals)],
            )
        )

    return result


#######################################################################


def make_funding_spreadsheet(start_date, end_date, format_, grad_date_adjustment=60):
    """
    Given a start_date, end_date, and file format, return the data stream
    for a spreadsheet.
    """
    date_range = [start_date, end_date]
    source_list = FundingSource.objects.active()

    grad_student_list = GraduateStudent.objects.in_range(
        date_range, grad_date_adjustment=grad_date_adjustment
    )
    dated_funding_list = (
        Funding.objects.active().in_range(date_range).filter(source__active=True)
    )
    gs_funding_ids = dated_funding_list.values_list("graduate_student_id", flat=True)
    grad_student_list |= (
        GraduateStudent.objects.active(status=None)
        .filter(pk__in=gs_funding_ids)
        .distinct()
    )
    student_groups = [
        ["PhD Students", grad_student_list.phd_filter(status=None)],
        ["MSc Students", grad_student_list.msc_filter(status=None)],
    ]

    table = augmented_table(
        date_range, student_groups, source_list, "Total", "Sub-total", "Student Total"
    )
    return sheetWriter(table, format_)


#######################################################################
