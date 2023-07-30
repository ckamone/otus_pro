from django.urls import path
from web import views

urlpatterns = [
    path('', views.new_questions, name='ask_list'),
    path('hot/', views.hot_questions, name='hot_list'),
    path('ask/', views.QuestionCreateView.as_view(), name='ask_create'),
    # path('ask/<int:pk>', views.QuestionDetailView.as_view(), name='ask_detail'),
    path('ask/<int:pk>', views.question_detailed, name='ask_detail'),
    path('tag', views.TagListView.as_view(), name='tag_list'),
    path('tag/create/', views.TagCreateView.as_view(), name='tag_create'),

    path('search/', views.search_questions, name='search'),
    path('mark/<int:pk>', views.mark_reply, name='mark_correct'),
    path('trending/', views.get_trending, name='get_trending'),
    # path('reply/', views.reply_questions, name='reply'),
]