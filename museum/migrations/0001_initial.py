# Generated by Django 3.2.8 on 2022-04-11 10:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Museum',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('museumname', models.TextField()),
                ('location', models.TextField()),
                ('description', models.TextField()),
                ('museumurl', models.TextField()),
                ('coverimage', models.TextField()),
                ('museumtype', models.CharField(blank=True, default='', max_length=255)),
                ('priority', models.IntegerField(default=0)),
                ('inserted', models.DateTimeField(auto_now_add=True)),
                ('edited', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Museums Information Table',
                'db_table': 'museums',
                'ordering': ('-priority',),
            },
        ),
        migrations.CreateModel(
            name='MuseumEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('eventname', models.TextField()),
                ('eventinfo', models.TextField()),
                ('eventurl', models.TextField()),
                ('eventperiod', models.CharField(blank=True, default='', max_length=255)),
                ('eventstartdate', models.DateTimeField()),
                ('eventenddate', models.DateTimeField()),
                ('coverimage', models.TextField()),
                ('eventstatus', models.CharField(blank=True, default='', max_length=20)),
                ('eventtype', models.CharField(blank=True, default='', max_length=255)),
                ('presenter', models.CharField(blank=True, default='', max_length=255)),
                ('priority', models.IntegerField(default=0)),
                ('inserted', models.DateTimeField(auto_now_add=True)),
                ('edited', models.DateTimeField(auto_now=True)),
                ('museum', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='museum.museum')),
            ],
            options={
                'verbose_name': 'Museum Events Information Table',
                'db_table': 'museumevents',
                'ordering': ('-priority',),
            },
        ),
        migrations.CreateModel(
            name='MuseumPieces',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('piecename', models.TextField()),
                ('creationdate', models.CharField(blank=True, default='', max_length=10)),
                ('artistname', models.CharField(blank=True, default='', max_length=255)),
                ('artistbirthyear', models.CharField(blank=True, default='', max_length=4)),
                ('artistdeathyear', models.CharField(blank=True, default='', max_length=4)),
                ('artistnationality', models.CharField(blank=True, default='', max_length=200)),
                ('medium', models.TextField()),
                ('size', models.CharField(blank=True, default='', max_length=255)),
                ('edition', models.CharField(blank=True, default='', max_length=255)),
                ('signature', models.TextField()),
                ('description', models.TextField()),
                ('detailurl', models.TextField()),
                ('provenance', models.TextField()),
                ('literature', models.TextField()),
                ('exhibited', models.TextField()),
                ('status', models.CharField(blank=True, default='', max_length=40)),
                ('image1', models.TextField()),
                ('image2', models.TextField()),
                ('image3', models.TextField()),
                ('image4', models.TextField()),
                ('priority', models.IntegerField(default=0)),
                ('inserted', models.DateTimeField(auto_now_add=True)),
                ('edited', models.DateTimeField(auto_now=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='museum.museumevent')),
                ('museum', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='museum.museum')),
            ],
            options={
                'verbose_name': 'Museum Pieces (artworks) Information Table',
                'db_table': 'museumpieces',
                'ordering': ('-priority',),
            },
        ),
        migrations.CreateModel(
            name='MuseumArticles',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('articlename', models.TextField()),
                ('writername', models.CharField(blank=True, default='', max_length=255)),
                ('articletype', models.CharField(blank=True, default='', max_length=255)),
                ('detailurl', models.TextField()),
                ('published', models.TextField()),
                ('thumbimage', models.TextField()),
                ('priority', models.IntegerField(default=0)),
                ('inserted', models.DateTimeField(auto_now_add=True)),
                ('edited', models.DateTimeField(auto_now=True)),
                ('museum', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='museum.museum')),
            ],
            options={
                'verbose_name': 'Museum Articles Information Table',
                'db_table': 'museumarticles',
                'ordering': ('-priority',),
            },
        ),
    ]
