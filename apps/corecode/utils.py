from apps.corecode.models import AcademicSession, AcademicTerm, Installment, Subject
from apps.academics.models import Exam
from location.models import Location, SchoolDays
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

def get_dashboard_data():
    """
    Fetch data for dashboard graphs and displays.
    Returns a context dictionary for the partial template.
    """
    logger.debug("Entering get_dashboard_data")
    context = {}

    try:
        # Fetch Academic Sessions
        sessions = AcademicSession.objects.all().order_by('-name')
        session_data = [
            {
                'name': session.name,
                'current': str(session.current).lower(),  # Convert True/False to 'true'/'false'
                'date_created': session.date_created.strftime('%Y-%m-%d'),
            }
            for session in sessions
        ]
        context['sessions'] = session_data
        logger.debug(f"Fetched {len(session_data)} sessions")

        # Fetch Academic Terms
        terms = AcademicTerm.objects.all().order_by('name')
        term_data = [
            {
                'name': term.name,
                'current': str(term.current).lower(),
                'date_created': term.date_created.strftime('%Y-%m-%d'),
            }
            for term in terms
        ]
        context['terms'] = term_data
        logger.debug(f"Fetched {len(term_data)} terms")

        # Fetch Installments
        installments = Installment.objects.all().order_by('name')
        installment_data = [
            {
                'name': installment.name,
                'current': str(installment.current).lower(),
                'date_created': installment.date_created.strftime('%Y-%m-%d'),
            }
            for installment in installments
        ]
        context['installments'] = installment_data
        logger.debug(f"Fetched {len(installment_data)} installments")

        # Fetch Exams
        exams = Exam.objects.all().order_by('date_created')
        exam_data = [
            {
                'name': exam.name,
                'is_current': str(exam.is_current).lower(),
                'date_created': exam.date_created.strftime('%Y-%m-%d'),
            }
            for exam in exams
        ]
        context['exams'] = exam_data
        logger.debug(f"Fetched {len(exam_data)} exams")

        # Fetch Subjects
        subjects = Subject.objects.all().order_by('name')
        subject_data = [
            {
                'id': idx + 1,  # S/N
                'subject_code': subject.subject_code or 'N/A',
                'name': subject.name,
                'date_created': subject.date_created.strftime('%Y-%m-%d %H:%M'),
                'date_updated': subject.date_updated.strftime('%Y-%m-%d %H:%M'),
            }
            for idx, subject in enumerate(subjects)
        ]
        context['subjects'] = subject_data
        logger.debug(f"Fetched {len(subject_data)} subjects")

        # Fetch Location
        try:
            location = Location.objects.first()  # Only one instance allowed
            if location:
                try:
                    latitude = float(location.latitude)
                    longitude = float(location.longitude)
                    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
                        logger.error(f"Invalid coordinates: lat={latitude}, lon={longitude}")
                        context['location'] = None
                    else:
                        context['location'] = {
                            'school_name': location.school_name or "Unnamed School",
                            'latitude': latitude,
                            'longitude': longitude,
                        }
                        logger.debug(f"Fetched location: {context['location']}")
                except (ValueError, TypeError) as e:
                    logger.error(f"Invalid location data: {e}")
                    context['location'] = None
            else:
                logger.warning("No location found")
                context['location'] = None
        except Exception as e:
            logger.error(f"Error fetching location: {e}")
            context['location'] = None

        # Fetch School Days
        school_days = SchoolDays.objects.all().order_by('day')
        school_days_data = []
        for day in school_days:
            start_dt = datetime.combine(date.today(), day.start_time)
            end_dt = datetime.combine(date.today(), day.end_time)
            delta = end_dt - start_dt
            working_minutes = delta.total_seconds() / 60
            if working_minutes <= 50:
                working_hours = 'X Closed'
            else:
                hours = int(working_minutes // 60)
                minutes = int(working_minutes % 60)
                working_hours_parts = []
                if hours > 0:
                    working_hours_parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
                if minutes > 0:
                    working_hours_parts.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
                working_hours = " and ".join(working_hours_parts) if working_hours_parts else "0 minutes"
            school_days_data.append({
                'day': day.get_day_display(),
                'start_time': day.start_time.strftime('%H:%M'),
                'end_time': day.end_time.strftime('%H:%M'),
                'working_hours': working_hours,
                'working_minutes': working_minutes,
            })
        context['school_days'] = school_days_data
        logger.debug(f"Fetched {len(school_days_data)} school days")

        # Support Contacts (static)
        context['support_contacts'] = [
            {'role': 'School academic', 'number': '+255680502671'},
            {'role': 'School Secretary', 'number': '+255781106089'},
            {'role': 'School Bursar', 'number': '+255743023365'},
            {'role': 'Technical Support', 'number': '+255741943155'},
        ]
        logger.debug("Added support contacts")

    except Exception as e:
        logger.error(f"Error in get_dashboard_data: {e}")

    logger.debug("Exiting get_dashboard_data")
    return context