from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ("calculadora", "0005_add_text_blocks_resultadoia"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE calculadora_resultadoia
            ADD COLUMN IF NOT EXISTS bloque_estructura TEXT DEFAULT '';
            """,
            reverse_sql="""
            ALTER TABLE calculadora_resultadoia
            DROP COLUMN IF EXISTS bloque_estructura;
            """
        ),
    ]
