from django.urls import path
from blog.views import (
	create_blog_view,
	detail_blog_view,
	edit_blog_view,
    BlogDeleteView,
     add_comment, 
     like_post
)

app_name = 'blog'

urlpatterns = [
    path('create/', create_blog_view, name="create"),
    path('<slug>/detail/', detail_blog_view, name="detail"),
    path('<slug>/edit/', edit_blog_view, name="edit"),
    path('<slug:slug>/delete/', BlogDeleteView.as_view(), name='delete'),
    path('post/<slug:slug>/comment/', add_comment, name='add_comment'),
    path('post/<slug:slug>/like/', like_post, name='like_post'),
 ]