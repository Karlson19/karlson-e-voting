from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.db import transaction, IntegrityError
from django.db.models import Count
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from django.conf import settings
from django.contrib import messages

from .models import Election, Candidate, Vote
from .forms import RegisterForm, ElectionForm, CandidateForm


class ElectionListView(generic.ListView):
    model = Election
    template_name = 'voting/election_list.html'
    context_object_name = 'elections'
    paginate_by = 20

    def get_queryset(self):
        # optional simple search by ?q=
        qs = Election.objects.all().order_by('-start_time')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(title__icontains=q)
        return qs


class ElectionDetailView(generic.DetailView):
    model = Election
    template_name = 'voting/election_detail.html'
    context_object_name = 'election'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        election = self.get_object()
        ctx['candidates'] = election.candidates.all()
        if self.request.user.is_authenticated:
            ctx['has_voted'] = Vote.objects.filter(voter=self.request.user, election=election).exists()
        else:
            ctx['has_voted'] = False
        return ctx


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect('voting:home')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')


@login_required
def cast_vote(request, pk):
    election = get_object_or_404(Election, id=pk)

    if not election.is_active:
        messages.error(request, "This election is not active.")
        return redirect('voting:election_detail', pk=election.id)

    if request.method == "POST":
        candidate_id = request.POST.get("candidate_id")
        candidate = get_object_or_404(Candidate, id=candidate_id, election=election)

        # Prevent duplicate votes
        if Vote.objects.filter(voter=request.user, election=election).exists():
            messages.error(request, "You have already voted in this election.")
        else:
            Vote.objects.create(voter=request.user, election=election, candidate=candidate)
            messages.success(request, f"Your vote for {candidate.name} has been cast successfully!")

        return redirect('voting:election_detail', pk=election.id)

    return redirect('voting:election_detail', pk=election.id)


def election_results(request, pk):
    election = get_object_or_404(Election, pk=pk)
    if not election.has_ended():
        messages.error(request, "Results are not available until the election ends.")
        return redirect('voting:election_detail', pk=pk)

    candidate_qs = election.candidates.annotate(vote_count=Count('votes')).order_by('-vote_count')
    total_votes = election.votes.count()

    # compute percentage per candidate for template
    candidates_with_pct = []
    for c in candidate_qs:
        pct = 0
        if total_votes > 0:
            pct = round((c.vote_count / total_votes) * 100, 2)
        candidates_with_pct.append({'candidate': c, 'vote_count': c.vote_count, 'percent': pct})

    return render(request, 'voting/admin/election_results.html', {
        'election': election,
        'candidates': candidates_with_pct,
        'total_votes': total_votes
    })


# ----------------- Admin (staff-only) views -----------------
# Use staff_member_required to be explicit and consistent.
@staff_member_required(login_url='login')
def admin_manage_elections(request):
    elections = Election.objects.all().order_by('-start_time')
    return render(request, 'voting/admin/manage_elections.html', {'elections': elections})


@staff_member_required(login_url='login')
def admin_create_election(request):
    if request.method == 'POST':
        form = ElectionForm(request.POST)
        if form.is_valid():
            election = form.save(commit=False)
            election.created_by = request.user
            election.save()
            messages.success(request, 'Election created.')
            return redirect('voting:admin_manage_elections')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = ElectionForm()
    return render(request, 'voting/admin/create_election.html', {'form': form})


@staff_member_required(login_url='login')
def admin_add_candidate(request, pk):
    election = get_object_or_404(Election, pk=pk)
    if request.method == 'POST':
        form = CandidateForm(request.POST)
        if form.is_valid():
            candidate = form.save(commit=False)
            candidate.election = election
            candidate.save()
            messages.success(request, 'Candidate added.')
            return redirect('voting:admin_manage_elections')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = CandidateForm()
    return render(request, 'voting/admin/add_candidate.html', {'form': form, 'election': election})


def api_election_counts(request, pk):
    election = get_object_or_404(Election, pk=pk)
    data = []
    for c in election.candidates.all():
        data.append({
            'candidate_id': c.id,
            'name': c.name,
            'count': c.votes.count()
        })
    data.append({'total_votes': election.votes.count()})
    return JsonResponse({'counts': data})


# ---------- Secure logout view (POST only) ----------
@require_POST
@login_required
def logout_view(request):
    from django.contrib.auth import logout as _logout
    _logout(request)
    messages.info(request, "You have been logged out.")
    return redirect(getattr(settings, 'LOGOUT_REDIRECT_URL', '/'))
