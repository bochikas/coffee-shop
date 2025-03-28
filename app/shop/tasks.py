from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from shop.models import Order

User = get_user_model()


@shared_task(ignore_result=True)
def delete_unverified_users():
    User.objects.delete_unverified_users()


@shared_task
def send_order_notification(order_id):
    order = Order.objects.select_related("user").get(id=order_id)
    subject = "Новый заказ"
    message = f"Пользователь {order.user.email} создал заказ #{order.id}.\nСумма: {order.total_price} руб."
    admin_emails = [user.email for user in User.objects.filter(is_staff=True) if user.email]

    if admin_emails:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, admin_emails)
