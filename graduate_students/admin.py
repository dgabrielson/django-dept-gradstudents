"""
Graduate Students admin
"""
from __future__ import print_function, unicode_literals

import datetime
from functools import update_wrapper

from django import forms
from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin.views.autocomplete import AutocompleteJsonView
from django.contrib.admin.widgets import AutocompleteSelect
from django.contrib.auth.decorators import permission_required
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.http import Http404, JsonResponse
from django.urls import path, reverse
from django.utils.html import format_html

from . import conf
from .forms import NoUrlFileWidget
from .mixins import ClassBasedViewsAdminMixin
from .models import (
    Funding,
    FundingSource,
    GraduateStudent,
    Milestone,
    MilestoneType,
    Paperwork,
)
from .views import CurrentTotalFundingReport, FundingReportAdminView, sendfile

#######################################################################


def graduatestudent_for_funding_queryset(queryset=None):
    """
    Helper function for the graduatestudent funding lists.
    """
    if queryset is None:
        queryset = GraduateStudent.objects.all()
    if not conf.get("funding:allow-historical"):
        queryset = queryset.filter(active=True, status__in=["P", "S"])
    return queryset


#######################################################################


class GraduationDateFilter(admin.SimpleListFilter):

    title = "graduation date (current students)"
    parameter_name = "grad-date"

    def lookups(self, request, modelAdmin):
        """
        Returns a list of tuples (coded-value, title).
        """
        this_year = datetime.date.today().year
        qs = modelAdmin.get_queryset(request)
        qs = qs.active()
        qs = qs.filter(graduation_date__isnull=False)
        qs = qs.filter(graduation_date__gte=datetime.date(this_year, 1, 1))
        date_list = sorted(
            list(
                set(
                    [
                        (d.year, d.month)
                        for d in qs.values_list("graduation_date", flat=True)
                    ]
                )
            )
        )
        return [
            ("{0}-{1}".format(y, m), datetime.date(y, m, 1).strftime("%B %Y"))
            for y, m in date_list
        ]

    def queryset(self, request, queryset):
        """
        Apply the filter to the existing queryset.
        """
        filter = self.value()
        if filter is None:
            return
        y, m = [int(e) for e in filter.split("-")]
        return queryset.filter(graduation_date__year=y, graduation_date__month=m)


#######################################################################


class FundingGradStudentFilter(admin.SimpleListFilter):

    title = "graduate student"
    parameter_name = "graduate_student_id__exact"

    def _get_label(self, obj):
        if obj.program == "P":
            program = "Ph.D."
        elif obj.program == "Z":
            program = "Pre-M"
        else:
            program = "M.Sc."
        if obj.status == "P":
            status = "PENDING"
        else:
            status = ""
        return "{} ({}) {}".format(obj, program, status).strip()

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples (coded-value, title).
        """
        qs = graduatestudent_for_funding_queryset()
        return [(obj.pk, self._get_label(obj)) for obj in qs]

    def queryset(self, request, queryset):
        """
        Apply the filter to the existing queryset.
        """
        filter_value = self.value()
        if filter_value is None:
            return
        return queryset.filter(graduate_student_id__exact=filter_value)


#######################################################################


def _gs_program_status_label(obj):
    label = "{} ({})".format(obj, obj.get_program_display())
    if obj.status != "S":
        label += ": {}".format(obj.get_status_display())
    return label


class LabelMixin(object):
    def label_from_instance(self, obj):
        return _gs_program_status_label(obj)


class GradStudentAndProgramModelChoiceField(LabelMixin, forms.ModelChoiceField):
    pass


class GradStudentAutocompleteLabelWidget(LabelMixin, AutocompleteSelect):
    url_name = "%s:%s_%s_autocomplete_label"


#######################################################################


class LabelAutocompleteJsonView(LabelMixin, AutocompleteJsonView):
    def get(self, request, *args, **kwargs):
        """
        Return a JsonResponse with search results of the form:
        {
            results: [{id: "123" text: "foo"}],
            pagination: {more: true}
        }
        """
        if not self.model_admin.get_search_fields(request):
            raise Http404(
                "%s must have search_fields for the autocomplete_view."
                % type(self.model_admin).__name__
            )
        if not self.has_perm(request):
            return JsonResponse({"error": "403 Forbidden"}, status=403)

        self.term = request.GET.get("term", "")
        self.paginator_class = self.model_admin.paginator
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return JsonResponse(
            {
                "results": [
                    {
                        "id": str(obj.pk),
                        "text": self.label_from_instance(obj),
                    }  # only change!
                    for obj in context["object_list"]
                ],
                "pagination": {"more": context["page_obj"].has_next()},
            }
        )


#######################################################################


class MilestoneInline(admin.TabularInline):
    """
    Inline for Milestone objects.
    """

    extra = 0
    model = Milestone


##########################################################################


class PaperworkInline(admin.TabularInline):
    model = Paperwork
    fields = ["file", "description", "changelist_buttons"]
    formfield_overrides = {models.FileField: {"widget": NoUrlFileWidget}}
    readonly_fields = ["changelist_buttons"]
    extra = 0

    def changelist_buttons(self, obj):
        if obj.pk:
            return format_html(
                '<a class="button" href="{}">View</a>&nbsp;'
                '<a class="button" href="{}">Download</a>',
                reverse(
                    "admin:graduatestudents_paperwork_inline", kwargs={"pk": obj.pk}
                ),
                reverse(
                    "admin:graduatestudents_paperwork_download", kwargs={"pk": obj.pk}
                ),
            )
        return ""

    changelist_buttons.short_description = "Actions"
    changelist_buttons.allow_tags = True

    def view_on_site(self, obj):
        """
        Don't show this link for this inline.
        """
        return None


#######################################################################


class GraduateStudentAdmin(admin.ModelAdmin):
    autocomplete_fields = ["person"]  #'advisor', ]
    # consider using django-select2 for restricted choices...
    # N.B.: Django 2.0 autocomplete fields do not respect limit_choices_to.
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "active",
                    "person",
                    "program",
                    "status",
                    "start_date",
                    "advisor",
                )
            },
        ),
        (
            "Graduation details",
            {
                "fields": (
                    "defense_date",
                    "thesis_title",
                    "thesis_url",
                    ("graduation_date", "graduation_date_confirmed"),
                )
            },
        ),
        (
            "Funding summary",
            {
                "fields": (
                    ("total_funding", "earliest_funding", "most_recent_funding"),
                    "current_funding",
                )
            },
        ),
    )

    filter_horizontal = ("advisor",)
    inlines = [MilestoneInline, PaperworkInline]
    list_display = [
        "person",
        "active",
        "program",
        "status",
        "graduation_date",
        "_confirmed_list_display",
    ]
    list_filter = [
        "status",
        "program",
        "start_date",
        GraduationDateFilter,
        "graduation_date_confirmed",
        "advisor",
        "active",
        "created",
        "modified",
    ]
    list_select_related = True
    readonly_fields = (
        "total_funding",
        "earliest_funding",
        "most_recent_funding",
        "current_funding",
    )
    search_fields = ["person__cn", "thesis_title"]
    ordering = ["person"]

    def _confirmed_list_display(self, obj):
        return obj.graduation_date_confirmed

    _confirmed_list_display.short_description = "confirmed"
    _confirmed_list_display.admin_order_field = "graduation_date_confirmed"
    _confirmed_list_display.boolean = True

    def get_readonly_fields(self, request, obj=None):
        """
        Dynamic readonly fields
        """
        readonly_dynamic = tuple()
        if obj:  # editing an existing object
            readonly_dynamic += ("person",)
            if not request.user.is_superuser:
                readonly_dynamic += ("program",)
            if obj.status in ["G", "C"] and not request.user.is_superuser:
                readonly_dynamic += (
                    "status",
                    "start_date",
                    "advisor",
                    "defense_date",
                    "thesis_title",
                    "graduation_date",
                    "graduation_date_confirmed",
                )

        return self.readonly_fields + readonly_dynamic

    def get_actions(self, request):
        actions = super(GraduateStudentAdmin, self).get_actions(request)
        if "delete_selected" in actions:
            actions.pop("delete_selected")
        return actions

    def autocomplete_label_view(self, request):
        return LabelAutocompleteJsonView.as_view(model_admin=self)(request)

    def get_urls(self):
        """
        Add in the paperwork view and download urls
        """
        urls = super(GraduateStudentAdmin, self).get_urls()

        # lots of super duplication... all for customized autocomplete labels.
        # implemented for Django 2.0
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name
        urls = [
            path(
                "autocomplete-label/",
                wrap(self.autocomplete_label_view),
                name="%s_%s_autocomplete_label" % info,
            ),
            url(
                r"^paperwork/(?P<pk>\d+)/inline/$",
                permission_required("graduate_students.change_graduatestudent")(
                    sendfile
                ),
                name="graduatestudents_paperwork_inline",
                kwargs={"download": False},
            ),
            url(
                r"^paperwork/(?P<pk>\d+)/download/$",
                permission_required("graduate_students.change_graduatestudent")(
                    sendfile
                ),
                name="graduatestudents_paperwork_download",
                kwargs={"download": True},
            ),
        ] + urls
        return urls


admin.site.register(GraduateStudent, GraduateStudentAdmin)

#######################################################################


class FundingSourceAdmin(admin.ModelAdmin):
    list_display = ["__str__", "name", "ordering"]
    list_editable = ["name", "ordering"]
    search_fields = ["name"]


admin.site.register(FundingSource, FundingSourceAdmin)

#######################################################################


class FundingAdmin(ClassBasedViewsAdminMixin, admin.ModelAdmin):
    """
    Admin class for Funding objects
    """

    autocomplete_fields = ["graduate_student", "source"]
    list_display = ["graduate_student", "source", "amount", "start_date", "end_date"]
    list_filter = ["source", "active", "created", "modified"]
    search_fields = ["graduate_student__person__cn", "source__name", "comments"]
    ordering = ["-start_date"]
    save_as = True

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "graduate_student":
            db = kwargs.get("using")
            kwargs["widget"] = GradStudentAutocompleteLabelWidget(
                db_field.remote_field, self.admin_site, using=db
            )
            kwargs["queryset"] = graduatestudent_for_funding_queryset()
            return GradStudentAndProgramModelChoiceField(**kwargs)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_urls(self):
        """
        Extend the admin urls for this model.
        Provide a link by subclassing the admin change_form,
        and adding to the object-tools block.
        """
        urls = super(FundingAdmin, self).get_urls()
        urls = [
            url(
                r"^report/$",
                self.admin_site.admin_view(
                    permission_required("graduate_students.change_funding")(
                        self.cb_changeform_view
                    )
                ),
                kwargs={
                    "view_class": FundingReportAdminView,
                    "title": "Generate funding report",
                    "add": False,
                    "original": "Generate funding report",
                },
                name="graduatestudent_funding_report",
            ),
            url(
                r"^current-totals/$",
                self.admin_site.admin_view(
                    permission_required("graduate_students.change_funding")(
                        CurrentTotalFundingReport.as_view()
                    )
                ),
                name="graduatestudent_funding_current_total",
            ),
        ] + urls
        return urls


admin.site.register(Funding, FundingAdmin)

#######################################################################


class MilestoneTypeAdmin(admin.ModelAdmin):
    """
    Admin class for MilestoneType objects
    """

    list_display = ["name", "active"]
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(MilestoneType, MilestoneTypeAdmin)

#######################################################################
