import django.db.models.deletion
from django.db import migrations, models

import liquidaciones.models


class Migration(migrations.Migration):
    """Separada de 0010: los ALTER TABLE no pueden correr en la misma
    transacción que los UPDATE de la migración de datos (las FK diferidas
    dejan trigger events pendientes en Postgres)."""

    dependencies = [
        ("liquidaciones", "0011_poblar_monedas_liquidacion"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="liquidacion",
            name="moneda_valor_imponible_old",
        ),
        migrations.AlterField(
            model_name="liquidacion",
            name="moneda_valor_imponible",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="liquidaciones_valor_imponible",
                to="liquidaciones.moneda",
            ),
        ),
        migrations.AlterField(
            model_name="liquidacion",
            name="moneda_factura",
            field=models.ForeignKey(
                default=liquidaciones.models.get_default_moneda_factura,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="liquidaciones_factura",
                to="liquidaciones.moneda",
            ),
        ),
    ]
