import debug_toolbar
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('charts/', views.charts, name='charts'),
    path('hand_history/', views.handhistory, name='handhistory'),
    path('waiting_room/', views.game_rule_view, name='waiting_room'),
    path('register', views.game_rule_view, name='register'),
    path('start_game/', views.start_game_view, name='start_game'),
    path('__debug__/', include(debug_toolbar.urls)),
    path('', views.home, name='home'),
]



if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)