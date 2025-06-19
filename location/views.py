from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.db import transaction
from .models import Location, SchoolDays
from django.core.exceptions import ValidationError
from datetime import time, datetime
import json
import math
from apps.corecode.decorators import admin_or_superuser_or_headmaster_or_second_master_required
from django.utils.decorators import method_decorator
from apps.corecode.decorators import restrict_to_authorized_roles

@method_decorator(restrict_to_authorized_roles, name='dispatch')
class LocationView(View):
    def get(self, request):
        location = Location.objects.first()
        schooldays = SchoolDays.objects.all().order_by('day')
        location_data = {
            'school_name': location.school_name,
            'latitude': float(location.latitude) if location else None,
            'longitude': float(location.longitude) if location else None,
        } if location else None
        schooldays_data = [
            {
                'day': day.day,
                'start_time': day.start_time.strftime('%I:%M %p') if day.start_time else '',
                'end_time': day.end_time.strftime('%I:%M %p') if day.end_time else ''
            } for day in schooldays
        ]
        print(f"LocationView: location={location}, location_data={location_data}, type(location_data)={type(location_data)}")
        print(f"LocationView: schooldays_data={schooldays_data}")
        print(f"LocationView: template context={{'location_data': {location_data}, 'schooldays_data': {json.dumps(schooldays_data)}}}")
        return render(request, 'location/location.html', {
            'location_data': location_data,
            'schooldays_data': json.dumps(schooldays_data),
        })

def save_location(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    try:
        data = json.loads(request.body)
        school_name = data.get('school_name')
        latitude = float(data.get('latitude'))
        longitude = float(data.get('longitude'))
        days = data.get('days', [])
        print(f"save_location: school_name={school_name}, latitude={latitude}, longitude={longitude}, days={days}")

        with transaction.atomic():
            location = Location.objects.first()
            if location:
                location.school_name = school_name
                location.latitude = latitude
                location.longitude = longitude
                location.save()
            else:
                location = Location.objects.create(
                    school_name=school_name,
                    latitude=latitude,
                    longitude=longitude
                )

            SchoolDays.objects.all().delete()
            for day_data in days:
                day = day_data.get('day')
                start_time_str = day_data.get('start_time')
                end_time_str = day_data.get('end_time')
                
                try:
                    start_time_dt = datetime.strptime(start_time_str, '%I:%M %p')
                    end_time_dt = datetime.strptime(end_time_str, '%I:%M %p')
                    start_time = time(start_time_dt.hour, start_time_dt.minute)
                    end_time = time(end_time_dt.hour, end_time_dt.minute)
                    print(f"save_location: Parsed {day}: start_time={start_time}, end_time={end_time}")
                except ValueError:
                    return JsonResponse({'error': f'Invalid time format for {day}'}, status=400)
                
                SchoolDays.objects.create(
                    day=day,
                    start_time=start_time,
                    end_time=end_time
                )

        return JsonResponse({
            'success': True,
            'location': {
                'school_name': location.school_name,
                'latitude': float(location.latitude),
                'longitude': float(location.longitude),
            },
            'schooldays': [
                {
                    'day': day.day,
                    'start_time': day.start_time.strftime('%I:%M %p'),
                    'end_time': day.end_time.strftime('%I:%M %p'),
                } for day in SchoolDays.objects.all().order_by('day')
            ]
        })

    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        print(f"save_location error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

from django.utils.decorators import method_decorator

@method_decorator(restrict_to_authorized_roles, name='dispatch')
def delete_location(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    try:
        with transaction.atomic():
            Location.objects.all().delete()
            SchoolDays.objects.all().delete()
        print("delete_location: Location and SchoolDays deleted")
        return JsonResponse({'success': True})
    except Exception as e:
        print(f"delete_location error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def get_current_location(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    try:
        location = Location.objects.first()
        if not location:
            return JsonResponse({'error': 'No school location set'}, status=400)
        
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            return R * c

        lat = float(request.GET.get('latitude'))
        lon = float(request.GET.get('longitude'))
        distance = haversine(float(location.latitude), float(location.longitude), lat, lon)
        print(f"get_current_location: lat={lat}, lon={lon}, distance={distance}")
        
        return JsonResponse({
            'success': True,
            'current_location': {'latitude': lat, 'longitude': lon},
            'school_location': {'latitude': float(location.latitude), 'longitude': float(location.longitude)},
            'distance_km': round(distance, 2)
        })
    except Exception as e:
        print(f"get_current_location error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)
    

class WelcomeView(View):
    def get(self, request):
        location = Location.objects.first()
        schooldays = SchoolDays.objects.all().order_by('day')
        location_data = {
            'school_name': location.school_name,
            'latitude': float(location.latitude) if location else None,
            'longitude': float(location.longitude) if location else None,
        } if location else None
        schooldays_data = [
            {
                'day': day.day,
                'start_time': day.start_time.strftime('%I:%M %p') if day.start_time else '',
                'end_time': day.end_time.strftime('%I:%M %p') if day.end_time else ''
            } for day in schooldays
        ]
        print(f"WelcomeView: location={location}, location_data={location_data}")
        print(f"WelcomeView: schooldays_data={schooldays_data}")
        return render(request, 'location/welcome.html', {
            'location_data': location_data,
            'schooldays_data': schooldays_data,
        })


def get_current_location(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    try:
        location = Location.objects.first()
        if not location:
            return JsonResponse({'error': 'No school location set'}, status=400)
        
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlat/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            return R * c

        lat = float(request.GET.get('latitude'))
        lon = float(request.GET.get('longitude'))
        distance = haversine(float(location.latitude), float(location.longitude), lat, lon)
        print(f"get_current_location: lat={lat}, lon={lon}, distance={distance}")
        
        return JsonResponse({
            'success': True,
            'current_location': {'latitude': lat, 'longitude': lon},
            'school_location': {'latitude': float(location.latitude), 'longitude': float(location.longitude)},
            'distance_km': round(distance, 2)
        })
    except Exception as e:
        print(f"get_current_location error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)


from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from .models import SchoolDays
from apps.corecode.decorators import restrict_to_authorized_roles
from accounts.models import AdminUser, StaffUser
from datetime import datetime

@method_decorator(restrict_to_authorized_roles, name='dispatch')
class SchoolDaysView(View):
    def get(self, request):
        print("Entering SchoolDaysView.get")
        schooldays = SchoolDays.objects.all().order_by('day')
        schooldays_data = []
        for day in schooldays:
            # Convert times to datetime for calculation
            start_dt = datetime.combine(datetime.today(), day.start_time)
            end_dt = datetime.combine(datetime.today(), day.end_time)
            # Calculate working hours in minutes
            delta = end_dt - start_dt
            working_minutes = delta.total_seconds() / 60
            print(f"SchoolDaysView: {day.day} working_minutes={working_minutes}")
            if working_minutes <= 50:
                # Non-working day
                day_data = {
                    'day': day.day,
                    'start_time': '',
                    'end_time': '',
                    'working_hours': 'X Closed'
                }
            else:
                # Working day
                hours = int(working_minutes // 60)
                minutes = int(working_minutes % 60)
                working_hours = []
                if hours > 0:
                    working_hours.append(f"{hours} hour{'s' if hours > 1 else ''}")
                if minutes > 0:
                    working_hours.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
                working_hours_str = " and ".join(working_hours) if working_hours else "0 minutes"
                day_data = {
                    'day': day.day,
                    'start_time': day.start_time.strftime('%I:%M %p') if day.start_time else '',
                    'end_time': day.end_time.strftime('%I:%M %p') if day.end_time else '',
                    'working_hours': working_hours_str
                }
            schooldays_data.append(day_data)
        print(f"SchoolDaysView: schooldays_data={schooldays_data}")

        # Determine base template based on user role
        user = request.user
        base_template = 'base.html'  # Default
        if user.is_authenticated:
            if user.is_superuser or AdminUser.objects.filter(username=user.username).exists():
                base_template = 'base.html'
                print(f"User {user.username} is superuser or AdminUser, using base_template=base.html")
            else:
                try:
                    staff_user = StaffUser.objects.get(username=user.username)
                    if staff_user.occupation == 'academic':
                        base_template = 'academic_base.html'
                        print(f"User {user.username} is academic, using base_template=academic_base.html")
                    elif staff_user.occupation in ['head_master', 'second_master']:
                        base_template = 'base.html'
                        print(f"User {user.username} is {staff_user.occupation}, using base_template=base.html")
                except StaffUser.DoesNotExist:
                    print(f"No StaffUser found for {user.username}, falling back to base.html")

        context = {
            'schooldays_data': schooldays_data,
            'base_template': base_template,
        }
        print(f"SchoolDaysView: template context={context}")
        return render(request, 'location/schooldays.html', context)
