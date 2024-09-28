from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserRegistrationForm, UserUpdateForm, PhysicalAddressForm, CreditCardForm, EmailAuthenticationForm, AddressForm
from equipment_management.forms import EquipmentForm
from .models import User, Address, PhysicalAddress, CreditCard
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.contrib import messages

def user_login_view(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)
                print(request.user.email)

                return redirect('user:profile')
            else:
                messages.error(request, 'Invalid email or password.')
        else:
            for field in form:
                if field.errors:
                    for error in field.errors:
                        messages.error(request, error)
    else:
        form = EmailAuthenticationForm()

    return render(request, 'user_management/user_login.html', {'form': form})



def user_logout(request):
    logout(request)  # Log the user out
    return redirect('user:login')



def create_user_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('user:login')  # Replace with your success URL
    else:
        form = UserRegistrationForm()
    return render(request, 'user_management/create_user.html', {'form': form})


@login_required
def update_user_view(request, pk):
    user = User.objects.get(pk=pk)
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user:profile')  # Replace with your success URL
    else:
        form = UserUpdateForm(instance=user)
    return render(request, 'user_management/update_user.html', {'form': form})


@login_required
def create_address_view(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = request.user
            form.save()
            return redirect('user:profile')  # Replace with your success URL
    else:
        form = AddressForm()
    return render(request, 'user_management/create_address.html', {'form': form})


@login_required
def update_address_view(request, pk):
    address = Address.objects.get(pk=pk)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect('user:profile')  # Replace with your success URL
    else:
        form = AddressForm(instance=address)
    return render(request, 'user_management/update_address.html', {'form': form})


def sync_billing_address(user, address):
    billing_address = Address.objects.filter(address_type='B', is_default=True).first()
    if billing_address:
        # Update the existing default billing address
        billing_address.full_name = address.full_name
        billing_address.company_name = address.company_name
        billing_address.street_address = address.street_address
        billing_address.address_line_2 = address.address_line_2
        billing_address.city = address.city
        billing_address.state = address.state
        billing_address.zip_code = address.zip_code
        billing_address.country = address.country
        billing_address.is_default = True
        billing_address.save()
    else:
        # Create a new billing address and set it as default
        new_billing_address = Address.objects.create(
            user=user,
            full_name=address.full_name,
            company_name=address.company_name,
            street_address=address.street_address,
            address_line_2=address.address_line_2,
            city=address.city,
            state=address.state,
            zip_code=address.zip_code,
            country=address.country,
            address_type='billing',
            is_default=True
        )
        user.billing_addresses.add(new_billing_address)


def sync_shipping_address(user, address):
    shipping_address = Address.objects.filter(address_type='S', is_default=True).first()
    if shipping_address:
        # Update the existing default shipping address
        shipping_address.full_name = address.full_name
        shipping_address.company_name = address.company_name
        shipping_address.street_address = address.street_address
        shipping_address.address_line_2 = address.address_line_2
        shipping_address.city = address.city
        shipping_address.state = address.state
        shipping_address.zip_code = address.zip_code
        shipping_address.country = address.country
        shipping_address.is_default = True
        shipping_address.save()
    else:
        # Create a new shipping address and set it as default
        new_shipping_address = Address.objects.create(
            user=user,
            full_name=address.full_name,
            company_name=address.company_name,
            street_address=address.street_address,
            address_line_2=address.address_line_2,
            city=address.city,
            state=address.state,
            zip_code=address.zip_code,
            country=address.country,
            address_type='shipping',
            is_default=True
        )
        user.shipping_addresses.add(new_shipping_address)


@login_required
def create_physical_address_view(request):
    user = request.user

    if request.method == 'POST':
        form = PhysicalAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = user
            address.save()

            # Assign the new physical address to the user
            user.physical_address = address

            # Handle "Same as Billing Address"
            if form.cleaned_data.get('same_as_billing'):
                sync_billing_address(user, address)

            # Handle "Same as Shipping Address"
            if form.cleaned_data.get('same_as_shipping'):
                sync_shipping_address(user, address)

            user.save()
            return redirect('user:profile')  # Replace with your success URL
    else:
        form = PhysicalAddressForm()

    return render(request, 'user_management/create_physical_address.html', {'form': form})


@login_required
def update_physical_address_view(request):
    user = request.user
    
    instance = PhysicalAddress.objects.get(user=user)

    

    if request.method == 'POST':
        form = PhysicalAddressForm(request.POST, instance=instance)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = user
            address.save()

            # Handle "Same as Billing Address"
            if form.cleaned_data.get('same_as_billing'):
                sync_billing_address(user, address)

            # Handle "Same as Shipping Address"
            if form.cleaned_data.get('same_as_shipping'):
                sync_shipping_address(user, address)

            user.save()
            return redirect('user:profile')  # Replace with your success URL
    else:
        form = PhysicalAddressForm(instance=instance)

    return render(request, 'user_management/update_physical_address.html', {'form': form})


@login_required
def create_credit_card_view(request):
    user = request.user

    if request.method == 'POST':
        form = CreditCardForm(request.POST)
        if form.is_valid():
            credit_card = form.save(commit=False)
            credit_card.user = user

            # Check if the new credit card should be set as default
            if credit_card.is_default:
                # Set all existing credit cards of the user to non-default
                CreditCard.objects.filter(user=user).update(is_default=False)

            # Save the new credit card
            credit_card.save()

            return redirect('user:profile')  # Replace with your success URL

    else:
        form = CreditCardForm()

    return render(request, 'user_management/create_credit_card.html', {'form': form})



@login_required
def update_credit_card_view(request):
    credit_card = CreditCard.objects.filter(user=request.user, is_default=True)
    if request.method == 'POST':
        form = CreditCardForm(request.POST, instance=credit_card)
        if form.is_valid():
            updated_credit_card = form.save(commit=False)

            if updated_credit_card.is_default:
                # Set all other credit cards of the user to non-default
                CreditCard.objects.filter(user=credit_card.user).exclude(pk=credit_card.pk).update(is_default=False)

            updated_credit_card.save()
            return redirect('user:profile')  # Replace with your success URL

    else:
        form = CreditCardForm(instance=credit_card)

    return render(request, 'user_management/update_credit_card.html', {'form': form})


# View to delete an address
@login_required
def delete_address_view(request, pk):
    address = get_object_or_404(Address, pk=pk)
    if request.method == 'POST':
        address.delete()
        return redirect('user:profile')  # Replace with the actual name of the URL for the address list page

    return render(request, 'user_management/delete_address.html', {'object': address})

# View to delete a credit card
@login_required
def delete_credit_card_view(request, pk):
    credit_card = get_object_or_404(CreditCard, pk=pk)
    if request.method == 'POST':
        credit_card.delete()
        return redirect('user:profile')  # Replace with the actual name of the URL for the credit card list page

    return render(request, 'user_management/delete_credit_card.html', {'object': credit_card})



@login_required
def profile(request):
    user = request.user
    physical_address = PhysicalAddress.objects.filter(user=user, is_default=True).first()
    billing_address = Address.objects.filter(user=user, address_type='billing', is_default=True).first()
    shipping_address = Address.objects.filter(user=user, address_type='shipping', is_default=True).first()
    payment_info = CreditCard.objects.filter(user=user, is_default=True).first()

    context = {
        'user': user,
        'physical_address': physical_address,
        'billing_address': billing_address,
        'shipping_address': shipping_address,
        'payment_info': payment_info,
        'eform': EquipmentForm()

    }
    
    return render(request, 'user_management/profile.html', context)

