# Generated by Django 2.0.3 on 2018-03-09 17:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_populate_tools'),
    ]

    operations = [
        migrations.AlterField(
            model_name='edit',
            name='batch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='edits', to='store.Batch'),
        ),
        migrations.AlterField(
            model_name='edit',
            name='comment',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='edit',
            name='parsedcomment',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='tool',
            name='usergroupid',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='tool',
            name='userregex',
            field=models.CharField(blank=True, max_length=190, null=True),
        ),
    ]
