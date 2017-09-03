from django.shortcuts import render, redirect, reverse, HttpResponse
from django.core.urlresolvers import reverse_lazy
from django.views.generic import View, TemplateView, FormView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from registration.backends.simple.views import RegistrationView
from profiles.forms import UserProfileForm
from profiles.models import User, UserProfile, Post, UserWall, Comment


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
        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.errors)
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
            print('{} not allowed to edit {} profile'.format(self.request.user.usernamem, self.user.username))
            return super().get(request, *args, **kwargs)

    def get_form(self, *args, **kwargs):

        return self.form_class(self.request.POST, self.request.FILES, instance=self.userprofile)

    def form_valid(self, form):
        form.save(commit=True)
        return redirect('profile', self.user.username)

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, context=self.get_context_data(**kwargs))


@method_decorator(login_required, name='dispatch')
class AddPostView(View):

    def post(self, request, *args, **kwargs):
        post_text = request.POST.get('post_text')
        post_author_id = request.POST.get('post_author_id')
        post_wall_id = request.POST.get('post_wall_id')
        author = UserProfile.objects.get(id=post_author_id)
        wall = UserWall.objects.get(id=post_wall_id)
        if post_text and author and wall:
            Post.objects.create(text=post_text, author=author, user_wall=wall)
        return redirect(reverse('profile', kwargs={'username': wall.profile.user.username}))


@method_decorator(login_required, name='dispatch')
class AddCommentView(View):

    def post(self, request, *args, **kwargs):
        comment_text = request.POST.get('comment_text')
        comment_author_id = request.POST.get('comment_author_id')
        post_id = request.POST.get('post_id')
        author = UserProfile.objects.get(id=comment_author_id)
        post = Post.objects.get(id=post_id)
        if comment_text and author and post:
            Comment.objects.create(text=comment_text, author=author, post=post)
            return redirect(reverse('profile', kwargs={'username': post.user_wall.profile.user.username}))


@method_decorator(login_required, name='dispatch')
class LikePostView(View):

    def get(self, request, *args, **kwargs):
        post_id = int(request.GET['post_id'])
        profile_id = int(request.GET['profile_id'])
        profile = UserProfile.objects.get(id=str(profile_id))
        likes = 0
        if post_id:
            post = Post.objects.get(id=post_id)
            try:
                did_user_already_liked_post = post.likes.get(id=profile_id)
                likes = post.unlike(profile)
                button = 'Like'
            except Exception as e:
                likes = post.like(profile) if post else 0
                button = 'unLike'
        import json
        response = json.dumps({
            'likes': likes,
            'button': button
        })
        return HttpResponse(response, content_type='application/json')


@method_decorator(login_required, name='dispatch')
class LikeCommentView(View):

    def get(self, request, *args, **kwargs):
        comment_id = request.GET['comment_id']
        profile_id = request.GET['profile_id']
        profile = UserProfile.objects.get(id=str(profile_id))
        likes = 0
        if comment_id:
            comment = Comment.objects.get(id=int(comment_id))
            if not comment.likes_set.get(id=profile_id):
                likes = comment.like(profile) if comment else 0
            else:
                likes = comment.unlike(profile)
        return HttpResponse(likes)
