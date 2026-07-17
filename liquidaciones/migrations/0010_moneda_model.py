import django.db.models.deletion
from django.db import migrations, models

import liquidaciones.models

MONEDAS = [
    ("USD", "USD"),
    ("EURO", "EURO"),
    ("PYG", "Guaraníes"),
    ("BRL", "Reales Brasileños"),
]


def crear_monedas(apps, schema_editor):
    Moneda = apps.get_model("liquidaciones", "Moneda")
    for codigo, nombre in MONEDAS:
        Moneda.objects.get_or_create(codigo=codigo, defaults={"nombre": nombre})


def eliminar_monedas(apps, schema_editor):
    Moneda = apps.get_model("liquidaciones", "Moneda")
    Moneda.objects.filter(codigo__in=[codigo for codigo, _ in MONEDAS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        (
            "liquidaciones",
            "0009_rename_tipo_cambio_liquidacion_tipo_cambio_despacho_and_more",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="Moneda",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("codigo", models.CharField(max_length=10, unique=True)),
                ("nombre", models.CharField(max_length=50)),
            ],
            options={
                "verbose_name": "Moneda",
                "verbose_name_plural": "Monedas",
                "ordering": ["nombre"],
            },
        ),
        migrations.RunPython(crear_monedas, eliminar_monedas),
        migrations.RenameField(
            model_name="liquidacion",
            old_name="moneda_valor_imponible",
            new_name="moneda_valor_imponible_old",
        ),
        migrations.AddField(
            model_name="liquidacion",
            name="moneda_valor_imponible",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="liquidaciones_valor_imponible",
                to="liquidaciones.moneda",
            ),
        ),
        migrations.AddField(
            model_name="liquidacion",
            name="moneda_factura",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="liquidaciones_factura",
                to="liquidaciones.moneda",
            ),
        ),
    ]
