# Generated by Django 3.1.7 on 2021-03-20 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ESP8266',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('macaddress', models.CharField(default='00:11:22:33:44:55', max_length=17)),
                ('multiplier', models.SmallIntegerField(help_text='The number indicates the important of heating (e.g. Cellar = 1, Living Room = 5)')),
                ('location', models.CharField(choices=[('inside', 'inside'), ('outside', 'outside')], default='inside', max_length=10)),
                ('expirytime', models.SmallIntegerField(default=3600, help_text='Time to expire temperatures in seconds if the device is powered off')),
            ],
        ),
        migrations.CreateModel(
            name='WirelessTemp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('macaddress', models.CharField(default='CC', max_length=4)),
                ('multiplier', models.SmallIntegerField(help_text='The number indicates the important of heating (e.g. Cellar = 1, Living Room = 5)')),
                ('location', models.CharField(choices=[('inside', 'inside'), ('outside', 'outside')], default='inside', max_length=10)),
                ('expirytime', models.SmallIntegerField(default=3600, help_text='Time to expire temperatures in seconds if the device is powered off')),
            ],
        ),
    ]
