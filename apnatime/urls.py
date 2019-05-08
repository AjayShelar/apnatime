"""apnatime URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
from django.conf.urls import url, include
from user_auth.views import RegisterView, LoginViewCustom, UserView

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^admin/', admin.site.urls),

    url(r'^register/', RegisterView.as_view()),
    url(r'^rest-auth/', include('rest_auth.urls')),

    url(r'^rest-auth/login/', LoginViewCustom.as_view(), name='rest_login'),
    url(r'^api/v1/user/((?P<pk>[0-9]+)/)?$', UserView.as_view()),



]
