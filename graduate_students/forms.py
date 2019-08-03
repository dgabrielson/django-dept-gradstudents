from __future__ import print_function, unicode_literals

import datetime
import mimetypes

from django import forms
from django.conf import settings
from django.contrib.admin import widgets
from django.forms import FileInput
from django.http import HttpResponse
from django.urls import reverse_lazy

from . import conf
from .models import GraduateStudent
from .utils import make_funding_spreadsheet

"""
Forms for the Graduate Students app
"""
#######################################################################

#######################################################################

SPREADSHEET_DOWNLOAD_FORMATS = conf.get("spreadsheet_formats")
DEFAULT_SPREADSHEET_FORMAT = conf.get("default_spreadsheet_format")

#######################################################################


class FundingReportForm(forms.Form):
    """
    Funding Report input form.
    """

    start_date = forms.DateField(required=True)
    end_date = forms.DateField(required=True)

    format_ = forms.ChoiceField(
        choices=SPREADSHEET_DOWNLOAD_FORMATS,
        label="Format",
        required=True,
        initial=DEFAULT_SPREADSHEET_FORMAT,
    )

    class Media:
        css = {"all": ("admin/css/widgets.css",)}

    # include_formulas = forms.BooleanField(required=False, initial=True,
    # label="Use Formulas",
    # help_text='Use formulas instead of values for computed marks.')

    def __init__(self, *args, **kwargs):
        super(FundingReportForm, self).__init__(*args, **kwargs)
        self.fields["start_date"].widget = widgets.AdminDateWidget()
        self.fields["end_date"].widget = widgets.AdminDateWidget()

    def get_result_data(self):
        """
        Assumed that is_valid() has been checked and is True.
        
        Returns the data stream for the spreadsheet.
        """
        return make_funding_spreadsheet(
            self.cleaned_data["start_date"],
            self.cleaned_data["end_date"],
            self.cleaned_data["format_"],
        )

    def on_success(self):
        """
        Assumed that is_valid() has been checked and is True.
        """
        filename = "funding-report_%s" % datetime.date.today()
        filename += "." + self.cleaned_data["format_"]
        content_type, encoding = mimetypes.guess_type(filename)
        stream = self.get_result_data()
        response = HttpResponse(content_type=content_type)
        response["Content-Disposition"] = "attachment; filename=" + filename
        response.write(stream)
        return response


#######################################################################


class GraduateStudentForm(forms.ModelForm):
    """
    Form for a graduate student record.
    """

    class Meta:
        model = GraduateStudent
        exclude = ["active"]
        widgets = {
            "advisor": widgets.FilteredSelectMultiple(
                verbose_name="advisors", is_stacked=False
            ),
            "start_date": widgets.AdminDateWidget,
            "defense_date": widgets.AdminDateWidget,
            "graduation_date": widgets.AdminDateWidget,
        }

    class Media:
        # Order matters!  Without ``extend = False``, the order is wrong,
        # and then the SelectFilter does not work.
        extend = False
        css = {
            "all": (
                "admin/css/widgets.css",
                "css/forms.css",
                "css/selector.css",
                "css/twoColumn.css",
            )
        }
        js = [
            conf.get("jsi18n_url"),
            "admin/js/core.js",
            "admin/js/vendor/jquery/jquery.js",
            "admin/js/jquery.init.js",
            "admin/js/SelectBox.js",
            "admin/js/SelectFilter2.js",
            "admin/js/calendar.js",
            "admin/js/admin/DateTimeShortcuts.js",
        ]

    def __init__(self, *args, **kwargs):
        result = super(GraduateStudentForm, self).__init__(*args, **kwargs)
        instance = getattr(self, "instance", None)
        if instance and instance.pk:
            # Do not change the person after this is set.
            self.fields["person"].widget = forms.HiddenInput()
        return result


#######################################################################


class NoUrlFileWidget(FileInput):
    """
    For files that use ``storage.NoUrlMixin``.
    """


#######################################################################
