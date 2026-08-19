# Generated manually for overall_rating field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0005_restaurant_delivery_time_restaurant_email_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='overall_rating',
            field=models.FloatField(default=0.0, help_text='Overall star rating (0.0 to 5.0)'),
        ),
    ]
