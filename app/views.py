from django.shortcuts import render
from django.http import JsonResponse
import json
import plotly.express as px
import re
from .api import client,weather_api_key
import requests
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Product, Farmer,Message  
from .forms import ProductForm
from django.contrib import messages
from .forms import FarmerRegistrationForm
from django.utils.timezone import now
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from .forms import UserRegistrationForm, FarmerRegistrationForm, ProductForm
from django.shortcuts import render
import datetime
def generate_response(user_message):
    farming_context = (
        "You are an AI assistant designed to provide information and assistance specifically for farmers. "
        "Please respond with detailed government schemes and loan information for farmers, including name, "
        "description, eligibility, reference (URL), and date."
    )

    try:
        completion = client.chat.completions.create(
            model="llama3-groq-70b-8192-tool-use-preview",
            messages=[
                {"role": "system", "content": farming_context},
                {"role": "user", "content": user_message}
            ],
            temperature=0.5,
            max_tokens=1024,
            top_p=0.65,
            stream=False,
        )

        if completion.choices:
            return completion.choices[0].message.content
        else:
            return "No response generated."

    except Exception as e:
        print(f"Error generating response: {e}")
        return "Error generating response."
def parse_schemes(response):
    schemes = []
    lines = response.split('\n')  

    for line in lines:
        if line.strip():  
            parts = line.split(':', 1)
            if len(parts) == 2:
                name_and_info = parts[0].strip()
                description = parts[1].strip()
                
                
                eligibility = "Eligibility not provided"  
                reference = "http://example.com"  
                date = datetime.now().strftime('%Y-%m-%d')  
                
                schemes.append({
                    "name": name_and_info,
                    "description": description,
                    "eligibility": eligibility,
                    "reference": reference,
                    "date": date,
                })

   
    schemes.sort(key=lambda x: x['date'], reverse=True)
    return schemes

@login_required
def fetch_and_display_schemes(request):
    user_message = "Provide government schemes and loans for farmers."
    response = generate_response(user_message)
    schemes = parse_schemes(response)
    return render(request, 'schemes.html', {'schemes': schemes})

@login_required
def chat_page(request):
    if not request.user.is_authenticated:
        return redirect('login') 
    messages = Message.objects.select_related('farmer').all()  
    return render(request, 'chat/room.html', {'messages': messages})

@csrf_exempt
def save_message(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message_content = data['message']
            farmer = request.user.farmer  

            
            Message.objects.create(farmer=farmer, content=message_content)

            return JsonResponse({'status': 'success'}, status=200)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def home(request):
    return render(request, 'home.html')

def farmproduct(request):
    products = Product.objects.filter(expiry_date__gte=now().date())
    
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        
    else:
        form = ProductForm()

    return render(request, 'product.html', {'products': products, 'form': form})
from .forms import UserRegistrationForm, FarmerRegistrationForm

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        farmer_form = FarmerRegistrationForm(request.POST)  

        if user_form.is_valid() and farmer_form.is_valid():
           
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password']) 
            user.save()

          
            farmer = farmer_form.save(commit=False)
            farmer.user = user
            farmer.save()

            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
        else:
           
            print("User form errors:", user_form.errors)
            print("Farmer form errors:", farmer_form.errors)
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserRegistrationForm()
        farmer_form = FarmerRegistrationForm()

    return render(request, 'users/register.html', {
        'user_form': user_form,
        'farmer_form': farmer_form
    })

def login_view(request):
    """Login view for users."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')  
    
    return render(request, 'users/login.html')
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product
from .forms import ProductForm
from django.contrib.auth.decorators import login_required
import pandas as pd
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Farmer, Product
from .forms import ProductForm  

@login_required
def farmer_dashboard(request):
    farmer = get_object_or_404(Farmer, user=request.user)
    products = Product.objects.filter(farmer=farmer)

    # Prepare data for visualization
    product_data = {
        'name': [],
        'quantity': [],
        'quality': [],
    }

    for product in products:
        product_data['name'].append(product.name)
        product_data['quantity'].append(product.quantity)
        product_data['quality'].append(product.quality)

    df = pd.DataFrame(product_data)

    # Create visualizations
    # Pie chart for product quality distribution
    quality_distribution = df['quality'].value_counts()
    fig_quality = px.pie(quality_distribution, values=quality_distribution.values,
                          names=quality_distribution.index, title='Product Quality Distribution',
                          color_discrete_sequence=px.colors.sequential.Viridis)

    # Bar chart for product quantities
    fig_quantity = px.bar(df, x='name', y='quantity', title='Product Quantities',
                          labels={'name': 'Product Name', 'quantity': 'Quantity'},
                          color='quantity', color_continuous_scale=px.colors.sequential.Viridis)

    # Convert figures to HTML for rendering
    quality_chart = fig_quality.to_html(full_html=False)
    quantity_chart = fig_quantity.to_html(full_html=False)

    if request.method == 'POST':
        # Handle adding a product
        if 'add_product' in request.POST:
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                product = form.save(commit=False)
                product.farmer = farmer  # Associate the product with the Farmer instance
                product.save()
                messages.success(request, 'Product added successfully!')
                return redirect('dashboard')

        # Handle updating a product
        elif 'update_product' in request.POST:
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id)
            form = ProductForm(request.POST, request.FILES, instance=product)
            if form.is_valid():
                form.save()
                messages.success(request, 'Product updated successfully!')
                return redirect('dashboard')

        # Handle deleting a product
        elif 'delete_product' in request.POST:
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id)
            product.delete()
            messages.success(request, 'Product deleted successfully!')
            return redirect('dashboard')

    else:
        form = ProductForm()

    return render(request, 'dashboard.html', {
        'form': form,
        'products': products,
        'quality_chart': quality_chart,
        'quantity_chart': quantity_chart,
    })

from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.views.generic import TemplateView


class CustomLogoutView(LogoutView):
    # Redirect to thank you page after logout
    next_page = reverse_lazy('logout_thank_you')  # This should match the URL name of the thank you page

class LogoutThankYouView(TemplateView):
    template_name = 'logout_thank_you.html' 

# chatbot purpose ----------------------------------------------------------------


def generate_response(user_message):
    """Interact with Groq API and generate a response focused on farming."""
    farming_context = (
        "You are an AI assistant designed to provide information and assistance specifically for farmers. "
        "Please respond with advice, tips, and information related to agriculture, crop management, "
        "livestock care, sustainability, and related topics."
    )

    
    completion = client.chat.completions.create(
        model="llama3-groq-70b-8192-tool-use-preview",
        messages=[
            {"role": "system", "content": farming_context},  # Provide context to the AI
            {"role": "user", "content": user_message}
        ],
        temperature=0.5,
        max_tokens=1024,
        top_p=0.65,
        stream=False,  # Disable streaming for backend response handling
    )

    # Correctly access the content from the message
    return completion.choices[0].message.content if completion.choices else "No response generated."

def chatbot(request):
    return render(request, "chatbot.html")

# endhere chatbot -----------------------------------------------------------------------------------------

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt 
def chat_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Load JSON data
            user_message = data.get('message')  # Get the user's message
            
            if user_message:
                response = generate_response(user_message)  # Your function to generate a response
                return JsonResponse({'response': response})
            else:
                return JsonResponse({'error': 'No message provided'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
from django.conf import settings

# Load location data from JSON file
json_file_path = os.path.join(settings.BASE_DIR, 'app', 'locations.json')
with open(json_file_path) as f:
    data = json.load(f)
from django.http import JsonResponse

@csrf_exempt
def get_suggestions(request):
    if request.method == "GET":
        query = request.GET.get('query', '').strip()
        state = request.GET.get('state', '').strip()
        district = request.GET.get('district', '').strip()

        states = []
        districts = []
        cities = []

        # Iterate over location details
        for location in data["location_details"]:
            # Get states
            if not state and location["State"].lower().startswith(query.lower()):
                if location["State"] not in states:
                    states.append(location["State"])
            # Get districts
            if state and location["State"].lower() == state.lower():
                if location["District"] not in districts:
                    districts.append(location["District"])
            # Get cities
            if district and location["District"].lower() == district.lower():
                if location["City"] not in cities:
                    cities.append(location["City"])

        response_data = {
            "states": states,
            "districts": districts,
            "cities": cities,
        }

        return JsonResponse(response_data)

    return JsonResponse({'error': 'Invalid request'}, status=400)


from datetime import datetime

def parse_crop_response(crop_response):
    """Convert the API response string into a list of crop dictionaries."""
    crops = []
    
    # Split the response into lines and process each line
    lines = crop_response.strip().split('\n')
    current_crop = {}
    
    for line in lines:
        # Check if the line starts with a number, indicating a new crop
        if re.match(r'^\d+\.\s', line):  # Matches "1. ", "2. ", etc.
            if current_crop:  # If current_crop is not empty, save it
                crops.append(current_crop)
                current_crop = {}  # Reset for the next crop
            
            # Extract the crop name (everything before the colon)
            current_crop['name'] = line.split(':')[0][2:].strip()  # Skip "1. " or "2. "
        
        # Extract cost, profit margin, and guide
        elif 'Cost:' in line:
            current_crop['cost'] = line.split(':')[1].strip()
        elif 'Profit Margin:' in line:
            current_crop['profit_margin'] = line.split(':')[1].strip()
        elif 'Guide:' in line:
            current_crop['guide'] = line.split(':')[1].strip()
    
    # Don't forget to append the last crop if exists
    if current_crop:
        crops.append(current_crop)
    
    return crops

def get_crop_recommendations(farmer):
    today = datetime.now().strftime('%Y-%m-%d')
    query = f"""
    Provide the top 10 crops suitable for {farmer.city}, {farmer.district}, {farmer.state} 
    on {today}. Consider these interests: {farmer.interests}. Include each crop's cost, 
    profit margin, and a brief guide on how to grow it.
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama3-groq-70b-8192-tool-use-preview",
            messages=[
                {"role": "user", "content": query}
            ],
            temperature=0.5,
            max_tokens=1024,
            top_p=0.65,
            stream=False,
        )
        
        api_response = completion.choices[0].message.content if completion.choices else None

        # Ensure we have a valid response before parsing
        if api_response:
            # Parse the response string to a structured list
            crops_data = parse_crop_response(api_response)
            return crops_data
        else:
            return {"error": "No response from API"}

    except Exception as e:
        return {"error": "Unable to fetch recommendations"}

@login_required
def crop_recommendation_view(request):
    try:
        farmer = Farmer.objects.get(user=request.user)
    except Farmer.DoesNotExist:
        return redirect('home') 

    crops = get_crop_recommendations(farmer)

    if isinstance(crops, dict) and "error" in crops:
        return render(request, 'crop_recommendations.html', {'farmer': farmer, 'crops': [], 'error': crops['error']})
    return render(request, 'crop_recommendations.html', {'farmer': farmer, 'crops': crops})

# Wheather with district details
from datetime import datetime

def get_coordinates(city_name):
    """Fetch latitude and longitude for a given city name."""
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={weather_api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data:
            return data[0]["lat"], data[0]["lon"]
        else:
            print(f"No coordinates found for city: {city_name}")
            return None, None
    except Exception as e:
        print(f"Error fetching coordinates: {e}")
        return None, None

def get_7day_forecast(city_name):
    """Fetch the 7-day weather forecast for a given city."""
    lat, lon = get_coordinates(city_name)
    
    if lat is None or lon is None:
        return []

    url = f"http://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=current,minutely,hourly&appid={weather_api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        forecast_data = response.json()
        
        daily_forecasts = forecast_data.get("daily", [])
        forecasts = []

        # Parse forecast data
        for day in daily_forecasts:
            # Ensure correct use of datetime
            dt = datetime.utcfromtimestamp(day["dt"]).strftime('%Y-%m-%d')
            temp_day = round(day["temp"]["day"] - 273.15, 2)  # Convert Kelvin to Celsius
            weather_desc = day["weather"][0]["description"]
            forecasts.append({'date': dt, 'temperature': temp_day, 'condition': weather_desc})

        return forecasts

    except Exception as e:
        print(f"Error fetching forecast: {e}")
        return []

def get_city_details_from_llama(city_name):
    """Generate detailed information about the city using the Llama API."""
    try:
        prompt = f"Tell me interesting facts and details about the city of {city_name} in India."

        # Ensure you are calling the client API correctly.
        response = client.chat.completions.create(
            model="llama3-groq-70b-8192-tool-use-preview",
            messages=[
                {"role": "system", "content": "You are an assistant providing information about cities in India."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=500,
            top_p=0.9
        )

        # Extract the response content properly
        city_details = response.choices[0].message.content.strip() if response.choices else "No details available at the moment."
        return city_details

    except Exception as e:
        print(f"Error fetching city details from Llama: {e}")
        return "No details available at the moment."

@login_required
def weather_view(request):
    """View to display weather and city details based on the farmer's city."""
    try:
        farmer = Farmer.objects.get(user=request.user)  # Get farmer's data
        city_name = farmer.city  # Use the farmer's city

        # Fetch weather and city details
        weather_data = get_7day_forecast(city_name)
        city_description = get_city_details_from_llama(city_name)  # Call Llama API for city insights

        context = {
    'farmer': farmer,
    'city_name': city_name,
    'weather_data': weather_data,  # Ensure this has valid data
    'city_description': city_description,  # Ensure this is not None
        }

        return render(request, 'weather.html', context)
    except Farmer.DoesNotExist:
        return redirect('login')  
    
def calculate_prediction(form_data):
    # Example logic for prediction (replace this with your actual logic)
    try:
        # Extract input values
        loan_irregular = int(form_data.get('loan_irregular', 0))
        loan_missed = int(form_data.get('loan_missed', 0))
        crop_reduced = int(form_data.get('crop_reduced', 0))
        weather_low = int(form_data.get('weather_low', 0))

        # Simplified prediction logic (replace this with your model's logic)
        risk_score = loan_irregular + loan_missed + crop_reduced + weather_low

        # Return a prediction based on the risk score
        if risk_score >= 6:
            return 3  # High risk
        elif risk_score >= 3:
            return 2  # Medium risk
        else:
            return 1  # Low risk
    except ValueError:
        return None  # Handle invalid inputs gracefully

def analyze_risk(request):
    if request.method == 'POST':
        prediction = calculate_prediction(request.POST)
        input_descriptions = {
            "loan_irregular": "Details about loan repayment status.",
            "loan_missed": "Details about missed loan payments.",
            "crop_reduced": "Details about crop purchases.",
            "weather_low": "Details about weather impacts."
        }
        advice = [
            "Financial Counseling: Seek professional advice to manage debts and repayment schedules.",
            "Community Support: Engage with local support groups or agricultural cooperatives."
        ]
        
        return render(request, 'analyze.html', {
            'prediction': prediction,
            'input_descriptions': input_descriptions,
            'advice': advice,
        })
    else:
        return render(request, 'analyze.html', {})