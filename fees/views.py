import json
import uuid as uuid_lib
import base64
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import FeeInvoice, Payment, MPesaTransaction
from students.models import Student
from academics.models import Stream
from schools.models import AcademicYear, Term
from schools.views import admin_required


@admin_required
def fee_dashboard(request):
    school = request.user.school
    invoices = FeeInvoice.objects.filter(school=school)
    total_expected = sum(i.total_expected for i in invoices)
    total_collected = sum(i.total_paid for i in invoices)
    context = {
        "school": school,
        "total_invoices": invoices.count(),
        "total_paid": invoices.filter(status="paid").count(),
        "total_pending": invoices.filter(status="pending").count(),
        "total_partial": invoices.filter(status="partial").count(),
        "total_expected": total_expected,
        "total_collected": total_collected,
        "recent_payments": Payment.objects.filter(school=school).order_by("-payment_date")[:10],
    }
    return render(request, "fees/fee_dashboard.html", context)


@admin_required
def invoice_list(request):
    school = request.user.school
    invoices = FeeInvoice.objects.filter(school=school).select_related(
        "student", "student__current_stream", "term", "academic_year"
    )
    status_filter = request.GET.get("status", "")
    search = request.GET.get("search", "")
    if status_filter:
        invoices = invoices.filter(status=status_filter)
    if search:
        invoices = invoices.filter(
            student__first_name__icontains=search
        ) | invoices.filter(
            student__last_name__icontains=search
        ) | invoices.filter(
            student__admission_number__icontains=search
        )
    context = {
        "invoices": invoices.order_by("-created_at"),
        "status_filter": status_filter,
        "search": search,
    }
    return render(request, "fees/invoice_list.html", context)


@admin_required
def generate_invoices(request):
    school = request.user.school
    if request.method == "POST":
        amount = request.POST.get("amount")
        term_id = request.POST.get("term")
        year_id = request.POST.get("year")
        description = request.POST.get("description", "")
        due_date = request.POST.get("due_date") or None

        try:
            term = Term.objects.get(id=term_id)
            academic_year = AcademicYear.objects.get(id=year_id, school=school)
        except Exception as e:
            messages.error(request, f"Invalid term or year: {e}")
            return redirect("generate_invoices")

        students = Student.objects.filter(school=school, is_active=True)
        stream_id = request.POST.get("stream")
        if stream_id:
            students = students.filter(current_stream_id=stream_id)

        created = 0
        for student in students:
            existing = FeeInvoice.objects.filter(
                school=school, student=student, term=term, academic_year=academic_year,
            ).exists()
            if not existing:
                invoice_number = f"INV-{school.id.hex[:4].upper()}-{uuid_lib.uuid4().hex[:6].upper()}"
                FeeInvoice.objects.create(
                    school=school, student=student, term=term,
                    academic_year=academic_year, invoice_number=invoice_number,
                    total_expected=amount, due_date=due_date, notes=description,
                )
                created += 1
        messages.success(request, f"Generated {created} invoices successfully!")
        return redirect("invoice_list")

    streams = Stream.objects.filter(school=school)
    terms = Term.objects.filter(academic_year__school=school)
    years = AcademicYear.objects.filter(school=school)
    context = {"streams": streams, "terms": terms, "years": years}
    return render(request, "fees/generate_invoices.html", context)


@admin_required
def invoice_detail(request, pk):
    school = request.user.school
    invoice = get_object_or_404(FeeInvoice, id=pk, school=school)
    payments = Payment.objects.filter(invoice=invoice).order_by("-payment_date")
    context = {"invoice": invoice, "payments": payments}
    return render(request, "fees/invoice_detail.html", context)


@admin_required
def record_payment(request, pk):
    school = request.user.school
    invoice = get_object_or_404(FeeInvoice, id=pk, school=school)
    if request.method == "POST":
        amount = float(request.POST.get("amount", 0))
        method = request.POST.get("method", "cash")
        reference = request.POST.get("reference", "")
        notes = request.POST.get("notes", "")
        receipt_number = f"RCP-{uuid_lib.uuid4().hex[:8].upper()}"
        Payment.objects.create(
            school=school, invoice=invoice, receipt_number=receipt_number,
            amount=amount, method=method, bank_reference=reference,
            notes=notes, payment_date=timezone.now(), received_by=request.user,
        )
        invoice.total_paid = float(invoice.total_paid) + amount
        if invoice.total_paid >= float(invoice.total_expected):
            invoice.status = "paid"
        elif invoice.total_paid > 0:
            invoice.status = "partial"
        invoice.save()
        messages.success(request, f"Payment of KES {amount:,.0f} recorded!")
        return redirect("invoice_detail", pk=invoice.id)
    context = {"invoice": invoice}
    return render(request, "fees/record_payment.html", context)


@admin_required
def mpesa_stk_push(request, pk):
    school = request.user.school
    invoice = get_object_or_404(FeeInvoice, id=pk, school=school)
    if request.method == "POST":
        phone = request.POST.get("phone", "").strip()
        amount = int(float(request.POST.get("amount", invoice.balance)))
        if phone.startswith("0"):
            phone = "254" + phone[1:]
        elif phone.startswith("+254"):
            phone = phone[1:]
        messages.success(
            request,
            f"STK Push sent to {phone} for KES {amount}. "
            f"Configure Daraja API keys in fees/views.py to go live."
        )
        return redirect("invoice_detail", pk=invoice.id)
    context = {"invoice": invoice}
    return render(request, "fees/mpesa_push.html", context)


@csrf_exempt
def mpesa_callback(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            result = data["Body"]["stkCallback"]
            checkout_id = result["CheckoutRequestID"]
            result_code = result["ResultCode"]
            txn = MPesaTransaction.objects.filter(checkout_request_id=checkout_id).first()
            if txn and result_code == 0:
                txn.status = "success"
                txn.save()
        except Exception:
            pass
    return JsonResponse({"ResultCode": 0, "ResultDesc": "Success"})