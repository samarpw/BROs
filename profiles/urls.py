from django.conf.urls import url
from profiles import views

urlpatterns = [
    url(r'^profile/(?P<username>[\w\-]+)/$', views.ProfileView.as_view(), name='profile'),
    url(r'^add_note/$', views.AddNoteView.as_view(), name='add_note'),
    url(r'^edit_note/$', views.EditNoteView.as_view(), name='edit_note'),
    url(r'^edit_note_form/$', views.EditNoteFormView.as_view(), name='edit_note_form'),
    url(r'^remove_post/$', views.RemovePostView.as_view(), name='remove_post'),
    url(r'^remove_comment/$', views.RemoveCommentView.as_view(), name='remove_comment'),
    url(r'^like/$', views.LikeView.as_view(), name='like_post'),
]
