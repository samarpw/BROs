from django.shortcuts import render, redirect, reverse
from django.core.urlresolvers import reverse_lazy
from django.views.generic import TemplateView, FormView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from registration.backends.simple.views import RegistrationView
from profiles.forms import User, UserProfile, UserProfileForm


class IndexView(TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class MyRegistrationView(RegistrationView):
    def get_success_url(self, user):
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


# @method_decorator(login_required, name='dispatch')
# class AddPostView(TemplateView):
#     template_name =
#     def get_context_data(self, **kwargs):