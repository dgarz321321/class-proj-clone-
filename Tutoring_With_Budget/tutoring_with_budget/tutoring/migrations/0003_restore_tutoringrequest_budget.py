from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import migrations, models


def ensure_budget_column(apps, schema_editor):
    request_model = apps.get_model("tutoring", "TutoringRequest")
    with schema_editor.connection.cursor() as cursor:
        columns = schema_editor.connection.introspection.get_table_description(
            cursor, request_model._meta.db_table
        )
    if "budget" not in {column.name for column in columns}:
        field = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("0.00"))
        field.set_attributes_from_name("budget")
        schema_editor.add_field(request_model, field)


class Migration(migrations.Migration):
    dependencies = [("tutoring", "0002_remove_tutoringrequest_budget")]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[migrations.RunPython(ensure_budget_column, migrations.RunPython.noop)],
            state_operations=[migrations.AddField(
                model_name="tutoringrequest",
                name="budget",
                field=models.DecimalField(
                    max_digits=6, decimal_places=2,
                    help_text="Max hourly rate in USD",
                    validators=[MinValueValidator(Decimal("0.00"))],
                ),
            )],
        ),
    ]
