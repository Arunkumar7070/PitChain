from django.urls import path
from .views import WalletLoginView, UserProfileView

urlpatterns = [
    path('wallet-login/', WalletLoginView.as_view(), name='wallet-login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
]
