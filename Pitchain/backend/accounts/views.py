from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from eth_account.messages import encode_defunct
from web3 import Web3
from .serializers import UserSerializer, WalletAuthSerializer

User = get_user_model()


class WalletLoginView(APIView):
    """
    Authenticate user by verifying MetaMask signature.
    POST /api/accounts/wallet-login/
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = WalletAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        wallet_address = serializer.validated_data['wallet_address'].lower()
        signature = serializer.validated_data['signature']
        message = serializer.validated_data['message']

        # Verify signature
        w3 = Web3()
        msg = encode_defunct(text=message)
        try:
            recovered = w3.eth.account.recover_message(msg, signature=signature)
            if recovered.lower() != wallet_address:
                return Response({'error': 'Invalid signature'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception:
            return Response({'error': 'Signature verification failed'}, status=status.HTTP_400_BAD_REQUEST)

        # Get or create user
        user, created = User.objects.get_or_create(
            wallet_address=wallet_address,
            defaults={'username': wallet_address[:20]}
        )

        # Issue JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
            'created': created,
        })


class UserProfileView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/accounts/profile/"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
