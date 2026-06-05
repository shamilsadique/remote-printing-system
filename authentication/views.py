from tokenize import generate_tokens
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from printing_service import settings
from django.core.mail import send_mail, EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from . tokens import generate_token
from user.models import UserDetail

# Create your views here.
def home(request):
    return render(request, "authentication/index.html")

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        fullname = request.POST['fullname']
        email = request.POST['email']
        password = request.POST['password']
        phone = request.POST['phone']
        address = request.POST['address']

        if User.objects.filter(username=username):
            messages.error(request, 'Username is already taken!')
            return redirect('signup')
        
        if User.objects.filter(email=email):
            messages.error(request, 'Email is already taken!')
            return redirect('signup')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        UserDetail.objects.create(user=user, phone=phone, address=address)
        user.first_name = fullname
        user.is_active = False
        user.save()

        messages.success(request, 'Account created successfully! Please check your email to activate your account.')

        #Welcome Email

        subject = 'Welcome to HomePrints'
        message = 'Thank you ' + user.first_name +  ' for signing up with HomePrints! We are excited to have you on board. You can now place orders for printing services on our platform. We look forward to serving you.'
        email_from = settings.EMAIL_HOST_USER
        to_list = [user.email]
        send_mail(subject, message, email_from, to_list, fail_silently=False)

        #Email for account activation

        current_site = get_current_site(request)
        mail_subject = 'Activate your HomePrints account'
        message2 = render_to_string('authentication/email_confirmation.html', {
            'name' : user.first_name,
            'domain' : current_site.domain,
            'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
            'token' : generate_token.make_token(user),
        })

        email = EmailMessage(
            mail_subject, 
            message2,
            settings.EMAIL_HOST_USER,
            [user.email]
        )
        email.fail_silently = True
        email.send()

        return redirect('signin')

    return render(request, "authentication/signup.html")

def signin(request):
    #if request.
    if request.method == 'POST':
        username = request.POST.get('username','')
        password = request.POST.get('password','')

        user = authenticate(username=username, password=password)

        if user is not None:
            login (request, user)
            return redirect('home')
        else:
            return HttpResponse("Invalid credentials")

    return render(request, "authentication/signin.html")

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and generate_token.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('home')
    else:
        return HttpResponse('Activation link is invalid!')

def signout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('signin')