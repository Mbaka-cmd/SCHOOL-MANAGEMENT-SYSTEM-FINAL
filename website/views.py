from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import KCSEResult, GalleryAlbum, CoCurricularActivity, NewsEvent
from communications.models import ParentComment
from notices.models import Notice
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


def student_life(request):
    school = get_school()
    # Get some sample data - you can expand this based on your models
    clubs = []  # You can add clubs/societies data here
    return render(request, "website/student_life.html", {
        "school": school, 
        "clubs": clubs
    })


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
    
    # Get NewsEvent objects
    news_events = NewsEvent.objects.filter(is_published=True)
    if post_type:
        news_events = news_events.filter(post_type=post_type)
    
    # Get Notice objects for "Everyone" audience
    notices = Notice.objects.filter(
        school=school,
        audience='all',
        is_active=True
    ).exclude(
        expires_at__lt=timezone.now().date()
    )
    
    if post_type == 'notice':
        # If filtering for notices only, don't include news/events
        combined_items = []
        for notice in notices:
            combined_items.append({
                'type': 'notice',
                'id': notice.id,
                'title': notice.title,
                'content': notice.content,
                'summary': notice.content[:200] + '...' if len(notice.content) > 200 else notice.content,
                'created_at': notice.created_at,
                'post_type': 'notice',
                'priority': notice.priority,
                'expires_at': notice.expires_at,
                'slug': f'notice-{notice.id}',  # Create a pseudo-slug
                'url_name': 'notice_detail',  # We'll need to create this URL
                'posted_by': notice.posted_by,
            })
    else:
        # Combine news/events and notices
        combined_items = []
        
        # Add news/events
        for news in news_events:
            combined_items.append({
                'type': 'news_event',
                'id': news.id,
                'title': news.title,
                'content': news.content,
                'summary': news.summary,
                'created_at': news.published_at or news.created_at,
                'post_type': news.post_type,
                'event_date': news.event_date,
                'event_location': news.event_location,
                'slug': news.slug,
                'url_name': 'news_detail',
                'cover_image': news.cover_image,
                'author': news.author,
            })
        
        # Add notices (only if not filtering for specific type)
        if not post_type:
            for notice in notices:
                combined_items.append({
                    'type': 'notice',
                    'id': notice.id,
                    'title': notice.title,
                    'content': notice.content,
                    'summary': notice.content[:200] + '...' if len(notice.content) > 200 else notice.content,
                    'created_at': notice.created_at,
                    'post_type': 'notice',
                    'priority': notice.priority,
                    'expires_at': notice.expires_at,
                    'slug': f'notice-{notice.id}',
                    'url_name': 'notice_detail',
                    'posted_by': notice.posted_by,
                })
    
    # Sort by creation date (newest first)
    combined_items.sort(key=lambda x: x['created_at'], reverse=True)
    
    context = {
        "school": school,
        "news": combined_items,
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


def notice_detail(request, notice_id):
    school = get_school()
    notice = get_object_or_404(Notice, id=notice_id, school=school, audience='all', is_active=True)
    
    # Get recent notices and news/events
    recent_notices = Notice.objects.filter(
        school=school, 
        audience='all', 
        is_active=True
    ).exclude(id=notice.id).exclude(expires_at__lt=timezone.now())[:2]
    
    recent_news = NewsEvent.objects.filter(is_published=True)[:2]
    recent = list(recent_notices) + list(recent_news)
    recent.sort(key=lambda x: x.created_at, reverse=True)
    recent = recent[:3]
    
    context = {
        "school": school,
        "post": notice,
        "recent": recent,
        "is_notice": True,
    }
    return render(request, "website/notice_detail.html", context)
