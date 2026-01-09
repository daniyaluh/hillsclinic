# Generated migration for SupportTeamMember fields

from django.db import migrations, models
from django.utils.text import slugify


def generate_slugs(apps, schema_editor):
    """Generate slugs for existing support team members."""
    SupportTeamMember = apps.get_model('core', 'SupportTeamMember')
    for member in SupportTeamMember.objects.all():
        if not member.slug:
            base_slug = slugify(member.name)
            slug = base_slug
            counter = 1
            while SupportTeamMember.objects.filter(slug=slug).exclude(pk=member.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            member.slug = slug
            member.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_doctor_order_alter_doctor_photo_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='supportteammember',
            name='slug',
            field=models.SlugField(blank=True, default='', help_text='URL-friendly name (auto-generated if blank)'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='supportteammember',
            name='bio',
            field=models.TextField(blank=True, help_text='Full biography (optional)'),
        ),
        migrations.AddField(
            model_name='supportteammember',
            name='experience_years',
            field=models.PositiveIntegerField(default=0, help_text='Years of experience'),
        ),
        migrations.RunPython(generate_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='supportteammember',
            name='slug',
            field=models.SlugField(blank=True, help_text='URL-friendly name (auto-generated if blank)', unique=True),
        ),
    ]
