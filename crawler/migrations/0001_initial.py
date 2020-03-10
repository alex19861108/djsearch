# Generated by Django 3.0.4 on 2020-03-08 05:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('name', models.CharField(db_index=True, max_length=20, primary_key=True, serialize=False, unique=True, verbose_name='英文名, 唯一标识')),
                ('cn_name', models.CharField(max_length=20, unique=True, verbose_name='中文名')),
                ('config', models.TextField(verbose_name='资源配置')),
                ('mapping', models.TextField(verbose_name='ES中的mapping配置')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='接入时间')),
                ('contact', models.CharField(max_length=20, verbose_name='联系人')),
                ('desc', models.TextField(verbose_name='资源描述')),
                ('deleted', models.BooleanField(default=False, verbose_name='逻辑删除标记')),
                ('order', models.IntegerField(default=0, verbose_name='排序序号')),
            ],
            options={
                'db_table': 'resource',
            },
        ),
    ]