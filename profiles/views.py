from django.shortcuts import render, redirect, reverse, HttpResponse
from django.core.urlresolvers import reverse_lazy
from django.views.generic import View, TemplateView, FormView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from registration.backends.simple.views import RegistrationView
from profiles.forms import UserProfileForm
from profiles.models import User, UserProfile, Post, UserWall, Comment
import json


class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            self.userprofile = UserProfile.objects.get(user=self.request.user)
            context['userprofile'] = self.userprofile
        except Exception as e:
            context['userprofile'] = None
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, context=self.get_context_data(**kwargs))


class MyRegistrationView(RegistrationView):

    def get_success_url(self, user=None):
        return reverse('register_profile')

    def form_invalid(self, form):
        messages.error(self.request, 'Can\'t create user because: {}'.format(form.errors))
        return super().form_invalid(form)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


@method_decorator(login_required, name='dispatch')
class RegisterProfileView(FormView):
    template_name = 'profiles/profile_registration.html'
    form_class = UserProfileForm
    success_url = reverse_lazy('index')
    context_dict = dict()

    def dispatch(self, request, *args, **kwargs):
        form = UserProfileForm()
        self.context_dict = {'form': form}
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return self.context_dict

    def form_valid(self, form):
        self.context_dict = {'form': form}
        user_profile = form.save(commit=False)
        user_profile.user = self.request.user
        user_profile.save()
        UserWall.objects.create(profile=user_profile)
        messages.info(self.request, '{} Profile created successfully!'.format(self.request.user.username))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Couldn\'t create profile: {}'.format(form.errors))
        return super().form_invalid(form)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, context=self.get_context_data(**kwargs))


@method_decorator(login_required, name='dispatch')
class ProfileView(FormView):
    template_name = 'profiles/profile.html'
    form_class = UserProfileForm

    def dispatch(self, request, *args, **kwargs):
        self.username = kwargs.get('username')
        try:
            self.user = User.objects.get(username=self.username)
        except User.DoesNotExist:
            return redirect('index')
        self.userprofile = UserProfile.objects.get_or_create(user=self.user)[0]
        self.form = UserProfileForm({'first_name': self.userprofile.first_name,
                                     'last_name': self.userprofile.last_name,
                                     'avatar': self.userprofile.avatar,
                                     'birthday': self.userprofile.birthday,
                                     'town': self.userprofile.town,
                                     'relationship': self.userprofile.relationship})
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return {'userprofile': self.userprofile, 'selecteduser': self.user, 'form': self.form}

    def post(self, request, *args, **kwargs):
        if self.request.user.username == self.user.username:
            return super().post(request, *args, **kwargs)
        else:
            messages.error(request,
                           '{} not allowed to edit {} profile'.format(self.request.user.usernamem, self.user.username))
            return super().get(request, *args, **kwargs)

    def get_form(self, *args, **kwargs):
        return self.form_class(self.request.POST, self.request.FILES, instance=self.userprofile)

    def form_valid(self, form):
        form.save(commit=True)
        messages.info(self.request, 'User Profile updated successfully')
        return redirect('profile', self.user.username)

    def form_invalid(self, form):
        messages.error(self.request, 'Couldn\'t update profile: {}'.format(form.errors))
        return super().form_invalid(form)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, context=self.get_context_data(**kwargs))


@method_decorator(login_required, name='dispatch')
class AddPostView(View):

    def post(self, request, *args, **kwargs):
        if request.POST.get('_method') == 'update':
            return self.update(request, *args, **kwargs)
        post_text = request.POST.get('post_text')
        post_author_id = request.POST.get('post_author_id')
        post_wall_id = request.POST.get('post_wall_id')
        author = UserProfile.objects.get(id=post_author_id)
        wall = UserWall.objects.get(id=post_wall_id)
        if post_text and author and wall:
            wall.add_post(text=post_text, author=author)
        messages.info(request, 'Post added successfully!')
        return redirect(reverse('profile', kwargs={'username': wall.profile.user.username}))

    def update(self, request, *args, **kwargs):
        post_id = request.POST.get('post_id')
        post_text = request.POST.get('post_text')
        post = Post.objects.get(id=str(post_id))
        post.text = post_text
        post.date = timezone.now()
        post.save()
        messages.info(request, 'Post updated successfully!')
        return redirect(reverse('profile', kwargs={'username': post.user_wall.profile.user.username}))


@method_decorator(login_required, name='dispatch')
class EditPostView(TemplateView):
    template_name = 'profiles/edit_post_form.html'

    def get_context_data(self, **kwargs):
        return {'post_id': self.request.GET.get('post_id')}


@method_decorator(login_required, name='dispatch')
class RemovePostView(View):

    def post(self, request, *args, **kwargs):
        post_id = str(request.POST.get('post_id'))
        userprofile_id = str(request.POST.get('userprofile_id'))
        post = Post.objects.get(id=post_id)
        userprofile = UserProfile.objects.get(id=userprofile_id)
        if post.author == userprofile:
            post.delete()
            messages.info(request, 'Post deleted!')
        else:
            messages.info(request, 'You are not authorised to remove this post!')
        return redirect(reverse('profile', kwargs={'username': post.user_wall.profile.user.username}))


@method_decorator(login_required, name='dispatch')
class AddCommentView(View):

    def post(self, request, *args, **kwargs):
        if request.POST.get('_method') == 'update':
            return self.update(request, *args, **kwargs)
        comment_text = request.POST.get('comment_text')
        comment_author_id = request.POST.get('comment_author_id')
        post_id = request.POST.get('post_id')
        author = UserProfile.objects.get(id=comment_author_id)
        post = Post.objects.get(id=post_id)
        if comment_text and author and post:
            post.add_comment(text=comment_text, author=author)
            messages.info(request, 'Comment added successfully!')
        return redirect(reverse('profile', kwargs={'username': post.user_wall.profile.user.username}))

    def update(self, request, *args, **kwargs):
        comment_id = request.POST.get('comment_id')
        comment_text = request.POST.get('comment_text')
        comment = Comment.objects.get(id=str(comment_id))
        comment.text = comment_text
        comment.date = timezone.now()
        comment.save()
        messages.info(request, 'Comment updated successfully!')
        return redirect(reverse('profile', kwargs={'username': comment.post.user_wall.profile.user.username}))


@method_decorator(login_required, name='dispatch')
class EditCommentView(TemplateView):
    template_name = 'profiles/edit_comment_form.html'

    def get_context_data(self, **kwargs):
        return {'comment_id': self.request.GET.get('comment_id')}


@method_decorator(login_required, name='dispatch')
class RemoveCommentView(View):

    def post(self, request, *args, **kwargs):
        comment_id = str(request.POST.get('comment_id'))
        userprofile_id = str(request.POST.get('userprofile_id'))
        comment = Comment.objects.get(id=comment_id)
        userprofile = UserProfile.objects.get(id=userprofile_id)
        if comment.author == userprofile:
            comment.delete()
            messages.info(request, 'Comment deleted!')
        else:
            messages.info(request, 'You are not authorised to remove this comment!')
        return redirect(reverse('profile', kwargs={'username': comment.post.user_wall.profile.user.username}))


@method_decorator(login_required, name='dispatch')
class LikePostView(View):

    def get(self, request, *args, **kwargs):
        post_id = str(request.GET.get('post_id'))
        profile_id = str(request.GET.get('profile_id'))
        profile = UserProfile.objects.get(id=profile_id)
        likes = 0
        button = 'Like'
        if post_id:
            post = Post.objects.get(id=post_id)
            try:
                did_user_already_liked_post = post.likes.get(id=profile_id)
                likes = post.unlike(profile)
                button = 'Like'
            except Exception as e:
                likes = post.like(profile) if post else 0
                button = 'unLike'
        response = json.dumps({
            'likes': likes,
            'button': button
        })
        return HttpResponse(response, content_type='application/json')


@method_decorator(login_required, name='dispatch')
class LikeCommentView(View):

    def get(self, request, *args, **kwargs):
        comment_id = str(request.GET['comment_id'])
        profile_id = str(request.GET['profile_id'])
        profile = UserProfile.objects.get(id=profile_id)
        likes = 0
        button = 'Like'
        if comment_id:
            comment = Comment.objects.get(id=comment_id)
            try:
                did_user_already_liked_comment = comment.likes.get(id=profile_id)
                likes = comment.unlike(profile)
                button = 'Like'
            except Exception as e:
                likes = comment.like(profile) if comment else 0
                button = 'unLike'
        response = json.dumps({
            'likes': likes,
            'button': button
        })
        return HttpResponse(response, content_type='application/json')


@method_decorator(login_required, name='dispatch')
class SearchView(TemplateView):
    template_name = 'suggestions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        starts_with = self.request.GET.get('suggestion')
        max_result = 8
        search_results = list()
        if starts_with:
            search_results = UserProfile.objects.filter(visible_name__istartswith=starts_with)
        context['suggestions'] = search_results[:max_result]
        return context
