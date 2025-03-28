from celery import shared_task
from django.contrib.auth import get_user_model

User = get_user_model()


@shared_task(ignore_result=True)
def delete_unverified_users():
    User.objects.delete_unverified_users()
