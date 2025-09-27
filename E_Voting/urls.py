from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from voting.views import logout_view
from voting.forms import CustomAuthForm

urlpatterns = [
    path('admin/', admin.site.urls),

    # App routes
    path('', include('voting.urls')),

    # Login route using our CustomAuthForm and custom template (overrides default template behavior)
    path('accounts/login/',
         auth_views.LoginView.as_view(template_name='registration/login.html',
                                      authentication_form=CustomAuthForm),
         name='login'),

    # Explicit logout (POST-only) - overrides default logout
    path('accounts/logout/', logout_view, name='logout'),

    # Keep the rest of auth URLs (password reset, etc.)
    path('accounts/', include('django.contrib.auth.urls')),
]
