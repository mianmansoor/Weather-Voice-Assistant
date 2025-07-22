import csv

cities = [
    "lahore", "karachi", "islamabad", "multan", "peshawar",
    "quetta", "faisalabad", "sialkot", "rawalpindi", "hyderabad",
    "gujranwala", "bahawalpur", "sargodha", "mirpur", "dera ghazi khan",
    "mardan", "abbottabad", "rahim yar khan", "sukkur", "larkana"
]

# Today weather templates
today_weather_templates = [
    "what's the weather in {city}?",
    "tell me the weather in {city}",
    "current weather in {city}",
    "{city} ka mausam kesa hai?",
    "{city} ka mausam batao",
    "is it raining in {city}?",
    "is it sunny in {city}?",
    "cloudy hai {city} mein?",
    "{city} mein barish ho rahi hai?",
    "{city} mein garmi hai?",
    "{city} ka temp batao",
    "{city} ka temperature kya hai?",
    "temperature in {city}",
    "weather report for {city}",
    "kya {city} mein barish hai?",
    "how hot is it in {city}?",
    "how cold is it in {city}?",
    "can you check weather for {city}?",
    "today's forecast for {city}"
]

# Tomorrow weather templates
tomorrow_weather_templates = [
    "kal {city} mein weather kaisa hoga?",
    "tomorrow's weather in {city}",
    "kal ka mausam {city} mein",
    "will it rain tomorrow in {city}?",
    "will it be hot in {city} tomorrow?",
    "kal {city} mein barish hogi?",
    "kal {city} ka temp kya hoga?",
    "kal {city} mein dhoop hogi?",
    "forecast for {city} tomorrow",
    "is {city} going to be cold tomorrow?"
]

precaution_templates = [
    "precautionary measures for {city}",
    "{city} mein kya ehtiyaat honi chahiye?",
    "{city} ke liye precautions?",
    "safety tips for {city}",
    "kya {city} mein mask pehnna chahiye?",
    "{city} ke mausam ke liye kya prepare karna chahiye?",
    "{city} mein flood ka risk hai?",
    "should I carry an umbrella in {city}?",
    "do I need sunscreen in {city}?",
    "can I go outside in {city} safely?",
    "{city} mein garmi se bachne ke tareeqe?",
    "{city} mein barish se bachne ke liye kya karun?"
]

unknowns = [
    "hello",
    "kaisa lag raha hai",
    "ap ka naam kya hai",
    "i like biryani",
    "acha acha",
    "tum kon ho",
    "kya hal hai",
    "ap kya karte ho",
    "khana khaya?",
    "who is your creator",
    "do you know cricket?",
    "i love rainy days",
    "mera mood kharab hai",
    "chai pilao",
    "let's go outside",
    "i am sad"
]

data = []

# Weather: today
for city in cities:
    for template in today_weather_templates:
        sentence = template.format(city=city)
        data.append((sentence, "get_weather"))

# Weather: tomorrow
for city in cities:
    for template in tomorrow_weather_templates:
        sentence = template.format(city=city)
        data.append((sentence, "get_weather"))

# Precautions
for city in cities:
    for template in precaution_templates:
        sentence = template.format(city=city)
        data.append((sentence, "precaution_request"))

# Unknown
for sentence in unknowns:
    data.append((sentence, "unknown"))

# Save
with open("weather_chatbot_data.csv", "w", newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["sentence", "intent"])
    writer.writerows(data)

print(f"✅ Dataset saved with {len(data)} rows (only sentence + intent).")
