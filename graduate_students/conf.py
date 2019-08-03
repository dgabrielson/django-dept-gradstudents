from __future__ import print_function, unicode_literals

from django.conf import settings
from django.urls import reverse_lazy

from .storage import PaperworkFileSystemStorage

"""
The DEFAULT configuration is loaded when the CONFIG_NAME dictionary
is not present in your settings.

All valid application settings must have a default value.
"""

CONFIG_NAME = "GRADUATE_STUDENT_CONFIG"  # must be uppercase!

DEFAULT = {
    # The person type slugs for graduate students, and the corresponding
    #   filters.  Another option would be:
    #   ``[("grad-students", "active"),]``
    #   if your directory does not distinguish between phd/msc students.
    # This is used to maintain directory synchronization, so if you
    #   don't use the directory app with graduate student, you can
    #   ignore this setting.
    "directory:typefilter_list": None,
    # the number of days *before* the graduation date to remove
    # graduate students from the directory.
    "directory:graduation_date_cutoff": 35,
    # the number of days *after* the defense, if any...
    "directory:defense_date_grace": 14,
    # slugs for person flags that denote appropriate advisors
    "advisor_flags": ["advisor"],
    # Define the list of available spreadsheet formats, and their descriptions.
    # Note that python-spreadsheet *must* understand the format string.
    # (optional)
    "spreadsheet_formats": (
        ("csv", "Comma Seperated Values"),
        ("xls", "Microsoft Excel"),
        ("xlsx", "Microsoft Excel XML"),  # warning: xlsx has issues with formulas.
        ("ods", "OpenOffice Spreadsheet"),
    ),
    # Extra graduate student fields to include in the funding report
    "spreadsheet_extra_fields": ["get_program_display", "start_date"],
    # Define the default spreadsheet format in the form.
    # (optional)
    "default_spreadsheet_format": "xlsx",
    # Define the number of days from the start of the current month
    # to show upcoming graduates. (Used by the context_processor.)
    # (optional)
    "upcoming_grads_days": 61,
    # define where to load the form assets from:
    #'form_static_url': settings.STATIC_URL + 'admin/',
    # Yo'll probably want to define this for your site,
    # e.g., url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', name='site-jsi18n'),
    "jsi18n_url": reverse_lazy("admin:jsi18n"),
    # When the graduate student flag is set on a person record, should
    #   a graduate student record automatically be created?
    "autocreate_on_gradstudent_flag": True,
    # 'storage_class' is the storage class backend for files.
    "storage_class": PaperworkFileSystemStorage,
    # This path *should not* be browsable from the webserver.
    # (required; do not use this default!)
    "storage_kwargs": {"location": "/dev/null"},
    # 'upload_to' is the variable portion of the path where files are stored.
    # (optional; default: '%Y/%m/%d')
    "upload_to": "%Y/%m/%d",
    # Enable Sendfile acceleration on servers that support it.
    # Note that sendfile is disabled when DEBUG == True.
    # (optional; default: False)
    "use_sendfile": False,
    # Experimental features
    "funding:allow-historical": False,
}


def get(setting):
    """
    get(setting) -> value

    setting should be a string representing the application settings to
    retrieve.
    """
    assert setting in DEFAULT, "the setting %r has no default value" % setting
    app_settings = getattr(settings, CONFIG_NAME, DEFAULT)
    return app_settings.get(setting, DEFAULT[setting])


def get_all():
    """
    Return all current settings as a dictionary.
    """
    app_settings = getattr(settings, CONFIG_NAME, DEFAULT)
    return dict(
        [(setting, app_settings.get(setting, DEFAULT[setting])) for setting in DEFAULT]
    )
