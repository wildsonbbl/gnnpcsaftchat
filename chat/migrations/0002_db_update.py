from django.db import migrations

from ..models import database_compatibility


class Migration(migrations.Migration):

    dependencies = [
        ("chat", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(database_compatibility),
    ]
