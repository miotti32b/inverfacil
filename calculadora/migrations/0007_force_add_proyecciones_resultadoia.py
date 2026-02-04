from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ("calculadora", "0006_force_add_bloque_estructura"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE calculadora_resultadoia
            ADD COLUMN IF NOT EXISTS proy_pos jsonb DEFAULT '[]'::jsonb,
            ADD COLUMN IF NOT EXISTS proy_med jsonb DEFAULT '[]'::jsonb,
            ADD COLUMN IF NOT EXISTS proy_neg jsonb DEFAULT '[]'::jsonb;
            """,
            reverse_sql="""
            ALTER TABLE calculadora_resultadoia
            DROP COLUMN IF EXISTS proy_pos,
            DROP COLUMN IF EXISTS proy_med,
            DROP COLUMN IF EXISTS proy_neg;
            """
        ),
    ]
