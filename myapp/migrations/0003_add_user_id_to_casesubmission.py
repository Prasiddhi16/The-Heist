from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_remove_suspect_age_remove_suspect_risk_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='casesubmission',
            name='user_id',
            field=models.IntegerField(blank=True, null=True, db_column='user_id'),
        ),
    ]