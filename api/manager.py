from django.contrib.auth.base_user import BaseUserManager

class CustomAccountManage(BaseUserManager):

    def create_superuser(self,email,password,**other_fields):
        other_fields.setdefault('is_staff',True)
        other_fields.setdefault('is_superuser',True)
        other_fields.setdefault('is_active',True)

        if other_fields.get('is_staff') is not True:
            raise ValueError("is_staff must be True")
        if other_fields.get('is_superuser') is not True:
            raise ValueError("is_superuser must be True")
        
        return self.create_user(email,password,**other_fields)

    def create_user(self,email,password,**other_fields):
        if not email:
            raise ValueError("Email cannot be blank")
        email=self.normalize_email(email)
        user=self.model(email=email,**other_fields)
        user.set_password(password)
        user.save()
        return user