from django.core.management.base import BaseCommand
from django.db.models import Q
from students.models import Student
import unicodedata


class Command(BaseCommand):
    help = 'Fix encoding issues in student names (e.g., â€– appearing instead of proper dashes)'

    def handle(self, *args, **options):
        """
        This command fixes common encoding issues in student names:
        - â€– (mojibake en-dash) → – or space
        - â€" (mojibake em-dash) → — or space
        - Other common UTF-8 encoding issues
        """
        
        # Common encoding issues to fix
        encoding_issues = {
            'â€–': '–',  # en-dash mojibake
            'â€"': '—',  # em-dash mojibake
            'â€™': "'",  # apostrophe mojibake
            'â€œ': '"',  # left quote mojibake
            'â€\x9d': '"',  # right quote mojibake
            'Â': '',  # Non-breaking space mojibake
        }
        
        fixed_count = 0
        students = Student.objects.all()
        
        for student in students:
            original_first = student.first_name
            original_middle = student.middle_name
            original_last = student.last_name
            
            # Fix first name
            for bad_char, good_char in encoding_issues.items():
                student.first_name = student.first_name.replace(bad_char, good_char)
                student.middle_name = student.middle_name.replace(bad_char, good_char)
                student.last_name = student.last_name.replace(bad_char, good_char)
            
            # Normalize whitespace
            student.first_name = ' '.join(student.first_name.split())
            student.middle_name = ' '.join(student.middle_name.split())
            student.last_name = ' '.join(student.last_name.split())
            
            # Check if any changes were made
            if (original_first != student.first_name or 
                original_middle != student.middle_name or 
                original_last != student.last_name):
                student.save()
                fixed_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Fixed: {original_first} {original_middle} {original_last} → "
                        f"{student.first_name} {student.middle_name} {student.last_name}"
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Successfully fixed encoding issues in {fixed_count} student records.')
        )
