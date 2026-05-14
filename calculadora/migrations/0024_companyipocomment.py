from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("calculadora", "0023_company_share_structure"),
    ]

    operations = [
        migrations.CreateModel(
            name="CompanyIpoComment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("alias", models.CharField(max_length=50)),
                ("body", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("update", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="comments", to="calculadora.companyipoupdate")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="ipo_comments", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["created_at"],
            },
        ),
    ]
