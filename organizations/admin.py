from django.contrib import admin
from django_use_email_as_username.admin import BaseUserAdmin

from .models import User, Organization


class OrganizationMixin():
    """This should be used as the first object to inherit the non user / organization admins from"""
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(organization=request.user.organization)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in "organization":
            # You could swap the name field Organization to organization to get rid of this
            # But I left it here to show limit query sets when the fiuld name isn't
            # .capitalize() away from the associated model name.
            kwargs['queryset'] = Organization.objects.filter(name=request.user.organization)
        else:
            # I would recommend that all field names be .capitalize() away from the model
            # name so that you don't have to keep adding code. I'd be interested to hear
            # other solutions to this.
            kwargs['queryset'] = globals()[db_field.name.capitalize()].objects.filter(organization=request.user.organization)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class OrganizationMetaModelAdmin(OrganizationPermissionMixin, admin.ModelAdmin):
    """You could use this to inherit the rest of your model admins or use it as
    an example of how to do the multi inheritance"""
    pass   

class OrganizationMetaTabularInline(OrganizationPermissionMixin, admin.TabularInline):
    """Tabular inlines get really cluttered with the organization field."""
    exclude = ["organization"]


class OrganizationAdmin(admin.ModelAdmin):
    """This lets root users see all organizations."""
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_root:
            return qs
        return qs.filter(name=request.user.organization)

class OrganizationUserAdmin(BaseUserAdmin):
    """This is close. Root users can swap their organization.
    What isn't quite right:
    - When a user creates a user they are not staff status. They are part of the correct org.
    """
    def get_fieldsets(self, request, obj=None):
        is_root = request.user.is_root
        fieldsets = list(super(BaseUserAdmin, self).get_fieldsets(request, obj))
        fieldsets.insert(
            2,
            ('Organization', {'fields': ('organization',)}))
        fieldsets.append(('Root', {'fields': ('is_root')}))
        if is_root:
            return fieldsets
        return fieldsets[:2]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(organization=request.user.organization)
    
    def get_changeform_initial_data(self, request):
        """Does the right thing for users so they don't have to touch the org field"""
        data = super().get_changeform_initial_data(request)
        data["organization"] = request.user.organization
        return data
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """This allows root users to swap the organization they are apart of based on the
        is_root user attribute. This is to try and help prevent a root user from swapping
        data between organizations accidentally"""
        # Should root users only be able to swap their own organization and not other users?
        # is obj in kwags?
        if db_field.name == "organization" and not request.user.is_root:
            kwargs["queryset"] = Organization.objects.filter(name=request.user.organization)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(User, OrganizationUserAdmin)
admin.site.register(Organization, OrganizationAdmin)
