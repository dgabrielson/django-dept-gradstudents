from __future__ import print_function, unicode_literals

import datetime
import mimetypes
import os

from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView, FormView, UpdateView
from django.views.generic.list import ListView
from spreadsheet import sheetWriter

from . import conf
from .forms import FundingReportForm, GraduateStudentForm
from .models import Funding, GraduateStudent, Paperwork

"""
Views for Graduate Students app.
"""

#######################################################################

#######################################################################


class FundingReportAdminView(FormView):
    """
    For generating funding reports.
    The view here extends admin functionality (for generating reports).

    It is *not* accessed by the regular graduate_students.urls.

    To enable this view, include the following *at the top level* urlconf:

        url(r'^admin/graduate_students/funding/report/',
            'graduate_students.views.admin_funding_report'),
        url(r'^admin/', include(admin.site.urls)),

    (it *must* be **before** the regular admin url conf).
    """

    form_class = FundingReportForm
    login_required = True
    template_name = "admin/graduate_students/funding/report.html"

    def get_initial(self):
        """
        Returns initial data for the form (a dictionary).
        """
        today = datetime.date.today()
        if today.month <= 8:
            start_year = today.year - 1
        else:
            start_year = today.year

        start_date = datetime.date(start_year, 9, 1)
        end_date = datetime.date(start_year + 1, 8, 31)
        return dict(start_date=start_date, end_date=end_date)

    def form_valid(self, form):
        """
        Define form valid, rather than a success url, because a valid
        form returns the spreadsheet.
        """
        return form.on_success()


#######################################################################


class CurrentTotalFundingReport(ListView):
    queryset = GraduateStudent.objects.active()
    format = "xlsx"
    grad_date_adjustment = 60

    def get_result_data(self, format):
        today = datetime.date.today()
        data = [
            [
                "Graduate student",
                "Program",
                "Total funding",
                "Total as of " + str(today),
                "Earlist funding",
                "Most recent funding",
            ]
        ]
        yesterday = today - datetime.timedelta(hours=24)
        date_range = [yesterday, today]
        grad_student_list = self.get_queryset().in_range(
            date_range, grad_date_adjustment=self.grad_date_adjustment
        )
        for gs in grad_student_list:
            try:
                total = gs.total_funding()
            except Funding.DoesNotExist:
                total = 0
            try:
                current = gs.current_funding()
            except Funding.DoesNotExist:
                current = 0
            try:
                earliest = gs.earliest_funding()
            except Funding.DoesNotExist:
                earliest = ""
            try:
                most_recent = gs.most_recent_funding()
            except Funding.DoesNotExist:
                most_recent = ""
            data.append(
                [
                    gs.person,
                    gs.get_program_display(),
                    total,
                    current,
                    earliest,
                    most_recent,
                ]
            )
        return sheetWriter(data, format)

    def render_to_response(self, context, **response_kwargs):
        filename = "funding-current-total_%s" % datetime.date.today()
        filename += "." + self.format
        content_type, encoding = mimetypes.guess_type(filename)
        stream = self.get_result_data(format=self.format)
        response = HttpResponse(content_type=content_type)
        response["Content-Disposition"] = "attachment; filename=" + filename
        response.write(stream)
        return response


#######################################################################


class GraduateStudentEditMixin(object):
    queryset = GraduateStudent.objects.all()
    form_class = GraduateStudentForm
    login_required = True


#######################################################################


class GraduateStudentCreateView(GraduateStudentEditMixin, CreateView):
    template_name = "graduate_students/graduatestudent_form.html"


graduate_student_create = permission_required("graduate_students.add_graduatestudent")(
    GraduateStudentCreateView.as_view()
)

#######################################################################


class GraduateStudentUpdateView(GraduateStudentEditMixin, UpdateView):
    pass


graduate_student_update = permission_required(
    "graduate_students.change_graduatestudent"
)(GraduateStudentUpdateView.as_view())

#######################################################################


class GraduateStudentDeleteView(GraduateStudentEditMixin, DeleteView):
    success_url = reverse_lazy("gradstudent-list")


graduate_student_delete = permission_required(
    "graduate_students.delete_graduatestudent"
)(GraduateStudentDeleteView.as_view())

#######################################################################


def sendfile(request, **kwargs):
    """
    Secure media file access
    Protocol:
        - application requires ``conf`` module with ``use_sendfile`` setting.
        - model manager requires: ``get_for_user(user, ...)`` method
        - model requires: ``file`` FileField (the secure file); should use
                          a custom storage path not normally browser accessible.
                          ``download_action([bool] download)`` method [optional]
                                - to perform any needed modifications to
                                the instance, e.g., for download counters.
    """
    Model = Paperwork
    download = kwargs.pop("download", False)
    try:
        instance = Model.objects.get_for_user(request.user, **kwargs)
    except Model.DoesNotExist:
        raise Http404

    location = instance.file.path
    if not os.path.exists(location):
        # a final sanity check.
        raise Http404

    basename = instance.file.name
    content_length = instance.file.size

    if hasattr(instance, "download_action"):
        instance.download_action(download)

    if conf.get("use_sendfile") and not getattr(settings, "DEBUG", False):
        response = HttpResponse()
        # For Nginx
        response["X-Accel-Redirect"] = location
        # For Apache and Lighttpd v1.5
        response["X-Sendfile"] = location
        # For Lighttpd v1.4
        response["X-LIGHTTPD-send-file"] = location
    else:
        # fallback, for debugging.
        response = HttpResponse(open(location, "rb"))

    if download:
        disp_type = "attachment"
    else:
        disp_type = "inline"
    response["Content-Disposition"] = "{}; filename={}".format(disp_type, basename)
    response["Content-Length"] = str(content_length)

    contenttype, encoding = mimetypes.guess_type(basename)
    if contenttype:
        response["Content-type"] = contenttype
    return response


#######################################################################
