# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("graduate_students", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="graduatestudent",
            name="advisor",
            field=models.ManyToManyField(
                help_text=b'Only people with the "advisor" flag are shown.',
                related_name="supervisor",
                to="people.Person",
                blank=True,
            ),
        )
    ]
