from __future__ import print_function, unicode_literals

"""
Graduate Students choices
"""
#######################################################################

PHD_PROGRAM_CHOICES = (("P", "Ph.D."),)

MSC_PROGRAM_CHOICES = (
    ("M", "M.Sc. Thesis"),
    ("N", "M.Sc. Practicum"),
    ("D", "M.Sc. Course Based"),
    ("Z", "Pre-Masters"),
    ("C", "M.Sc. Comprehensive"),
)

PROGRAM_CHOICES = PHD_PROGRAM_CHOICES + MSC_PROGRAM_CHOICES

STATUS_CHOICES = (
    ("P", "Pending Student (not yet accepted)"),
    ("S", "Current Student"),
    ("AW", "Authorized Withdrawl"),
    ("CW", "Compulsary Withdrawl"),
    ("VW", "Voluntary Withdrawl"),
    ("G", "Graduated"),
    ("C", "Completed (Pre-MSc)"),
)

#######################################################################
