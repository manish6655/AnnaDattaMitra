# Generated by Django 5.0.3 on 2024-10-23 08:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_quality_product_created_at_product_expiry_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productimage',
            name='product',
        ),
        migrations.DeleteModel(
            name='Quality',
        ),
        migrations.AddField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='products/images/'),
        ),
        migrations.AlterField(
            model_name='product',
            name='expiry_date',
            field=models.DateField(null=True),
        ),
        migrations.DeleteModel(
            name='ProductImage',
        ),
    ]
