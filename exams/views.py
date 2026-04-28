from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Exam, ExamResult, ReportCard, score_to_grade, GRADE_POINTS
from fees.models import FeeInvoice
from students.models import Student
from academics.models import Subject, Stream
from schools.models import AcademicYear, Term
from schools.views import admin_required


@admin_required
def exam_list(request):
    school = request.user.school
    exams = Exam.objects.filter(school=school).select_related(
        "academic_year", "term"
    ).order_by("-created_at")
    context = {"exams": exams}
    return render(request, "exams/exam_list.html", context)


@admin_required
def exam_detail(request, pk):
    school = request.user.school
    exam = get_object_or_404(Exam, pk=pk, school=school)

    # Get exam statistics
    total_students = exam.streams.count() * 40  # Rough estimate
    submitted_results = ExamResult.objects.filter(exam=exam).values('student').distinct().count()
    total_subjects = ExamResult.objects.filter(exam=exam).values('subject').distinct().count()

    context = {
        "exam": exam,
        "total_students": total_students,
        "submitted_results": submitted_results,
        "total_subjects": total_subjects,
    }
    return render(request, "exams/exam_detail.html", context)


@admin_required
def exam_create(request):
    school = request.user.school
    if request.method == "POST":
        name = request.POST.get("name")
        exam_type = request.POST.get("exam_type")
        year_id = request.POST.get("academic_year")
        term_id = request.POST.get("term")
        start_date = request.POST.get("start_date") or None
        end_date = request.POST.get("end_date") or None
        stream_ids = request.POST.getlist("streams")
        exam_paper = request.FILES.get("exam_paper")
        action = request.POST.get("action", "create")  # 'create', 'draft', or 'clear'

        if action == "clear":
            # Clear the form - just redirect back to empty form
            return redirect("exam_create")

        try:
            academic_year = AcademicYear.objects.get(id=year_id, school=school)
            term = Term.objects.get(id=term_id) if term_id else None

            status = "draft" if action == "draft" else "active"

            exam = Exam.objects.create(
                school=school, name=name, exam_type=exam_type,
                academic_year=academic_year, term=term,
                start_date=start_date, end_date=end_date,
                exam_paper=exam_paper, status=status,
            )
            if stream_ids:
                exam.streams.set(Stream.objects.filter(id__in=stream_ids, school=school))

            if action == "draft":
                messages.info(request, f"Exam '{name}' saved as draft!")
            else:
                messages.success(request, f"Exam '{name}' created successfully!")

            return redirect("exam_detail", pk=exam.id)
        except Exception as e:
            messages.error(request, f"Error creating exam: {e}")
    years = AcademicYear.objects.filter(school=school)
    terms = Term.objects.filter(academic_year__school=school)
    streams = Stream.objects.filter(school=school).order_by("class_level__level_order", "name")
    context = {"years": years, "terms": terms, "streams": streams}
    return render(request, "exams/exam_create.html", context)


@admin_required
def exam_publish(request, pk):
    school = request.user.school
    exam = get_object_or_404(Exam, id=pk, school=school)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "publish":
            exam.is_published = True
            exam.save()
            messages.success(request, f"Exam '{exam.name}' published successfully!")
        elif action == "unpublish":
            exam.is_published = False
            exam.save()
            messages.success(request, f"Exam '{exam.name}' unpublished!")

    return redirect("exam_detail", pk=exam.id)


@admin_required
def exam_delete(request, pk):
    school = request.user.school
    exam = get_object_or_404(Exam, id=pk, school=school)

    if request.method == "POST":
        if not exam.is_published:
            exam_name = exam.name
            exam.delete()
            messages.success(request, f"Exam '{exam_name}' deleted successfully!")
            return redirect("exam_list")
        else:
            messages.error(request, "Cannot delete a published exam. Unpublish it first.")

    return redirect("exam_detail", pk=exam.id)


@admin_required
def enter_marks(request, pk):
    school = request.user.school
    exam = get_object_or_404(Exam, id=pk, school=school)
    stream_id = request.GET.get("stream") or request.POST.get("stream")
    subject_id = request.GET.get("subject") or request.POST.get("subject")
    streams = exam.streams.all()
    subjects = Subject.objects.filter(school=school)
    students = []
    selected_stream = None
    selected_subject = None

    if stream_id and subject_id:
        selected_stream = get_object_or_404(Stream, id=stream_id, school=school)
        selected_subject = get_object_or_404(Subject, id=subject_id, school=school)
        students = Student.objects.filter(
            school=school, current_stream=selected_stream, is_active=True,
        ).order_by("last_name", "first_name")

        if request.method == "POST" and "save_marks" in request.POST:
            saved = 0
            for student in students:
                score_key = f"score_{student.id}"
                absent_key = f"absent_{student.id}"
                score_val = request.POST.get(score_key, "").strip()
                is_absent = absent_key in request.POST

                if is_absent:
                    result, _ = ExamResult.objects.get_or_create(
                        exam=exam, student=student, subject=selected_subject,
                        defaults={"entered_by": request.user}
                    )
                    result.is_absent = True
                    result.grade = "X"
                    result.points = 0
                    result.entered_by = request.user
                    result.save()
                    saved += 1
                elif score_val:
                    try:
                        score = float(score_val)
                        grade = score_to_grade(score)
                        points = GRADE_POINTS.get(grade, 0)
                        result, _ = ExamResult.objects.get_or_create(
                            exam=exam, student=student, subject=selected_subject,
                            defaults={"entered_by": request.user}
                        )
                        result.raw_score = score
                        result.grade = grade
                        result.points = points
                        result.is_absent = False
                        result.entered_by = request.user
                        result.save()
                        saved += 1
                    except ValueError:
                        pass
            messages.success(request, f"Saved {saved} marks for {selected_subject.name}!")
            return redirect(f"{request.path}?stream={stream_id}&subject={subject_id}")

    existing_results = {}
    if students and selected_subject:
        for result in ExamResult.objects.filter(
            exam=exam, student__in=students, subject=selected_subject
        ):
            existing_results[str(result.student_id)] = result

    context = {
        "exam": exam, "streams": streams, "subjects": subjects,
        "students": students, "selected_stream": selected_stream,
        "selected_subject": selected_subject, "existing_results": existing_results,
        "stream_id": stream_id, "subject_id": subject_id,
    }
    return render(request, "exams/enter_marks.html", context)


@admin_required
def exam_results(request, pk):
    school = request.user.school
    exam = get_object_or_404(Exam, id=pk, school=school)
    stream_id = request.GET.get("stream")
    streams = exam.streams.all()
    selected_stream = None
    student_summaries = []

    if stream_id:
        selected_stream = get_object_or_404(Stream, id=stream_id, school=school)
        students = Student.objects.filter(school=school, current_stream=selected_stream, is_active=True)
        for student in students:
            results = ExamResult.objects.filter(exam=exam, student=student).select_related("subject")
            total_points = sum(r.points or 0 for r in results)
            total_score = sum(float(r.raw_score or 0) for r in results)
            subjects_sat = results.filter(is_absent=False).count()
            mean_score = total_score / subjects_sat if subjects_sat > 0 else 0
            mean_grade = score_to_grade(mean_score) if subjects_sat > 0 else "—"
            student_summaries.append({
                "student": student, "results": results,
                "total_points": total_points, "total_score": round(total_score, 1),
                "mean_score": round(mean_score, 1), "mean_grade": mean_grade,
                "subjects_sat": subjects_sat,
            })
        student_summaries.sort(key=lambda x: x["total_points"], reverse=True)
        for i, s in enumerate(student_summaries):
            s["position"] = i + 1

    context = {
        "exam": exam, "streams": streams,
        "selected_stream": selected_stream, "student_summaries": student_summaries,
    }
    return render(request, "exams/exam_results.html", context)


@admin_required
def report_card_list(request, pk):
    school = request.user.school
    exam = get_object_or_404(Exam, id=pk, school=school)
    stream_id = request.GET.get("stream")
    streams = exam.streams.all()
    selected_stream = None
    report_cards = []

    if stream_id:
        selected_stream = get_object_or_404(Stream, id=stream_id, school=school)
        report_cards = ReportCard.objects.filter(
            exam=exam, stream=selected_stream
        ).select_related("student").order_by("stream_position")

    context = {
        "exam": exam, "streams": streams,
        "selected_stream": selected_stream, "report_cards": report_cards,
    }
    return render(request, "exams/report_card_list.html", context)


@admin_required
def generate_report_cards(request, pk):
    school = request.user.school
    exam = get_object_or_404(Exam, id=pk, school=school)
    stream_id = request.POST.get("stream")

    if request.method == "POST" and stream_id:
        stream = get_object_or_404(Stream, id=stream_id, school=school)
        students = Student.objects.filter(school=school, current_stream=stream, is_active=True)
        generated = 0
        for student in students:
            results = ExamResult.objects.filter(exam=exam, student=student)
            total_score = sum(float(r.raw_score or 0) for r in results if not r.is_absent)
            total_points = sum(r.points or 0 for r in results if not r.is_absent)
            subjects_sat = results.filter(is_absent=False).count()
            mean_score = total_score / subjects_sat if subjects_sat > 0 else 0
            mean_grade = score_to_grade(mean_score) if subjects_sat > 0 else "X"

            fee_invoices = FeeInvoice.objects.filter(student=student, school=school)
            fee_balance = sum(float(inv.total_expected - inv.total_paid) for inv in fee_invoices)

            # Generate remarks based on performance
            if mean_grade in ['A', 'A-']:
                principal_remarks = "Excellent performance. Keep it up!"
                class_teacher_remarks = "Outstanding academic achievement."
            elif mean_grade in ['B+', 'B', 'B-']:
                principal_remarks = "Good performance. Room for improvement."
                class_teacher_remarks = "Satisfactory progress. Focus on weak areas."
            elif mean_grade in ['C+', 'C', 'C-']:
                principal_remarks = "Average performance. Needs significant improvement."
                class_teacher_remarks = "Below average. Extra effort required."
            else:
                principal_remarks = "Poor performance. Urgent attention needed."
                class_teacher_remarks = "Very poor results. Immediate intervention required."

            ReportCard.objects.update_or_create(
                student=student, exam=exam,
                defaults={
                    "stream": stream, "total_marks": total_score,
                    "total_points": total_points, "mean_score": mean_score,
                    "mean_grade": mean_grade, "subjects_sat": subjects_sat,
                    "stream_size": students.count(), "fee_balance": fee_balance,
                    "principal_remarks": principal_remarks,
                    "class_teacher_remarks": class_teacher_remarks,
                },
            )
            generated += 1

        all_reports = ReportCard.objects.filter(exam=exam, stream=stream).order_by("-total_points")
        for i, report in enumerate(all_reports):
            report.stream_position = i + 1
            report.save(update_fields=["stream_position"])

        messages.success(request, f"Generated {generated} report cards for {stream.full_name}!")
        return redirect("report_card_list", pk=exam.id)

    return redirect("exam_detail", pk=exam.id)


@admin_required
def report_card_view(request, pk):
    report = get_object_or_404(ReportCard, id=pk)
    school = request.user.school
    results = ExamResult.objects.filter(
        exam=report.exam, student=report.student
    ).select_related("subject").order_by("subject__name")
    
    # Grade distribution for this student
    grade_counts = {}
    for grade in ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'E']:
        grade_counts[grade] = 0
    
    for result in results:
        if result.grade in grade_counts and not result.is_absent:
            grade_counts[result.grade] += 1
    
    # Convert to list for easier template access
    grade_data = [
        grade_counts['A'], grade_counts['A-'], grade_counts['B+'],
        grade_counts['B'], grade_counts['B-'], grade_counts['C+'],
        grade_counts['C'], grade_counts['C-'], grade_counts['D+'],
        grade_counts['D'], grade_counts['D-'], grade_counts['E']
    ]
    
    context = {
        "report": report, 
        "school": school, 
        "results": results,
        "grade_counts": grade_counts,
        "grade_data": grade_data
    }
    return render(request, "exams/report_card_view.html", context)