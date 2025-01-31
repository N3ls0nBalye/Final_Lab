from django.db import models
from django.db.models.signals import pre_save, post_delete
from django.utils.text import slugify
from django.conf import settings
from django.dispatch import receiver
from django.contrib.auth.models import User

def upload_location(instance, filename):
    author_id = str(instance.author.id) if instance.author else "unknown"
    title = str(instance.title) if instance.title else "untitled"
    return f'blog/{author_id}/{title}-{filename}'


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)  # This field should not be null

    def save(self, *args, **kwargs):
        # Automatically generate a slug based on the name field before saving
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class BlogPost(models.Model):
    title = models.CharField(max_length=50, null=False, blank=False)
    body = models.TextField(max_length=500, null=False, blank=False)
    image = models.ImageField(upload_to=upload_location, null=True, blank=True)
    date_published = models.DateTimeField(auto_now_add=True, verbose_name="date published")
    date_updated = models.DateTimeField(auto_now=True, verbose_name="date updated")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    slug = models.SlugField(blank=True, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title

@receiver(post_delete, sender=BlogPost)
def submission_delete(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(False)

def pre_save_blog_post_receiver(sender, instance, *args, **kwargs):
    if instance.author and not instance.slug:
        instance.slug = slugify(f"{instance.author.username}-{instance.title}")

pre_save.connect(pre_save_blog_post_receiver, sender=BlogPost)



class Comment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.created_at}"

class Like(models.Model):
    post = models.ForeignKey('BlogPost', on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')  # Ensures a user can only like a post once