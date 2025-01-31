from django import forms
from blog.models import BlogPost, Category, Comment

choice = Category.objects.all().values_list('name','name')
choice_list = [
        ('tech', 'Technology'),
        ('life', 'Lifestyle'),
        ('travel', 'Rides'),
    ]
class CreateBlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'body', 'image', 'category']
        widgets ={
            'category': forms.Select(choices=choice_list,attrs={'class':'form-control'}),
        }

class UpdateBlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'body', 'image', 'category']

    def save(self, commit=True):
        blog_post = self.instance
        blog_post.title = self.cleaned_data['title']
        blog_post.body = self.cleaned_data['body']
        blog_post.category = self.cleaned_data['category']

        if self.cleaned_data['image']:
            blog_post.image = self.cleaned_data['image']

        if commit:
            blog_post.save()
        return blog_post

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']