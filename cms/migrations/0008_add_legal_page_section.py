# Generated migration to add LegalPageSection model

from django.db import migrations, models
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0007_seed_faqs'),
    ]

    operations = [
        migrations.CreateModel(
            name='LegalPageSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('page_type', models.CharField(choices=[('privacy', 'Privacy Policy'), ('terms', 'Terms of Service'), ('cookies', 'Cookie Policy')], default='privacy', help_text='Which legal page this section belongs to', max_length=50)),
                ('section_id', models.SlugField(help_text="URL-friendly ID for this section (e.g., 'data-protection')", max_length=100)),
                ('title', models.CharField(max_length=255)),
                ('content', wagtail.fields.RichTextField(help_text='Section content with formatting')),
                ('order', models.IntegerField(default=0, help_text='Display order within the page')),
            ],
            options={
                'verbose_name': 'Legal Page Section',
                'verbose_name_plural': 'Legal Page Sections',
                'ordering': ['page_type', 'order', 'title'],
            },
        ),
    ]
