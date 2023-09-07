# Emails as usernames makes more sense when we are letting users create users.
from django_use_email_as_username.models import BaseUser, BaseUserManager
from django.db import models

class Organization(models.Model):
    def __str__(self):
        return self.name
    name = models.CharField(max_length=200)

    class Meta:
        # Makes the ui a little more coherent.
        verbose_name_plural = 'Organization'


class OrganizationMetaModel(models.Model):
    """This is a model to use as the base inheritance for the rest of your models."""
    name = models.CharField(max_length=200)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    def __str__(self):
        return self.name
    
    class Meta:
        abstract = True

class OrganizationUserManager(BaseUserManager):
    """With organization a required field on a user this will create a dummy org to have the first user associated with."""
    def create_superuser(self, email, password, **extra_fields):
        org = Organization(name='rootorg')
        org.save()

        user = self.create_user(
            email=email,
            password=password,
            organization=org
        )
        user.is_superuser = True
        user.is_staff = True
        user.is_root = True
        user.save()
        return user


class User(BaseUser):
    objects = OrganizationUserManager()
    # I thought it would be safer to make a specific security bit than reuse superuser.
    root = models.BooleanField(name="is_root", default=False, verbose_name='Root status', help_text="Full Site Control, should not be given to customers.")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
