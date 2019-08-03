# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("people", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="Funding",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("active", models.BooleanField(default=True)),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name=b"creation time"
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True, verbose_name=b"last modification time"
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(
                        help_text=b"The total amount of funding for this period.",
                        max_digits=8,
                        decimal_places=2,
                    ),
                ),
                (
                    "comments",
                    models.CharField(
                        help_text=b"A short comment about the funding.",
                        max_length=250,
                        blank=True,
                    ),
                ),
                (
                    "start_date",
                    models.DateField(
                        help_text=b"The day the funding begins or occurs."
                    ),
                ),
                (
                    "end_date",
                    models.DateField(
                        help_text=b"Leave this blank for a one-time payment.",
                        null=True,
                        blank=True,
                    ),
                ),
            ],
            options={
                "ordering": ("start_date", "end_date"),
                "verbose_name_plural": "Funding",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="FundingSource",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("active", models.BooleanField(default=True)),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name=b"creation time"
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True, verbose_name=b"last modification time"
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                (
                    "ordering",
                    models.PositiveSmallIntegerField(
                        default=0,
                        help_text=b"Determines the sequence in the pull-down list.",
                    ),
                ),
            ],
            options={"ordering": ("ordering", "name")},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="GraduateStudent",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("active", models.BooleanField(default=True)),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name=b"creation time"
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True, verbose_name=b"last modification time"
                    ),
                ),
                (
                    "program",
                    models.CharField(
                        default=b"M",
                        help_text=b"You should not change this after a student has started their program. \n                                    If somebody does a second graduate degree, a new graduate student record should be created.",
                        max_length=1,
                        choices=[
                            (b"P", b"Ph.D."),
                            (b"M", b"M.Sc. Thesis"),
                            (b"N", b"M.Sc. Practicum"),
                            (b"D", b"M.Sc. Course Based"),
                            (b"Z", b"Pre-Masters"),
                            (b"C", b"M.Sc. Comprehensive"),
                        ],
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        default=b"P",
                        max_length=2,
                        choices=[
                            (b"P", b"Pending Student (not yet accepted)"),
                            (b"S", b"Current Student"),
                            (b"AW", b"Authorized Withdrawl"),
                            (b"CW", b"Compulsary Withdrawl"),
                            (b"VW", b"Voluntary Withdrawl"),
                            (b"G", b"Graduated"),
                        ],
                    ),
                ),
                ("start_date", models.DateField()),
                ("defense_date", models.DateField(null=True, blank=True)),
                ("graduation_date", models.DateField(null=True, blank=True)),
                (
                    "graduation_date_confirmed",
                    models.BooleanField(
                        default=False,
                        help_text=b"If this is <em>not</em> set, then the graduation is considered tentative, and will not be advertised.",
                    ),
                ),
                ("thesis_title", models.CharField(max_length=250, blank=True)),
                (
                    "advisor",
                    models.ManyToManyField(
                        help_text=b'Only people with the "advisor" flag are shown.',
                        related_name=b"supervisor",
                        null=True,
                        to="people.Person",
                        blank=True,
                    ),
                ),
                (
                    "person",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        help_text=b'Only people with the "gradstudent" flag are shown. \n                                    You should not change this after it has been set.',
                        to="people.Person",
                    ),
                ),
            ],
            options={"ordering": ("-program", "status", "person")},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Milestone",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("active", models.BooleanField(default=True)),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name=b"creation time"
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True, verbose_name=b"last modification time"
                    ),
                ),
                ("date", models.DateField(default=datetime.date.today)),
                (
                    "graduate_student",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        to="graduate_students.GraduateStudent",
                    ),
                ),
            ],
            options={"ordering": ["date"], "get_latest_by": "date"},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="MilestoneType",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("active", models.BooleanField(default=True)),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name=b"creation time"
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True, verbose_name=b"last modification time"
                    ),
                ),
                ("name", models.CharField(unique=True, max_length=100)),
                ("slug", models.SlugField(unique=True)),
            ],
            options={"ordering": ["name"]},
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="milestone",
            name="type",
            field=models.ForeignKey(
                on_delete=models.deletion.CASCADE, to="graduate_students.MilestoneType"
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="funding",
            name="graduate_student",
            field=models.ForeignKey(
                on_delete=models.deletion.CASCADE,
                to="graduate_students.GraduateStudent",
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="funding",
            name="source",
            field=models.ForeignKey(
                on_delete=models.deletion.CASCADE, to="graduate_students.FundingSource"
            ),
            preserve_default=True,
        ),
    ]
