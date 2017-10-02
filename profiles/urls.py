from django.conf.urls import url
from profiles import views

urlpatterns = [
    url(r'^profile/(?P<username>[\w\-]+)/$', views.ProfileView.as_view(), name='profile'),
    url(r'^add_note/$', views.AddNoteView.as_view(), name='add_note'),
    url(r'^edit_note/$', views.EditNoteView.as_view(), name='edit_note'),
    url(r'^edit_note_form/$', views.EditNoteFormView.as_view(), name='edit_note_form'),
    url(r'^remove_note/$', views.RemoveNoteView.as_view(), name='remove_note'),
    url(r'^send_friend_request/$', views.SendFriendRequestView.as_view(), name='send_friend_request'),
    url(r'^add_friend/$', views.AddFriendView.as_view(), name='add_friend'),
    url(r'^like/$', views.LikeView.as_view(), name='like_post'),
    url(r'^profile/(?P<username>[\w\-]+)/friends/$', views.FriendsListView.as_view(), name='friends'),
    url(r'^notifications/$', views.NotificationsListView.as_view(), name='notifications'),
]
