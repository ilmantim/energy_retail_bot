from django.db import models

# Create your models here.


class Mro(models.Model):
    name = models.CharField(
        'название МРО',
        max_length=50,
        null=True,
        blank=True
    )
    general = models.TextField(
        'общая инфа',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name


class Address(models.Model):
    name = models.TextField(
        'детализированная инфа',
        null=True,
        blank=True
    )
    department = models.ForeignKey(
        Mro,
        verbose_name='связь с МРО',
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='addresses'
    )
    num = models.IntegerField(
        'номер кнопки',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name


class Customer(models.Model):
    chat_id = models.IntegerField(
        'id персоны',
        null=True,
        blank=True
    )


class Bill(models.Model):
    customers = models.ManyToManyField(
        Customer,
        verbose_name='клиенты',
        blank=True,
        related_name='bills'
    )
    value = models.IntegerField(
        'номер лицевого счета',
        null=True,
        blank=True
    )
    address = models.TextField(
        'адрес счета',
        null=True,
        blank=True
    )
    number_and_type_pu = models.TextField(
        'Номер и тип ПУ',
        null=True,
        blank=True
    )
    readings = models.IntegerField(
        'Показания счетчика',
        null=True,
        blank=True
    )
    registration_date = models.DateTimeField(
        'Дата приёма',
        null=True,
        blank=True
    )


class Favorite(models.Model):
    customer = models.ForeignKey(
        Customer,
        verbose_name='юзер избранного ЛС',
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    bill = models.ForeignKey(
        Bill,
        verbose_name='Избранный ЛС',
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    is_favorite = models.BooleanField(
        'Избранный или нет',
        null=True,
        blank=True
    )

