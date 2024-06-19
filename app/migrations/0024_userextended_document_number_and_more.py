# Generated by Django 5.0.4 on 2024-06-18 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0023_alter_driverpayment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='userextended',
            name='document_number',
            field=models.CharField(blank=True, max_length=12, null=True, verbose_name='Número de documento'),
        ),
        migrations.AlterField(
            model_name='driverpayment',
            name='status',
            field=models.CharField(choices=[('created', 'Transacción creada'), ('approved', 'Transacción aprobada'), ('failed', 'Transacción fallida'), ('declined', 'Transacción rechazada'), ('pending', 'Transacción pendiente')], default='approved', verbose_name='Estado'),
        ),
    ]
