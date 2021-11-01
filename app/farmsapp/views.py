from django.shortcuts import render, redirect

# Farms Management Module Views

## Farms table for all users except Technicians
def farms(request):
    return render(request, 'farmstemp/farms.html', {})

## Add Farm Page
def addFarm(request):
    return render(request, 'farmstemp/add-farm.html', {})

## Save Farm Details
def saveFarm(request):
    # Collect all input
    code = request.POST.get('input-code')
    raiser_name = request.POST.get('input-name')
    farmer_contact = request.POST.get('input-contact')
    # directly_manage = request.POST.get('cb-directly')

    farmer_address = request.POST.get('input-address')
    # area
    roof_height = request.POST.get('input-roof')
    wh-warehouse_length = request.POST.get('wh-length')
    warehouse_width = request.POST.get('wh-width')
    # feeding trough
    bldg_cap = request.POST.get('input-roof')

    # pig pens
    # biosec


    print("NEW FARM CODE: " + code)
    # print(directly_manage)


    # Transform address to longitude and latitude values

    # Save to db

    return render(request, 'farmstemp/farms.html', {}) 

