# Generated by Django 5.0.4 on 2024-05-17 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0015_userextended_status_alter_userextended_is_active_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="service",
            name="date_reservation",
            field=models.DateField(
                blank=True, null=True, verbose_name="Fecha de reserva"
            ),
        ),
        migrations.AlterField(
            model_name="service",
            name="charge",
            field=models.BooleanField(default=False, verbose_name="Carga"),
        ),
        migrations.AlterField(
            model_name="service",
            name="disability",
            field=models.BooleanField(default=False, verbose_name="Discapacidad"),
        ),
        migrations.AlterField(
            model_name="service",
            name="passengers",
            field=models.BooleanField(default=False, verbose_name="Pasajeros"),
        ),
        migrations.AlterField(
            model_name="service",
            name="pet",
            field=models.BooleanField(default=False, verbose_name="Mascota"),
        ),
    ]