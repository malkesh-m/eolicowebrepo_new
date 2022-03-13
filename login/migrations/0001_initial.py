# Generated by Django 3.2.12 on 2022-03-05 17:22

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import login.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Privilege',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('privname', models.CharField(max_length=50, unique=True)),
                ('privdesc', models.TextField(default='')),
                ('createdate', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Authorization Information',
                'verbose_name_plural': 'Privileges Information',
                'db_table': 'Auth_privilege',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstname', models.CharField(max_length=100)),
                ('middlename', models.CharField(max_length=20)),
                ('lastname', models.CharField(max_length=100)),
                ('displayname', models.CharField(max_length=100, unique=True)),
                ('password', models.CharField(max_length=100)),
                ('emailid', models.EmailField(max_length=254, unique=True, validators=[django.core.validators.EmailValidator()])),
                ('active', models.BooleanField(default=False, help_text='Specifies whether the user is an active member or not.')),
                ('istest', models.BooleanField(default=False, help_text='Specifies whether the user object is a result of some testing or not.')),
                ('joindate', models.DateTimeField(auto_now_add=True)),
                ('sex', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('U', 'Undisclosed')], default='U', max_length=3)),
                ('usertype', models.CharField(choices=[('CORP', 'Corporate'), ('CONS', 'Consultant'), ('ACAD', 'Academic'), ('CERT', 'Certification')], max_length=4)),
                ('mobileno', models.CharField(blank=True, max_length=12)),
                ('userpic', models.ImageField(help_text="Path to user's profile image.", upload_to=login.models.profpicpath)),
                ('newuser', models.BooleanField(default=False, help_text="False if user hasn't validated her/his email address")),
            ],
            options={
                'verbose_name': 'User Information Table',
                'db_table': 'Auth_user',
            },
        ),
        migrations.CreateModel(
            name='UserPrivilege',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lastmod', models.DateTimeField(auto_now=True)),
                ('status', models.BooleanField(default=True)),
                ('privilege', models.ForeignKey(db_column='privilegeid_id', on_delete=django.db.models.deletion.CASCADE, to='login.privilege')),
                ('user', models.ForeignKey(db_column='userid_id', on_delete=django.db.models.deletion.CASCADE, to='login.user')),
            ],
            options={
                'verbose_name': 'User Privileges Information',
                'db_table': 'Auth_userprivilege',
            },
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sessioncode', models.CharField(max_length=50, unique=True)),
                ('status', models.BooleanField(default=True)),
                ('starttime', models.DateTimeField(auto_now_add=True)),
                ('endtime', models.DateTimeField(default=None)),
                ('sourceip', models.GenericIPAddressField(help_text="IP of the client's/user's host")),
                ('istest', models.BooleanField(default=False)),
                ('useragent', models.CharField(default='', help_text='Signature of the browser of the client/user', max_length=255)),
                ('user', models.ForeignKey(db_column='userid_id', on_delete=django.db.models.deletion.CASCADE, to='login.user')),
            ],
            options={
                'verbose_name': 'Session Information Table',
                'db_table': 'Auth_session',
            },
        ),
    ]
