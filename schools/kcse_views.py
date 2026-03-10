from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from schools.models import School
from website.models import KCSEResult
import openpyxl


def get_school():
    return School.objects.first()


@login_required
def kcse_upload(request):
    school = get_school()
    results = KCSEResult.objects.filter(school=school).order_by('-year')

    if request.method == 'POST':
        # Manual entry
        if 'manual_submit' in request.POST:
            try:
                year = int(request.POST.get('year'))
                KCSEResult.objects.update_or_create(
                    school=school, year=year,
                    defaults={
                        'candidates_sat': request.POST.get('candidates_sat', 0),
                        'mean_grade': request.POST.get('mean_grade', ''),
                        'mean_points': request.POST.get('mean_points') or None,
                        'university_qualifiers': request.POST.get('university_qualifiers', 0),
                        'county_position': request.POST.get('county_position') or None,
                        'national_position': request.POST.get('national_position') or None,
                        'count_a_plain': request.POST.get('count_a_plain', 0),
                        'count_a_minus': request.POST.get('count_a_minus', 0),
                        'count_b_plus': request.POST.get('count_b_plus', 0),
                        'count_b_plain': request.POST.get('count_b_plain', 0),
                        'count_b_minus': request.POST.get('count_b_minus', 0),
                        'count_c_plus': request.POST.get('count_c_plus', 0),
                        'count_c_plain': request.POST.get('count_c_plain', 0),
                        'count_c_minus': request.POST.get('count_c_minus', 0),
                        'count_d_plus': request.POST.get('count_d_plus', 0),
                        'count_d_plain': request.POST.get('count_d_plain', 0),
                        'count_d_minus': request.POST.get('count_d_minus', 0),
                        'count_e': request.POST.get('count_e', 0),
                        'top_student_name': request.POST.get('top_student_name', ''),
                        'top_student_points': request.POST.get('top_student_points') or None,
                        'top_student_grade': request.POST.get('top_student_grade', ''),
                        'summary': request.POST.get('summary', ''),
                        'is_published': 'is_published' in request.POST,
                    }
                )
                messages.success(request, f'KCSE {year} results saved successfully.')
            except Exception as e:
                messages.error(request, f'Error saving results: {e}')
            return redirect('kcse_upload')

        # Excel upload
        if 'excel_submit' in request.POST and request.FILES.get('excel_file'):
            try:
                excel_file = request.FILES['excel_file']
                wb = openpyxl.load_workbook(excel_file)
                ws = wb.active
                saved = 0
                for row in ws.iter_rows(min_row=2, values_only=True):
                    if not row[0]:
                        continue
                    year = int(row[0])
                    KCSEResult.objects.update_or_create(
                        school=school, year=year,
                        defaults={
                            'candidates_sat': row[1] or 0,
                            'mean_grade': row[2] or '',
                            'mean_points': row[3] or None,
                            'university_qualifiers': row[4] or 0,
                            'county_position': row[5] or None,
                            'national_position': row[6] or None,
                            'count_a_plain': row[7] or 0,
                            'count_a_minus': row[8] or 0,
                            'count_b_plus': row[9] or 0,
                            'count_b_plain': row[10] or 0,
                            'count_b_minus': row[11] or 0,
                            'count_c_plus': row[12] or 0,
                            'count_c_plain': row[13] or 0,
                            'count_c_minus': row[14] or 0,
                            'count_d_plus': row[15] or 0,
                            'count_d_plain': row[16] or 0,
                            'count_d_minus': row[17] or 0,
                            'count_e': row[18] or 0,
                            'top_student_name': row[19] or '',
                            'top_student_points': row[20] or None,
                            'top_student_grade': row[21] or '',
                            'is_published': True,
                        }
                    )
                    saved += 1
                messages.success(request, f'{saved} KCSE result(s) uploaded successfully.')
            except Exception as e:
                messages.error(request, f'Excel error: {e}')
            return redirect('kcse_upload')

    return render(request, 'schools/kcse_upload.html', {
        'school': school,
        'results': results,
        'current_year': timezone.now().year,
    })


@login_required
def kcse_toggle_publish(request, year):
    school = get_school()
    result = KCSEResult.objects.get(school=school, year=year)
    result.is_published = not result.is_published
    result.save()
    status = "published" if result.is_published else "unpublished"
    messages.success(request, f'KCSE {year} results {status}.')
    return redirect('kcse_upload')
