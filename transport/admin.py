from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import path
from django.utils.html import format_html
import json
import csv
from datetime import datetime
from .models import Profile, Vehicle, Shipment, ShipmentOffer, Tour, ChatMessage, Notification, Location

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'company_name', 'phone_number', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('user__username', 'user__email', 'company_name', 'phone_number')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Osnovne informacije', {
            'fields': ('user', 'role')
        }),
        ('Kontakt informacije', {
            'fields': ('phone_number', 'address')
        }),
        ('Poslovne informacije', {
            'fields': ('company_name',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'owner', 'vehicle_type', 'capacity', 'is_available', 'created_at')
    list_filter = ('vehicle_type', 'is_available', 'created_at')
    search_fields = ('license_plate', 'owner__username')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Osnovne informacije', {
            'fields': ('owner', 'vehicle_type', 'license_plate', 'is_available')
        }),
        ('Specifikacije', {
            'fields': ('capacity', 'volume')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'sender', 'pickup_city', 'delivery_city', 'status', 'budget', 'created_at')
    list_filter = ('status', 'cargo_type', 'created_at')
    search_fields = ('title', 'sender__username', 'pickup_city', 'delivery_city')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Osnovne informacije', {
            'fields': ('title', 'sender', 'description', 'status')
        }),
        ('Lokacije preuzimanja', {
            'fields': ('pickup_address', 'pickup_city')
        }),
        ('Lokacije dostave', {
            'fields': ('delivery_address', 'delivery_city')
        }),
        ('Informacije o teretu', {
            'fields': ('cargo_type', 'cargo_weight', 'cargo_volume')
        }),
        ('Datumi', {
            'fields': ('pickup_date', 'delivery_date')
        }),
        ('Cena', {
            'fields': ('budget',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ShipmentOffer)
class ShipmentOfferAdmin(admin.ModelAdmin):
    list_display = ('shipment', 'carrier', 'vehicle', 'price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('shipment__title', 'carrier__username', 'vehicle__license_plate')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Osnovne informacije', {
            'fields': ('shipment', 'carrier', 'vehicle', 'status')
        }),
        ('Ponuda', {
            'fields': ('price', 'message')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('shipment', 'driver', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('shipment__title', 'driver__username')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('tour', 'sender', 'message', 'timestamp', 'is_read')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('sender__username', 'message')
    readonly_fields = ('timestamp',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at', 'notification_type')
    search_fields = ('user__username', 'title', 'message')
    readonly_fields = ('created_at',)

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('tour', 'latitude', 'longitude', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('tour__shipment__title',)
    readonly_fields = ('timestamp',)

# Inline Profile u User admin
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

# Prošireni User admin
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role')
    list_filter = BaseUserAdmin.list_filter + ('profile__role',)
    actions = ['export_users_json', 'export_users_csv']
    
    def get_role(self, obj):
        try:
            return obj.profile.role
        except Profile.DoesNotExist:
            return 'Nema profil'
    get_role.short_description = 'Uloga'
    
    def export_users_json(self, request, queryset):
        """Export korisnika u JSON format za migraciju"""
        users_data = []
        for user in queryset:
            user_data = {
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'date_joined': user.date_joined.isoformat(),
                'password': user.password,  # Hashed password
            }
            
            # Dodaj profile podatke ako postoje
            try:
                profile = user.profile
                user_data['profile'] = {
                    'role': profile.role,
                    'phone_number': profile.phone_number,
                    'address': profile.address,
                    'company_name': profile.company_name,
                }
            except Profile.DoesNotExist:
                user_data['profile'] = None
                
            users_data.append(user_data)
        
        response = HttpResponse(
            json.dumps(users_data, indent=2, ensure_ascii=False),
            content_type='application/json'
        )
        response['Content-Disposition'] = f'attachment; filename="users_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
        return response
    export_users_json.short_description = "📤 Izvezi korisnike (JSON za Render)"
    
    def export_users_csv(self, request, queryset):
        """Export korisnika u CSV format"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="users_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Username', 'Email', 'First Name', 'Last Name', 'Role', 
            'Phone', 'Address', 'Company', 'Is Active', 'Date Joined'
        ])
        
        for user in queryset:
            try:
                profile = user.profile
                role = profile.role
                phone = profile.phone_number
                address = profile.address
                company = profile.company_name
            except Profile.DoesNotExist:
                role = phone = address = company = ''
                
            writer.writerow([
                user.username, user.email, user.first_name, user.last_name,
                role, phone, address, company, user.is_active, 
                user.date_joined.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response
    export_users_csv.short_description = "📊 Izvezi korisnike (CSV)"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-users/', self.admin_site.admin_view(self.import_users_view), name='import_users'),
        ]
        return custom_urls + urls
    
    def import_users_view(self, request):
        """View za import korisnika iz JSON fajla"""
        if request.method == 'POST' and request.FILES.get('users_file'):
            try:
                uploaded_file = request.FILES['users_file']
                if uploaded_file.name.endswith('.json'):
                    users_data = json.loads(uploaded_file.read().decode('utf-8'))
                    
                    imported_count = 0
                    skipped_count = 0
                    
                    for user_data in users_data:
                        username = user_data.get('username')
                        email = user_data.get('email')
                        
                        # Proveri da li korisnik već postoji
                        if User.objects.filter(username=username).exists():
                            skipped_count += 1
                            continue
                            
                        # Kreiraj korisnika
                        user = User.objects.create(
                            username=username,
                            email=email,
                            first_name=user_data.get('first_name', ''),
                            last_name=user_data.get('last_name', ''),
                            is_active=user_data.get('is_active', True),
                            is_staff=user_data.get('is_staff', False),
                            is_superuser=user_data.get('is_superuser', False),
                            password=user_data.get('password', '')  # Already hashed
                        )
                        
                        # Kreiraj profil ako postoji
                        profile_data = user_data.get('profile')
                        if profile_data:
                            Profile.objects.create(
                                user=user,
                                role=profile_data.get('role', 'naručilac'),
                                phone_number=profile_data.get('phone_number', ''),
                                address=profile_data.get('address', ''),
                                company_name=profile_data.get('company_name', '')
                            )
                        
                        imported_count += 1
                    
                    messages.success(
                        request, 
                        f'Uspešno importovano {imported_count} korisnika. Preskočeno {skipped_count} (već postoje).'
                    )
                else:
                    messages.error(request, 'Molimo uploadujte JSON fajl.')
                    
            except Exception as e:
                messages.error(request, f'Greška pri importu: {str(e)}')
            
            return redirect('..')
        
        context = {
            'title': 'Import korisnika',
            'opts': self.model._meta,
        }
        return render(request, 'admin/import_users.html', context)
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['import_url'] = 'import-users/'
        extra_context['show_import_button'] = True
        
        # Dodaj import dugme direktno u response
        response = super().changelist_view(request, extra_context)
        
        # Dodaj JavaScript za kreiranje dugmeta ako template ne radi
        if hasattr(response, 'content'):
            content = response.content.decode('utf-8')
            if 'Import korisnika' not in content:
                # Dodaj dugme preko JavaScript-a
                js_code = '''
                <script>
                document.addEventListener('DOMContentLoaded', function() {
                    var objectTools = document.querySelector('.object-tools');
                    if (objectTools) {
                        var importButton = document.createElement('li');
                        importButton.innerHTML = '<a href="import-users/" class="addlink" style="background: #28a745; color: white; padding: 10px 15px; border-radius: 4px; text-decoration: none; font-weight: bold;">📥 Import korisnika</a>';
                        objectTools.appendChild(importButton);
                    }
                });
                </script>
                '''
                content = content.replace('</body>', js_code + '</body>')
                response.content = content.encode('utf-8')
        
        return response
    
    def get_changelist_instance(self, request):
        """Dodaj custom dugme u changelist"""
        changelist = super().get_changelist_instance(request)
        return changelist

# Unregister the default User admin and register the new one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Dodaj custom admin site naslov
admin.site.site_header = "Tovar Taxi Administracija"
admin.site.site_title = "Tovar Taxi Admin"
admin.site.index_title = "Dobrodošli u Tovar Taxi Admin Panel"
