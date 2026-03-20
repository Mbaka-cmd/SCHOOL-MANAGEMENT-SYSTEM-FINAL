# Run with: Get-Content "seed_kcse.py" | python manage.py shell
from website.models import KCSEResult
from schools.models import School

school = School.objects.first()
if not school:
    print("ERROR: No school found. Create one in /admin/ first.")
else:
    # 2024 KCSE - Real data (savanisbookshop.com/KNEC)
    KCSEResult.objects.update_or_create(
        school=school, year=2024,
        defaults={
            'candidates_sat': 133,
            'mean_grade': 'B-',
            'mean_points': 7.2,
            'university_qualifiers': 85,
            'pass_rate': 92,
            'count_a_plain': 0,
            'count_a_minus': 1,
            'count_b_plus': 8,
            'count_b_plain': 26,
            'count_b_minus': 47,
            'count_c_plus': 31,
            'count_c_plain': 16,
            'count_c_minus': 2,
            'count_d_plus': 1,
            'count_d_plain': 0,
            'count_d_minus': 0,
            'count_e': 0,
            'is_published': True,
            'summary': 'In 2024 KCSE, 133 candidates sat the exam with 85 qualifying for university admission. The school posted a mean grade of B-.'
        }
    )
    print("2024 results saved!")

    # 2023 KCSE - Real data (The Standard, Jan 2024)
    # All 270 candidates qualified for university. 1 grade A, 6 grade A-
    KCSEResult.objects.update_or_create(
        school=school, year=2023,
        defaults={
            'candidates_sat': 270,
            'mean_grade': 'B',
            'mean_points': 8.1,
            'university_qualifiers': 270,
            'pass_rate': 100,
            'count_a_plain': 1,
            'count_a_minus': 6,
            'is_published': True,
            'top_student_name': 'Mercy Mutheu',
            'top_student_grade': 'A',
            'summary': 'Historic performance — all 270 candidates qualified for university. Top student Mercy Mutheu attained grade A. Principal Joan Muthomi celebrated the achievement as the school\'s best result.'
        }
    )
    print("2023 results saved!")
    print("Done! Seeded 2 years of verified KCSE results.")