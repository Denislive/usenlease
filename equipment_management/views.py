from django.shortcuts import render, get_object_or_404


def home(request):
    return render(request, 'equipment_management/index.html')

def about_us(request):
    return render(request, 'equipment_management/about_us.html')

def services(request):
    return render(request, 'equipment_management/services.html')

def equipment_list(request):
    # equipments = Equipment.objects.all()
    return render(request, 'equipment_management/equipment_list.html')

def equipment_detail(request, pk):
    # equipment = get_object_or_404(Equipment, pk=pk)
    return render(request, 'equipment_management/equipment_detail.html')

def contact_us(request):
    return render(request, 'equipment_management/contact_us.html')
