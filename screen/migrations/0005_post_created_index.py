from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('screen', '0004_post_image'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='post',
            index=models.Index(fields=['created_at'], name='screen_post_created_idx'),
        ),
    ]
