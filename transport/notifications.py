from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
import json

class NotificationManager:
    """
    Sistem za upravljanje notifikacijama u real-time
    """
    
    NOTIFICATION_TYPES = {
        'new_shipment': 'Nova pošiljka dostupna',
        'shipment_assigned': 'Pošiljka dodeljena',
        'shipment_started': 'Transport počet',
        'shipment_delivered': 'Pošiljka isporučena',
        'offer_received': 'Nova ponuda primljena',
        'offer_accepted': 'Ponuda prihvaćena',
        'offer_rejected': 'Ponuda odbijena',
        'payment_due': 'Plaćanje dospelo',
        'penalty_applied': 'Penal primenjen',
        'route_suggestion': 'Predlog rute',
        'driver_nearby': 'Vozač u blizini',
        'delivery_delayed': 'Kašnjenje u dostavi',
        'rating_request': 'Zahtev za ocenu',
    }
    
    @classmethod
    def create_notification(cls, user, notification_type, title, message, 
                          related_shipment=None, data=None):
        """
        Kreira novu notifikaciju
        """
        from .models import Notification
        
        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            related_shipment=related_shipment,
            data=json.dumps(data) if data else None
        )
        
        # Pošalji real-time notifikaciju
        cls._send_realtime_notification(user, notification)
        
        return notification
    
    @classmethod
    def _send_realtime_notification(cls, user, notification):
        """
        Šalje real-time notifikaciju preko WebSocket-a
        """
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"notifications_{user.id}",
                {
                    'type': 'send_notification',
                    'notification': {
                        'id': notification.id,
                        'type': notification.notification_type,
                        'title': notification.title,
                        'message': notification.message,
                        'created_at': notification.created_at.isoformat(),
                        'is_read': notification.is_read,
                        'data': json.loads(notification.data) if notification.data else None
                    }
                }
            )
    
    @classmethod
    def notify_new_shipment(cls, shipment):
        """
        Obavesti vozače o novoj pošiljci na njihovoj ruti
        """
        from .route_suggestions import DriverMatchingEngine
        
        # Pronađi vozače u blizini
        nearby_drivers = DriverMatchingEngine.find_nearby_drivers(shipment)
        
        for driver in nearby_drivers:
            cls.create_notification(
                user=driver,
                notification_type='new_shipment',
                title='Nova pošiljka dostupna!',
                message=f'Pošiljka {shipment.reference_number} od {shipment.pickup_city} do {shipment.delivery_city}',
                related_shipment=shipment,
                data={
                    'shipment_id': shipment.id,
                    'pickup_city': shipment.pickup_city,
                    'delivery_city': shipment.delivery_city,
                    'weight': float(shipment.weight),
                    'offered_price': float(shipment.offered_price)
                }
            )
    
    @classmethod
    def notify_shipment_assigned(cls, shipment, carrier):
        """
        Obavesti naručioca da je pošiljka dodeljena
        """
        cls.create_notification(
            user=shipment.shipper,
            notification_type='shipment_assigned',
            title='Pošiljka dodeljena vozaču!',
            message=f'Vaša pošiljka {shipment.reference_number} je dodeljena vozaču {carrier.get_full_name() or carrier.username}',
            related_shipment=shipment,
            data={
                'shipment_id': shipment.id,
                'carrier_name': carrier.get_full_name() or carrier.username,
                'carrier_phone': getattr(carrier.profile, 'phone_number', '')
            }
        )
        
        # Obavesti i vozača
        cls.create_notification(
            user=carrier,
            notification_type='shipment_assigned',
            title='Nova pošiljka dodeljena!',
            message=f'Dodeljena vam je pošiljka {shipment.reference_number}',
            related_shipment=shipment,
            data={
                'shipment_id': shipment.id,
                'pickup_address': shipment.pickup_address,
                'delivery_address': shipment.delivery_address,
                'contact_person': shipment.contact_person,
                'contact_phone': shipment.contact_phone
            }
        )
    
    @classmethod
    def notify_offer_received(cls, offer):
        """
        Obavesti naručioca o novoj ponudi
        """
        cls.create_notification(
            user=offer.shipment.shipper,
            notification_type='offer_received',
            title='Nova ponuda primljena!',
            message=f'Primili ste ponudu od {offer.carrier.get_full_name() or offer.carrier.username} za {offer.offered_price} RSD',
            related_shipment=offer.shipment,
            data={
                'offer_id': offer.id,
                'carrier_name': offer.carrier.get_full_name() or offer.carrier.username,
                'offered_price': float(offer.offered_price),
                'vehicle_type': offer.vehicle.get_vehicle_type_display(),
                'message': offer.message
            }
        )
    
    @classmethod
    def notify_penalty_applied(cls, shipment, penalty_amount, minutes_late):
        """
        Obavesti o primenjenom penalu
        """
        cls.create_notification(
            user=shipment.carrier,
            notification_type='penalty_applied',
            title='Penal za kašnjenje!',
            message=f'Primenjen penal od {penalty_amount} RSD za kašnjenje od {minutes_late} minuta',
            related_shipment=shipment,
            data={
                'penalty_amount': float(penalty_amount),
                'minutes_late': minutes_late,
                'shipment_id': shipment.id
            }
        )
        
        # Obavesti i naručioca
        cls.create_notification(
            user=shipment.shipper,
            notification_type='penalty_applied',
            title='Penal za kašnjenje vozača',
            message=f'Vozač je kasnio {minutes_late} minuta. Primenjen penal od {penalty_amount} RSD',
            related_shipment=shipment,
            data={
                'penalty_amount': float(penalty_amount),
                'minutes_late': minutes_late,
                'shipment_id': shipment.id
            }
        )
    
    @classmethod
    def notify_delivery_completed(cls, shipment):
        """
        Obavesti o završenoj dostavi
        """
        cls.create_notification(
            user=shipment.shipper,
            notification_type='shipment_delivered',
            title='Pošiljka isporučena!',
            message=f'Vaša pošiljka {shipment.reference_number} je uspešno isporučena',
            related_shipment=shipment,
            data={
                'shipment_id': shipment.id,
                'delivery_time': timezone.now().isoformat()
            }
        )
        
        # Zahtevaj ocenu
        cls.create_notification(
            user=shipment.shipper,
            notification_type='rating_request',
            title='Ocenite vozača',
            message=f'Molimo ocenite vozača za pošiljku {shipment.reference_number}',
            related_shipment=shipment,
            data={
                'shipment_id': shipment.id,
                'carrier_name': shipment.carrier.get_full_name() or shipment.carrier.username
            }
        )
        
        # Zahtevaj ocenu od vozača
        cls.create_notification(
            user=shipment.carrier,
            notification_type='rating_request',
            title='Ocenite naručioca',
            message=f'Molimo ocenite naručioca za pošiljku {shipment.reference_number}',
            related_shipment=shipment,
            data={
                'shipment_id': shipment.id,
                'shipper_name': shipment.shipper.get_full_name() or shipment.shipper.username
            }
        )
    
    @classmethod
    def get_user_notifications(cls, user, unread_only=False, limit=50):
        """
        Vraća notifikacije korisnika
        """
        from .models import Notification
        
        queryset = Notification.objects.filter(user=user)
        
        if unread_only:
            queryset = queryset.filter(is_read=False)
        
        return queryset.order_by('-created_at')[:limit]
    
    @classmethod
    def mark_as_read(cls, notification_ids, user):
        """
        Označava notifikacije kao pročitane
        """
        from .models import Notification
        
        Notification.objects.filter(
            id__in=notification_ids,
            user=user
        ).update(is_read=True, read_at=timezone.now())
    
    @classmethod
    def get_unread_count(cls, user):
        """
        Vraća broj nepročitanih notifikacija
        """
        from .models import Notification
        
        return Notification.objects.filter(
            user=user,
            is_read=False
        ).count()


class Notification(models.Model):
    """
    Model za čuvanje notifikacija
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    message = models.TextField()
    related_shipment = models.ForeignKey('Shipment', on_delete=models.CASCADE, null=True, blank=True)
    data = models.TextField(blank=True, help_text='JSON data')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def mark_as_read(self):
        """Označava notifikaciju kao pročitanu"""
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=['is_read', 'read_at'])
