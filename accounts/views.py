from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes

from accounts.forms import RegistrationForm
from accounts.models import Account


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            phone_number = form.cleaned_data["phone_number"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            username = email

            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password,
            )

            user.phone_number = phone_number
            user.save()

            # USER ACTIVATION
            current_site = get_current_site(request)
            mail_subject = "Please activate your account"
            message = render_to_string(
                "accounts/account_verification_email.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(user),
                },
            )
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            # messages.success(request,
            #                  f"Thank you for registration. We have sent you a verification email to {to_email}."
            #                  f" Please verify it")
            return redirect(f"/accounts/login/?command=verification&email={email}")

    else:
        form = RegistrationForm()

    context = {
        "form": form,
    }

    return render(request, "accounts/register.html", context=context)


def login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, "Login Successful")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid Login Credentials")
            return redirect("login")

    return render(request, "accounts/login.html")


@login_required(login_url="login")
def logout(request):
    auth.logout(request)
    messages.success(request, "Logout Successful")
    return redirect("login")


def activate(request, uidb64, token):
    # return HttpResponse("OK")
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulations! Your account has been activated!")
        return redirect("login")
    else:
        messages.error(request, "Invalid activation link")
        return redirect("Register")


@login_required(login_url="login")
def dashboard(request):
    return render(request, "accounts/dashboard.html")


def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            # Reset password email
            current_site = get_current_site(request)
            mail_subject = "Please reset your password"
            message = render_to_string(
                "accounts/reset_password_email.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(user),
                },
            )
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(
                request, "Password reset email has been sent to your email address"
            )

            return redirect("login")

        else:
            messages.error(request, "Account does not exist")
            return redirect("forgot_password")

    return render(request, "accounts/forgot_password.html")


def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session["uid"] = uid
        #     user.is_active = True
        #     user.save()
        messages.success(request, "Please reset your password")
        return redirect("reset_password")
    else:
        messages.error(request, "This link has been expired")
        return redirect("login")


def reset_password(request):
    if request.method == "POST":
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password == confirm_password:
            uid = request.session.get("uid", None)
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, "Password reset successful")
            return redirect("login")
        else:
            messages.error(request, "Passwords do not match")
            return redirect("reset_password")
    else:
        return render(request, "accounts/reset_password.html")
