from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from loanApp import views
from django.contrib.staticfiles.urls import static, staticfiles_urlpatterns
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('account/', include('loginApp.urls')),
    path('loan/', include('loanApp.urls')),
    path('manager/', include('managerApp.urls')),

]
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
handler404 = 'loanApp.views.error_404_view'
