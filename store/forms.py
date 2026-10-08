from django import forms

from .models import Category, ContactSettings, Product, ShopSettings
from .utils import is_valid_upi_id


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('category', 'name', 'slug', 'description', 'price', 'stock', 'image', 'is_active')
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if slug:
            slug = slug.strip().lower()
        return slug


class ShopSettingsForm(forms.ModelForm):
    class Meta:
        model = ShopSettings
        fields = ('upi_id', 'upi_payee_name', 'upi_qr', 'upi_enabled')
        widgets = {
            'upi_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'shop@okhdfcbank'}),
            'upi_payee_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'LocalShop'}),
            'upi_qr': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'upi_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_upi_id(self):
        upi_id = (self.cleaned_data.get('upi_id') or '').strip()
        if upi_id and not is_valid_upi_id(upi_id):
            raise forms.ValidationError('Enter a valid UPI ID in the format name@bank.')
        return upi_id


class ContactSettingsForm(forms.ModelForm):
    class Meta:
        model = ContactSettings
        fields = ('email', 'phone', 'whatsapp_number', 'address', 'opening_hours')
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'shop@example.com',
                'autocomplete': 'email',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+91 88373 51115',
                'autocomplete': 'tel',
                'inputmode': 'tel',
            }),
            'whatsapp_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '918837351115',
                'inputmode': 'numeric',
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Shop name, street, area, landmark, city, PIN code',
            }),
            'opening_hours': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Mon - Sat: 9:00 AM - 8:00 PM',
            }),
        }

    def clean_phone(self):
        return (self.cleaned_data.get('phone') or '').strip()

    def clean_whatsapp_number(self):
        number = ''.join(
            ch for ch in (self.cleaned_data.get('whatsapp_number') or '')
            if ch.isdigit() or ch == '+'
        )
        return number.lstrip('+')


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name', 'slug', 'description', 'image', 'is_active')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }