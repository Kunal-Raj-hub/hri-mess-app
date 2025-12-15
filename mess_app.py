import streamlit as st
import datetime
import re
import google.generativeai as genai
import os

# --- 1. SETUP & SECURITY ---

# Try to get the key from the Cloud Vault (Secrets)
# If running on laptop, it might use a placeholder or local environment
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    GOOGLE_API_KEY = "MISSING_KEY"

# Configure AI
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    AI_AVAILABLE = True
except:
    AI_AVAILABLE = False

# --- 2. TIMEZONE FIX (INDIA) ---
def get_india_time():
    """Returns the current time in India (UTC+5:30)"""
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    india_tz = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    return utc_now.astimezone(india_tz)

def get_week_number():
    today = get_india_time()
    return (today.day - 1) // 7 + 1

# --- 3. MENU DATA ---
menu_data = {
    "Monday": {
        "Breakfast": "Methi paratha, Ghugni (1st, 3rd) / Sattu Paratha (2nd, 4th), Chutney",
        "Lunch": "Rice, Roti, Moong dal, Dalma, Palak corn, Aloo-gobi, Jhuri aloo with peanuts, Tomato rice, Beetroot-gajar-muli salad, Fruits",
        "Tiffin": "Pav bhaji (1st, 3rd, 5th) / Dabeli (2nd & 4th)",
        "Dinner": "Sweet-pulao, Rice, Roti, Masoor Dal, Arhar Dal, Dum-Aloo, Mushroom-matar masala. [Extra: Handi paneer/ Paneer do pyaza]. Sweet: Malpua"
    },
    "Tuesday": {
        "Breakfast": "Besan chilla, chutney (1st, 3rd) / Kala-Channa, suji halwa (2nd, 4th)",
        "Lunch": "Rice, Roti, Masoor dal, Lobia dal, Aloo-lehsun, Gajar-Gobi-matar sabji, Curd rice, Sprouts salad, Fruits",
        "Tiffin": "Chicken roll, Paneer roll",
        "Dinner": "Makki-di roti, Rice, Roti, Masoor Dal, Arhar Dal, Sarson-da saag, Hara bhara aloo, Mix-veg soup. [Extra: Kadhai paneer]. Sweet: Sewai ki kheer"
    },
    "Wednesday": {
        "Breakfast": "Poha, Jalebi",
        "Lunch": "Rice, Roti, Sodhi dal, Masoor dal, Aloo-baingan chokha, Veg Korma, Lemon rice, Aloo chips, Peanut salad, Fruits",
        "Tiffin": "Pani puri",
        "Dinner": "Maida/Atta naan, Rice, Roti, Rajma, Masoor dal, Aloo-gobi, malai kofta. [Extra: Nonveg]. Sweet: Kaju Barfi"
    },
    "Thursday": {
         "Breakfast": "Idli, Masala Idli, Vada, Sambar, Nariyal Chutney",
         "Lunch": "Rice, Roti, Masoor dal, Dalma, Soyabean curry, Aloo-methi dry, Jhuri-aloo peanut, Imli rice, Fruits",
         "Tiffin": "Cheese veg sandwich",
         "Dinner": "Lachha paratha, Rice, Roti, Dal makhni, Masoor dal, Gobi Manchurian, Dum-Aloo. [Extra: Paneer butter masala]. Sweet: Gajar ka halwa"
    },
     "Friday": {
         "Breakfast": "Aloo Paratha (1st, 3rd) / Daal Paratha (2nd, 4th), green Chutney",
         "Lunch": "Rice, Roti, ghee roti, Masoor dal, Arhar Dal, Mix saag dry, Aloo-posto, French Fry, Beetroot-gajar-muli salad, Fruits",
         "Tiffin": "Dhokla",
         "Dinner": "Rice, Roti, Tadka dal (sabut moong), Masoor Dal, Matar Cabbage, Lauki kofta, Tomato soup. [Extra: Nonveg]. Sweet: Rasmalai"
    },
    "Saturday": {
        "Breakfast": "Pongal, Vada, Sambar, Nariyal Chutney (1st, 3rd) / Sewai Upma, Daliya (2nd, 4th)",
        "Lunch": "Rice, Roti, Bisi-bele bhat, Moong dal, Pakora, Khajoor chutney, Mixed veg, fryums, Peanut salad, Fruits",
        "Tiffin": "Chicken Chop / Paneer Chop",
        "Dinner": "Fried Rice, Roti, Dal fry, Masoor dal, Capsicum-aloo dum, Veg Manchurian, Sweet Corn soup. [Extra: Chilli paneer]. Sweet: Gulab Jamun"
    },
    "Sunday": {
        "Breakfast": "Dosa (Plain/Masala), Sambar, Nariyal chutney",
        "Lunch": "Rice, Roti, Masoor Dal, Paneer Biriyani, Kashmiri Aloo-Dum, Veg Jalfrezi, Onion-Cucumber Raita, Fruits",
        "Tiffin": "Kala-Channa (1st, 3rd)/ Sweet Corn Chat (2nd, 4th)",
        "Dinner": "Stuffed/Normal kulcha, Rice, Roti, Chole, Chilli potato, Sem beans sabji. [Extra: Nonveg]. Sweet: Motichur Laddoo"
    }
}

# --- 4. LOGIC ENGINE ---
def parse_smart_menu(menu_item, week_num):
    if not isinstance(menu_item, str) or "/" not in menu_item: return menu_item
    options = menu_item.split("/")
    valid_option = []
    for option in options:
        match = re.search(r'\((.*?)\)', option)
        if match:
            nums = []
            if '1st' in match.group(1): nums.append(1)
            if '2nd' in match.group(1): nums.append(2)
            if '3rd' in match.group(1): nums.append(3)
            if '4th' in match.group(1): nums.append(4)
            if '5th' in match.group(1): nums.append(5)
            if week_num in nums:
                valid_option.append(re.sub(r'\(.*?\)', '', option).strip())
        else:
            valid_option.append(option.strip())
    return " + ".join(valid_option) if valid_option else menu_item

# --- 5. APP INTERFACE ---
st.set_page_config(page_title="HRI Smart Mess", page_icon="🍛")

# Get Time info
now_india = get_india_time()
week_num = get_week_number()
day_name = now_india.strftime("%A")

st.title("🍛 HRI Physics Mess App")
st.caption(f"📅 Today is **{day_name}** (Week {week_num}) | 🕒 Time: {now_india.strftime('%I:%M %p')}")

tab1, tab2 = st.tabs(["🍽️ Daily Menu", "🤖 AI Chef"])

with tab1:
    if day_name in menu_data:
        day_menu = menu_data[day_name]
        
        # Highlight current meal based on time
        current_hour = now_india.hour
        if current_hour < 10: active = "Breakfast"
        elif current_hour < 14: active = "Lunch"
        elif current_hour < 18: active = "Tiffin"
        else: active = "Dinner"

        st.info(f"Upcoming/Current Meal: **{active}**")

        for meal in ["Breakfast", "Lunch", "Tiffin", "Dinner"]:
            raw = day_menu.get(meal, "Not Available")
            final_item = parse_smart_menu(raw, week_num)
            
            # If it's the active meal, keep it open
            with st.expander(f"{meal}", expanded=(meal==active)):
                st.markdown(f"### {final_item}")
    else:
        st.error("Menu data not found for today.")

with tab2:
    st.header("Ask the AI Chef")
    st.write("Ask questions like: _'Is lunch spicy?'_ or _'Protein in dinner?'_")
    
    if not AI_AVAILABLE:
        st.warning("⚠️ AI Key not found. Please check Secrets settings.")
    else:
        user_q = st.text_input("Your Question:")
        if st.button("Ask AI"):
            with st.spinner("Analyzing nutritional quantum states..."):
                context = f"You are a nutritionist at HRI Physics Institute. Today is {day_name}. Menu: {menu_data.get(day_name)}. User asks: {user_q}"
                try:
                    response = model.generate_content(context)
                    st.success(response.text)
                except Exception as e:
                    st.error(f"AI Error: {e}")
