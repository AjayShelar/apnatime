from django.shortcuts import render

# Create your views here.
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, GenericAPIView, UpdateAPIView, \
    RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from user_auth.models import *

from user_auth.serializers import *

from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser, SAFE_METHODS, BasePermission


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(CreateAPIView):
    permission_classes = (AllowAny, )

    queryset = User.objects.all()
    serializer_class = RegisterSerializer


from rest_framework.authentication import TokenAuthentication
from rest_auth.registration.views import LoginView


class LoginViewCustom(LoginView):
    authentication_classes = ()


class IsAdminUserOrReadAndWrite(IsAdminUser):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        is_admin = super(IsAdminUserOrReadAndWrite,
                         self).has_permission(request, view)

        return (request.user and request.user.is_authenticated) or is_admin


from django_filters import rest_framework as filters
import rest_framework.filters


def user_qs(user):
    if user.is_staff:
        return User.objects.all()

    return User.objects.filter(id=user.id)


from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

from django.http import HttpResponse, Http404, JsonResponse


def get_object_or_exception(queryset, model, *args, **kwargs):
    # First get the object from the QS.
    # If the Object is not in QS, it is possible that the object still exists but the user does not have permissions
    #
    # This might be more inefficient because Queryset here might use some JOINs which are slow.
    try:
        return queryset.get(*args, **kwargs)
    except ObjectDoesNotExist:
        # Check if the object exists in the model
        try:
            model.objects.get(*args, **kwargs)
            raise PermissionDenied()
        except ObjectDoesNotExist:
            raise Http404()


class UserFilter(filters.FilterSet):
    class Meta:
        model = User
        fields = []


from rest_framework.response import Response


class UserView(CreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView):
    permission_classes = (IsAdminUserOrReadAndWrite, )

    queryset = User.objects.all()
    serializer_class = UserDataSerializer
    filter_backends = (filters.DjangoFilterBackend,
                       rest_framework.filters.SearchFilter)
    search_fields = ('first_name', 'phone_number')
    filterset_class = UserFilter

    def get_queryset(self):
        q = user_qs(self.request.user).select_related('profile')

        return q

    def get_object(self):
        if self.request.query_params.get('phone_number', None):
            return get_object_or_exception(
                self.get_queryset(),
                User,
                phone_number='+' + self.request.query_params.get('phone_number'))

        return get_object_or_exception(
            self.get_queryset(), User, id=self.kwargs.get('pk'))

    def get(self, request, *args, **kwargs):
        if not kwargs.get('pk', None) and not self.request.query_params.get(
                'phone_number', None):
            # TODO: Copied from self.list because filterset backend is not working
            queryset = self.filter_queryset(
                UserFilter(request.GET, self.get_queryset()).qs)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return self.retrieve(request, *args, **kwargs)


from rest_framework.parsers import MultiPartParser, FormParser


class PhotoUploadView(CreateAPIView):
    permission_classes = (IsAdminUserOrReadAndWrite, )

    queryset = UserProfile.objects.all()
    serializer_class = PhotoUploadSerializer
    parser_classes = (
        MultiPartParser,
        FormParser,
    )
