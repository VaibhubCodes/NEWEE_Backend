from django.db import models
from django.contrib.auth import get_user_model
from questions.models import Subject, Chapter, Topic
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
User = get_user_model()

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name



class Blog(models.Model):
    title = models.CharField(max_length=255)
    content = RichTextUploadingField()  # Use CKEditor for the blog content
    main_image = models.ImageField(upload_to='blogs/main_images/')
    additional_images = models.ImageField(upload_to='blogs/additional_images/', blank=True, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="blogs")
    chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL, null=True, blank=True, related_name="blogs")
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name="blogs")
    tags = models.ManyToManyField(Tag, related_name="blogs", blank=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="authored_blogs")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    view_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title


class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.blog.title}"

class SavedBlog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_blogs")
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="saved_by_users")
    saved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} saved {self.blog.title}"
