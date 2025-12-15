import streamlit as st
import datetime
import re
import google.generativeai as genai
import os

# ==========================================
# 🔴 SETUP AREA
# Paste your "AIza..." key inside the quotes below:
GOOGLE_API_KEY = "AIzaSyARVlx9KzFeczumMI0GxXws7IQPSNjh6BQ"
# ==========================================

# --- 1. THE DATA (From your uploaded Menu) ---
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

# --- 2. LOGIC FUNCTIONS ---
def get_week_number():
    today = datetime.date.today()
    return (today.day - 1) // 7 + 1

def parse_smart_menu(menu_item, week_num):
    """Filters menu based on week number (e.g., shows only 1st week item)"""
    if "/" not in menu_item: return menu_item
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

# --- 3. AI CONFIGURATION ---
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    AI_AVAILABLE = True
except:
    AI_AVAILABLE = False

# --- 4. THE UI ---
st.set_page_config(page_title="HRI Smart Mess", page_icon="🍛")

st.title("🍛 HRI Physics Mess App")
week_num = get_week_number()
today = datetime.datetime.now()
day_name = today.strftime("%A")
st.caption(f"Today is {day_name} (Week {week_num} of Dec)")

tab1, tab2 = st.tabs(["📅 Daily Menu", "🤖 AI Chef"])

with tab1:
    if day_name in menu_data:
        day_menu = menu_data[day_name]
        
        # Show specific meals
        meals = ["Breakfast", "Lunch", "Tiffin", "Dinner"]
        for meal in meals:
            raw = day_menu.get(meal, "Not Available")
            final_item = parse_smart_menu(raw, week_num)
            
            with st.expander(f"{meal}", expanded=True):
                st.markdown(f"### {final_item}")
    else:
        st.error("Menu data not found for today.")

with tab2:
    st.header("Ask the AI Chef")
    if not AI_AVAILABLE or "PASTE_YOUR" in GOOGLE_API_KEY:
        st.warning("⚠️ Please paste your API Key in the code to use this feature.")
    else:
        user_q = st.text_input("Ask about today's food (e.g., 'Is lunch spicy?', 'Protein content?')")
        if st.button("Ask AI"):
            with st.spinner("Analyzing menu..."):
                context = f"You are a nutritionist at HRI. Today's menu ({day_name}): {menu_data[day_name]}. User asks: {user_q}"
                response = model.generate_content(context)
                st.success(response.text)