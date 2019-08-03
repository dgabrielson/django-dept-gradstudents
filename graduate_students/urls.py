from __future__ import print_function, unicode_literals

from django.conf.urls import url
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from people.models import Person

from . import views
from .models import GraduateStudent

"""
url patterns for Graduate Students app.
"""
#######################################################################

#######################################################################

urlpatterns = [
    url(
        r"^$",
        ListView.as_view(
            queryset=GraduateStudent.objects.active().prefetch_related("advisor")
        ),
        name="gradstudent-list",
    ),
    url(
        r"^advisor/$",
        ListView.as_view(
            queryset=Person.objects.active().filter(flags__slug="advisor"),
            template_name="graduate_students/advisor_list.html",
        ),
        name="gradstudent-advisor-list",
    ),
    url(
        r"^alumni/$",
        ListView.as_view(
            queryset=GraduateStudent.objects.alumni_filter()
            .active(status=None)
            .select_related("person")
            .prefetch_related("advisor"),
            template_name="graduate_students/alumni_list.html",
        ),
        name="gradstudent-alumni-list",
    ),
    url(r"^add/$", views.graduate_student_create, name="gradstudent-create"),
    url(
        r"^(?P<pk>\d+)/$",
        DetailView.as_view(model=GraduateStudent),
        name="gradstudent-detail",
    ),
    url(
        r"^(?P<pk>\d+)/edit/$", views.graduate_student_update, name="gradstudent-update"
    ),
    url(
        r"^(?P<pk>\d+)/delete/$",
        views.graduate_student_delete,
        name="gradstudent-delete",
    ),
]

#######################################################################
