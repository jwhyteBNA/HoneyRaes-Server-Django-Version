from django.contrib import admin
from django.conf.urls import include
from django.urls import path
from rest_framework import routers
from repairsapi.views import CustomerView, EmployeeView, ServiceTicketView, login_user, register_user

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'customers', CustomerView, 'customer')
router.register(r'employees', EmployeeView, 'employee')
router.register(r'tickets', ServiceTicketView, 'ticket')

urlpatterns = [
    path('register', register_user),
    path('login', login_user),
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
]
