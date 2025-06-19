from django.db import migrations, models
import django.core.validators  # Add this import

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0002_initial'),  # Keep your actual previous migration
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='confirmation_code',
            field=models.CharField(
                max_length=6,
                null=True,
                blank=True,
                validators=[django.core.validators.RegexValidator(
                    message='Confirmation code must be exactly 6 digits.',
                    regex='^\\d{6}$'
                )]
            ),
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_agreed_to_terms',
            field=models.BooleanField(
                default=False,
                help_text='User must agree to terms to complete signup.'
            ),
        ),
    ]
