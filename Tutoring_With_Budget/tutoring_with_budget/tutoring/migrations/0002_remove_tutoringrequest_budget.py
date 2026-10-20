from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("tutoring", "0001_initial")]

    # Preserve existing budget values when upgrading the original project.
    # Installations that already ran the old removal are repaired by 0003.
    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[migrations.RemoveField(model_name="tutoringrequest", name="budget")],
            database_operations=[],
        ),
    ]
