from __future__ import print_function, unicode_literals

import operator

from django.core.exceptions import ImproperlyConfigured
from django.db import models

# from people.models import Person
from .querysets import (
    FundingQuerySet,
    FundingSourceQuerySet,
    GraduateStudentQuerySet,
    MilestoneQuerySet,
    MilestoneTypeQuerySet,
)

"""
Graduate Students managers
"""

#######################################################################
#######################################################################
#######################################################################
#######################################################################


class CustomQuerySetManager(models.Manager):
    """
    Custom Manager for an arbitrary model, just a wrapper for returning
    a custom QuerySet
    """

    queryset_class = models.query.QuerySet
    always_select_related = None

    def get_queryset(self):
        """
        Return the custom QuerySet
        """
        queryset = self.queryset_class(self.model)
        if self.always_select_related is not None:
            queryset = queryset.select_related(*self.always_select_related)
        return queryset


#######################################################################
#######################################################################
#######################################################################


class GraduateStudentManager(CustomQuerySetManager):
    """
    Custom manager for GraduateStudent objects.
    """

    queryset_class = GraduateStudentQuerySet
    always_select_related = ["person"]


GraduateStudentManager = GraduateStudentManager.from_queryset(GraduateStudentQuerySet)

#######################################################################


class FundingSourceManager(CustomQuerySetManager):
    """
    Custom manager for FundingSource objects.
    """

    queryset_class = FundingSourceQuerySet


FundingSourceManager = FundingSourceManager.from_queryset(FundingSourceQuerySet)

#######################################################################


class FundingManager(CustomQuerySetManager):
    """
    Custom manager for Funding objects.
    """

    queryset_class = FundingQuerySet
    always_select_related = ["graduate_student", "graduate_student__person", "source"]


FundingManager = FundingManager.from_queryset(FundingQuerySet)

#####################################################################


class MilestoneTypeManager(CustomQuerySetManager):
    """
    Custom manager for MilestoneType objects.
    """

    queryset_class = MilestoneTypeQuerySet


MilestoneTypeManager = MilestoneTypeManager.from_queryset(MilestoneTypeQuerySet)

#####################################################################


class MilestoneManager(CustomQuerySetManager):
    """
    Custom manager for Milestone objects.
    """

    queryset_class = MilestoneQuerySet


MilestoneManager = MilestoneManager.from_queryset(MilestoneQuerySet)

#####################################################################
