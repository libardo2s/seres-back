# Generated by Django 5.0.4 on 2024-05-25 20:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0018_rename_time_reservation_service_reservation_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='DriverBalance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('total_value', models.FloatField(default=0.0, verbose_name='Total Balance Conductor')),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='balance_driver', to='app.userextended')),
            ],
        ),
        migrations.CreateModel(
            name='DriverBalanceDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('value', models.FloatField(default=0.0, verbose_name='Valor recarga - uso')),
                ('type', models.CharField(choices=[('recarga', 'Recarga'), ('servicio', 'Servicio')], default='recarga', verbose_name='Tipo de balance')),
                ('driver_balance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='driver_balance', to='app.driverbalance')),
            ],
        ),
    ]
