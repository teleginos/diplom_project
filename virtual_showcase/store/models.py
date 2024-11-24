from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class Subcategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # Категория товара
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    stock = models.PositiveIntegerField(default=0)  # Количество на складе
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Pending')  # Статус заказа, например, 'В обработке', 'Доставлен'
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # Общая сумма заказа

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"
    
    def calculate_total(self):
        """
        Персчитывает общую сумму заказа на основе всех позиций
        """
        self.total_price = sum(item.quantity * item.price_at_time for item in self.items.all())
        self.save()

    def add_item(self, product, quantity):
        item, created = OrderItem.objects.get_or_create(
            order=self,
            product=product,
            defaults={'quantity': quantity, 'price_at_time': product.price}
        )
        if not created:
            item.quantity += quantity
            item.save()
        self.calculate_total()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  # Количество товара в заказе
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"