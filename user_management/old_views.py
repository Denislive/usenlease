from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import User, CreditCard, Address, UserProfile
from django.http import HttpResponse
from .forms import CreditCardUpdateForm,PhysicalAddressForm, AddressForm, UserForm
from equipment_management.forms import EquipmentForm
from django.contrib.auth.decorators import login_required



def user_register(request):
    if request.method == 'POST':
        # Extract form data
        username = request.POST.get('full_name')  # Assuming full_name maps to username
        phone_number = request.POST.get('phone')
        role = request.POST.get('role')
        id_upload = request.FILES.get('id_upload')
        physical_address = request.POST.get('physical_address')
        proof_of_address = request.FILES.get('proof_address')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        business_name = request.POST.get('business_name', '')
        business_license = request.FILES.get('business_license')
        income_verification = request.FILES.get('income_verification')
        terms = request.POST.get('terms')

        print(request.POST)

        
        # Basic validations
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'user_management/register.html')

        if not terms:
            messages.error(request, 'You must agree to the terms and conditions.')
            return render(request, 'user_management/register.html')
        
        # Create a new user instance
        user = User(
            username=username,
            phone_number=phone_number,
            role=role,
            id_upload=id_upload,
            physical_address=physical_address,
            proof_of_address=proof_of_address,
            business_name=business_name,
            business_license=business_license,
            income_verification=income_verification
        )

        # Save the user
        try:
            user.set_password(password)
            user.full_clean()  # Will raise validation errors if any
            user.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('index')  # Redirect to a home page or another page
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'user_management/register.html')


def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(request.POST)
        
        # Authenticate user
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('index')  # Redirect to a different page after login
        else:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'user_management/login.html')



@login_required
def profile(request):
    user = request.user
    physical_address = Address.objects.filter(user=user, address_type='physical', is_default=True).first()
    billing_address = Address.objects.filter(user=user, address_type='billing', is_default=True).first()
    shipping_address = Address.objects.filter(user=user, address_type='shipping', is_default=True).first()
    payment_info = CreditCard.objects.filter(user=user, is_default=True).first()
    
    physical_address_form = PhysicalAddressForm(instance=physical_address)
    address_form = AddressForm(instance=AddressForm)
    equipment_form = EquipmentForm(instance=EquipmentForm)

    context = {
        'user': user,
        'physical_address': physical_address,
        'billing_address': billing_address,
        'shipping_address': shipping_address,
        'payment_info': payment_info,

        'equipment_form': equipment_form,
        'physical_address_form': physical_address_form,
        'address_form': address_form,
    }
    
    return render(request, 'user_management/profile.html', context)


def create_physical_address(request):
    user = request.user
    if request.method == 'POST':
        physical_address_form = PhysicalAddressForm(request.POST)
        if physical_address_form.is_valid():
            address = physical_address_form.save(commit=False)
            address.user = user
            address.address_type = 'physical'
            address.save()


            # Handle checkboxes for billing and shipping address
            same_for_billing = request.POST.get('same_for_billing', False)
            same_for_shipping = request.POST.get('same_for_shipping', False)

            if same_for_billing:
                # Update or create a billing address
                Address.objects.update_or_create(
                    user=request.user,
                    address_type='billing',
                    defaults={
                        'full_name': address.full_name,
                        'street_address': address.street_address,
                        'address_line_2': address.address_line_2,
                        'city': address.city,
                        'state': address.state,
                        'zip_code': address.zip_code,
                        'country': address.country,
                        'is_default': address.is_default,
                    }
                )

            if same_for_shipping:
                # Update or create a shipping address
                Address.objects.update_or_create(
                    user=request.user,
                    address_type='shipping',
                    defaults={
                        'full_name': address.full_name,
                        'street_address': address.street_address,
                        'address_line_2': address.address_line_2,
                        'city': address.city,
                        'state': address.state,
                        'zip_code': address.zip_code,
                        'country': address.country,
                        'is_default': address.is_default,
                    }
                )

            redirect('user:profile')  # Replace with the URL or view name you want to redirect to after successful form submission
        else:
            # Handle form errors
            errors = physical_address_form.errors.as_data()
            error_messages = []
            for field, field_errors in errors.items():
                for error in field_errors:
                    error_messages.append(f"{field}: {error.message}")

            return HttpResponse(f"Errors: <br> {'<br>'.join(error_messages)}", content_type="text/html")
    else:
        physical_address_form = PhysicalAddressForm()  # Pass the user to the form

    return redirect('user:profile')


def update_physical_address(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    address_instance = profile.location
    if request.method == 'POST':
        physical_address_form = PhysicalAddressForm(request.POST, instance=address_instance)
        if physical_address_form.is_valid():
            if 'is_default' in request.POST:
                address = physical_address_form.save(commit=False)
                address.user = request.user
                address.is_default = True
                address.address_type = 'physical'

            address.save()

            # Handle checkboxes for billing and shipping address
            same_for_billing = request.POST.get('same_for_billing', False)
            same_for_shipping = request.POST.get('same_for_shipping', False)

            if same_for_billing:
                # Update or create a billing address
                Address.objects.update_or_create(
                    user=request.user,
                    address_type='billing',
                    defaults={
                        'full_name': address.full_name,
                        'street_address': address.street_address,
                        'address_line_2': address.address_line_2,
                        'city': address.city,
                        'state': address.state,
                        'zip_code': address.zip_code,
                        'country': address.country,
                        'is_default': address.is_default,
                    }
                )

            if same_for_shipping:
                # Update or create a shipping address
                Address.objects.update_or_create(
                    user=request.user,
                    address_type='shipping',
                    defaults={
                        'full_name': address.full_name,
                        'street_address': address.street_address,
                        'address_line_2': address.address_line_2,
                        'city': address.city,
                        'state': address.state,
                        'zip_code': address.zip_code,
                        'country': address.country,
                        'is_default': address.is_default,
                    }
                )

            redirect('user:profile')  # Replace with the URL or view name you want to redirect to after successful form submission
        else:
            # Handle form errors
            errors = physical_address_form.errors.as_data()
            error_messages = []
            for field, field_errors in errors.items():
                for error in field_errors:
                    error_messages.append(f"{field}: {error.message}")

            return HttpResponse(f"Errors: <br> {'<br>'.join(error_messages)}", content_type="text/html")
    else:
        physical_address_form = PhysicalAddressForm(instance=address_instance)  # Pass the user to the form

    return render()



def create_address(request):
    if request.method == 'POST':
        address_form = AddressForm(request.POST)
        if address_form.is_valid():
            if 'is_default' in request.POST:
                address = address_form.save(commit=False)
                address.user = request.user
                address.address_type = request.POST.get('address_type')
                address.is_default = True
                address.save()
                print("Address Created")
    else:
        address_form = AddressForm()

    return redirect('user:profile')


@login_required
def update_address(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    address_instance = profile.location

    if request.method == 'POST':
        address_form = AddressForm(request.POST, instance=address_instance)

        if address_form.is_valid():
            address = address_form.save(commit=False)
            address.user = user  # Set the user field explicitly
            address.save()  # Save the address to get the primary key

            if address_form.cleaned_data.get('is_default'):
                profile.location = address

            profile.save()  # Save the user profile with updated location
            return redirect('user:index')  # Redirect to the profile page

    else:
        address_form = AddressForm(instance=address_instance)

    return redirect('user:profile')



def credit(request):
    if request.method == 'POST':
        form = CreditCardForm(request.POST, user=request.user)
        if form.is_valid():
            credit_card = form.save(commit=False)
            credit_card.user = request.user

            if credit_card.is_default:
                # If the new card is set as default, update the current default card (if any) to be non-default
                existing_default_card = CreditCard.objects.filter(user=request.user, is_default=True).exclude(pk=credit_card.pk).first()
                if existing_default_card:
                    existing_default_card.is_default = False
                    existing_default_card.save()

            # Save the new card (will be default if specified, or not default otherwise)
            credit_card.save()
            
            return redirect('index')  # Replace with the URL or view name you want to redirect to after successful form submission
        else:
            # Handle form errors
            errors = form.errors.as_data()
            error_messages = []
            for field, field_errors in errors.items():
                for error in field_errors:
                    error_messages.append(f"{field}: {error.message}")

            return HttpResponse(f"Errors: <br> {'<br>'.join(error_messages)}", content_type="text/html")
    else:
        form = CreditCardForm(user=request.user)

    return render(request, 'user_management/credit.html', {'form': form})



def user(request):
    if request.method == 'POST':
        print("POST Data:", request.POST)
        print("FILES Data:", request.FILES)
        
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            print("Form is valid")
            form.save()
            return redirect('index')
        else:
            print("Form Errors:", form.errors)
            errors = form.errors.as_data()
            error_messages = []
            for field, field_errors in errors.items():
                for error in field_errors:
                    error_messages.append(f"{field}: {error.message}")
            return render(request, 'user_management/user.html', {'form': form, 'errors': error_messages})
    else:
        form = UserForm()

    return render(request, 'user_management/user.html', {'form': form})







@login_required
def update_credit_card(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    credit_card_instance = profile.credit_card

    if request.method == 'POST':
        credit_card_form = CreditCardUpdateForm(request.POST, instance=credit_card_instance)

        if credit_card_form.is_valid():
            credit_card = credit_card_form.save(commit=False)
            credit_card.user = user  # Set the user field explicitly
            credit_card.save()  # Save the credit card to get the primary key

            if credit_card_form.cleaned_data.get('is_default'):
                profile.credit_card = credit_card

            profile.save()  # Save the user profile with updated credit card
            return redirect('user:profile')  # Redirect to the profile page

    else:
        credit_card_form = CreditCardUpdateForm(instance=credit_card_instance)

    # Always return an HttpResponse
    return render(request, 'user_management/profile.html', {
        'credit_card_form': credit_card_form,
    })









def create_or_update_physical_address_view(request):
    user = request.user

    # Check if the user already has a physical address
    if hasattr(user, 'physical_address') and user.physical_address:
        # If the user already has an address, use it to pre-fill the form
        instance = user.physical_address

    else:
        instance = None

    if request.method == 'POST':
        form = PhysicalAddressForm(request.POST, instance=instance)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            user.physical_address = address

            # Handle "Same as Billing Address"
            if form.cleaned_data['same_as_billing']:
                billing_address = user.billing_addresses.filter(is_default=True).first()
                if billing_address:
                    # Replace the existing default billing address with the new one
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

            # Handle "Same as Shipping Address"
            if form.cleaned_data['same_as_shipping']:
                shipping_address = user.shipping_addresses.filter(is_default=True).first()
                if shipping_address:
                    # Replace the existing default shipping address with the new one
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

            # Save the user instance to update the related address
            user.save()
            return redirect('success_url')  # Replace with your success URL

    else:
        form = PhysicalAddressForm(instance=instance)

    return render(request, 'user_management/create_physical_address.html', {'form': form})
