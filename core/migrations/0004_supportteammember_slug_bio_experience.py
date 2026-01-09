# Generated migration for SupportTeamMember fields
# Handles case where slug field/index may already exist from previous failed deployment

from django.db import migrations, models
from django.utils.text import slugify
from django.db.utils import ProgrammingError


def generate_slugs(apps, schema_editor):
    """Generate slugs for existing support team members."""
    SupportTeamMember = apps.get_model('core', 'SupportTeamMember')
    for member in SupportTeamMember.objects.all():
        if not member.slug:
            base_slug = slugify(member.name) if member.name else 'member'
            slug = base_slug
            counter = 1
            while SupportTeamMember.objects.filter(slug=slug).exclude(pk=member.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            member.slug = slug
            member.save()


def add_fields_safely(apps, schema_editor):
    """Add fields safely, ignoring if they already exist."""
    from django.db import connection
    
    with connection.cursor() as cursor:
        # Check existing columns
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'core_supportteammember'
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        # Add slug if not exists
        if 'slug' not in existing_columns:
            cursor.execute("""
                ALTER TABLE core_supportteammember 
                ADD COLUMN slug VARCHAR(50) NOT NULL DEFAULT ''
            """)
        
        # Add bio if not exists
        if 'bio' not in existing_columns:
            cursor.execute("""
                ALTER TABLE core_supportteammember 
                ADD COLUMN bio TEXT NOT NULL DEFAULT ''
            """)
        
        # Add experience_years if not exists
        if 'experience_years' not in existing_columns:
            cursor.execute("""
                ALTER TABLE core_supportteammember 
                ADD COLUMN experience_years INTEGER NOT NULL DEFAULT 0
            """)


def make_slug_unique_safely(apps, schema_editor):
    """Add unique constraint to slug, ignoring if already exists."""
    from django.db import connection
    
    with connection.cursor() as cursor:
        try:
            # Try to create unique index (PostgreSQL) - IF NOT EXISTS handles duplicates
            cursor.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS core_supportteammember_slug_unique 
                ON core_supportteammember (slug)
            """)
        except ProgrammingError:
            pass  # Index already exists


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_doctor_order_alter_doctor_photo_and_more'),
    ]

    operations = [
        # Use RunPython to handle existing fields/indexes gracefully
        migrations.RunPython(add_fields_safely, migrations.RunPython.noop),
        migrations.RunPython(generate_slugs, migrations.RunPython.noop),
        migrations.RunPython(make_slug_unique_safely, migrations.RunPython.noop),
        
        # Use SeparateDatabaseAndState to sync Django's state with actual DB
        # The database operations are handled above, this just updates Django's knowledge
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name='supportteammember',
                    name='slug',
                    field=models.SlugField(blank=True, unique=True, help_text='URL-friendly name (auto-generated if blank)'),
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
            ],
            database_operations=[],  # Already handled above
        ),
    ]
