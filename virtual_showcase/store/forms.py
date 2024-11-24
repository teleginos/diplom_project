from django import forms
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth.models import User
from . models import Product, Subcategory, OrderItem, Order

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Please enter a valid email address.')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']



class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class CustomUserProfileForm(forms.ModelForm):
    password = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,  # Пароль может быть необязательным
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']  # Только нужные поля
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get('password')
        if new_password:
            user.set_password(new_password)  # Установить новый пароль
        if commit:
            user.save()
        return user

class CreateProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'subcategory', 'image', 'stock']


class CreateOrder(forms.ModelForm):

    class Meta:
        model = Order
        fields = ['user', 'status', 'total_price']

class CreateOrderItem(forms.ModelForm):

    class Meta:
        model = OrderItem
        fields = ['order', 'product', 'quantity']

class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("Данные формы:", self.data)
        print("Экземпляр объекта:", self.instance)

        if 'category' in self.data:
            print("Выбранная категория:", self.data.get('category'))
        if self.instance.pk:
            print("Текущая категория объекта:", self.instance.category)
        self.fields['subcategory'].queryset = Subcategory.objects.none()  # Пустой список по умолчанию

        if self.instance and self.instance.pk:  # Для редактирования существующего объекта
            if self.instance.category:
                self.fields['subcategory'].queryset = Subcategory.objects.filter(category=self.instance.category)
        elif 'category' in self.data:  # Если категория передана через форму
            try:
                category_id = int(self.data.get('category'))
                self.fields['subcategory'].queryset = Subcategory.objects.filter(category_id=category_id)
            except (ValueError, TypeError):
                pass