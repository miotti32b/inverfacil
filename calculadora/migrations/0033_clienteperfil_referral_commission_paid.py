from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("calculadora", "0032_investorprofile_offeringevidence_offeringquestion"),
    ]

    operations = [
        migrations.AddField(
            model_name="clienteperfil",
            name="referral_commission_paid",
            field=models.BooleanField(default=False),
        ),
    ]
