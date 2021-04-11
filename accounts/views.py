from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib import auth
from . models import Users
from . serializers import UserTokenObtainPairSerializer, UsersSerializer
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from email.message import EmailMessage
from django.template import Context
from django.template.loader import render_to_string
import smtplib,requests
from .serializers import *
from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.conf import settings
from django.urls import reverse
from django.utils.encoding import force_bytes,force_text,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from  .utils import token_generator
from django.views import View

@api_view(['POST'])
@permission_classes((AllowAny,))

def signup(request):
  
  try:
    
    if 'first_name' not in request.data and request.data['type']  == 'front_user':
      return Response({'status':'error', 'message': 'first_name required.'}, status=404)
    if 'type' not in request.data:
      return Response({'status':'error', 'message': 'user type required.'}, status=404)


    
    password = request.data.get('password')

    serializer = UsersSerializer(data=request.data)

    serializer.is_valid(raise_exception=True)

    data = serializer.validated_data
    print(data)

    data['is_active'] = True

    if not password:
        return Response({'status':'error','message': 'user password is required'}, status=404)

    if Users.objects.filter(email=data.get('email')).exists():
        return Response({'status':'error','message': 'Email is taken'}, status=400)
    else:
        user = Users(**data)
        user.set_password(password)
        name=data.get('first_name')
        user.is_active=False
        user.save()
        #path to view
 

        uid64=urlsafe_base64_encode(force_bytes(user.pk))
        d=get_current_site(request)
        domain=str(d)
        link=reverse('activate',kwargs={
                      'uid64':uid64,
                      'token':token_generator.make_token(user)})
        print(domain)
        print(type(domain))
        print(link)
        print(type(link))
        activate_url='http://'+domain+link
        print(activate_url)
        print("activate",activate_url)
        email_subject= 'Activate your Account'
        email_body='hey please use this link to verify your account\n'+activate_url


        user = EmailMessage(
                email_subject,
                email_body,
                'noreply@semycolon.com',
                [user],
        )
        user.send(fail_silently=True)

        return Response({'status':'success', 'message': 'Successfully signed up please login.'}, status=201)

    return Response({'status':'success', 'message': 'Successfully signed up please login.'}, status=201)
  
  except ValidationError as e: 
    return Response({'status':'error', 'message': e.detail}, status=404)
  except Exception as e: 
    return Response({'status':'error', 'message': str(e)}, status=404)


class UserProfileView(APIView):

  permission_classes = (IsAuthenticated,)

  def get(self, request, *args, **kwargs):

    return Response(UsersSerializer(request.user).data, status=200)

  def patch(self, request, *args, **kwargs):
    user = request.user

    serializer = UsersSerializer(user, data=request.data)
    if serializer.is_valid():
      serializer.save()
    else:
      return Response(serializer.errors, status=400)

    return Response(serializer.data, status=201)


class FrontUserLoginTokenObtainPairView(TokenObtainPairView):
    serializer_class = UserTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        
        if not (Users.objects.filter(email=request.data.get('email'), type='front_user').count()==1):
            return Response({'status': 'error', 'message': 'No active account found with the given credentials'}, status=403)
        
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)

        except Exception as e:
            
            return Response({'status': 'error', 'message': 'No active account found with the given credentials'}, status=403)
            
        return Response(serializer.validated_data, status=200)

class AdminLoginTokenObtainPairView(TokenObtainPairView):
    
    serializer_class = UserTokenObtainPairSerializer

    def post(self, request,*args, **kwargs):
        
        if not (Users.objects.filter(email=request.data.get('email'), type='admin').count()==1):
            return Response({'status': 'error', 'message': 'No active account found with the given credentials'}, status=403)
        
        serializer = self.get_serializer(data=request.data)
        
        #result=Users.objects.get(email=request.data['email'])
        
        
        try:
            serializer.is_valid(raise_exception=True)
            # uids=serializer.validated_data['id']
            # print("views", uid)
            
            
            
        except Exception as e:
            return Response({'status': 'error', 'message': 'No active account found with the given credentials'}, status=403)
        
        
        # return redirect('dashbord')
        datas=serializer.validated_data
        callapi=requests.get('http://127.0.0.1:8000/listings/r/view/')
        result=callapi.json()
        data=result['results']
        # return redirect('dashbord')
        # return render(request,'partials/_topbar.html',{'datas':datas,'data':data})
        return Response(serializer.validated_data, status=200)
# class SupplierLoginTokenObtainPairView(TokenObtainPairView):
#     serializer_class = UserTokenObtainPairSerializer

#     def post(self, request, *args, **kwargs):
        
#         if not (Users.objects.filter(email=request.data.get('email'), type='supplier').count()==1):
#             return Response({'status': 'error', 'message': 'No active account found with the given credentials'}, status=403)
        
#         serializer = self.get_serializer(data=request.data)
        
#         try:
#             serializer.is_valid(raise_exception=True)
#         except Exception as e:
#             return Response({'status': 'error', 'message': 'No active account found with the given credentials'}, status=403)
            

#         return Response(serializer.validated_data, status=200)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def logout(request):
  if request.method == 'POST':
    auth.logout(request)
    return Response({'status':'success','message': 'Logout Success'}, status=200)
  else:
    return Response({'status':'error','message': 'Method Not Allowed'}, status=405)


class VerificationView(View):

  def get(self, request, uid64, token):
    return redirect('register')