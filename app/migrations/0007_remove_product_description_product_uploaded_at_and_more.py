# Generated by Django 5.0.3 on 2024-10-23 09:56

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_remove_productimage_product_delete_quality_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='description',
        ),
        migrations.AddField(
            model_name='product',
            name='uploaded_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2024, 10, 23, 9, 56, 16, 586444, tzinfo=datetime.timezone.utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='product',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='expiry_date',
            field=models.DateField(default=datetime.datetime(2024, 10, 23, 9, 56, 28, 738186, tzinfo=datetime.timezone.utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='product',
            name='farmer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='app.farmer'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='product/'),
        ),
        migrations.AlterField(
            model_name='product',
            name='quality',
            field=models.CharField(max_length=50),
        ),
    ]