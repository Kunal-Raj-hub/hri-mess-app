import streamlit as st
import datetime
import re

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="HRI Smart Mess", page_icon="🍛")

# --- 2. GLOBAL VOTE MANAGER (The "Server Memory") ---
# This creates a shared memory that stays alive across different users
@st.cache_resource
class VoteManager:
    def __init__(self):
        self.votes = {
            "Breakfast": 0,
            "Lunch": 0,
            "Tiffin": 0,
            "Dinner": 0
        }
    
    def add_vote(self, meal):
        self.votes[meal] += 1
        
    def get_count(self, meal):
        return self.votes[meal]

# Initialize the manager
vote_manager = VoteManager()

# SET THE THRESHOLD HERE (Change to 40 later, keeping 5 for you to test easily)
ALERT_THRESHOLD = 40 

# --- 3. BACKGROUND IMAGE ---
bg_url = "https://images.unsplash.com/photo-1543353071-873f1753ade2?q=80&w=2070&auto=format&fit=crop"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("{bg_url}");
        background-attachment: fixed;
        background-size: cover;
    }}
    .stExpander, .stTextInput, .stMarkdown, .stTab, .stHeader, .stCaption, .stInfo, .stSuccess, .stWarning, .stError {{
        background-color: rgba(0, 0, 0, 0.75);
        border-radius: 10px;
        padding: 10px;
    }}
    h1, h2, h3, p, div, label, span, th, td {{
        color: white !important;
    }}
    /* High Alert Animation */
    @keyframes blink {{
        0% {{ opacity: 1; }}
        50% {{ opacity: 0.5; }}
        100% {{ opacity: 1; }}
    }}
    .critical-alert {{
        color: #ff4b4b !important;
        font-weight: bold;
        border: 2px solid #ff4b4b;
        padding: 10px;
        border-radius: 5px;
        animation: blink 2s infinite;
        text-align: center;
        background-color: rgba(50, 0, 0, 0.9);
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- 4. TIME CALCULATION ---
utc_now = datetime.datetime.now(datetime.timezone.utc)
india_tz = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
now_india = utc_now.astimezone(india_tz)

today_name = now_india.strftime("%A")
today_date_str = now_india.strftime("%d %b %Y")
today_week_num = (now_india.day - 1) // 7 + 1

tomorrow_date = now_india + datetime.timedelta(days=1)
tomorrow_name = tomorrow_date.strftime("%A")
tomorrow_date_str = tomorrow_date.strftime("%d %b")
tomorrow_week_num = (tomorrow_date.day - 1) // 7 + 1

# --- 5. MENU DATA (JAN 2026) ---
menu_data = {
    "Monday": {
        "Breakfast": "Methi paratha, Ghugni (1st, 3rd) / Sattu Paratha (2nd, 4th), Chutney",
        "Lunch": "Rice, Roti, Moong dal, Dalma, Palak corn, Aloo-gobi, Tomato rice, Beetroot-gajar-muli salad, Fruits",
        "Tiffin": "Pasta",
        "Dinner": "Sweet-pulao, Rice, Roti, Masoor Dal, Arhar Dal, Dum-Aloo, Mushroom-matar masala. [Extra: Handi paneer/ Paneer do pyaza]. Sweet: Malpua"
    },
    "Tuesday": {
        "Breakfast": "Besan chilla, chutney (1st, 3rd) / Kala-Channa, suji halwa (2nd, 4th)",
        "Lunch": "Rice, Roti, Masoor dal, Arhar dal, Aloo-lehsun, Gajar-Gobi-matar sabji, Curd rice, soaked-peanuts salad, Fruits",
        "Tiffin": "Chicken roll, Paneer roll",
        "Dinner": "Makki-di roti, Rice, Roti, Masoor Dal, Arhar Dal, Sarson-da saag, Hara bhara aloo, Mix-veg soup. [Extra: Kadhai paneer]. Sweet: Sewai ki kheer"
    },
    "Wednesday": {
        "Breakfast": "Poha, Jalebi",
        "Lunch": "Rice, Roti, Sodhi dal, Sambhar, Aloo-baingan chokha, Veg Korma, Lemon rice, Aloo chips, sprouts salad, Fruits",
        "Tiffin": "Pani puri",
        "Dinner": "Naan, Rice, Roti, Rajma, Aloo-mushroom-chilli, Masoor dal, Aloo-gobi. [Extra: Nonveg]. Sweet: Kaju Barfi"
    },
    "Thursday": {
         "Breakfast": "Idli, Masala Idli, Vada, Sambar, Nariyal Chutney",
         "Lunch": "Rice, Roti, Masoor dal, Dalma, Soyabean curry, Aloo-methi dry, Imli rice, Fruits",
         "Tiffin": "Cheese veg sandwich",
         "Dinner": "Lachha paratha, Rice, Roti, Dal makhni, Masoor dal, Gobi-chilli dry, Dum-Aloo. [Extra: Paneer butter masala]. Sweet: Gajar ka halwa"
    },
     "Friday": {
         "Breakfast": "Aloo Paratha (1st, 3rd) / Daal Paratha (2nd, 4th), green Chutney",
         "Lunch": "Rice, Roti, ghee roti, Masoor dal, Arhar Dal, Mix saag dry, Aloo-posto, Sambhar rice, Beetroot-gajar-muli salad, Fruits",
         "Tiffin": "Dhokla",
         "Dinner": "Rice, Roti, Tadka dal (sabut moong), Masoor Dal, Matar Cabbage, Lauki kofta, Tomato soup. [Extra: Nonveg]. Sweet: Rasmalai"
    },
    "Saturday": {
        "Breakfast": "Pongal, Vada, Sambar, Nariyal Chutney (1st, 3rd) / Sewai Upma, Daliya (2nd, 4th)",
        "Lunch": "Rice, Roti, Bisi-bele bhat, Moong dal, Pakora, Khajoor chutney, Mixed veg, fryums, Soaked-Peanut salad, Fruits",
        "Tiffin": "Chicken Chop / Paneer Chop",
        "Dinner": "Fried Rice, Roti, Dal fry, Masoor dal, Capsicum-aloo dum, Sweet Corn soup. [Extra: Chilli paneer]. Sweet: Gulab Jamun"
    },
    "Sunday": {
        "Breakfast": "Dosa (Plain/Masala), Sambar, Nariyal chutney",
        "Lunch": "Rice, Roti, Masoor Dal, Paneer Biriyani, Kashmiri Aloo-Dum, Veg Jalfrezi, Red-lehsun Raita, Fruits",
        "Tiffin": "Kala-Channa (1st, 3rd)/ Sweet Corn Chat (2nd, 4th)",
        "Dinner": "Stuffed/Normal kulcha, Rice, Roti, Chole, Chilli potato, Sem beans sabji. [Extra: Nonveg]. Sweet: Motichur Laddoo"
    }
}

# --- 6. CHECK FOR HIGH ALERTS ---
# This runs every time the app loads to check if any meal crossed the threshold
alert_msg = None
for meal in ["Breakfast", "Lunch", "Tiffin", "Dinner"]:
    if vote_manager.get_count(meal) >= ALERT_THRESHOLD:
        alert_msg = f"⚠️ HIGH ALERT: {meal} has received {vote_manager.get_count(meal)} complaints! Committee has been notified."

# --- 7. MAIN APP UI ---
st.title("🍛 HRI Mess App")

# SHOW ALERT IF ACTIVE
if alert_msg:
    st.markdown(f'<div class="critical-alert">{alert_msg}</div>', unsafe_allow_html=True)

st.caption(f"📅 {today_date_str} | **{today_name}** (Week {today_week_num})")

tab1, tab2, tab3, tab4 = st.tabs(["🍽️ Today", "🔮 Tomorrow", "🔔 Set Alarms", "⚠️ Report Issue"])

# TAB 1: TODAY
with tab1:
    if today_name in menu_data:
        current_hour = now_india.hour + (now_india.minute / 60)
        active_meal = None
        if 7.5 <= current_hour < 10.5: active_meal = "Breakfast"
        elif 12.5 <= current_hour < 15.5: active_meal = "Lunch"
        elif 16.5 <= current_hour < 18.5: active_meal = "Tiffin"
        elif 19.5 <= current_hour < 22.0: active_meal = "Dinner"

        if active_meal:
            st.success(f"🔔 NOW SERVING: **{active_meal}**")
        else:
            st.info("🕒 Kitchen Closed")

        for meal in ["Breakfast", "Lunch", "Tiffin", "Dinner"]:
            raw_item = menu_data[today_name].get(meal, "Not Available")
            # Cleaning Logic
            clean_item = raw_item
            if "/" in raw_item:
                parts = raw_item.split("/")
                valid_parts = []
                for part in parts:
                    if "(" in part:
                        if str(today_week_num) in part:
                            valid_parts.append(re.sub(r'\(.*?\)', '', part).strip()) 
                    else:
                        valid_parts.append(part.strip())
                if valid_parts:
                    clean_item = " + ".join(valid_parts)

            with st.expander(f"{meal}", expanded=(meal == active_meal)):
                st.markdown(f"**{clean_item}**")
    else:
        st.error("Menu data not found.")

# TAB 2: TOMORROW
with tab2:
    st.header(f"Tomorrow: {tomorrow_name}")
    st.caption(f"📅 {tomorrow_date_str} | Week {tomorrow_week_num}")
    if tomorrow_name in menu_data:
        for meal in ["Breakfast", "Lunch", "Tiffin", "Dinner"]:
            raw_item = menu_data[tomorrow_name].get(meal, "Not Available")
            # Cleaning Logic
            clean_item = raw_item
            if "/" in raw_item:
                parts = raw_item.split("/")
                valid_parts = []
                for part in parts:
                    if "(" in part:
                        if str(tomorrow_week_num) in part:
                            valid_parts.append(re.sub(r'\(.*?\)', '', part).strip())
                    else:
                        valid_parts.append(part.strip())
                if valid_parts:
                    clean_item = " + ".join(valid_parts)
            with st.expander(f"{meal}", expanded=False):
                st.markdown(f"**{clean_item}**")

# TAB 3: ALARMS
with tab3:
    st.header("🔔 Set Daily Reminders")
    st.write("Click to add alarms to Google Calendar:")
    st.markdown("[➕ **Breakfast**](https://www.google.com/calendar/render?action=TEMPLATE&text=HRI+Breakfast&dates=20260101T020000Z/20260101T030000Z&recur=RRULE:FREQ=DAILY)")
    st.markdown("[➕ **Lunch**](https://www.google.com/calendar/render?action=TEMPLATE&text=HRI+Lunch&dates=20260101T070000Z/20260101T080000Z&recur=RRULE:FREQ=DAILY)")
    st.markdown("[➕ **Tiffin**](https://www.google.com/calendar/render?action=TEMPLATE&text=HRI+Tiffin&dates=20260101T110000Z/20260101T120000Z&recur=RRULE:FREQ=DAILY)")
    st.markdown("[➕ **Dinner**](https://www.google.com/calendar/render?action=TEMPLATE&text=HRI+Dinner&dates=20260101T140000Z/20260101T150000Z&recur=RRULE:FREQ=DAILY)")

# TAB 4: SMART ISSUE TRACKER (THE NEW LOGIC)
with tab4:
    st.header("⚠️ Report Bad Food")
    st.write("Is the food bad today? Vote below. If votes cross 40, an alert is sent to the Committee.")
    
    # 1. Check if user already voted in this session
    if 'has_voted' not in st.session_state:
        st.session_state.has_voted = False

    if st.session_state.has_voted:
        st.info("✅ Your vote has been recorded. Thank you for helping improve the Mess.")
        st.divider()
        st.write("Current Complaint Counts:")
    else:
        st.write("Select the meal that needs improvement:")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚩 Breakfast Bad"):
                vote_manager.add_vote("Breakfast")
                st.session_state.has_voted = True
                st.rerun() # Refresh to show updated data
            if st.button("🚩 Lunch Bad"):
                vote_manager.add_vote("Lunch")
                st.session_state.has_voted = True
                st.rerun()

        with col2:
            if st.button("🚩 Tiffin Bad"):
                vote_manager.add_vote("Tiffin")
                st.session_state.has_voted = True
                st.rerun()
            if st.button("🚩 Dinner Bad"):
                vote_manager.add_vote("Dinner")
                st.session_state.has_voted = True
                st.rerun()

    # Show Live Stats
    st.subheader("📊 Live Complaint Counter")
    
    # We use a progress bar to show how close we are to 40
    for meal in ["Breakfast", "Lunch", "Tiffin", "Dinner"]:
        count = vote_manager.get_count(meal)
        percentage = min(count / ALERT_THRESHOLD, 1.0)
        
        st.write(f"**{meal}:** {count} votes")
        
        # Color changes based on severity
        if count >= ALERT_THRESHOLD:
            st.progress(percentage, text="CRITICAL LEVEL REACHED")
        elif count > (ALERT_THRESHOLD / 2):
             st.progress(percentage, text="Warning Level")
        else:
             st.progress(percentage)

    st.caption(f"Alert triggers at {ALERT_THRESHOLD} votes.")
