from django import newforms as forms
from django.contrib.auth.models import User
from django.newforms.util import ValidationError
from django.core.validators import alnum_re
from flowgram.core.models import GENDER_CHOICES, FREQ_CHOICES, Regcode, UserProfile, PRESS_CATEGORY
from flowgram.localsettings import my_URL_BASE, FEATURE
from django.newforms.extras.widgets import SelectDateWidget
from django.utils.dates import MONTHS_LONG, REG_YEARS, REG_DAYS

def CustomBooleanField(**kwargs):
    return forms.BooleanField(widget=forms.CheckboxInput(attrs={'class':'checkbox'}), **kwargs)

class ProfileForm(forms.Form):
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=False)
    homepage = forms.URLField(max_length=100, required=False, verify_exists=False)
    email = forms.EmailField(required=False)
    description = forms.CharField(label='Tell the Flowgram world about yourself', required=False, widget=forms.Textarea, max_length=1000)
    birthdate = forms.DateField(required=False,widget=SelectDateWidget(years=REG_YEARS, months=MONTHS_LONG, days=REG_DAYS))
    newsletter_optin = forms.BooleanField(required=False,label='Let me know about new Flowgram features and news')  

#==== Subscriptions & Notificaitons ====
class NotifyForm(forms.Form):
	notification_freq = forms.ChoiceField(choices=FREQ_CHOICES, label="If so, how often do you want it sent? ")
	notify_by_email = forms.BooleanField(required=False,label='Would you like your newsfeed sent to your email?')
	has_public_news_feed = forms.BooleanField(required=False,label='Would you like your newsfeed public, including RSS?')
#========================================

class FlowgramPressForm(forms.Form):
    link_date = forms.DateField(widget=SelectDateWidget(years=REG_YEARS, months=MONTHS_LONG, days=REG_DAYS))
    link_text = forms.CharField(max_length=2048)
    link_url = forms.URLField(max_length=2048, required=False, verify_exists=False)
    lede_text = forms.CharField(required=False, widget=forms.Textarea, max_length=4096)
    full_text = forms.CharField(required=False, widget=forms.Textarea)
    press_category = forms.ChoiceField(choices=PRESS_CATEGORY)
    
class RegistrationForm(forms.Form):
    # This form largely copied from django-registration app -andrew
    username = forms.CharField(max_length=30,required=True, help_text="Required")
    email = forms.EmailField(max_length=256, help_text="Required")
    password1 = forms.CharField(max_length=16,widget=forms.PasswordInput,label='Password', help_text="Required")
    password2 = forms.CharField(max_length=16,widget=forms.PasswordInput,label='Confirm Password', help_text="Required")
    gender = forms.ChoiceField(choices=GENDER_CHOICES,required=False,label='Gender')
    newsletter_optin = forms.BooleanField(required=False,initial=True,label='Let me know about new Flowgram features and news')
    description = forms.CharField(label='Tell the Flowgram world about yourself', required=False, widget=forms.Textarea, max_length=1000)
    birthdate = forms.DateField(required=False,widget=SelectDateWidget(years=REG_YEARS, months=MONTHS_LONG, days=REG_DAYS)) 
    homepage = forms.URLField(max_length=100, required=False, verify_exists=False)
    registration_code = forms.CharField(max_length=16, help_text="Required", required=False)
    
    def clean_username(self):
        """
        Validates that the username is alphanumeric and is not already
        in use.
        
        """
        if not alnum_re.search(self.cleaned_data['username']):
            raise forms.ValidationError('Usernames can only contain letters, numbers and underscores')
        try:
            user = User.objects.get(username__exact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError('This username is already taken. Please choose another.')

    def clean_password2(self):
        if self.cleaned_data['password1'] != self.cleaned_data['password2']:
            raise ValidationError('Passwords must match.')
        else:
            return self.cleaned_data['password2']
    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return email
        reset_url = my_URL_BASE + 'reset/'
        raise ValidationError("The email address '%s' already has an account. Go to %s to reset your password." % (email, reset_url))
    def clean_registration_code(self):
        if FEATURE['use_regcode']:
            code = self.cleaned_data['registration_code'].upper()
            try: 
                regcode = Regcode.objects.get(code=code)
            except Regcode.DoesNotExist:
                raise ValidationError("Invalid registration code.")
            if regcode.used and regcode.count <= 0:
                raise ValidationError("Registration code has already been used.")
            return regcode
        else:
            return ''

class RegistrationFormStep1(forms.Form):
    username = forms.CharField(max_length=30,required=True, help_text="Required")
    password1 = forms.CharField(max_length=16,widget=forms.PasswordInput,label='Password', help_text="Required")
    password2 = forms.CharField(max_length=16,widget=forms.PasswordInput,label='Confirm Password', help_text="Required")

    def clean_username(self):
        """
        Validates that the username is alphanumeric and is not already
        in use.

        """
        if not alnum_re.search(self.cleaned_data['username']):
            raise forms.ValidationError('Usernames can only contain letters, numbers and underscores')
        try:
            user = User.objects.get(username__exact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError('This username is already taken. Please choose another.')

    def clean_password2(self):
        if self.cleaned_data['password1'] != self.cleaned_data['password2']:
            raise ValidationError('Passwords must match.')
        else:
            return self.cleaned_data['password2']

class RegistrationFormStep2(forms.Form):
    email = forms.EmailField(max_length=256, help_text="Required")
    gender = forms.ChoiceField(choices=GENDER_CHOICES,required=False,label='Gender')
    newsletter_optin = forms.BooleanField(required=False,initial=True,label='Let me know about new Flowgram features and news')
    description = forms.CharField(label='Tell the Flowgram world about yourself', required=False, widget=forms.Textarea, max_length=1000)
    birthdate = forms.DateField(required=False,widget=SelectDateWidget(years=REG_YEARS, months=MONTHS_LONG, days=REG_DAYS)) 
    homepage = forms.URLField(max_length=100, required=False, verify_exists=False)
    registration_code = forms.CharField(max_length=16, help_text="Required", required=False)

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return email
        reset_url = my_URL_BASE + 'reset/'
        raise ValidationError("The email address '%s' already has an account. Go to %s to reset your password." % (email, reset_url))
    def clean_registration_code(self):
        if FEATURE['use_regcode']:
            code = self.cleaned_data['registration_code'].upper()
            try: 
                regcode = Regcode.objects.get(code=code)
            except Regcode.DoesNotExist:
                raise ValidationError("Invalid registration code.")
            if regcode.used and regcode.count <= 0:
                raise ValidationError("Registration code has already been used.")
            return regcode
        else:
            return ''

class ChangePasswordForm(forms.Form):
    password1 = forms.CharField(max_length=16,widget=forms.PasswordInput, label='New password')
    password2 = forms.CharField(max_length=16,widget=forms.PasswordInput, label='New password (again)')
    def clean_password2(self):
        if self.cleaned_data['password1'] != self.cleaned_data['password2']:
            raise ValidationError('Passwords must match.')
        else:
            return self.cleaned_data['password2']

from django.newforms import widgets

class LoginForm(forms.Form):
    """Login form for users."""
    username = forms.RegexField(r'^[a-zA-Z0-9_]{1,30}$',
                                min_length = 1,
                                max_length = 30,
                                error_message = 'Invalid username, please try again.')
    password = forms.CharField(min_length = 1, 
                               max_length = 128, 
                               widget = widgets.PasswordInput,
                               label = 'Password')
    remember_user = CustomBooleanField(required = False, 
                                       label = 'Remember Me')

    def clean(self):
        #TODO: make it validate fields seperately
        user = None
        if 'username' in self.cleaned_data.keys():
            try:
                user = User.objects.get(username__iexact = self.cleaned_data['username'])
            except User.DoesNotExist, KeyError:
                raise forms.ValidationError('Invalid username, please try again.')

        if user and ('password' in self.cleaned_data.keys()):
            if not user.check_password(self.cleaned_data['password']):
                raise forms.ValidationError('Invalid password, please try again.')

        return self.cleaned_data

class AvatarForm(forms.Form):
    avatar = forms.ImageField(label="Upload a new avatar:")

class AdminFilesForm(forms.Form):
    image = forms.ImageField(label="Upload an image:")
    filename_prefix = forms.CharField(max_length=32, label="Choose a filename prefix:")

class TutorialForm(forms.Form):
    position = forms.CharField(max_length=4)
    title = forms.CharField(max_length=2048)
    content = forms.CharField(widget=forms.Textarea, required=False)
    active = forms.BooleanField(required=False)
    video = forms.FileField(required = False, label = 'Upload Video')
    filename_prefix = forms.CharField(required = False, max_length=32, label="Choose a filename prefix:")
    
class FeedSettingsForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('subscribe_fg_on_comment', 'subscribed_to_own_fgs', 'subscribed_to_self', 'get_news_via_email')
