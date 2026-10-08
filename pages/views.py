from django.conf import settings
from django.contrib import messages as django_messages
from django.core.mail import send_mail
from django.shortcuts import render

from store.models import Category, Product

from .forms import ContactForm
from .utils import build_gmail_link, build_whatsapp_link


def home(request):
    featured = Product.objects.filter(is_active=True, is_deleted=False, stock__gt=0)[:8]
    categories = Category.objects.filter(is_active=True)
    return render(request, 'pages/home.html', {
        'featured': featured,
        'categories': categories,
    })


def about(request):
    return render(request, 'pages/about.html')


def contact(request):
    whatsapp_link = build_whatsapp_link()
    gmail_link = build_gmail_link()

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            recipient = getattr(settings, 'CONTACT_EMAIL', '')
            try:
                sent = send_mail(
                    subject=f'[LocalShop] {cd["subject"]}',
                    message=f'From: {cd["name"]} <{cd["email"]}>\n\n{cd["message"]}',
                    from_email=getattr(settings, 'EMAIL_HOST_USER', None) or cd['email'],
                    recipient_list=[recipient] if recipient else [],
                )
                if sent:
                    django_messages.success(request, 'Thank you! Your message was sent.')
                else:
                    django_messages.error(request, 'Email delivery failed. Please use WhatsApp or Gmail below.')
            except Exception:
                django_messages.error(request, 'Email delivery failed. Please use WhatsApp or Gmail below.')
            whatsapp_link = form.whatsapp_link()
            gmail_link = form.gmail_link()
        else:
            django_messages.error(request, 'Please correct the errors in the form.')
    else:
        form = ContactForm()

    return render(request, 'pages/contact.html', {
        'form': form,
        'whatsapp_link': whatsapp_link,
        'gmail_link': gmail_link,
    })