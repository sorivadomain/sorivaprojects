# accounts/utils.py
from functools import wraps
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import CustomUser, ParentUser, StaffUser, AdminUser
from apps.staffs.models import Staff
from apps.students.models import Student

def user_type_decorator(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        context = {
            'user_type': 'unknown',
            'buttons': [],
            'allowed': False,
            'header_title': "DEAR , WELCOME TO MANUS DEI SCHOOL MANAGEMENT SYSTEM, ",
            'header_subtitle': "",
        }

        # Define configurable button sets
        all_buttons = [
            {'name': 'General Analysis', 'url': '#', 'class': 'bg-analysis', 'icon': '📊', 'desc': 'Overall system insights'},
            {'name': 'Settings', 'url': reverse('settings_home'), 'class': 'bg-settings', 'icon': '⚙️', 'desc': 'Configure the system'},
            {'name': 'Finance', 'url': reverse('finance-home'), 'class': 'bg-finance', 'icon': '💰', 'desc': 'Billing & financial data'},
            {'name': 'Academics', 'url': reverse('academics_home'), 'class': 'bg-result', 'icon': '📈', 'desc': 'Academic performance'},
            {'name': 'Staffs', 'url': reverse('staff-home'), 'class': 'bg-staffs', 'icon': '👨‍🏫', 'desc': 'Teaching & Non-teaching'},
            {'name': 'Students', 'url': reverse('students_home'), 'class': 'bg-students', 'icon': '👨‍🎓', 'desc': 'Manage all students'},
            {'name': 'Attendance', 'url': reverse('attendance_home'), 'class': 'bg-attendance', 'icon': '✅', 'desc': 'Track presence'},
            {'name': 'Properties', 'url': reverse('properties_home'), 'class': 'bg-bursor', 'icon': '💼', 'desc': 'Manage school properties'},
            {'name': 'Events', 'url': reverse('events-home'), 'class': 'bg-events', 'icon': '🎉', 'desc': 'School calendar'},
            {'name': 'Library', 'url': reverse('library_home'), 'class': 'bg-library', 'icon': '📚', 'desc': 'Books & references'},
            {'name': 'Meetings', 'url': reverse('meetings_home'), 'class': 'bg-meetings', 'icon': '👥', 'desc': 'Schedule & records'},
            {'name': 'SMS', 'url': reverse('sms_home'), 'class': 'bg-sms', 'icon': '📱', 'desc': 'Send quick messages'},
            {'name': 'Public Comment', 'url': '#', 'class': 'bg-public-post', 'icon': '📢✍️', 'desc': 'Share feedback publicly'},
        ]

        parent_buttons = [
            {'name': 'General Student Analysis', 'url': '#', 'class': 'bg-analysis', 'icon': '📊', 'desc': 'Overview of student progress'},
            {'name': 'Student Details', 'url': '#', 'class': 'bg-students', 'icon': '👨‍🎓', 'desc': 'View student information'},
            {'name': 'Student Invoices', 'url': '#', 'class': 'bg-finance', 'icon': '💰', 'desc': 'View payment details'},
            {'name': 'Student Attendances', 'url': '#', 'class': 'bg-attendance', 'icon': '✅', 'desc': 'Track student presence'},
            {'name': 'Meetings', 'url': '#', 'class': 'bg-meetings', 'icon': '👥', 'desc': 'Schedule & records'},
            {'name': 'Parents Public Comments', 'url': '#', 'class': 'bg-public-post', 'icon': '📢✍️', 'desc': 'Share feedback publicly'},
        ]

        academic_buttons = [btn for btn in all_buttons if btn['name'] not in ['Finance', 'Staffs', 'Properties']]
        secretary_buttons = [btn for btn in all_buttons if btn['name'] not in ['Finance', 'Academics', 'Staffs', 'Library']]
        bursar_buttons = [btn for btn in all_buttons if btn['name'] not in ['Settings', 'Academics', 'Staffs', 'Students', 'Properties', 'Library']]
        teacher_buttons = [btn for btn in all_buttons if btn['name'] not in ['General Analysis', 'Settings', 'Finance', 'Academics', 'Staffs', 'Students', 'Properties', 'Library', 'SMS']]

        if user.is_superuser or hasattr(user, 'admin_id'):
            context['user_type'] = 'admin'
            context['buttons'] = all_buttons
            context['allowed'] = True
            
            try:
                admin_user = AdminUser.objects.get(pk=user.pk)
                full_name = admin_user.admin_name if admin_user.admin_name else user.username
            except AdminUser.DoesNotExist:
                full_name = user.username
            
            context['header_title'] = f"DEAR {full_name.upper()}, WELCOME TO MANUS DEI SCHOOL MANAGEMENT SYSTEM, ADMIN DASHBOARD"

        elif hasattr(user, 'parentuser'):
            context['user_type'] = 'parent'
            parent_user = user.parentuser
            student = parent_user.student
            if student:
                full_name = f"{parent_user.parent_first_name or ''} {parent_user.parent_middle_name or ''} {parent_user.parent_last_name or ''}".strip() or user.username
                context['header_title'] = f"DEAR {full_name.upper()}, WELCOME TO MANUS DEI SCHOOL MANAGEMENT SYSTEM, PARENT DASHBOARD"
                context['buttons'] = parent_buttons
                context['allowed'] = True

        elif hasattr(user, 'staffuser'):
            context['user_type'] = 'staff'
            staff_user = user.staffuser
            staff = staff_user.staff
            occupation = staff.occupation if staff and staff.occupation else None
            full_name = f"{staff.firstname} {staff.middle_name or ''} {staff.surname}".strip() or user.username
            context['header_title'] = f"DEAR {full_name.upper()}, WELCOME TO MANUS DEI SCHOOL MANAGEMENT SYSTEM, "

            if occupation == 'head_master':
                context['header_title'] += "HEADMASTER DASHBOARD"
                context['buttons'] = all_buttons
                context['allowed'] = True
            elif occupation == 'second_master':
                context['header_title'] += "SECONDMASTER DASHBOARD"
                context['buttons'] = all_buttons
                context['allowed'] = True
            elif occupation == 'academic':
                context['header_title'] += "ACADEMIC DASHBOARD"
                context['buttons'] = academic_buttons
                context['allowed'] = True
            elif occupation == 'secretary':
                context['header_title'] += "SECRETARY DASHBOARD"
                context['buttons'] = secretary_buttons
                context['allowed'] = True
            elif occupation == 'bursar':
                context['header_title'] += "BURSAR DASHBOARD"
                context['buttons'] = bursar_buttons
                context['allowed'] = True
            elif occupation in ['discipline', 'librarian', 'teacher', 'property_admin']:
                context['header_title'] += "TEACHER DASHBOARD"
                context['buttons'] = teacher_buttons
                context['allowed'] = True

        if not context['allowed']:
            return HttpResponseRedirect(reverse('custom_login'))

        response = view_func(request, *args, **kwargs)
        if isinstance(response, dict):  # If view returns a context dictionary
            response.update(context)
        elif hasattr(response, 'context_data'):  # If view is a TemplateView
            response.context_data.update(context)
        return response

    return _wrapped_view



from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.urls import reverse
from apps.staffs.models import Staff


def restrict_to_authorized_users(view_func):
    """
    Decorator to restrict access to superusers, admins, or active staff with Headmaster or Second Master roles.
    """
    def check_user(user):
        # Check if user is authenticated
        if not user.is_authenticated:
            return False

        # Allow superusers
        if user.is_superuser:
            return True

        # Allow admin users (AdminUser)
        if hasattr(user, 'adminuser'):
            return True

        # Allow active StaffUsers with Headmaster or Second Master occupation
        if hasattr(user, 'staffuser') and user.staffuser.staff:
            staff = user.staffuser.staff
            return (
                staff.current_status == 'active' and
                staff.occupation in ['head_master', 'second_master']
            )

        # Deny access to all other users
        return False

    def wrapped_view(request, *args, **kwargs):
        if check_user(request.user):
            return view_func(request, *args, **kwargs)
        return redirect(reverse('custom_login'))

    return wrapped_view


from apps.students.models import Student
from apps.corecode.models import StudentClass

def analyze_student_data():
    """
    Analyze student data to generate statistics and bar graph data.
    Returns a dictionary with active student counts by class, total active,
    male/female breakdowns, and counts for dropped out, shifted, and graduated students.
    Includes pre-computed female counts per class and zipped class data for template.
    """
    # Initialize data structures
    data = {
        'classes': [],
        'active_counts': [],
        'class_data': [],  # List of tuples: (class_name, total, male, female)
        'active_total': 0,
        'active_male': 0,
        'active_female': 0,
        'active_by_class': {},
        'active_male_by_class': {},
        'active_female_by_class': {},
        'dropped_out_total': 0,
        'dropped_out_male': 0,
        'dropped_out_female': 0,
        'shifted_total': 0,
        'shifted_male': 0,
        'shifted_female': 0,
        'graduated_total': 0,
        'graduated_male': 0,
        'graduated_female': 0,
    }

    # Get all student classes
    student_classes = StudentClass.objects.all()

    # Analyze active students by class
    for student_class in student_classes:
        class_name = str(student_class)
        active_students = Student.objects.filter(
            current_status='active', current_class=student_class
        )
        active_count = active_students.count()
        active_male_count = active_students.filter(gender='male').count()
        active_female_count = active_students.filter(gender='female').count()

        if active_count > 0:  # Only include classes with active students
            data['classes'].append(class_name)
            data['active_counts'].append(active_count)
            data['class_data'].append({
                'name': class_name,
                'total': active_count,
                'male': active_male_count,
                'female': active_female_count
            })
            data['active_by_class'][class_name] = active_count
            data['active_male_by_class'][class_name] = active_male_count
            data['active_female_by_class'][class_name] = active_female_count

        # Update totals
        data['active_total'] += active_count
        data['active_male'] += active_male_count
        data['active_female'] += active_female_count

    # Analyze dropped out students
    dropped_out_students = Student.objects.filter(current_status='dropped_out')
    data['dropped_out_total'] = dropped_out_students.count()
    data['dropped_out_male'] = dropped_out_students.filter(gender='male').count()
    data['dropped_out_female'] = dropped_out_students.filter(gender='female').count()

    # Analyze shifted students
    shifted_students = Student.objects.filter(current_status='shifted')
    data['shifted_total'] = shifted_students.count()
    data['shifted_male'] = shifted_students.filter(gender='male').count()
    data['shifted_female'] = shifted_students.filter(gender='female').count()

    # Analyze graduated students
    graduated_students = Student.objects.filter(current_status='graduated')
    data['graduated_total'] = graduated_students.count()
    data['graduated_male'] = graduated_students.filter(gender='male').count()
    data['graduated_female'] = graduated_students.filter(gender='female').count()

    return data


from apps.students.models import Student
from apps.corecode.models import StudentClass
from django.db.models.functions import ExtractYear
from django.db.models import Count


def analyze_admission_trends():
    """
    Analyze student admissions by year of admission.
    Returns a dictionary with years, admission counts, highest/lowest years,
    trend analysis, comments, and advice based on admission trends.
    """
    # Initialize data
    data = {
        'years': [],
        'admission_counts': [],
        'highest_year': None,
        'highest_count': 0,
        'lowest_year': None,
        'lowest_count': 0,
        'trend': 'N/A',
        'trend_description': '',
        'comments': '',
        'advice': ''
    }

    # Query admissions by year
    admissions = (Student.objects
                  .annotate(year=ExtractYear('date_of_admission'))
                  .values('year')
                  .annotate(count=Count('id'))
                  .order_by('year'))

    if not admissions:
        return data

    # Populate years and counts
    for entry in admissions:
        data['years'].append(entry['year'])
        data['admission_counts'].append(entry['count'])

    # Find highest and lowest
    if data['years']:
        data['highest_count'] = max(data['admission_counts'])
        data['lowest_count'] = min(data['admission_counts'])
        data['highest_year'] = data['years'][data['admission_counts'].index(data['highest_count'])]
        data['lowest_year'] = data['years'][data['admission_counts'].index(data['lowest_count'])]

    # Analyze trend
    if len(data['years']) > 1:
        changes = [data['admission_counts'][i+1] - data['admission_counts'][i] 
                   for i in range(len(data['admission_counts'])-1)]
        positive = sum(1 for c in changes if c > 0)
        negative = sum(1 for c in changes if c < 0)
        zero = sum(1 for c in changes if c == 0)

        if positive > negative and positive >= zero:
            data['trend'] = 'Increasing'
            avg_increase = sum(c for c in changes if c > 0) / max(positive, 1)
            data['trend_description'] = (f"Admissions are increasing, with an average increase of "
                                        f"{avg_increase:.1f} students per year.")
            data['comments'] = (
                f"Congratulations! Your school has shown a positive trend in student admissions from "
                f"{data['years'][0]} to {data['years'][-1]}. The peak was in {data['highest_year']} with "
                f"{data['highest_count']} students, compared to the lowest in {data['lowest_year']} with "
                f"{data['lowest_count']} students. This growth indicates effective marketing, strong community "
                f"reputation, or improved educational offerings. The consistent increase suggests that your "
                f"strategies are resonating with parents and students, fostering trust and interest in your "
                f"institution."
            )
            data['advice'] = (
                f"To sustain and amplify this growth, consider the following roadmap:\n\n"
                f"1. **Strengthen Marketing Efforts**: Continue leveraging successful channels (e.g., social media, "
                f"community events) and explore new ones like targeted digital ads or partnerships with local "
                f"businesses. Highlight unique programs (e.g., STEM, arts) in your campaigns.\n"
                f"2. **Enhance Facilities**: Invest in modern classrooms, labs, and extracurricular spaces to attract "
                f"more students. Showcase these upgrades in open houses and virtual tours.\n"
                f"3. **Engage the Community**: Host regular events like workshops or fairs to build stronger ties with "
                f"local families. Offer scholarships or financial aid to make your school accessible to diverse groups.\n"
                f"4. **Improve Academic Offerings**: Introduce advanced courses, vocational training, or international "
                f"exchange programs to differentiate your school. Publish success stories of alumni to build credibility.\n"
                f"5. **Monitor Feedback**: Collect parent and student feedback through surveys to identify areas for "
                f"improvement. Address concerns promptly to maintain satisfaction.\n"
                f"6. **Plan for Capacity**: With increasing admissions, ensure you have enough teachers, classrooms, and "
                f"resources. Hire qualified staff and train existing ones to maintain quality.\n\n"
                f"By maintaining these strategies, you can solidify your school’s reputation and continue this upward "
                f"trajectory. Keep monitoring admission trends to stay proactive!"
            )
        elif negative > positive and negative >= zero:
            data['trend'] = 'Decreasing'
            avg_decrease = abs(sum(c for c in changes if c < 0) / max(negative, 1))
            data['trend_description'] = (f"Admissions are decreasing, with an average decline of "
                                        f"{avg_decrease:.1f} students per year.")
            data['comments'] = (
                f"Warning: Your school is experiencing a concerning decline in student admissions from "
                f"{data['years'][0]} to {data['years'][-1]}. The highest admission was in {data['highest_year']} "
                f"with {data['highest_count']} students, while the lowest was in {data['lowest_year']} with "
                f"{data['lowest_count']} students. This downward trend may stem from increased competition, economic "
                f"challenges, or perceptions about the school’s quality. Immediate action is needed to reverse "
                f"this trend and restore growth."
            )
            data['advice'] = (
                f"To address this decline and boost admissions, implement this comprehensive roadmap:\n\n"
                f"1. **Conduct a Root Cause Analysis**: Survey parents and former applicants to understand why admissions "
                f"are dropping. Identify issues like cost, academic reputation, or facilities.\n"
                f"2. **Revamp Marketing**: Launch a robust campaign emphasizing your school’s strengths. Use social "
                f"media, SEO, and local media to reach parents. Host open houses and virtual tours to showcase your "
                f"school.\n"
                f"3. **Offer Incentives**: Introduce scholarships, sibling discounts, or flexible payment plans to make "
                f"your school more affordable. Promote these widely.\n"
                f"4. **Upgrade Facilities**: Invest in modern technology, sports facilities, or libraries to attract "
                f"families. Highlight these improvements in marketing materials.\n"
                f"5. **Enhance Academic Programs**: Introduce specialized programs like coding bootcamps or AP courses to "
                f"stand out. Partner with local universities or businesses for internships to boost credibility.\n"
                f"6. **Build Community Trust**: Engage local communities through events, alumni networks, or charity "
                f"drives. Address negative perceptions through transparent communication.\n"
                f"7. **Hire Marketing Experts**: Consider professional consultants to redesign your admissions strategy "
                f"and improve outreach.\n\n"
                f"Act swiftly to implement these strategies. Regularly track admissions data to measure progress and "
                f"adjust your approach. Reversing this trend is critical for your school’s sustainability."
            )
        else:
            data['trend'] = 'Constant'
            data['trend_description'] = "Admissions are relatively stable, with minimal year-over-year changes."
            data['comments'] = (
                f"Your school’s admissions have remained stable from {data['years'][0]} to {data['years'][-1]}, "
                f"with a peak in {data['highest_year']} at {data['highest_count']} students and a low in "
                f"{data['lowest_year']} at {data['lowest_count']} students. While stability is positive, it also "
                f"indicates a lack of significant growth, which could limit your school’s potential in a competitive "
                f"educational landscape. Opportunities exist to increase admissions and enhance your school’s impact."
            )
            data['advice'] = (
                f"To break from this plateau and boost admissions, adopt this strategic roadmap:\n\n"
                f"1. **Market Aggressively**: Develop a dynamic marketing plan using social media, local radio, and "
                f"community boards. Highlight unique programs like music, sports, or tech to attract attention.\n"
                f"2. **Improve Visibility**: Create a professional website with SEO optimization and virtual tours. "
                f"Participate in education fairs to reach prospective families.\n"
                f"3. **Offer Incentives**: Provide introductory discounts, referral bonuses, or financial aid to attract "
                f"new students. Advertise these offers prominently.\n"
                f"4. **Diversify Programs**: Add extracurriculars or specialized courses (e.g., robotics, languages) to "
                f"appeal to diverse interests. Promote these to differentiate your school.\n"
                f"5. **Engage Alumni**: Build an alumni network to share success stories, which can inspire trust in "
                f"prospective parents. Invite alumni to mentor or speak at events.\n"
                f"6. **Collect Data**: Use surveys to understand parent preferences and market demands. Tailor your "
                f"offerings based on feedback.\n\n"
                f"By implementing these strategies, you can shift from stability to growth. Set clear admission goals "
                f"and monitor progress annually to ensure sustained improvement."
            )

    return data


from django.db.models import Avg, Count
from apps.corecode.models import AcademicSession, AcademicTerm, StudentClass, Subject
from apps.students.models import Student
from apps.academics.models import Result, Exam
from decimal import Decimal

def analyze_academic_performance():
    print("[analyze_academic_performance] Starting analysis")
    
    try:
        current_session = AcademicSession.objects.get(current=True)
        current_term = AcademicTerm.objects.get(current=True)
        current_exam = Exam.objects.get(is_current=True)
        print(f"[analyze_academic_performance] Current: session={current_session}, term={current_term}, exam={current_exam}")
    except (AcademicSession.DoesNotExist, AcademicTerm.DoesNotExist, Exam.DoesNotExist) as e:
        print(f"[analyze_academic_performance] Error: {str(e)}")
        return {
            'error': 'Current session, term, or exam not found.',
            'class_data': [],
            'chart_labels': [],
            'chart_pass_data': [],
            'chart_fail_data': [],
            'chart_ignored_data': [],
            'highest_class': None,
            'lowest_class': None,
            'comments': '',
            'advice': ''
        }

    result = {
        'class_data': [],
        'chart_labels': [],
        'chart_pass_data': [],
        'chart_fail_data': [],
        'chart_ignored_data': [],
        'highest_class': None,
        'lowest_class': None,
        'comments': '',
        'advice': ''
    }

    classes = StudentClass.objects.all()
    print(f"[analyze_academic_performance] Found {classes.count()} classes")

    weak_subjects = []
    high_ignored_classes = []

    for student_class in classes:
        print(f"[analyze_academic_performance] Processing class: {student_class.name}")
        class_data = {
            'name': student_class.name,
            'overall_average': 0,
            'pass_percentage': 0,
            'fail_percentage': 0,
            'ignored_percentage': 0,
            'subject_data': []
        }

        students = Student.objects.filter(current_class=student_class, current_status='active')
        student_results = Result.objects.filter(
            session=current_session,
            term=current_term,
            exam=current_exam,
            student_class=student_class,
            student__in=students
        ).values(
            'student_id'
        ).annotate(
            subject_count=Count('subject'),
            avg_marks=Avg('marks')
        )

        total_students = students.count()
        valid_students = [sr for sr in student_results if sr['subject_count'] >= 7]
        pass_students = len([sr for sr in valid_students if sr['avg_marks'] >= 50])
        fail_students = len([sr for sr in valid_students if sr['avg_marks'] < 50])
        ignored_students = total_students - len(valid_students)

        if total_students > 0:
            class_data['pass_percentage'] = (pass_students / total_students * 100)
            class_data['fail_percentage'] = (fail_students / total_students * 100)
            class_data['ignored_percentage'] = (ignored_students / total_students * 100)
            if valid_students:
                class_data['overall_average'] = float(sum(sr['avg_marks'] for sr in valid_students) / len(valid_students))
            print(f"[analyze_academic_performance] Class {student_class.name}: "
                  f"pass={class_data['pass_percentage']:.2f}%, fail={class_data['fail_percentage']:.2f}%, "
                  f"ignored={class_data['ignored_percentage']:.2f}%, avg={class_data['overall_average']:.2f}")

        if class_data['ignored_percentage'] > 20:
            high_ignored_classes.append(student_class.name)

        subjects = student_class.subjects.all()
        for subject in subjects:
            print(f"[analyze_academic_performance] Processing subject: {subject.name} in class: {student_class.name}")
            subject_data = {
                'name': subject.name,
                'pass_percentage': 0,
                'fail_percentage': 0,
                'ignored_percentage': 0
            }

            subject_results = Result.objects.filter(
                session=current_session,
                term=current_term,
                exam=current_exam,
                student_class=student_class,
                subject=subject,
                student__in=students
            )

            total_subject_students = students.count()
            pass_subject = subject_results.filter(marks__gte=50).count()
            fail_subject = subject_results.filter(marks__lt=50).count()
            ignored_subject = total_subject_students - (pass_subject + fail_subject)

            if total_subject_students > 0:
                subject_data['pass_percentage'] = (pass_subject / total_subject_students * 100)
                subject_data['fail_percentage'] = (fail_subject / total_subject_students * 100)
                subject_data['ignored_percentage'] = (ignored_subject / total_subject_students * 100)
                print(f"[analyze_academic_performance] Subject {subject.name}: "
                      f"pass={subject_data['pass_percentage']:.2f}%, fail={subject_data['fail_percentage']:.2f}%, "
                      f"ignored={subject_data['ignored_percentage']:.2f}%")

            if subject_data['fail_percentage'] > 50:
                weak_subjects.append(f"{subject.name} in {student_class.name}")

            class_data['subject_data'].append(subject_data)

        result['class_data'].append(class_data)

    sorted_class_data = sorted(result['class_data'], key=lambda x: x['name'])
    result['chart_labels'] = [cd['name'] for cd in sorted_class_data]
    result['chart_pass_data'] = [cd['pass_percentage'] for cd in sorted_class_data]
    result['chart_fail_data'] = [cd['fail_percentage'] for cd in sorted_class_data]
    result['chart_ignored_data'] = [cd['ignored_percentage'] for cd in sorted_class_data]
    print(f"[analyze_academic_performance] Chart data: labels={result['chart_labels']}")

    valid_classes = [cd for cd in result['class_data'] if cd['overall_average'] > 0]
    if valid_classes:
        result['highest_class'] = max(valid_classes, key=lambda x: x['overall_average'])
        result['lowest_class'] = min(valid_classes, key=lambda x: x['overall_average'])
        print(f"[analyze_academic_performance] Highest: {result['highest_class']['name']}, "
              f"avg={result['highest_class']['overall_average']:.2f}")
        print(f"[analyze_academic_performance] Lowest: {result['lowest_class']['name']}, "
              f"avg={result['lowest_class']['overall_average']:.2f}")

    try:
        previous_session = AcademicSession.objects.filter(current=False).latest('date_updated')
        previous_term = AcademicTerm.objects.get(current=True)
        previous_exam = Exam.objects.get(is_current=True)
        print(f"[analyze_academic_performance] Previous: session={previous_session}, term={previous_term}, exam={previous_exam}")

        previous_data = analyze_academic_performance_for_session(previous_session, previous_term, previous_exam)
        current_avg = float(sum(cd['overall_average'] for cd in result['class_data']) / len(valid_classes)) if valid_classes else 0
        prev_avg = float(sum(cd['overall_average'] for cd in previous_data['class_data'] if cd['overall_average'] > 0) / len(previous_data['class_data']) if previous_data['class_data'] else 0)

        comments = []
        advice = []
        if current_avg > prev_avg:
            improvement = current_avg - prev_avg
            comments.append(f"Overall performance has improved significantly from {prev_avg:.2f}% to {current_avg:.2f}% (a gain of {improvement:.2f}%).")
            comments.append(f"The highest performing class, {result['highest_class']['name']}, achieved an average of {result['highest_class']['overall_average']:.2f}%, indicating strong teaching practices or student engagement in this class.")
            if weak_subjects:
                comments.append(f"However, specific weaknesses persist in subjects like {', '.join(weak_subjects)}, where failure rates exceed 50%. These areas require immediate attention.")
            if high_ignored_classes:
                comments.append(f"High ignored rates in classes like {', '.join(high_ignored_classes)} (over 20%) suggest incomplete result submissions or student absences, impacting overall data reliability.")

            advice.append("**Roadmap for Sustained Improvement**:")
            advice.append(f"1. **Replicate Success**: Analyze teaching methods in high-performing classes like {result['highest_class']['name']} (e.g., lesson plans, student engagement strategies). Organize workshops for teachers to share these practices.")
            advice.append(f"2. **Address Weak Subjects**: For subjects like {', '.join(weak_subjects)}, schedule remedial classes and provide additional resources (e.g., textbooks, online tools). Evaluate teacher performance in these subjects through peer reviews or student feedback.")
            advice.append(f"3. **Reduce Ignored Rates**: Investigate high ignored rates in {', '.join(high_ignored_classes)}. Ensure teachers submit results promptly and track student attendance. Consider parental meetings to address absenteeism.")
            advice.append("4. **Long-Term Strategy**: Invest in teacher professional development (e.g., subject-specific training) and monitor progress through monthly performance reviews. Allocate budget for learning aids to support weaker subjects.")
        elif current_avg < prev_avg:
            decline = prev_avg - current_avg
            comments.append(f"Overall performance has declined from {prev_avg:.2f}% to {current_avg:.2f}% (a drop of {decline:.2f}%).")
            comments.append(f"The lowest performing class, {result['lowest_class']['name']}, scored an average of {result['lowest_class']['overall_average']:.2f}%, indicating potential issues in teaching, student motivation, or resource availability.")
            if weak_subjects:
                comments.append(f"High failure rates in subjects like {', '.join(weak_subjects)} (over 50%) highlight critical areas for intervention.")
            if high_ignored_classes:
                comments.append(f"Ignored rates above 20% in classes like {', '.join(high_ignored_classes)} suggest data gaps or student disengagement, affecting analysis accuracy.")

            advice.append("**Roadmap for Recovery**:")
            advice.append(f"1. **Immediate Intervention**: For low-performing classes like {result['lowest_class']['name']}, conduct teacher evaluations and student surveys to identify barriers (e.g., unclear lessons, lack of resources).")
            advice.append(f"2. **Targeted Remediation**: Implement after-school tutoring for subjects like {', '.join(weak_subjects)}. Pair struggling students with peer mentors and provide extra practice materials.")
            advice.append(f"3. **Data Integrity**: Address high ignored rates in {', '.join(high_ignored_classes)} by enforcing result submission deadlines and tracking absences. Use SMS alerts to notify parents of student absences.")
            advice.append("4. **Strategic Planning**: Form a task force to review curriculum delivery in weak subjects. Allocate funds for teacher training and classroom resources. Set quarterly performance targets and review progress with staff.")
        else:
            comments.append(f"Overall performance is stable at {current_avg:.2f}%, matching the previous session.")
            comments.append(f"While stability is positive, classes like {result['lowest_class']['name']} (average {result['lowest_class']['overall_average']:.2f}%) underperform, indicating room for improvement.")
            if weak_subjects:
                comments.append(f"Subjects like {', '.join(weak_subjects)} show failure rates above 50%, requiring focused efforts.")
            if high_ignored_classes:
                comments.append(f"Ignored rates over 20% in classes like {', '.join(high_ignored_classes)} point to data collection or attendance issues.")

            advice.append("**Roadmap for Progress**:")
            advice.append(f"1. **Boost Underperformers**: For classes like {result['lowest_class']['name']}, introduce weekly progress checks and motivational programs (e.g., rewards for improvement).")
            advice.append(f"2. **Strengthen Subjects**: For weak subjects like {', '.join(weak_subjects)}, provide teachers with specialized training and access to digital learning platforms.")
            advice.append(f"3. **Improve Data Quality**: Tackle ignored rates in {', '.join(high_ignored_classes)} by streamlining result entry processes and engaging parents to ensure student attendance.")
            advice.append("4. **Continuous Improvement**: Establish a school improvement committee to set annual goals, monitor subject performance, and allocate resources effectively.")

        result['comments'] = '\n'.join(comments)
        result['advice'] = '\n'.join(advice)
        print(f"[analyze_academic_performance] Comments: {result['comments']}")
        print(f"[analyze_academic_performance] Advice: {result['advice']}")
    except (AcademicSession.DoesNotExist, AcademicTerm.DoesNotExist, Exam.DoesNotExist):
        result['comments'] = "No previous session data available for comparison, limiting trend analysis."
        result['advice'] = (
            "Ensure consistent data entry for sessions, terms, and exams to enable performance tracking.\n"
            "Start by setting up a data management protocol to record all student results promptly.\n"
            "Train staff on using the system and conduct regular audits to maintain data integrity."
        )
        print("[analyze_academic_performance] No previous data")

    print("[analyze_academic_performance] Analysis complete")
    return result

def analyze_academic_performance_for_session(session, term, exam):
    print(f"[analyze_academic_performance_for_session] Analyzing: {session}, {term}, {exam}")
    result = {'class_data': []}
    classes = StudentClass.objects.all()

    for student_class in classes:
        class_data = {
            'name': student_class.name,
            'overall_average': 0,
            'pass_percentage': 0,
            'fail_percentage': 0,
            'ignored_percentage': 0,
            'subject_data': []
        }

        students = Student.objects.filter(current_class=student_class, current_status='active')
        student_results = Result.objects.filter(
            session=session,
            term=term,
            exam=exam,
            student_class=student_class,
            student__in=students
        ).values(
            'student_id'
        ).annotate(
            subject_count=Count('subject'),
            avg_marks=Avg('marks')
        )

        total_students = students.count()
        valid_students = [sr for sr in student_results if sr['subject_count'] >= 7]
        pass_students = len([sr for sr in valid_students if sr['avg_marks'] >= 50])
        fail_students = len([sr for sr in valid_students if sr['avg_marks'] < 50])
        ignored_students = total_students - len(valid_students)

        if total_students > 0:
            class_data['pass_percentage'] = (pass_students / total_students * 100)
            class_data['fail_percentage'] = (fail_students / total_students * 100)
            class_data['ignored_percentage'] = (ignored_students / total_students * 100)
            if valid_students:
                class_data['overall_average'] = float(sum(sr['avg_marks'] for sr in valid_students) / len(valid_students))

        result['class_data'].append(class_data)

    print(f"[analyze_academic_performance_for_session] Completed for {session}")
    return result



from django.db.models import Avg, Count
from apps.corecode.models import AcademicSession, AcademicTerm, StudentClass
from apps.students.models import Student
from apps.academics.models import Result
import random

def analyze_class_performance_trends():
    print("[analyze_class_performance_trends] Starting analysis")
    
    result = {
        'chart_data_list': [],
        'class_period_data': [],
        'trends': [],
        'predictions': [],
        'alerts': [],
        'advice': ''
    }

    # Get all session-term-exam combinations, ordered by date_updated
    sessions = AcademicSession.objects.all().order_by('date_updated')
    terms = AcademicTerm.objects.all().order_by('date_updated')
    exams = Exam.objects.all().order_by('date_updated')
    
    # Generate periods for processing
    periods = [(s, t, e) for s in sessions for t in terms for e in exams]
    period_names = [f"{s.name}-{t.name}-{e.name}" for s, t, e in periods]
    print(f"[analyze_class_performance_trends] Periods: {period_names}")

    classes = StudentClass.objects.all()
    trends = []
    predictions = []
    alerts = []

    for idx, student_class in enumerate(classes):
        print(f"[analyze_class_performance_trends] Processing class: {student_class.name}")
        averages = []
        class_data = {'name': student_class.name, 'periods': []}
        
        for session, term, exam in periods:
            students = Student.objects.filter(current_class=student_class, current_status='active')
            student_results = Result.objects.filter(
                session=session,
                term=term,
                exam=exam,
                student_class=student_class,
                student__in=students
            ).values('student_id').annotate(
                subject_count=Count('subject'),
                avg_marks=Avg('marks')
            )

            total_students = students.count()
            valid_students = [sr for sr in student_results if sr['subject_count'] >= 1 and sr['avg_marks'] is not None]
            taken_students = len(valid_students)
            valid_marks = [float(sr['avg_marks']) for sr in valid_students if sr['avg_marks'] is not None]
            avg = sum(valid_marks) / len(valid_marks) if valid_marks else 0

            class_data['periods'].append({
                'period': f"{session.name}-{term.name}-{exam.name}",
                'overall_average': avg
            })

            averages.append(avg)
            print(f"[analyze_class_performance_trends] Class {student_class.name}, {session.name}-{term.name}-{exam.name}: "
                  f"avg={avg:.2f}, taken={taken_students}, total={total_students}, marks={[sr['avg_marks'] for sr in valid_students]}")

        result['class_period_data'].append(class_data)

        # Create dataset for Chart.js
        chart_data = {
            'labels': [],  # No X-axis labels
            'datasets': [{
                'label': student_class.name,
                'data': averages,
                'borderColor': f'rgb({random.randint(50, 200)}, {random.randint(50, 200)}, {random.randint(50, 200)})',
                'fill': "false",
                'tension': 0.1
            }]
        }
        result['chart_data_list'].append({
            'class_name': student_class.name,
            'chart_data': chart_data,
            'canvas_id': f'classTrendsChart_{idx}'
        })

        # Analyze trend
        non_zero_avgs = [avg for avg in averages if avg > 0]
        if len(non_zero_avgs) >= 1:
            if len(non_zero_avgs) > 1:
                slope = (non_zero_avgs[-1] - non_zero_avgs[0]) / (len(non_zero_avgs) - 1)
                trend_status = 'improving' if slope > 0.5 else 'declining' if slope < -0.5 else 'stable'
                predicted_avg = max(0, min(100, non_zero_avgs[-1] + slope))
            else:
                slope = 0
                trend_status = 'stable'
                predicted_avg = non_zero_avgs[0]
            
            trends.append({'class_name': student_class.name, 'status': trend_status, 'slope': slope})
            predictions.append({'class_name': student_class.name, 'predicted_avg': predicted_avg})
            print(f"[analyze_class_performance_trends] Trend for {student_class.name}: {trend_status}, slope={slope:.2f}")
            print(f"[analyze_class_performance_trends] Prediction for {student_class.name}: {predicted_avg:.2f}")

            if trend_status == 'declining':
                alerts.append(student_class.name)
        else:
            trends.append({'class_name': student_class.name, 'status': 'no_data', 'slope': 0})
            predictions.append({'class_name': student_class.name, 'predicted_avg': 0})
            print(f"[analyze_class_performance_trends] No data for {student_class.name}")

    result['trends'] = trends
    result['predictions'] = predictions
    result['alerts'] = alerts

    # Generate simplified advice based on trends
    advice = ["**Roadmap for Strategic Academic Improvement**:"]
    if trends:
        improving = [t['class_name'] for t in trends if t['status'] == 'improving']
        declining = [t['class_name'] for t in trends if t['status'] == 'declining']
        stable = [t['class_name'] for t in trends if t['status'] == 'stable']
        no_data = [t['class_name'] for t in trends if t['status'] == 'no_data']
        
        if improving:
            advice.append(f"- **Sustain Improving Classes ({', '.join(improving)})**: Continue effective teaching strategies and invest in resources like digital tools to maintain growth.")
        if stable:
            advice.append(f"- **Enhance Stable Classes ({', '.join(stable)})**: Introduce enrichment programs or innovative methods to boost performance.")
        if declining:
            advice.append(f"- **Address Declining Classes ({', '.join(declining)})**: Implement targeted interventions like remedial classes and evaluate teaching methods.")
        if no_data:
            advice.append(f"- **Collect Data for Classes ({', '.join(no_data)})**: Ensure complete result data to enable performance analysis.")
        if not (improving or stable or declining or no_data):
            advice.append("- **No Data Available**: Ensure result data is entered for analysis.")

    result['advice'] = '\n'.join(advice)
    print(f"[analyze_class_performance_trends] Advice: {result['advice']}")

    print("[analyze_class_performance_trends] Analysis complete")
    return result