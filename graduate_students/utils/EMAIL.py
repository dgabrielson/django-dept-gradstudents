#!/usr/bin/env python
"""
EMAIL.py

Generate a listing of department relevant email addresses/lists
"""
from __future__ import print_function, unicode_literals

from django.template.defaultfilters import slugify
from graduate_students.models import GraduateStudent


def main():
    result = {}

    # individual aliases
    #     for student in GraduateStudent.objects.active():
    #         if student.person.email is None:
    #             continue
    #         slug = student.person.slug or slugify(student.person.cn)
    #         slug_email = slug.replace('-', '.')
    #         base_email = student.person.email.address.split('@')[0].lower()
    #         if base_email not in result.keys():
    #             result[base_email] = student.person.email.address
    #         if slug not in result.keys():
    #             result[slug_email] = student.person.email.address

    # groups
    result["phd-students"] = ",".join(
        set(
            list(
                [
                    o.person.email.address
                    for o in GraduateStudent.objects.phd_filter().active()
                    if o.person.email is not None
                ]
            )
        )
    )
    result["msc-students"] = ",".join(
        set(
            list(
                [
                    o.person.email.address
                    for o in GraduateStudent.objects.msc_filter().active()
                    if o.person.email is not None
                ]
            )
        )
    )
    result["grad-students"] = ",".join(
        [e + "@stats.umanitoba.ca" for e in ["phd-students", "msc-students"]]
    )

    return result
