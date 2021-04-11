
from django.utils import timezone
from rest_framework.serializers import ModelSerializer
from . models import Users
from accounts.views import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

uid=0
class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    
    def validate(self, args):
        # global uid
        
        data = super(TokenObtainPairSerializer, self).validate(args)
        refresh = self.get_token(self.user)
        
        data['access-token'] = str(refresh.access_token)
        data['refresh-token'] = str(refresh)
        data['email'] = self.user.email
        data['id']=self.user.id
        data['name'] = self.user.first_name
        data['date_of_birth'] = self.user.date_of_birth
        data['gender']=self.user.gender
        self.user.last_login = timezone.now()
        self.user.save()
        uid=data['name']     
        print("validate",uid)
        return data



class UsersSerializer(ModelSerializer):

    class Meta:
        model = Users
        fields = ('id', 'email', 'first_name', 'last_name', 'phone', 'type')
