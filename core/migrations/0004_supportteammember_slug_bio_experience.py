# Generated migration for SupportTeamMember fields
# Handles case where slug field/index may already exist from previous failed deployment

from django.db import migrations, models
from django.utils.text import slugify
from django.db.utils import ProgrammingError


def add_fields_safely(apps, schema_editor):
    """Add fields safely, ignoring if they already exist."""
    with schema_editor.connection.cursor() as cursor:
        existing_columns = [column.name for column in schema_editor.connection.introspection.get_table_description(cursor, 'core_supportteammember')]
        
        # Add slug if not exists
        if 'slug' not in existing_columns:
            schema_editor.execute("ALTER TABLE core_supportteammember ADD COLUMN slug VARCHAR(50) NOT NULL DEFAULT ''")
        
        # Add bio if not exists
        if 'bio' not in existing_columns:
            schema_editor.execute("ALTER TABLE core_supportteammember ADD COLUMN bio TEXT NOT NULL DEFAULT ''")
        
        # Add experience_years if not exists
        if 'experience_years' not in existing_columns:
            schema_editor.execute("ALTER TABLE core_supportteammember ADD COLUMN experience_years INTEGER NOT NULL DEFAULT 0")


def generate_slugs(apps, schema_editor):
    """Generate slugs for existing support team members using raw SQL."""
    with schema_editor.connection.cursor() as cursor:
        # Get all members
        cursor.execute("SELECT id, name, slug FROM core_supportteammember")
        members = cursor.fetchall()
        
        for member_id, name, current_slug in members:
            if not current_slug:  # Empty slug
                base_slug = slugify(name) if name else 'member'
                slug = base_slug
                counter = 1
                
                # Check for uniqueness
                while True:
                    cursor.execute(
                        "SELECT COUNT(*) FROM core_supportteammember WHERE slug = %s AND id != %s",
                        [slug, member_id]
                    )
                    count = cursor.fetchone()[0]
                    if count == 0:
                        break
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                
                cursor.execute(
                    "UPDATE core_supportteammember SET slug = %s WHERE id = %s",
                    [slug, member_id]
                )


def make_slug_unique_safely(apps, schema_editor):
    """Add unique constraint to slug, ignoring if already exists."""
    try:
        schema_editor.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS core_supportteammember_slug_unique ON core_supportteammember (slug)"
        )
    except ProgrammingError:
        pass  # Index already exists


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_doctor_order_alter_doctor_photo_and_more'),
    ]

    operations = [
        # Step 1: Add columns at DB level safely
        migrations.RunPython(add_fields_safely, migrations.RunPython.noop),
        
        # Step 2: Generate slugs using raw SQL (no model dependency)
        migrations.RunPython(generate_slugs, migrations.RunPython.noop),
        
        # Step 3: Add unique constraint safely
        migrations.RunPython(make_slug_unique_safely, migrations.RunPython.noop),
        
        # Step 4: Update Django's state to know about these fields
        # No DB operations - just syncing Django's knowledge
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
