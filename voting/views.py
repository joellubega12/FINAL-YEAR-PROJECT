from django.shortcuts import render, redirect, reverse
from account.views import account_login
from .models import Position, Candidate, Voter, Votes
from django.http import JsonResponse
from django.utils.text import slugify
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
import json
from django.http import HttpResponse

def preview_vote(request):
    return HttpResponse("Vote Preview Page")

def index(request):
    if not request.user.is_authenticated:
        return account_login(request)
    return redirect(reverse('voterDashboard'))


# ==============================
# BALLOT GENERATION 
# ==============================
def generate_ballot(display_controls=False):
    positions = Position.objects.order_by('priority').all()
    output = ""
    candidates_data = ""
    num = 1

    for position in positions:
        name = position.name
        position_name = slugify(name)
        candidates = Candidate.objects.filter(position=position)

        for candidate in candidates:
            if position.max_vote > 1:
                instruction = f"You may select up to {position.max_vote} candidates"
                input_box = f'<input type="checkbox" value="{candidate.id}" class="flat-red {position_name}" name="{position_name}[]">'
            else:
                instruction = "Select only one candidate"
                input_box = f'<input value="{candidate.id}" type="radio" class="flat-red {position_name}" name="{position_name}">'

            image = "/media/" + str(candidate.photo)
            candidates_data += f'''
            <li>
                {input_box}
                <button type="button" class="btn btn-primary btn-sm btn-flat clist platform"
                    data-fullname="{candidate.fullname}" data-bio="{candidate.bio}">
                    <i class="fa fa-search"></i> Platform
                </button>
                <img src="{image}" height="100px" width="100px" class="clist">
                <span class="cname clist">{candidate.fullname}</span>
            </li>
            '''

        output += f"""
        <div class="box box-solid">
            <div class="box-header"><b>{name}</b></div>
            <div class="box-body">
                <p>{instruction}</p>
                <ul>{candidates_data}</ul>
            </div>
        </div>
        """

        position.priority = num
        position.save()
        num += 1
        candidates_data = ""

    return output


def fetch_ballot(request):
    return JsonResponse(generate_ballot(True), safe=False)


# ==============================
# OTP GENERATION
# ==============================
def generate_otp():
    import random
    return str(random.randint(100000, 999999))


# ==============================
# DASHBOARD
# ==============================
def dashboard(request):
    user = request.user

    if user.voter.voted:
        context = {
            'my_votes': Votes.objects.filter(voter=user.voter),
        }
        return render(request, "voting/voter/result.html", context)

    return redirect(reverse('show_ballot'))


# ==============================
# VERIFY PAGE
# ==============================
def verify(request):
    return render(request, "voting/voter/verify.html", {
        'page_title': 'Email Verification'
    })


# ==============================
# SEND OTP VIA EMAIL (UPDATED)
# ==============================
def resend_otp(request):
    user = request.user
    voter = user.voter
    error = False

    if voter.otp_sent >= 3:
        return JsonResponse({
            "data": "You have reached max OTP requests.",
            "error": True
        })

    # Generate OTP if not exists
    if voter.otp is None:
        voter.otp = generate_otp()

    try:
        send_mail(
            'Your Voting Verification Code',
            f'Hello {user.username}, your verification code is: {voter.otp}',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

        voter.otp_sent += 1
        voter.save()

        return JsonResponse({
            "data": "OTP sent to your email successfully.",
            "error": False
        })

    except Exception as e:
        return JsonResponse({
            "data": f"Email sending failed: {str(e)}",
            "error": True
        })


# ==============================
# VERIFY OTP
# ==============================
def verify_otp(request):
    if request.method != 'POST':
        messages.error(request, "Access Denied")
        return redirect(reverse('voterVerify'))

    otp = request.POST.get('otp')
    voter = request.user.voter

    if not otp:
        messages.error(request, "Enter OTP")
        return redirect(reverse('voterVerify'))

    if voter.otp != otp:
        messages.error(request, "Invalid OTP")
        return redirect(reverse('voterVerify'))

    voter.verified = True
    voter.save()

    messages.success(request, "Email verified successfully")
    return redirect(reverse('show_ballot'))


# ==============================
# SHOW BALLOT
# ==============================
def show_ballot(request):
    if request.user.voter.voted:
        messages.error(request, "You have already voted")
        return redirect(reverse('voterDashboard'))

    return render(request, "voting/voter/ballot.html", {
        'ballot': generate_ballot(False)
    })


# ==============================
# SUBMIT BALLOT
# ==============================
def submit_ballot(request):
    if request.method != 'POST':
        messages.error(request, "Invalid request")
        return redirect(reverse('show_ballot'))

    voter = request.user.voter

    if voter.voted:
        messages.error(request, "You have already voted")
        return redirect(reverse('voterDashboard'))

    form = dict(request.POST)
    form.pop('csrfmiddlewaretoken', None)

    if not form:
        messages.error(request, "No vote selected")
        return redirect(reverse('show_ballot'))

    form_count = 0

    for position in Position.objects.all():
        key = slugify(position.name)
        selected = form.get(key) or form.get(key + "[]")

        if not selected:
            continue

        if not isinstance(selected, list):
            selected = [selected]

        for candidate_id in selected:
            candidate = Candidate.objects.get(id=candidate_id)
            Votes.objects.create(
                voter=voter,
                candidate=candidate,
                position=position
            )
            form_count += 1

    if Votes.objects.filter(voter=voter).count() != form_count:
        Votes.objects.filter(voter=voter).delete()
        messages.error(request, "Vote failed. Try again.")
        return redirect(reverse('show_ballot'))

    voter.voted = True
    voter.save()

    messages.success(request, "Vote submitted successfully")
    return redirect(reverse('voterDashboard'))