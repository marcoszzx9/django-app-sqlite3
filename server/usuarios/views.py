from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from .models import Reminder, EmailVerification, PasswordResetCode
from django.utils import timezone

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Usuário já existe!')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'E-mail já cadastrado!')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.is_active = False
            user.save()

            code = EmailVerification.generate_code()
            EmailVerification.objects.create(user=user, code=code)

            send_mail(
                'Confirme seu e-mail',
                f'Seu código de verificação é: {code}',
                'no-reply@seudominio.com',
                [email],
                fail_silently=False,
            )

            messages.info(request, 'Verificação enviada! Verifique seu e-mail.')
            return redirect('verify_email')

    return render(request, 'signup.html')


def verify_email_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        code = request.POST['code']
        try:
            user = User.objects.get(username=username)
            ev = EmailVerification.objects.get(user=user)
            if ev.code == code:
                ev.verified = True
                ev.save()
                user.is_active = True
                user.save()
                messages.success(request, 'E-mail confirmado! Você já pode fazer login.')
                return redirect('login')
            else:
                messages.error(request, 'Código incorreto.')
        except (User.DoesNotExist, EmailVerification.DoesNotExist):
            messages.error(request, 'Usuário não encontrado.')
    return render(request, 'verify_email.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Credenciais inválidas.')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def init_view(request):
    reminders = Reminder.objects.filter(user=request.user)
    return render(request, 'dashboard.html', {'reminders': reminders})


@login_required
def add_reminder(request):
    if request.method == "POST":
        Reminder.objects.create(
            title=request.POST.get("title"),
            description=request.POST.get("description"),
            date=timezone.now(),
            user=request.user
        )
        messages.success(request, 'Lembrete criado!')
        return redirect('dashboard')
    return render(request, 'reminder_form.html')

@login_required
def edit_reminder(request, pk):
    rem = get_object_or_404(Reminder, pk=pk, user=request.user)
    if request.method == 'POST':
        rem.title = request.POST['title']
        rem.description = request.POST.get('description', '')
        rem.date = request.POST.get('date')
        rem.done = 'done' in request.POST
        rem.save()
        messages.info(request, 'Lembrete atualizado!')
        return redirect('dashboard')
    return render(request, 'reminder_form.html', {'rem': rem})


@login_required
def delete_reminder(request, pk):
    rem = get_object_or_404(Reminder, pk=pk, user=request.user)
    rem.delete()
    messages.warning(request, 'Lembrete removido!')
    return redirect('dashboard')


@login_required
def account_view(request):
    return render(request, 'account.html', {'user': request.user})


# ------------------ REDEFINIÇÃO DE SENHA POR CÓDIGO ------------------
def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            code = PasswordResetCode.generate_code()
            PasswordResetCode.objects.create(user=user, code=code)

            send_mail(
                'Código de redefinição de senha',
                f'Seu código é: {code}',
                'no-reply@seudominio.com',
                [email],
                fail_silently=False,
            )

            messages.success(request, 'Código enviado! Verifique seu e-mail.')
            return redirect('password_reset_confirm')
        except User.DoesNotExist:
            messages.error(request, 'E-mail não encontrado.')

    return render(request, 'password_reset.html')


def password_reset_confirm(request):
    if request.method == "POST":
        email = request.POST.get("email")
        code = request.POST.get("code")
        new_password = request.POST.get("password")
        try:
            user = User.objects.get(email=email)
            reset = PasswordResetCode.objects.filter(user=user, code=code, verified=False).first()
            if reset:
                if reset.is_expired():
                    messages.error(request, "Código expirou.")
                else:
                    user.password = make_password(new_password)
                    user.save()
                    reset.verified = True
                    reset.save()
                    messages.success(request, "Senha alterada com sucesso!")
                    return redirect('login')
            else:
                messages.error(request, "Código inválido.")
        except User.DoesNotExist:
            messages.error(request, "E-mail não encontrado.")

    return render(request, 'password_reset_confirm.html')
