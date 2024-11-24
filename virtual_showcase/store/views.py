from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, CreateProductForm, CustomUserProfileForm
from .models import Category, Order, Product, Subcategory, OrderItem
from django.contrib.auth import logout

def home_page(request):
    categories = Category.objects.prefetch_related('subcategories').all()
    context = {
        "categories": categories
    }
    return render(request, 'store/home.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Аккаунт {username} был успешно создан')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'store/register.html', {'form': form})


def create_product(request):
    if request.method == 'POST':
        form = CreateProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = CreateProductForm()
    return render(request, 'store/create_product.html', {'form': form})

def subcategory_products(request, subcategory_id):
    subcategory = get_object_or_404(Subcategory, id=subcategory_id)
    products = Product.objects.filter(subcategory=subcategory)
    categories = Category.objects.all()

    context = {
        'subcategory': subcategory,
        'products': products,
        'categories': categories,

    }
    return render(request, 'store/subcategory_products.html', context)

def orders(request):
    # Логика для отображения заказов пользователя
    return render(request, 'store/orders.html')

@login_required
def profile_view(request):
    user = request.user
    orders = Order.objects.filter(user=user).prefetch_related('items__product').order_by('-created_at')
    context = {
        'user': user,
        'orders': orders,
    }
    return render(request, 'store/profile.html', context)
    


@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        form = CustomUserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ваш профиль успешно обновлён.')
            return redirect('profile')  # Замените на ваш URL для профиля
    else:
        form = CustomUserProfileForm(instance=request.user)

    return render(request, 'store/profile_edit.html', {'form': form})

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Получаем текущий заказ пользователя
    order, created = Order.objects.get_or_create(user=request.user, status='Pending')

    # Добавляем товар в корзину
    order_item, created = OrderItem.objects.get_or_create(
        order=order,
        product=product,
        defaults={
            'price_at_time': product.price,  # Указываем текущую цену товара
            'quantity': 1
        }
    )

    if not created:
        # Если товар уже есть в корзине, увеличиваем его количество
        order_item.quantity += 1
        order_item.save()

    # Пересчитываем общую стоимость заказа
    order.calculate_total()

    return redirect('cart')

@login_required
def cart_view(request):
    try:
        # Находим текущую корзину пользователя (заказ в статусе "Pending")
        order = Order.objects.get(user=request.user, status='Pending')
        cart_items = order.items.all()  # Получаем все OrderItem, связанные с этим заказом
    except Order.DoesNotExist:
        # Если корзина отсутствует, создаем пустую
        order = None
        cart_items = []

    return render(request, 'store/cart.html', {'order': order, 'cart_items': cart_items})
@login_required
def checkout(request):
    # Получаем текущий заказ пользователя, если он есть
    order = Order.objects.get_or_create(user=request.user, status='Pending')

    # Если заказ пустой (пользователь уже завершил заказ или корзина пуста), редиректим на страницу корзины
    cart_items = OrderItem.objects.filter(order__user=request.user, order__status='Pending')
    if not cart_items.exists():
        return redirect('cart')

    # Если корзина не пуста, создаем новый заказ и добавляем товары
    for item in cart_items:
        order.add_item(item.product, item.quantity)
    
    # Рассчитываем итоговую сумму заказа
    order.calculate_total()
    
    # Удаляем элементы корзины
    # cart_items.delete()

    # Перенаправляем пользователя на страницу с его заказами
    return redirect('profile')

@login_required
def remove_from_cart(request, item_id):
    order_item = get_object_or_404(OrderItem, id=item_id, order__user=request.user, order__status='Pending')
    order = order_item.order
    order_item.delete()
    order.calculate_total()
    return redirect('cart')