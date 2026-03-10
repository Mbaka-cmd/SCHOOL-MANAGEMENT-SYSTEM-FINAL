from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Notice
from schools.models import School


def get_school():
    return School.objects.first()


@login_required
def notice_list(request):
    school = get_school()
    notices = Notice.objects.filter(school=school, is_active=True)
    return render(request, 'notices/notice_list.html', {
        'school': school,
        'notices': notices,
    })


@login_required
def notice_create(request):
    school = get_school()
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        audience = request.POST.get('audience')
        priority = request.POST.get('priority')
        expires_at = request.POST.get('expires_at') or None
        Notice.objects.create(
            school=school,
            title=title,
            content=content,
            audience=audience,
            priority=priority,
            expires_at=expires_at,
            posted_by=request.user,
        )
        messages.success(request, f'Notice "{title}" posted successfully.')
        return redirect('notice_list')
    return render(request, 'notices/notice_form.html', {'school': school})


@login_required
def notice_delete(request, notice_id):
    notice = get_object_or_404(Notice, id=notice_id)
    if request.method == 'POST':
        notice.is_active = False
        notice.save()
        messages.success(request, 'Notice removed.')
    return redirect('notice_list')


def public_notices(request):
    school = get_school()
    notices = Notice.objects.filter(school=school, is_active=True, audience__in=['all', 'parents'])
    return render(request, 'notices/public_notices.html', {
        'school': school,
        'notices': notices,
    })
