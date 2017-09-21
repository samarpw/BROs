from django.shortcuts import render, redirect, reverse, HttpResponse
from django.core.urlresolvers import reverse_lazy
from django.views.generic import View, TemplateView, FormView, ListView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from registration.backends.simple.views import RegistrationView
from profiles.forms import UserProfileForm
from profiles.models import User, UserProfile, UserWall, Notification
import json


class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            userprofile = UserProfile.objects.get(user=self.request.user)
            context['userprofile'] = userprofile
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
class AddNoteView(View):

    def post(self, request, *args, **kwargs):
        note_class = request.POST.get('_class')
        note_class = globals()[note_class]
        note_text = request.POST.get('note_text')
        parent_id = request.POST.get('parent_id')
        parent_class = note_class._meta.get_field('parent').rel.to
        parent = parent_class.objects.get(id=parent_id)
        author_id = request.POST.get('author_id')
        author = UserProfile.objects.get(id=author_id)
        if note_text and author and parent:
            note = parent.add_note(text=note_text, author=author)
            messages.info(request, '{} added successfully!'.format(note_class.__name__))
            return redirect('profile', username=note.get_wall().profile.user.username)


@method_decorator(login_required, name='dispatch')
class EditNoteView(View):

    def post(self, request, *args, **kwargs):
        note_class = request.POST.get('_class')
        note_class = globals()[note_class]
        note_text = request.POST.get('note_text')
        note_id = request.POST.get('note_id')
        note = note_class.objects.get(id=note_id)
        note.text = note_text
        note.date = timezone.now()
        note.save()
        messages.info(request, '{} updated successfully!'.format(note_class.__name__))
        return redirect('profile', username=note.get_wall().profile.user.username)


@method_decorator(login_required, name='dispatch')
class EditNoteFormView(TemplateView):

    def dispatch(self, request, *args, **kwargs):
        if self.request.GET.get('note_class') == 'Post':
            self.template_name = 'profiles/edit_post_form.html'
        elif self.request.GET.get('note_class') == 'Comment':
            self.template_name = 'profiles/edit_comment_form.html'
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return {'note_id': self.request.GET.get('note_id')}


@method_decorator(login_required, name='dispatch')
class RemoveNoteView(View):

    def post(self, request, *args, **kwargs):
        note_id = request.POST.get('note_id')
        class_name = request.POST.get('_class')
        note_class = globals()[class_name]
        userprofile_id = request.POST.get('userprofile_id')
        note = note_class.objects.get(id=note_id)
        userprofile = UserProfile.objects.get(id=userprofile_id)
        if note.author == userprofile:
            note.delete()
            messages.info(request, '{} deleted!'.format(class_name))
        else:
            messages.info(request, 'You are not authorised to remove this {}!'.format(class_name))
        return redirect('profile', username=note.get_wall().profile.user.username)


@method_decorator(login_required, name='dispatch')
class LikeView(View):

    def get(self, request, *args, **kwargs):
        object_id = request.GET.get('object_id')
        profile_id = request.GET.get('profile_id')
        object_class = request.GET.get('object_class')
        object_class = globals()[object_class]
        profile = UserProfile.objects.get(id=profile_id)
        likes = 0
        button = 'Like'
        if object_id:
            obj = object_class.objects.get(id=object_id)
            try:
                did_user_already_liked_object = obj.likes.get(id=profile_id)
                likes = obj.unlike(profile)
                button = 'Like'
            except Exception as e:
                likes = obj.like(profile) if obj else 0
                button = 'unLike'
        response = json.dumps({
            'likes': likes,
            'button': button
        })
        return HttpResponse(response, content_type='application/json')


@method_decorator(login_required, name='dispatch')
class FriendsListView(TemplateView):
    template_name = 'profiles/list_friends.html'

    def get_context_data(self, **kwargs):
        username = kwargs.get('username')
        user = User.objects.get(username=username)
        userprofile = UserProfile.objects.get(user=user)
        return {'profile': userprofile,
                'requests': userprofile.friend_requests.all(),
                'friends': userprofile.friends.all()}


@method_decorator(login_required, name='dispatch')
class NotificationsListView(ListView):
    model = Notification
    template_name = 'profiles/list_notifications.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        return self.request.user.userprofile.notification_set.all()


@method_decorator(login_required, name='dispatch')
class SendFriendRequestView(View):

    def get(self, request, *args, **kwargs):
        profile_id = request.GET.get('profile_id')
        requester_id = request.GET.get('requester_id')
        target = UserProfile.objects.get(id=profile_id)
        requester = UserProfile.objects.get(id=requester_id)
        target.send_friend_request(requester)
        message = 'Friend request to {} sent!'.format(target.visible_name)
        messages.info(request, message)
        return redirect('profile', username=target.user.username)


@method_decorator(login_required, name='dispatch')
class CancelFriendRequestView(View):
    pass


@method_decorator(login_required, name='dispatch')
class AddFriendView(View):
    pass


@method_decorator(login_required, name='dispatch')
class RemoveFriendView(View):
    pass


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
