from django import forms

from .utils import build_gmail_link, build_whatsapp_link


class ContactForm(forms.Form):
    name = forms.CharField(max_length=120, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Your name',
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control', 'placeholder': 'you@example.com',
    }))
    subject = forms.CharField(max_length=200, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'What is this about?',
    }))
    message = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control', 'rows': 5, 'placeholder': 'Write your message...',
    }))

    def whatsapp_link(self):
        # Pre-select the subject and message for the WhatsApp conversation.
        text = f"Hi! I'm {self.data.get('name', '')}. "
        if self.data.get('subject'):
            text += f"Regarding: {self.data.get('subject')}. "
        if self.data.get('message'):
            text += self.data['message']
        return build_whatsapp_link(text.strip())

    def gmail_link(self):
        return build_gmail_link(
            subject=self.data.get('subject', '') or 'LocalShop inquiry',
            body=f"Hi,\n\n{self.data.get('message', '')}\n\nBest regards,\n{self.data.get('name', '')}",
        )