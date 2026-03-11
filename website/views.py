from django.shortcuts import render, get_object_or_404
from .models import KCSEResult, GalleryAlbum, CoCurricularActivity, NewsEvent
from communications.models import ParentComment
from schools.models import School


def get_school():
    return School.objects.filter(is_active=True).first()


def home(request):
    school = get_school()
    news = NewsEvent.objects.filter(is_published=True)[:3]
    featured_comments = ParentComment.objects.filter(status="approved", is_featured=True)[:3]
    latest_kcse = KCSEResult.objects.filter(is_published=True).first()
    context = {
        "school": school,
        "news": news,
        "featured_comments": featured_comments,
        "latest_kcse": latest_kcse,
    }
    return render(request, "website/home.html", context)


def about(request):
    school = get_school()
    return render(request, "website/about.html", {"school": school})


def academics(request):
    school = get_school()
    return render(request, "website/academics.html", {"school": school})


def gallery(request):
    school = get_school()
    albums = GalleryAlbum.objects.filter(is_published=True)
    return render(request, "website/gallery.html", {"school": school, "albums": albums})


def kcse_results(request):
    school = get_school()
    results = KCSEResult.objects.filter(is_published=True)
    return render(request, "website/kcse_results.html", {"school": school, "results": results})


def co_curricular(request):
    school = get_school()
    activities = CoCurricularActivity.objects.filter(is_published=True)
    return render(request, "website/co_curricular.html", {"school": school, "activities": activities})


def contact(request):
    school = get_school()
    return render(request, "website/contact.html", {"school": school})


def parent_comments(request):
    school = get_school()
    comments = ParentComment.objects.filter(status="approved")
    return render(request, "website/parent_comments.html", {"school": school, "comments": comments})


def news_list(request):
    school = get_school()
    post_type = request.GET.get("type", "")
    news = NewsEvent.objects.filter(is_published=True)
    if post_type:
        news = news.filter(post_type=post_type)
    context = {
        "school": school,
        "news": news,
        "post_type": post_type,
    }
    return render(request, "website/news_list.html", context)


def news_detail(request, slug):
    school = get_school()
    post = get_object_or_404(NewsEvent, slug=slug, is_published=True)
    recent = NewsEvent.objects.filter(is_published=True).exclude(id=post.id)[:3]
    context = {
        "school": school,
        "post": post,
        "recent": recent,
    }
    return render(request, "website/news_detail.html", context)
