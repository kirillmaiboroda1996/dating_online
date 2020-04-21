import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views.generic import UpdateView, DetailView, ListView

from django.contrib.auth.models import User
from django.views.generic.edit import FormMixin
from django.views.generic.list import MultipleObjectMixin

from .forms import ExtendedUserCreationForm, UserProfileForm
from .models import UserProfile, MatchFriend, Dialog


def login(request):
    return render(request, 'registration/login.html')


# showing user profile
class UserProfileDetailView(LoginRequiredMixin, DetailView):
    Model = UserProfile
    template_name = 'dating_app/profile_detail.html'
    success_url = "/accounts/profile/"

    def get_object(self, queryset=None):
        return UserProfile.objects.get(user=self.request.user)


# user profile edition
class UserProfileUpdateView(UpdateView):
    template_name = 'dating_app/profile_update.html'
    model = UserProfile
    # fields = ['genders', 'age', 'location', 'about_me', 'avatar']
    form_class = UserProfileForm
    # template_name_suffix = '_update'
    success_url = "/accounts/profile/"

    def form_valid(self, form):
        print(form.cleaned_data)
        return super().form_valid(form)


# user edition (password, login...)
class UserUpdateView(UpdateView):
    template_name = 'dating_app/user_form.html'
    model = User
    form_class = ExtendedUserCreationForm
    success_url = "/accounts/profile/"
    # template_name_suffix = '_form'

    def form_valid(self, form):
        print(form.cleaned_data)
        return super().form_valid(form)


class DatingListView(ListView):
    # queryset = UserProfile.objects.filter()
    model = UserProfile
    template_name_suffix = 'dating.html'
    template_name = 'dating_app/dating.html'
    paginate_by = 1

    def get_queryset(self):
        profile = self.request.user.userprofile
        skip_pk = profile.skip_ids.values_list('pk', flat=True)
        like_pk = profile.like_ids.values_list('pk', flat=True)
        return UserProfile.objects.filter(age__lte=profile.to_age,
                                          age__gte=profile.from_age,
                                          genders=profile.gender_pref).exclude(pk__in=skip_pk).exclude(pk__in=like_pk)


# function for skip in /dating/ page
def send_skip_or_like_to_profile(request, operation, pk):
    user = request.user.userprofile
    like_or_skip_user = get_object_or_404(UserProfile, pk=pk)
    if operation == 'skip':
        user.skip_ids.add(like_or_skip_user)
    elif operation == 'like':
        user.skip_ids.add(like_or_skip_user)
    return HttpResponseRedirect('/dating/')


class MutualMatchView(ListView, MultipleObjectMixin):
    model = UserProfile
    template_name_suffix = 'match.html'
    template_name = 'dating_app/match.html'

    def get_queryset(self):
        profile = self.request.user.userprofile
        # my_likes = profile.like_ids.values_list('like_ids', flat=True)
        who_liked_me = UserProfile.objects.values_list('pk', flat=True)

        return profile.like_ids.filter(pk__in=who_liked_me)


def chat(request):
    return render(request, 'dating_app/chat.html')


@login_required
def room(request, room_name):
    return render(request, 'dating_app/room.html', {
        'room_name_json': mark_safe(json.dumps(room_name)),
        'username': mark_safe(json.dumps(request.user.username)),
    })


def get_last_10_messages(chatId):
    chat = get_object_or_404(Dialog, id=chatId)
    return chat.messages.order_by('-timestamp').all()[:10]


def get_user_contact(username):
    user = get_object_or_404(User, username=username)
    return get_object_or_404(User, user=user)


def get_current_chat(chatId):
    return get_object_or_404(Dialog, id=chatId)
