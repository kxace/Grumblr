from django import forms
from grumblr.models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=20)
    firstname = forms.CharField(max_length = 20)
    lastname = forms.CharField(max_length = 20)
    password1 = forms.CharField(max_length = 20,
                                label='Password1',
                                widget=forms.PasswordInput())
    password2 = forms.CharField(max_length = 20,
                                label = 'Password2',
                                widget=forms.PasswordInput())
    email = forms.EmailField(max_length=40,
                             label = 'Email',
                             widget=forms.EmailInput())
    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords did not match')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("username is already taken")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__exact=email):
            raise forms.ValidationError("email is already taken")

class LoginForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.CharField(max_length=20,
                                label='Password',
                                widget=forms.PasswordInput())
    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        user = authenticate(username=cleaned_data.get('username'), password=cleaned_data.get('password'))
        if not user:
            raise forms.ValidationError("username or password does not match")

class EntryForm(forms.ModelForm):
    class Meta:
        model = Grumbler
        exclude = ('owner',)
        widgets = {'picture' : forms.FileInput() }

class PasswordReset(forms.Form):
    password1 = forms.CharField(max_length=20,
                                label='Password1',
                                widget=forms.PasswordInput())
    password2 = forms.CharField(max_length=20,
                                label='Password2',
                                widget=forms.PasswordInput())
    def clean(self):
        cleaned_data = super(PasswordReset, self).clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords did not match')

class Email(forms.Form):
    email = forms.EmailField(max_length=40,
                             label = 'Email',
                             widget=forms.EmailInput())
    def clean(self):
        cleaned_data = super(Email, self).clean()

    def clean_email(self):
        user = Grumbler.objects.filter(email=self.cleaned_data.get('email'))
        if not user:
            raise forms.ValidationError('cannot find that email')

class CommentForm(forms.Form):
    text = forms.CharField(max_length=200)