from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import Item, UserSettings


class ItemPriceGraphForm(forms.Form):
    item_category = forms.ChoiceField(label="Select Category", required=False)
    item_id = forms.ChoiceField(label="Select Item", required=False)
    time_range = forms.ChoiceField(
        label="Select a Time Range", initial=24, required=False
    )
    TIME_CHOICES = (
        (7 * 24, "Last 7 days"),
        (5 * 24, "Last 5 days"),
        (24, "Last 24 hours"),
        (12, "Last 12 hours"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        items = Item.objects.all()  # Replace YourModel with your actual model
        self.fields["item_id"].choices = [(item.id, item.item_name) for item in items]
        self.fields["time_range"].choices = ItemPriceGraphForm.TIME_CHOICES
        # Set field for category make sure we are only getting unique
        # categories
        self.fields["item_category"].choices = [
            (item.category, item.category) for item in items.distinct("category")
        ]


class BulkTrackForm(forms.Form):
    """BulkTrackForm is a form that allows users to enter a catagory page and track all
    items within that catagory."""

    url = forms.CharField(label="Enter URL", required=False)
    category = forms.CharField(label="Enter Category", required=False)


class SignUpForm(UserCreationForm):
    """SignupForm is a form that allows users to signup for an account."""

    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(
        max_length=254, help_text="Required. Inform a valid email address."
    )
    notification = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
            "notification",
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.notification = self.cleaned_data["notification"]
        UserSettings.objects.create(user=user, notification=user.notification)
        if commit:
            user.save()
        return user


# Add the missing import for UserUpdateForm
class UserSettingsForm(forms.ModelForm):
    """UserSettingsForm is a form that allows users to change their settings."""

    username = forms.CharField(max_length=30)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    notification = forms.BooleanField(required=False)

    class Meta:
        model = UserSettings
        fields = ("notification",)
