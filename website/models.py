# ================================================================
# FILE: website/models.py
# REPLACE your entire website/models.py with this.
# This has ALL fields that your views and templates reference,
# including both candidates_sat AND total_candidates as a property.
# ================================================================

from django.db import models
from django.utils import timezone


class KCSEResult(models.Model):
    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        related_name='kcse_results'
    )
    year = models.IntegerField()

    # Core stats
    candidates_sat = models.IntegerField(default=0)
    mean_grade = models.CharField(max_length=5, blank=True)
    mean_points = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # Performance indicators
    university_qualifiers = models.IntegerField(default=0)
    pass_rate = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    county_position = models.IntegerField(null=True, blank=True)
    national_position = models.IntegerField(null=True, blank=True)

    # Grade distribution
    count_a_plain  = models.IntegerField(default=0)
    count_a_minus  = models.IntegerField(default=0)
    count_b_plus   = models.IntegerField(default=0)
    count_b_plain  = models.IntegerField(default=0)
    count_b_minus  = models.IntegerField(default=0)
    count_c_plus   = models.IntegerField(default=0)
    count_c_plain  = models.IntegerField(default=0)
    count_c_minus  = models.IntegerField(default=0)
    count_d_plus   = models.IntegerField(default=0)
    count_d_plain  = models.IntegerField(default=0)
    count_d_minus  = models.IntegerField(default=0)
    count_e        = models.IntegerField(default=0)

    # Top student
    top_student_name   = models.CharField(max_length=200, blank=True)
    top_student_grade  = models.CharField(max_length=5, blank=True)
    top_student_points = models.IntegerField(null=True, blank=True)

    # Summary / notes
    summary = models.TextField(blank=True)

    is_published = models.BooleanField(default=False)
    created_at   = models.DateTimeField(default=timezone.now)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year']
        unique_together = ['school', 'year']

    def __str__(self):
        return f"KCSE {self.year} - {self.school.name}"

    @property
    def total_candidates(self):
        """Alias for candidates_sat — kept for backward compatibility."""
        return self.candidates_sat

    @property
    def above_c_plus(self):
        """Students who scored C+ and above (university entry)."""
        return (
            self.count_a_plain + self.count_a_minus +
            self.count_b_plus + self.count_b_plain + self.count_b_minus +
            self.count_c_plus
        )


class NewsEvent(models.Model):
    POST_TYPES = [
        ('news', 'News'),
        ('event', 'Event'),
        ('notice', 'Notice'),
        ('achievement', 'Achievement'),
    ]
    school       = models.ForeignKey('schools.School', on_delete=models.CASCADE)
    title        = models.CharField(max_length=300)
    slug         = models.SlugField(unique=True, blank=True)
    post_type    = models.CharField(max_length=20, choices=POST_TYPES, default='news')
    content      = models.TextField()
    summary      = models.CharField(max_length=500, blank=True)
    cover_image  = models.ImageField(upload_to='news/', blank=True, null=True)
    is_published = models.BooleanField(default=False)
    is_featured  = models.BooleanField(default=False)
    created_at   = models.DateTimeField(default=timezone.now)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class GalleryAlbum(models.Model):
    school       = models.ForeignKey('schools.School', on_delete=models.CASCADE)
    title        = models.CharField(max_length=200)
    description  = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)
    created_at   = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


class GalleryPhoto(models.Model):
    album       = models.ForeignKey(GalleryAlbum, on_delete=models.CASCADE, related_name='photos')
    image       = models.ImageField(upload_to='gallery/')
    caption     = models.CharField(max_length=300, blank=True)
    is_featured = models.BooleanField(default=False)
    created_at  = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Photo in {self.album.title}"


class ParentComment(models.Model):
    school      = models.ForeignKey('schools.School', on_delete=models.CASCADE)
    author_name = models.CharField(max_length=200)
    comment     = models.TextField()
    rating      = models.IntegerField(default=5, choices=[(i, i) for i in range(1, 6)])
    is_featured = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    created_at  = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.author_name} - {self.school.name}"


class CoCurricularActivity(models.Model):
    school      = models.ForeignKey('schools.School', on_delete=models.CASCADE)
    name        = models.CharField(max_length=200)
    category    = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    image       = models.ImageField(upload_to='cocurricular/', blank=True, null=True)
    is_active   = models.BooleanField(default=True)

    def __str__(self):
        return self.name