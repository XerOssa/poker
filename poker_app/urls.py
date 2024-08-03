import debug_toolbar
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from . import views, consumers


urlpatterns = [
    path('admin/', admin.site.urls),
    path('charts/', views.charts, name='charts'),
    path('poker_app/', views.handhistory, name='handhistory'),
    path('waiting_room/', views.waiting_room_view, name='waiting_room'),
    path('hero_registration/', views.waiting_room_view, name='hero_registration'),
    path('start_game/', views.start_game_view, name='start_game'),
    path('__debug__/', include(debug_toolbar.urls)),
    path('', views.home, name='home'),
    re_path(r'ws/pokersocket/$', consumers.PokerConsumer.as_asgi()),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)