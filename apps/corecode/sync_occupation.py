# Run this in your Django shell: `python manage.py shell`
from accounts.models import StaffUser

def sync_staffuser_occupations():
    staff_users = StaffUser.objects.all()
    for staff_user in staff_users:
        if staff_user.staff and staff_user.staff.occupation:
            if staff_user.occupation != staff_user.staff.occupation:
                print(f"Fixing {staff_user.username}: StaffUser.occupation={staff_user.occupation}, Staff.occupation={staff_user.staff.occupation}")
                staff_user.occupation = staff_user.staff.occupation
                staff_user.save()
            else:
                print(f"No fix needed for {staff_user.username}: Occupations match ({staff_user.occupation})")
        else:
            print(f"Skipping {staff_user.username}: No staff or staff.occupation")

# Run the function
sync_staffuser_occupations()