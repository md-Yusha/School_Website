from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('school', '0006_remove_feeitem_category_remove_feeitem_transaction_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='registration_number',
            field=models.CharField(max_length=20, unique=True, help_text="Student's unique registration number", null=True),
        ),
    ] 