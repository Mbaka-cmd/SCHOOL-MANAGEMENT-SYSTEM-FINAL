from django.shortcuts import render, get_object_or_404
from .models import NewsEvent, GalleryAlbum, KCSEResult, CoCurricularActivity
from notices.models import Notice
from schools.models import School


def get_school():
    return School.objects.filter(is_active=True).first()


def home(request):
    school = get_school()
    news = NewsEvent.objects.filter(is_published=True).order_by("-created_at")[:3]
    gallery_albums = GalleryAlbum.objects.filter(is_published=True)[:6]
    return render(request, "website/home.html", {"school": school, "news": news, "gallery_albums": gallery_albums})


def about(request):
    return render(request, "website/about.html", {"school": get_school()})


def academics(request):
    return render(request, "website/academics.html", {"school": get_school()})


def contact(request):
    return render(request, "website/contact.html", {"school": get_school()})


def gallery(request):
    school = get_school()
    albums = GalleryAlbum.objects.filter(is_published=True)
    return render(request, "website/gallery.html", {"school": school, "albums": albums})


def kcse_results(request):
    school = get_school()
    results = KCSEResult.objects.filter(is_published=True).order_by("-year")
    return render(request, "website/kcse_results.html", {"school": school, "results": results})


def co_curricular(request):
    school = get_school()
    activities = CoCurricularActivity.objects.filter(is_active=True)
    return render(request, "website/co_curricular.html", {"school": school, "activities": activities})


def student_life(request):
    return render(request, "website/student_life.html", {"school": get_school()})


def parent_comments(request):
    return render(request, "website/parent_comments.html", {"school": get_school()})


def news_list(request):
    school = get_school()
    news = NewsEvent.objects.filter(is_published=True).order_by("-created_at")
    return render(request, "website/news_list.html", {"school": school, "news": news})


def news_detail(request, slug):
    school = get_school()
    post = get_object_or_404(NewsEvent, slug=slug, is_published=True)
    recent = NewsEvent.objects.filter(is_published=True).exclude(id=post.id)[:3]
    return render(request, "website/news_detail.html", {"school": school, "post": post, "recent": recent})


def notice_detail(request, notice_id):
    school = get_school()
    notice = get_object_or_404(Notice, id=notice_id, school=school, is_published=True)
    return render(request, "website/notice_detail.html", {"school": school, "post": notice})
