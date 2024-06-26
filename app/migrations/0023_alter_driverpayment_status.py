# Generated by Django 5.0.4 on 2024-06-12 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0022_driverpayment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='driverpayment',
            name='status',
            field=models.CharField(choices=[('approved', 'Transacción aprobada'), ('failed', 'Transacción fallida'), ('declined', 'Transacción rechazada'), ('pending', 'Transacción pendiente')], default='approved', verbose_name='Estado'),
        ),
    ]
