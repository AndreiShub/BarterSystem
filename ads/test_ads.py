import pytest
from django.contrib.auth.models import User
from ads.models import Ad, ExchangeProposal
from django.test import Client
from django.urls import reverse

@pytest.fixture
def test_user(db):
    return User.objects.create_user(username='testuser', password='testpass')

@pytest.fixture
def ad_data():
    return {
        'title': 'Test Title',
        'description': 'This is a description of a test ad.',
        'category': 'electronics',
        'condition': 'new',
    }

@pytest.fixture
def test_ad(db, test_user, ad_data):
    return Ad.objects.create(user=test_user, **ad_data)

@pytest.mark.django_db
def test_create_ad(test_ad):
    assert test_ad.title == "Test Title"
    assert test_ad.description == "This is a description of a test ad."
    assert test_ad.category == "electronics"
    assert test_ad.condition == "new"
    assert test_ad.user.username == "testuser"

@pytest.mark.django_db
def test_ad_create_view(client, test_user, ad_data):
    client.login(username="testuser", password="testpass")
    response = client.post(reverse("ad_create"), data=ad_data)

    assert response.status_code == 302
    assert Ad.objects.filter(title="Test Title", user=test_user).exists()

@pytest.mark.django_db
def test_ad_update_view(client, test_user, test_ad):
    client.login(username="testuser", password="testpass")
    update_data = {
        "title": "Updated Title",
        "description": "Updated description.",
        "category": "books",
        "condition": "used_good",
    }

    url = reverse("ad_update", args=[test_ad.id])
    response = client.post(url, data=update_data)

    assert response.status_code == 302

    test_ad.refresh_from_db()
    assert test_ad.title == "Updated Title"
    assert test_ad.description == "Updated description."
    assert test_ad.category == "books"
    assert test_ad.condition == "used_good"

@pytest.mark.django_db
def test_ad_delete_view(client, test_user, test_ad):
    client.login(username="testuser", password="testpass")

    url = reverse("ad_delete", args=[test_ad.id])
    response = client.post(url)

    assert response.status_code == 302
    assert not Ad.objects.filter(id=test_ad.id).exists()

@pytest.mark.django_db
def test_ad_search(client, test_user):
    Ad.objects.create(
        user=test_user,
        title="Guitar",
        description="11111",
        category="electronics",
        condition="used_good"
    )

    Ad.objects.create(
        user=test_user,
        title="Book",
        description="222222",
        category="books",
        condition="new"
    )

    response = client.get(reverse("ad_list") + "?q=guitar")

    assert response.status_code == 200
    content = response.content.decode()

    assert "<strong>Guitar</strong>" in content
    assert "<strong>Book</strong>" not in content

@pytest.mark.django_db
def test_propose_exchange_view(client):
    user1 = User.objects.create_user(username='user1', password='pass123')
    user2 = User.objects.create_user(username='user2', password='pass123')
    ad_user2 = Ad.objects.create(
        user=user2,
        title="Bike",
        description="A mountain bike",
        category="other",
        condition="used_good"
    )
    ad_user1 = Ad.objects.create(
        user=user1,
        title="Book",
        description="A sci-fi novel",
        category="books",
        condition="new"
    )
    client.force_login(user1)

    url = reverse('propose_exchange', args=[ad_user2.id])
    response = client.post(url, {
        'ad_sender': ad_user1.id,
        'comment': 'Wanna trade?'
    })

    assert response.status_code == 302

    proposal = ExchangeProposal.objects.first()
    assert proposal is not None
    assert proposal.ad_sender == ad_user1
    assert proposal.ad_receiver == ad_user2
    assert proposal.comment == 'Wanna trade?'
    assert proposal.status == 'pending'