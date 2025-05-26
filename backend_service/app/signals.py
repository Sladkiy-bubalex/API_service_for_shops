from typing import Type
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from app.models import ConfirmEmailToken, User, Order


new_order = Signal()

@receiver(post_save, sender=User)
def new_user_registered_signal(sender: Type[User], instance: User, created: bool, **kwargs):
    """
     Отправление письма для подтрердждения почты
    """
    if created and not instance.is_active:
        # Создание email
        token, _ = ConfirmEmailToken.objects.get_or_create(user_id=instance.id)

        msg = EmailMultiAlternatives(
            # title:
            subject="Подтверждение вашей учетной записи",
            # message:
            body=(
            f"Здравствуйте, {instance.username}!\n\n"
            "Спасибо за регистрацию. Чтобы активировать вашу учетную запись, "
            "пожалуйста, подтвердите свой адрес электронной почты, перейдя по следующей ссылке:\n\n"
            f"http://localhost:8000/api/v1/confirm-email/{token.key}/\n\n"
            "С уважением,\n"
            "Команда поддержки"
            ),
            from_email=settings.EMAIL_HOST_USER,
            to=[instance.email]
        )
        msg.send()
    
@receiver(new_order, sender=Order)
def new_order_signal(sender: Type[Order], user_id, **kwargs):
    """
    отправляем письмо при изменении статуса заказа
    """
    # send an e-mail to the user
    user = User.objects.get(id=user_id)

    msg = EmailMultiAlternatives(
        # title:
        subject="Обновление статуса заказа",
        # message:
        body=(
            f"Здравствуйте, {user.username}!\n\n"
            "Ваш заказ сформирован. Спасибо за покупку!"
        ),
        # from:
        from_email=settings.EMAIL_HOST_USER,
        # to:
        to=[user.email]
    )
    msg.send()
