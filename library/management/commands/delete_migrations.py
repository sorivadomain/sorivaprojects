from django.core.management.base import BaseCommand
import os
import glob

class Command(BaseCommand):
    help = 'Deletes all migration files in the library app'

    def handle(self, *args, **options):
        # Get path to migrations directory
        migrations_dir = os.path.join("library", "migrations")
        
        # Find all .py files except __init__.py
        migration_files = glob.glob(os.path.join(migrations_dir, "[0-9]*.py"))
        
        # Delete the files
        for file in migration_files:
            try:
                os.remove(file)
                self.stdout.write(self.style.SUCCESS(f'Deleted {file}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error deleting {file}: {e}'))

        self.stdout.write(self.style.SUCCESS('Successfully deleted all library migrations'))
