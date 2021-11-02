from django.shortcuts import render
import psycopg2

#Establish connection
conn = psycopg2.connect(
        database = "sidcDB",
        user= "sidcdbuser",
        password = "sidcdb123",
        host = "localhost",
        port = "5432"
)

#Setting auto commit false
conn.autocommit = True

#Creating a cursor object using the cursor() method
cursor = conn.cursor()

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
    farmer_code = request.POST.get('input-code')
    raiser_name = request.POST.get('input-name')
    farmer_contact = request.POST.get('input-contact')
    # directly_manage = request.POST.get('cb-directly')

    farmer_address = request.POST.get('input-address')
    # area
    roof_height = request.POST.get('input-roof')
    warehouse_length = request.POST.get('wh-length')
    warehouse_width = request.POST.get('wh-width')
    # feeding trough
    bldg_cap = request.POST.get('input-roof')

    # pig pens
    # biosec

    print("NEW FARM CODE: " + farmer_code)
    # print(directly_manage)

    # Transform address to longitude and latitude values

    # Insert farm record to db
    cursor.execute("""INSERT INTO farmsapp_farm(farmer_code, raiser_uname, farmer_contact)
                      VALUES ('911', 'Jack', '0917824')""")
   
    conn.commit()
    print("-- NEW FARM ADDED TO DB --")

    # Closing the connection
    conn.close()
    return render(request, 'farmstemp/farms.html', {}) 

