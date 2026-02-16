from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import MaidProfileForm
from .models import MaidProfile, Profile
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import translation
from django.conf import settings
from django.utils.translation import gettext as _

def switch_language(request):
    if request.method == 'POST':
        language = request.POST.get('language')
        if language:
            translation.activate(language)
            request.session[translation.LANGUAGE_SESSION_KEY] = language
            
            # Determine redirect URL
            next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or '/'
            return redirect(next_url)
    return redirect('home')

def home(request):
    return render(request, 'main/index.html')

@login_required
def register_maid(request):
    # Check if user already has a maid profile
    if MaidProfile.objects.filter(user=request.user).exists():
        messages.info(request, _("You have already registered as a maid."))
        return redirect('home')

    if request.method == 'POST':
        form = MaidProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            
            # Update User Profile role to 'maid'
            if hasattr(request.user, 'profile'):
                request.user.profile.role = 'maid'
                request.user.profile.save()
            
            messages.success(request, _("Registered as Maid Successfully. Admin will verify your profile soon."))
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        initial_data = {
            'email': request.user.email,
            'name': request.user.get_full_name() or request.user.username
        }
        form = MaidProfileForm(initial=initial_data)

    return render(request, 'main/register_maid.html', {'form': form})

@login_required
def maid_list_view(request):
    """
    View to display a list of verified maids with filtering options.
    """
    # 1. Base Query: Only show verified maids
    maids = MaidProfile.objects.filter(status='verified')
    
    # 2. Get Filtering Parameters from Request
    skill_filter = request.GET.get('skill')
    location_filter = request.GET.get('location')
    min_salary = request.GET.get('min_salary')
    max_salary = request.GET.get('max_salary')

    # 3. Apply Filters
    if skill_filter:
        # distinct_skills in context will rely on exact matches usually, 
        # but icontains allows partial matches which is flexible for search.
        maids = maids.filter(skills__icontains=skill_filter)
    
    if location_filter:
        maids = maids.filter(location__icontains=location_filter)
        
    if min_salary:
        maids = maids.filter(expected_salary__gte=min_salary)
        
    if max_salary:
        maids = maids.filter(expected_salary__lte=max_salary)

    # Order by newest first
    maids = maids.order_by('-created_at')
    
    # 4. Prepare Dynamic Filter Data (Distinct Skills)
    # Fetch all verified maids to generate the complete list of available skills
    all_verified_maids = MaidProfile.objects.filter(status='verified')
    distinct_skills = set()
    
    for m in all_verified_maids:
        if m.skills:
            # unique skills extraction
            raw_skills = m.skills.split(',')
            for s in raw_skills:
                clean_skill = s.strip()
                if clean_skill:  # Avoid empty strings
                    distinct_skills.add(clean_skill)
            
    # 5. Pre-process maids for template display (convert comma-string to list)
    # We do this iteration because we need to display badges for each skill
    for m in maids:
        if m.skills:
            m.skills_list = [s.strip().title() for s in m.skills.split(',') if s.strip()]
        else:
            m.skills_list = []
            
    context = {
        'maids': maids,
        'distinct_skills': sorted(list(distinct_skills)), # Sort for dropdown
        'current_filters': {
            'skill': skill_filter,
            'location': location_filter,
            'min_salary': min_salary,
            'max_salary': max_salary,
        }
    }
    return render(request, 'main/maid_list.html', context)

@login_required
def customer_maid_profile(request, maid_id):
    maid = MaidProfile.objects.get(id=maid_id, status='verified')
    # Pre-process skills for template usage
    if maid.skills:
        maid.skills_list = [s.strip().title() for s in maid.skills.split(',') if s.strip()]
    else:
        maid.skills_list = []
    
    maid.first_name = maid.name.split()[0] if maid.name else ""
    return render(request, 'main/customer_maid_profile.html', {'maid': maid})

def register_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role = request.POST.get('role')

        if password != confirm_password:
            messages.error(request, _("Passwords do not match."))
            return render(request, 'main/register.html')

        if User.objects.filter(username=email).exists():
            messages.error(request, _("Email already registered."))
            return render(request, 'main/register.html')

        user = User.objects.create_user(username=email, email=email, password=password)
        # Create Profile
        Profile.objects.create(user=user, full_name=full_name, phone_number=phone_number, role=role)

        messages.success(request, _("Account created successfully. Please sign in."))
        return redirect('login')

    return render(request, 'main/register.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('admin_dashboard')
            return redirect('home')
        else:
            messages.error(request, _("Invalid email or password."))
    
    return render(request, 'main/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

# Admin Dashboard Implementation
@staff_member_required
def admin_dashboard(request):
    total_users = User.objects.filter(is_superuser=False).count()
    customers_count = Profile.objects.filter(role='customer').count()
    verified_maids_count = MaidProfile.objects.filter(status='verified').count()
    unverified_maids_count = MaidProfile.objects.filter(status='pending').count()
    
    context = {
        'total_users': total_users,
        'customers_count': customers_count,
        'verified_maids_count': verified_maids_count,
        'unverified_maids_count': unverified_maids_count,
    }
    return render(request, 'main/admin/dashboard.html', context)

@staff_member_required
def admin_user_list(request, category):
    users = []
    title = ""
    
    if category == 'total':
        users = User.objects.filter(is_superuser=False)
        title = "Total Users"
    elif category == 'customers':
        users = User.objects.filter(profile__role='customer')
        title = "Customers"
    elif category == 'verified':
        users = User.objects.filter(maid_profile__status='verified')
        title = "Verified Maids"
    elif category == 'unverified':
        users = User.objects.filter(maid_profile__status='pending')
        title = "Unverified Maids"
        
    for u in users:
        u.display_name = u.username
        if hasattr(u, 'profile') and u.profile and u.profile.full_name:
            u.display_name = u.profile.full_name
        elif hasattr(u, 'maid_profile') and u.maid_profile and u.maid_profile.name:
            u.display_name = u.maid_profile.name
        
        u.display_initial = u.display_name[0].upper() if u.display_name else "?"

    return render(request, 'main/admin/user_list.html', {'users_list': users, 'title': title, 'category': category})

@staff_member_required
def admin_user_profile(request, user_id):
    target_user = User.objects.get(id=user_id)
    # Ensure profile exists to avoid template errors
    if not hasattr(target_user, 'profile'):
        Profile.objects.create(user=target_user, role='customer', full_name=target_user.username)
    
    target_user.display_name = target_user.username
    if target_user.profile and target_user.profile.full_name:
        target_user.display_name = target_user.profile.full_name
    elif hasattr(target_user, 'maid_profile') and target_user.maid_profile and target_user.maid_profile.name:
        target_user.display_name = target_user.maid_profile.name
    
    target_user.display_initial = target_user.display_name[0].upper() if target_user.display_name else "?"
    
    return render(request, 'main/admin/user_profile.html', {'target_user': target_user})

@staff_member_required
def admin_maid_detail(request, maid_id):
    maid = MaidProfile.objects.get(id=maid_id)
    maid.display_name = maid.name
    maid.display_initial = maid.name[0].upper() if maid.name else "?"
    
    # Pre-process skills for template usage
    if maid.skills:
        maid.skills_list = [s.strip().title() for s in maid.skills.split(',') if s.strip()]
    else:
        maid.skills_list = []
    
    return render(request, 'main/admin/maid_detail.html', {'maid': maid})

@staff_member_required
def approve_maid(request, maid_id):
    maid = MaidProfile.objects.get(id=maid_id)
    maid.status = 'verified'
    maid.save()
    
    # Send Email
    subject = "Maid Registration Verified - Maid Hiring System"
    message = f"""Hello {maid.name},

Congratulations! Your registration as a maid has been verified by our admin team.
You are now active in our system and customers can contact you for services.

Please log in to your dashboard to view your profile status.

Best regards,
Maid Hiring System Team
"""
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [maid.user.email], fail_silently=False)
        messages.success(request, "Verified maid successfully. Email notification sent.")
    except Exception as e:
        messages.warning(request, f"Verified maid successfully, but failed to send email: {str(e)}")
    
    return redirect('admin_dashboard')

@staff_member_required
def admin_send_formal_rejection_email(request, maid_id):
    try:
        maid = MaidProfile.objects.get(id=maid_id)
        
        # Mark as rejected if not already
        if maid.status != 'rejected':
            maid.status = 'rejected'
            maid.save()
            
        subject = "Update on your Maid Registration - Not Eligible"
        message = f"""Hello {maid.name},

Thank you for your interest in joining the Maid Hiring System.

After a thorough review of your application and verification documents, we regret to inform you that you are not eligible for registration in our system at this time.

Our verification process is designed to ensure the highest standards of safety and service for our customers, and unfortunately, your application does not meet the current criteria.

Best regards,
Admin Team
Maid Hiring System
"""
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [maid.user.email],
            fail_silently=False
        )
        messages.success(request, f"Formal rejection email sent to {maid.name}.")
    except Exception as e:
        messages.error(request, f"Failed to send formal email: {str(e)}")
        
    return redirect('admin_maid_detail', maid_id=maid_id)

@staff_member_required
def reject_maid(request, maid_id):
    maid = MaidProfile.objects.get(id=maid_id)
    maid.status = 'rejected'
    maid.save()
    
    # Send Email
    subject = "Maid Registration Update - Maid Hiring System"
    message = f"""Hello {maid.name},

We regret to inform you that your registration for the Maid Hiring System has been rejected.
After reviewing your profile and documents, we found that you are not eligible to be registered in our system at this time.

Reasons for rejection may include:
- Incomplete or unclear documentation provided.
- Does not meet our current verification criteria.

If you believe this is an error or if you have updated documents, please contact our support team.

Best regards,
Maid Hiring System Team
"""
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [maid.user.email], fail_silently=False)
        messages.error(request, "Rejected maid registration. Email notification sent.")
    except Exception as e:
        messages.warning(request, f"Rejected maid registration, but failed to send email: {str(e)}")
    
    return redirect('admin_dashboard')

@login_required
def send_email_to_maid(request, maid_id):
    if request.method == 'POST':
        try:
            maid = MaidProfile.objects.get(id=maid_id)
            subject = request.POST.get('subject')
            message = request.POST.get('message')
            
            sender_name = request.user.get_full_name() or request.user.username
            if hasattr(request, 'user') and hasattr(request.user, 'profile') and request.user.profile.full_name:
                sender_name = request.user.profile.full_name

            # Prepare email content
            email_subject = f"[Inquiry] {subject}"
            email_message = f"""
Hello {maid.name},

You have received a new inquiry from {sender_name} ({request.user.email}).

Message:
{message}

--------------------------------------------------
To reply, please email {request.user.email} directly.
"""
            
            email = EmailMessage(
                subject=email_subject,
                body=email_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[maid.user.email],
                reply_to=[request.user.email]
            )
            email.send(fail_silently=False)
            messages.success(request, _("Your email has been sent successfully!"))
        except MaidProfile.DoesNotExist:
             messages.error(request, _("Maid profile not found."))
        except Exception as e:
            messages.error(request, _(f"Failed to send email: {str(e)}"))
            
    return redirect('customer_maid_profile', maid_id=maid_id)
