from django.db import models
import uuid


class GalleryAlbum(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("schools.School", on_delete=models.CASCADE, related_name="gallery_albums")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=30,
        choices=[
            ("academics", "Academics"), ("sports", "Sports"),
            ("culture", "Culture & Arts"), ("trips", "Trips & Excursions"),
            ("graduations", "Graduations & Awards"), ("facilities", "Facilities"), ("other", "Other"),
        ],
        default="other",
    )
    cover_image = models.ImageField(upload_to="gallery/covers/", null=True, blank=True)
    is_published = models.BooleanField(default=False)
    event_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-event_date", "-created_at"]

    def __str__(self):
        return f"{self.school.name} â€” {self.title}"


class GalleryPhoto(models.Model):
    album = models.ForeignKey(GalleryAlbum, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="gallery/photos/")
    caption = models.CharField(max_length=300, blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    uploaded_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "uploaded_at"]


class KCSEResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("schools.School", on_delete=models.CASCADE, related_name="kcse_results")
    year = models.PositiveIntegerField()
    total_candidates = models.PositiveSmallIntegerField(default=0)
    candidates_sat = models.PositiveSmallIntegerField(default=0)
    count_a_plain = models.PositiveSmallIntegerField(default=0)
    count_a_minus = models.PositiveSmallIntegerField(default=0)
    count_b_plus = models.PositiveSmallIntegerField(default=0)
    count_b_plain = models.PositiveSmallIntegerField(default=0)
    count_b_minus = models.PositiveSmallIntegerField(default=0)
    count_c_plus = models.PositiveSmallIntegerField(default=0)
    count_c_plain = models.PositiveSmallIntegerField(default=0)
    count_c_minus = models.PositiveSmallIntegerField(default=0)
    count_d_plus = models.PositiveSmallIntegerField(default=0)
    count_d_plain = models.PositiveSmallIntegerField(default=0)
    count_d_minus = models.PositiveSmallIntegerField(default=0)
    count_e = models.PositiveSmallIntegerField(default=0)
    mean_grade = models.CharField(max_length=3, blank=True)
    mean_points = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    county_position = models.PositiveSmallIntegerField(null=True, blank=True)
    national_position = models.PositiveSmallIntegerField(null=True, blank=True)
    university_qualifiers = models.PositiveSmallIntegerField(default=0)
    top_student_name = models.CharField(max_length=200, blank=True)
    top_student_points = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    top_student_grade = models.CharField(max_length=3, blank=True)
    summary = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("school", "year")
        ordering = ["-year"]

    def __str__(self):
        return f"KCSE {self.year} â€” {self.school.name} â€” Mean: {self.mean_grade}"

    @property
    def pass_rate(self):
        if not self.candidates_sat:
            return 0
        passers = (self.count_a_plain + self.count_a_minus + self.count_b_plus +
                   self.count_b_plain + self.count_b_minus + self.count_c_plus + self.count_c_plain)
        return round((passers / self.candidates_sat) * 100, 1)

    @property
    def grade_breakdown(self):
        return [
            ('A', self.count_a_plain),
            ('A-', self.count_a_minus),
            ('B+', self.count_b_plus),
            ('B', self.count_b_plain),
            ('B-', self.count_b_minus),
            ('C+', self.count_c_plus),
            ('C', self.count_c_plain),
            ('C-', self.count_c_minus),
            ('D+', self.count_d_plus),
            ('D', self.count_d_plain),
            ('D-', self.count_d_minus),
            ('E', self.count_e),
        ]


class CoCurricularActivity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("schools.School", on_delete=models.CASCADE, related_name="activities")
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=30,
        choices=[
            ("sports", "Sports"), ("arts", "Music, Drama & Arts"),
            ("academics", "Academic Clubs"), ("community", "Community Service"),
            ("religious", "Religious"), ("other", "Other"),
        ],
        default="other",
    )
    description = models.TextField(blank=True)
    patron = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="patronized_activities")
    image = models.ImageField(upload_to="activities/", null=True, blank=True)
    achievements = models.TextField(blank=True)
    meeting_schedule = models.CharField(max_length=200, blank=True)
    is_published = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["category", "order", "name"]

    def __str__(self):
        return f"{self.name} â€” {self.school.name}"


class NewsEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("schools.School", on_delete=models.CASCADE, related_name="news_events")
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=320)
    content = models.TextField()
    summary = models.CharField(max_length=500, blank=True)
    cover_image = models.ImageField(upload_to="news/", null=True, blank=True)
    post_type = models.CharField(max_length=10,
        choices=[("news", "News"), ("event", "Event"), ("notice", "Notice")],
        default="news",
    )
    event_date = models.DateField(null=True, blank=True)
    event_location = models.CharField(max_length=200, blank=True)
    author = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("school", "slug")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} â€” {self.school.name}"

