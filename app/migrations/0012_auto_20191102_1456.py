# Generated by Django 2.2.4 on 2019-11-02 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_baseprice'),
    ]

    operations = [
        migrations.AddField(
            model_name='userextended',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Conductor'),
        ),
        migrations.AlterField(
            model_name='userextended',
            name='birth_date',
            field=models.DateField(blank=True, null=True, verbose_name='Fecha de nacimiento'),
        ),
        migrations.AlterField(
            model_name='userextended',
            name='is_driver',
            field=models.BooleanField(default=False, null=True, verbose_name='Conductor'),
        ),
        migrations.AlterField(
            model_name='userextended',
            name='phone',
            field=models.CharField(max_length=10, unique=True, verbose_name='Telefono'),
        ),
    ]