from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Ad, ExchangeProposal
from .forms import AdForm, ExchangeProposalForm
from django.db.models import Q
from django.core.paginator import Paginator

def ad_list(request):
    ads = Ad.objects.all()
    query = request.GET.get('q')
    category = request.GET.get('category')
    condition = request.GET.get('condition')

    if query:
        ads = ads.filter(title__icontains=query)

    if category:
        ads = ads.filter(category=category)

    if condition:
        ads = ads.filter(condition=condition)
    
    paginator = Paginator(ads, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'ads/ad_list.html', {
        'page_obj': page_obj,
        'query': query,
        'category': category,
        'condition': condition,
        'categories': Ad.CATEGORY_CHOICES,
        'conditions': Ad.CONDITION_CHOICES,
    })

@login_required
def ad_create(request):
    if request.method == 'POST':
        form = AdForm(request.POST, request.FILES)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.user = request.user
            ad.save()
            return redirect('ad_list')
    else:
        form = AdForm()
    return render(request, 'ads/ad_form.html', {'form': form, 'action': 'Create'})

@login_required
def ad_update(request, pk):
    ad = get_object_or_404(Ad, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AdForm(request.POST, request.FILES, instance=ad)
        if form.is_valid():
            form.save()
            return redirect('ad_list')
    else:
        form = AdForm(instance=ad)
    return render(request, 'ads/ad_form.html', {'form': form, 'action': 'Update'})

@login_required
def ad_delete(request, pk):
    ad = get_object_or_404(Ad, pk=pk, user=request.user)
    if request.method == 'POST':
        ad.delete()
        return redirect('ad_list')
    return render(request, 'ads/ad_confirm_delete.html', {'ad': ad})

@login_required
def propose_exchange(request, ad_id):
    ad_receiver = get_object_or_404(Ad, id=ad_id)

    if ad_receiver.user == request.user:
        return HttpResponseForbidden("You cannot propose a trade on your own ad.")

    if request.method == 'POST':
        form = ExchangeProposalForm(request.POST, user=request.user)
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.ad_receiver = ad_receiver
            proposal.save()
            return redirect('ad_list')
    else:
        form = ExchangeProposalForm(user=request.user)

    return render(request, 'ads/propose_exchange.html', {
        'form': form,
        'ad_receiver': ad_receiver
    })

@login_required
def incoming_proposals(request):
    proposals = ExchangeProposal.objects.filter(ad_receiver__user=request.user).order_by('-created_at')
    return render(request, 'ads/incoming_proposals.html', {'proposals': proposals})

@login_required
def sent_proposals(request):
    proposals = ExchangeProposal.objects.filter(ad_sender__user=request.user).order_by('-created_at')
    return render(request, 'ads/sent_proposals.html', {'proposals': proposals})

@login_required
def respond_proposal(request, proposal_id, action):
    proposal = get_object_or_404(ExchangeProposal, id=proposal_id)

    if proposal.ad_receiver.user != request.user:
        return HttpResponseForbidden("Not your ad!")

    if request.method == 'POST' and proposal.status == 'pending':
        if action == 'accepted':
            proposal.status = 'accepted'
        elif action == 'rejected':
            proposal.status = 'rejected'
        proposal.save()
    
    return redirect('incoming_proposals')