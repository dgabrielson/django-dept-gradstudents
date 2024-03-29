# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-27 20:40
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("graduate_students", "0005_auto_20170602_1055")]

    operations = [
        migrations.AlterModelOptions(
            name="graduatestudent",
            options={
                "base_manager_name": "objects",
                "ordering": ("-program", "-status", "person"),
            },
        ),
        migrations.AddField(
            model_name="graduatestudent",
            name="thesis_url",
            field=models.URLField(
                blank=True, help_text="(Optional) a link to the thesis."
            ),
        ),
        migrations.AlterField(
            model_name="funding",
            name="amount",
            field=models.DecimalField(
                decimal_places=2,
                help_text="The total amount of funding for this period.",
                max_digits=8,
            ),
        ),
        migrations.AlterField(
            model_name="funding",
            name="comments",
            field=models.CharField(
                blank=True,
                help_text="A short comment about the funding.",
                max_length=250,
            ),
        ),
        migrations.AlterField(
            model_name="funding",
            name="created",
            field=models.DateTimeField(auto_now_add=True, verbose_name="creation time"),
        ),
        migrations.AlterField(
            model_name="funding",
            name="end_date",
            field=models.DateField(
                blank=True,
                help_text="Leave this blank for a one-time payment.",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="funding",
            name="modified",
            field=models.DateTimeField(
                auto_now=True, verbose_name="last modification time"
            ),
        ),
        migrations.AlterField(
            model_name="funding",
            name="start_date",
            field=models.DateField(help_text="The day the funding begins or occurs."),
        ),
        migrations.AlterField(
            model_name="fundingsource",
            name="created",
            field=models.DateTimeField(auto_now_add=True, verbose_name="creation time"),
        ),
        migrations.AlterField(
            model_name="fundingsource",
            name="modified",
            field=models.DateTimeField(
                auto_now=True, verbose_name="last modification time"
            ),
        ),
        migrations.AlterField(
            model_name="fundingsource",
            name="ordering",
            field=models.PositiveSmallIntegerField(
                default=0, help_text="Determines the sequence in the pull-down list."
            ),
        ),
        migrations.AlterField(
            model_name="graduatestudent",
            name="advisor",
            field=models.ManyToManyField(
                blank=True,
                help_text='Only people with the "advisor" flag are shown.',
                related_name="supervisor",
                to="people.Person",
            ),
        ),
        migrations.AlterField(
            model_name="graduatestudent",
            name="created",
            field=models.DateTimeField(auto_now_add=True, verbose_name="creation time"),
        ),
        migrations.AlterField(
            model_name="graduatestudent",
            name="graduation_date_confirmed",
            field=models.BooleanField(
                default=False,
                help_text="If this is <em>not</em> set, then the graduation is considered tentative, and will not be advertised.",
            ),
        ),
        migrations.AlterField(
            model_name="graduatestudent",
            name="modified",
            field=models.DateTimeField(
                auto_now=True, verbose_name="last modification time"
            ),
        ),
        migrations.AlterField(
            model_name="graduatestudent",
            name="person",
            field=models.ForeignKey(
                help_text='Only people with the "gradstudent" flag are shown.\n                                    You should not change this after it has been set.',
                on_delete=django.db.models.deletion.PROTECT,
                to="people.Person",
            ),
        ),
        migrations.AlterField(
            model_name="graduatestudent",
            name="program",
            field=models.CharField(
                choices=[
                    ("P", "Ph.D."),
                    ("M", "M.Sc. Thesis"),
                    ("N", "M.Sc. Practicum"),
                    ("D", "M.Sc. Course Based"),
                    ("Z", "Pre-Masters"),
                    ("C", "M.Sc. Comprehensive"),
                ],
                default="M",
                help_text="You should not change this after a student has started their program.\n                                    If somebody does a second graduate degree, a new graduate student record should be created.",
                max_length=1,
            ),
        ),
        migrations.AlterField(
            model_name="graduatestudent",
            name="status",
            field=models.CharField(
                choices=[
                    ("P", "Pending Student (not yet accepted)"),
                    ("S", "Current Student"),
                    ("AW", "Authorized Withdrawl"),
                    ("CW", "Compulsary Withdrawl"),
                    ("VW", "Voluntary Withdrawl"),
                    ("G", "Graduated"),
                    ("C", "Completed (Pre-MSc)"),
                ],
                default="P",
                max_length=2,
            ),
        ),
        migrations.AlterField(
            model_name="milestone",
            name="created",
            field=models.DateTimeField(auto_now_add=True, verbose_name="creation time"),
        ),
        migrations.AlterField(
            model_name="milestone",
            name="modified",
            field=models.DateTimeField(
                auto_now=True, verbose_name="last modification time"
            ),
        ),
        migrations.AlterField(
            model_name="milestonetype",
            name="created",
            field=models.DateTimeField(auto_now_add=True, verbose_name="creation time"),
        ),
        migrations.AlterField(
            model_name="milestonetype",
            name="modified",
            field=models.DateTimeField(
                auto_now=True, verbose_name="last modification time"
            ),
        ),
    ]
