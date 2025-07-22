import datetime
import calendar
import requests  # Don't forget to keep this for API calls

# Context to remember previous input
context = {
    "name": None,
    "city": None,
    "forecast_date": None,
    "last_intent": None
}

weekday_map = {
    "monday": 0, "tuesday": 1, "wednesday": 2,
    "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6
}

def extract_weekday_date(user_input):
    user_input = user_input.lower()
    today = datetime.date.today()
    for day_name, day_index in weekday_map.items():
        if day_name in user_input:
            days_ahead = (day_index - today.weekday() + 7) % 7
            if days_ahead == 0:
                days_ahead = 7  # assume next Monday if today is Monday
            forecast_date = today + datetime.timedelta(days=days_ahead)
            return forecast_date.strftime('%Y-%m-%d')
    return None

def get_forecast_date(user_input):
    user_input = user_input.lower()
    if "today" in user_input:
        return datetime.date.today().strftime('%Y-%m-%d')
    elif "tomorrow" in user_input:
        return (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    weekday_date = extract_weekday_date(user_input)
    if weekday_date:
        return weekday_date
    return None

def get_weather_data(city):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}"
    geo_res = requests.get(url).json()
    if "results" not in geo_res:
        return None, None
    lat = geo_res["results"][0]["latitude"]
    lon = geo_res["results"][0]["longitude"]

    weather_url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode&timezone=auto"
    )
    weather_res = requests.get(weather_url).json()
    return weather_res, geo_res["results"][0]["name"]

def interpret_weather_code(code):
    descriptions = {
        0: "Aaj aasman bilkul saaf hai.",
        1: "Halka baadal hai.",
        2: "Thoda zyada baadal hai.",
        3: "Poori tarah baadal chhaye hue hain.",
        45: " Halka kohra ya dhund hai.",
        48: " Gaari dhund hai.",
        51: " Halki halki boonden gir rahi hain.",
        53: " Darmiyani boonden gir rahi hain.",
        55: " Zyada boonden gir rahi hain.",
        56: " Halki baraf ke sath barish.",
        57: " Tez baraf ke sath barish.",
        61: " Halka baarish ho rahi hai.",
        63: " Darmiyani baarish ho rahi hai.",
        65: " Zor daar baarish ho rahi hai.",
        66: " Halki baraf wali baarish ho rahi hai.",
        67: " Zyada baraf wali baarish ho rahi hai.",
        71: " Halki baraf gir rahi hai.",
        73: " Darmiyani baraf gir rahi hai.",
        75: " Tez baraf gir rahi hai.",
        77: " Barf ke chhote tukde gir rahe hain.",
        80: " Thodi thodi baarish ho rahi hai.",
        81: " Darmiyani baarish ho rahi hai.",
        82: " Zyada tez baarish ho rahi hai.",
        85: " Baraf ke sath halki baarish ho rahi hai.",
        86: " Baraf ke sath tez baarish ho rahi hai.",
        95: " Aandhi tufan ke saath bijli chamak rahi hai.",
        96: " Halki bijli ke saath aandhi tufan.",
        99: "Tez bijli ke sath zyada aandhi tufan.",
    }
    return descriptions.get(code, "Mosam ka code samajh nahi aaya.")


def get_weather_response(city, forecast_date):
    weather_data, proper_city = get_weather_data(city)
    if not weather_data:
        return f"Weather info not found for {city}."

    dates = weather_data["daily"]["time"]
    if forecast_date not in dates:
        return f"{proper_city} ke liye {forecast_date} ka forecast mojood nahi."

    idx = dates.index(forecast_date)
    temp = weather_data["daily"]["temperature_2m_max"][idx]
    code = weather_data["daily"]["weathercode"][idx]
    day_name = calendar.day_name[datetime.datetime.strptime(forecast_date, "%Y-%m-%d").weekday()]

    urdu_day = {
        "Monday": "Pehla din (Monday)", "Tuesday": "Doosra din (Tuesday)",
        "Wednesday": "Teesra din (Wednesday)", "Thursday": "Chautha din (Thursday)",
        "Friday": "Paanchwa din (Friday)", "Saturday": "Chhata din (Saturday)",
        "Sunday": "Aakhri din (Sunday)"
    }.get(day_name, day_name)

    desc = interpret_weather_code(code)

    # Personalized name greeting if available
    name_prefix = f"{context['name']}, " if context.get("name") else ""
    return f"{name_prefix}{proper_city} ka {urdu_day} ka mosam: temperature: {temp}°C\n{desc}"

def get_precaution_message(code):
    precaution_messages = {
        0: "Aasman saaf hai, lekin dhoop mein zyada dair na rahain. Sunscreen lagayein aur hydrated rahain.",
        1: "Halka baadal hai. Ghar se nikalne se pehle dhup aur baadal dono ka khayal rakhein.",
        2: "Thoda zyada baadal hai. Ghar se nikalte waqt chhata lein toh behtar hoga.",
        3: "Poori tarah baadal chhaye hain. Baarish ka imkaan ho sakta hai, chhata le jana behtar hai.",
        45: "Halka kohra hai. Drive karte waqt fog lights ka istemal karein aur dheemi raftaar mein chalayen.",
        48: "Ghaani dhund hai. Nazr kam ho sakti hai, sirf zarurat padne par hi safar karein.",
        51: "Halki halki boonden gir rahi hain. Chhata ya waterproof jacket saath lein.",
        53: "Darmiyani barish ho rahi hai. Ghar se nikalte waqt proper raincoat aur chhata lein.",
        55: "Zyada barish ho rahi hai. Bheegne se bachne ke liye boots aur rainwear zaroori hai.",
        56: "Halki barish aur baraf dono. Sard mosam mein garam kapray aur waterproof cheezein pehn kar niklein.",
        57: "Tez barish ke sath baraf. Ghar se na nikalna behtar hai, roads slippery ho sakti hain.",
        61: "Halki baarish. Chhata zaroor lein aur bheegne se bachne ki koshish karein.",
        63: "Darmiyani baarish. Naazuk saman cover karein, aur pani jam hone se bachayein.",
        65: "Zor daar baarish ho rahi hai. Bahar na nikalna behtar hai, bijli girne ka imkaan bhi ho sakta hai.",
        66: "Halki baraf wali baarish. Sard hawa se bachne ke liye garam aur waterproof layering zaroori hai.",
        67: "Zyada baraf wali baarish. Slippery roads aur visibility ka masla ho sakta hai, ghar mein rahna behtar hai.",
        71: "Halki baraf gir rahi hai. Garam kapray aur gloves pehn kar niklein.",
        73: "Darmiyani baraf. Sard mosam se bachne ke liye layering aur boots pehnna zaroori hai.",
        75: "Tez baraf gir rahi hai. Roads block ya frozen ho sakti hain, zarurat ke ilawa bahar na niklein.",
        77: "Barf ke tukde gir rahe hain. Sar par kuch pehn kar niklein, aur barf se bachne ki koshish karein.",
        80: "Thodi thodi baarish ho rahi hai. Chhata saath lein, takay achanak bheeg na jayein.",
        81: "Darmiyani baarish. Safety ke liye non-slip shoes aur chhata zaroori hai.",
        82: "Zyada tez baarish. Flooding aur bijli ka khatra ho sakta hai, travel avoid karein.",
        85: "Baraf ke sath halki baarish. Slippery surface se bachne ke liye grip wale jootay zaroori hain.",
        86: "Baraf ke sath tez baarish. Emergency ke siwa bahar na niklein.",
        95: "Aandhi tufan aur bijli chamak rahi hai. Bijli ke poles aur darakhton se door rahain.",
        96: "Halki bijli ke sath tufan. Secure jagah par rahain aur electronics unplug kar dein.",
        99: "Tez bijli aur zyada aandhi tufan. Bahar jana khatarnaak ho sakta hai, emergency alerts ka khayal rakhein."
    }

    return precaution_messages.get(code, "Is mosam ke liye koi khaas ehtiyaat nahi batayi ja sakti.")


def get_precaution_response(city, forecast_date):
    weather_data, proper_city = get_weather_data(city)
    if not weather_data:
        return f"{city} ka mosam nahi mil saka, is wajah se ehtiyaati tadabeer nahi dein sakta."

    dates = weather_data["daily"]["time"]
    if forecast_date not in dates:
        return f"{proper_city} ke liye {forecast_date} ka forecast mojood nahi."

    idx = dates.index(forecast_date)
    code = weather_data["daily"]["weathercode"][idx]

    precaution = get_precaution_message(code)

    # Personalized name prefix if available
    name_prefix = f"{context.get('name')}, " if context.get("name") else ""
    return f"{name_prefix}{precaution}"


def extract_name(user_input):
    keywords = ["my name is", "mera naam", "i am", "i'm", "mai", "main"]
    for key in keywords:
        if key in user_input:
            words = user_input.split()
            for i, word in enumerate(words):
                if word in ["is", "naam", "am", "i’m", "i'm"]:
                    if i + 1 < len(words):
                        return words[i + 1].capitalize()
    return None

def handle_input(user_input):
    user_input = user_input.lower()

    if user_input in ["exit", "quit"]:
        return "exit"

    # Extract name if provided
    name = extract_name(user_input)
    if name:
        context["name"] = name
        return f"Shukriya {name}, aapka naam yaad rakh liya gaya hai."

    # Extract city (update if mentioned)
    cities = ["lahore", "karachi", "islamabad", "multan", "peshawar", "faisalabad", "quetta"]
    for city in cities:
        if city in user_input:
            context["city"] = city
            break

    # Extract forecast date (update if mentioned)
    forecast_date = get_forecast_date(user_input)
    if forecast_date:
        context["forecast_date"] = forecast_date

    # Detect intent
    if "precaution" in user_input or "measures" in user_input or "ehtiyaati" in user_input:
        context["last_intent"] = "precaution"
    elif "weather" in user_input or "mosam" in user_input:
        context["last_intent"] = "weather"

    name_prefix = f"{context['name']}, " if context["name"] else ""

    # Execute intent based on context completeness
    if context["last_intent"] == "weather":
        if not context["city"]:
            return f"{name_prefix}Mujhe sheher ka naam nahi mila. Kya aap city bata sakte hain?"
        if not context["forecast_date"]:
            return f"{name_prefix}Aapko aaj ka mosam chahiye ya kisi aur din ka?"
        return get_weather_response(context["city"], context["forecast_date"])

    elif context["last_intent"] == "precaution":
        if not context["city"]:
            return f"{name_prefix}Pehle mujhe sheher ka naam batayein jiska mosam maloom karna hai."
        if not context["forecast_date"]:
            return f"{name_prefix}Pehle mujhe din batayein jiska mosam maloom karna hai."
        return get_precaution_response(context["city"], context["forecast_date"])

    return f"{name_prefix}Maaf kijiye, mujhe samajh nahi aaya. Aap mosam ya ehtiyaati tadabeer se related sawal pooch sakte hain."

