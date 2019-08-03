"""
Graduate Students models
"""
from __future__ import print_function, unicode_literals

import os
from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import localtime, now
from people.models import Person

from . import conf, signals
from .choices import (
    MSC_PROGRAM_CHOICES,
    PHD_PROGRAM_CHOICES,
    PROGRAM_CHOICES,
    STATUS_CHOICES,
)
from .managers import (
    FundingManager,
    FundingSourceManager,
    GraduateStudentManager,
    MilestoneManager,
    MilestoneTypeManager,
)
from .querysets import PaperworkQuerySet

#######################################################################
#######################################################################


class GSBaseModel(models.Model):
    """
    Abstract base class for common fields.
    """

    active = models.BooleanField(default=True)
    created = models.DateTimeField(
        auto_now_add=True, editable=False, verbose_name="creation time"
    )
    modified = models.DateTimeField(
        auto_now=True, editable=False, verbose_name="last modification time"
    )

    class Meta:
        abstract = True


#######################################################################
#######################################################################


@python_2_unicode_compatible
class GraduateStudent(GSBaseModel):
    """
    Graduate Students and People are not more directly linked because:

        * The Person object may be created long before the Graduate Student
            is accepted (e.g., during initial contact)

        * The graduate student is a record of one person in a single program,
            so if someone does a Master's and then a Thesis, they should have
            one ``Person`` object but two ``GraduateStudent`` objects.
    """

    person = models.ForeignKey(
        Person,
        on_delete=models.PROTECT,
        # limit_choices_to={'active': True,
        #          'flags__slug': 'gradstudent'},
        # help_text='''Only people with the "gradstudent" flag are shown.
        #      You should not change this after it has been set.''',
    )

    program = models.CharField(
        max_length=1,
        choices=PROGRAM_CHOICES,
        default="M",
        help_text="""You should not change this after a student has started their program.
                                    If somebody does a second graduate degree, a new graduate student record should be created.""",
    )
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default="P")

    start_date = models.DateField()
    defense_date = models.DateField(blank=True, null=True)
    graduation_date = models.DateField(blank=True, null=True)
    graduation_date_confirmed = models.BooleanField(
        default=False,
        help_text="If this is <em>not</em> set, then the graduation is "
        + "considered tentative, and will not be advertised.",
    )

    advisor = models.ManyToManyField(
        Person,
        blank=True,
        related_name="supervisor",
        limit_choices_to={"active": True, "flags__slug__in": conf.get("advisor_flags")},
    )
    thesis_title = models.CharField(max_length=250, blank=True)
    thesis_url = models.URLField(
        blank=True, help_text="(Optional) a link to the thesis."
    )

    objects = GraduateStudentManager()

    class Meta:
        ordering = ("-program", "-status", "person")
        base_manager_name = "objects"

    def __str__(self):
        return "{}".format(self.person)

    def clean(self, *args, **kwargs):
        """
        Update the person's group, based on program and status.
        """
        try:
            if self.status == "G":
                self.person.add_flag_by_name("alumni")
            if self.status not in ["P", "S"]:
                self.person.remove_flag_by_name("gradstudent")
        except Person.DoesNotExist:
            # This happens for certain improperly submitted forms.
            pass
        return super(GraduateStudent, self).clean(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("gradstudent-detail", kwargs={"pk": self.pk})

    def is_msc(self):
        return self.program in [e[0] for e in MSC_PROGRAM_CHOICES]

    def is_phd(self):
        return self.program in [e[0] for e in PHD_PROGRAM_CHOICES]

    def total_funding(self):
        return self.funding_set.active().sum()

    # total_funding.short_description = "Total funding"

    def current_funding(self):
        funding_list = self.funding_set.active()
        date_range = [self.earliest_funding(), localtime(now()).date()]
        return funding_list.sum_for_range(date_range)

    current_funding.help = "Funding payed out as of today"

    def earliest_funding(self):
        return self.funding_set.active().earliest_start_date()

    earliest_funding.short_description = "Started on"

    def most_recent_funding(self):
        return self.funding_set.active().latest_end_date()

    most_recent_funding.short_description = "Up to"


if conf.get("autocreate_on_gradstudent_flag"):
    models.signals.m2m_changed.connect(
        signals.person_m2m_changed_autocreate_graduatestudent,
        sender=Person.flags.through,
    )

#######################################################################


@python_2_unicode_compatible
class FundingSource(GSBaseModel):
    """
    An editable drop-down list for the funding source.
    """

    name = models.CharField(max_length=100)
    ordering = models.PositiveSmallIntegerField(
        default=0, help_text="Determines the sequence in the pull-down list."
    )

    objects = FundingSourceManager()

    class Meta:
        ordering = ("ordering", "name")
        base_manager_name = "objects"

    def __str__(self):
        return self.name


#######################################################################


@python_2_unicode_compatible
class Funding(GSBaseModel):
    """
    An instance of funding for a particular graduate student

    Note the amount is a python ``decimal.Decimal()`` type; when coding:
    ``from decimal import Decimal``

    For now, the amount is assumed to occur daily; i.e., there is no
    sense of different schedules or recurring payments.
    (If this changes, there will be a Payment model, which is why
    this model is called Funding and *not* Payment.)

    Note that amount is capped at 999999.99 (8 digits, 2 decimal places).
    (We should have such a problem!)
    """

    graduate_student = models.ForeignKey(GraduateStudent, on_delete=models.CASCADE)
    source = models.ForeignKey(
        FundingSource, on_delete=models.PROTECT, limit_choices_to={"active": True}
    )

    amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="The total amount of funding for this period.",
    )
    comments = models.CharField(
        max_length=250, blank=True, help_text="A short comment about the funding."
    )
    start_date = models.DateField(help_text="The day the funding begins or occurs.")
    end_date = models.DateField(
        blank=True, null=True, help_text="Leave this blank for a one-time payment."
    )

    objects = FundingManager()

    class Meta:
        ordering = ("start_date", "end_date")
        verbose_name_plural = "funding"
        base_manager_name = "objects"

    def __str__(self):
        return "$%2.2d for %s from %s" % (
            self.amount,
            self.graduate_student,
            self.source,
        )

    def clean(self, *args, **kwargs):
        """
        Ensure the end_date, if not None, is *after* start_date.
        """
        if self.end_date is not None:
            if not (self.start_date < self.end_date):
                raise ValidationError("The end date must be after the start date")

        return super(Funding, self).clean(*args, **kwargs)

    def for_range(self, date_range):
        """
        Compute the amount of funding for the given date range.
        """
        dt_start, dt_end = date_range
        if self.end_date is None:
            # one time funding... is it in the date range or not?
            if dt_start <= self.start_date <= dt_end:
                return self.amount
            else:
                return Decimal("0.00")
        # ongoing funding -- compute daily amount
        days = (self.end_date - self.start_date).days + 1  # always inclusive
        assert days != 0, "this makes no sense"  # should not happen w/ valid inst
        daily_amount = self.amount / days
        # compute the number of days of overlap:
        overlap_start = max([dt_start, self.start_date])
        overlap_end = min([dt_end, self.end_date])
        overlap_days = (overlap_end - overlap_start).days + 1  # always inclusive
        # compute!
        return (overlap_days * daily_amount).quantize(Decimal(".01"))


#######################################################################


@python_2_unicode_compatible
class MilestoneType(GSBaseModel):
    """
    A type of milestone that a graduate student can acheive or may require.
    """

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    objects = MilestoneTypeManager()

    class Meta:
        ordering = ["name"]
        base_manager_name = "objects"

    def __str__(self):
        return self.name


#######################################################################


@python_2_unicode_compatible
class Milestone(GSBaseModel):
    """
    A type of milestone that a graduate student can acheive or may require.
    """

    graduate_student = models.ForeignKey(GraduateStudent, on_delete=models.CASCADE)
    type = models.ForeignKey(MilestoneType, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)

    objects = MilestoneManager()

    class Meta:
        ordering = ["date"]
        get_latest_by = "date"
        base_manager_name = "objects"

    def __str__(self):
        return "{self.type} for {self.graduate_student}".format(self=self)


#######################################################################


@python_2_unicode_compatible
class Paperwork(GSBaseModel):
    """
    A (secure) paperwork file asset for a graduate student.
    """

    graduate_student = models.ForeignKey(GraduateStudent, on_delete=models.CASCADE)
    file = models.FileField(
        upload_to=conf.get("upload_to"),
        storage=conf.get("storage_class")(**conf.get("storage_kwargs")),
    )
    description = models.CharField(max_length=250, blank=True)

    def get_absolute_url(self):
        if self.pk:
            return reverse(
                "admin:graduatestudents_paperwork_inline", kwargs={"pk": self.pk}
            )

    get_absolute_url.short_description = "url"

    def get_download_url(self):
        if self.pk:
            return reverse(
                "admin:graduatestudents_paperwork_inline", kwargs={"pk": self.pk}
            )

    get_download_url.short_description = "download url"

    objects = PaperworkQuerySet.as_manager()

    def __str__(self):
        name = os.path.basename(self.file.name)
        return name


#######################################################################
