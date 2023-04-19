from Tools.scripts.var_access_benchmark import A
from django.shortcuts import render
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import *
from .serializers import *
from .models import *
import jwt, datetime


# Create your views here.
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()
        if user is None:
            raise AuthenticationFailed('User Not found!')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password')

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),  # Expiration Time
            'iat': datetime.datetime.utcnow()  # Token Creation time
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')

        # Cookie Method
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token
        }

        return response


class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Un-Authenticated")
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Un-Authenticated")

        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)

        return Response(serializer.data)
'''
    class UserView(APIView):
        def get(self, request):
            token = request.COOKIES.get('jwt')

            if not token:
                raise AuthenticationFailed("Un-Authenticated")
            try:
                payload = jwt.decode(token, 'secret', algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                raise AuthenticationFailed("Un-Authenticated")

            user = User.objects.filter(id=payload['id']).first()
            serializer = UserSerializer(user)

            return Response(serializer.data)
            
In this code, we define a UserViewSet which inherits from ModelViewSet. We set the serializer_class to UserSerializer which is used to serialize the response. We define the list method which handles GET requests to list all users.

The code inside the list method is the same as the code inside the get method of the UserView class. We get the JWT token from the cookie, decode it, and then retrieve the user from the database. We then serialize the user using the UserSerializer and return the serialized data in a response.

Note that we use the many=True argument when calling self.get_serializer since we are returning a list of users, not a single user.
'''

class LogoutView(APIView):
    def post(self,request):
        response=Response()
        response.delete_cookie('jwt')
        response.data={
            'message':"Log Out Success"
        }

        return response


