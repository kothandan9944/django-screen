from pathlib import Path

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.files.uploadedfile import UploadedFile
from .models import Post, Comment

MAX_IMAGE_BYTES = 5 * 1024 * 1024
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'body', 'image']

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not isinstance(image, UploadedFile):
            return image
        if image.size > MAX_IMAGE_BYTES:
            raise forms.ValidationError('Image must be 5 MB or smaller.')
        extension = Path(image.name).suffix.lower()
        if extension not in ALLOWED_IMAGE_EXTENSIONS:
            raise forms.ValidationError('Use a JPG, PNG, WEBP, or GIF image.')
        return image


class CommentForm(forms.ModelForm):
    hp = forms.CharField(
        required=False,
        label='',
        widget=forms.HiddenInput(attrs={'autocomplete': 'off', 'tabindex': '-1'}),
    )

    class Meta:
        model = Comment
        fields = ['name', 'text']

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if not name:
            raise forms.ValidationError('Enter a name.')
        return name

    def clean_text(self):
        text = self.cleaned_data['text'].strip()
        if not text:
            raise forms.ValidationError('Write a comment.')
        if len(text) > 2000:
            raise forms.ValidationError('Keep the comment under 2000 characters.')
        return text

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('hp'):
            raise forms.ValidationError('Could not submit that comment.')
        return cleaned


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
