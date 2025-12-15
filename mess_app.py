import streamlit as st
import streamlit.components.v1 as components  # Required for the Google Form
import datetime
import re

# --- 1. APP CONFIG ---
st.set_page_config(page_title="HRI Smart Mess", page_icon="🍛")

# --- 2. BACKGROUND IMAGE SETUP ---
def add_bg_from_url():
    # You can change this background link later if you want
    bg_url = "https://images.unsplash.com/photo-1543353071-873f1753ade2?q=80&w=2070&auto=format&fit=crop"
    
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("{bg_url}");
             background-attachment: fixed;
             background-size: cover;
         }}
         /* Make text background semi-transparent so we can read it */
         .stExpander, .stTextInput, .stMarkdown, .stTab, .stHeader, .stCaption {{
             background-color: rgba(0, 0, 0, 0.7);
             border-radius: 10px;
             padding: 10px;
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

# Call the function to set the background
add_bg_from_url()

# --- 3. TIME LOGIC ---
def get_india_time():
    """Returns the current time in India (UTC+5:30)"""
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    india_tz = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    return utc_now.astimezone(india_tz)

def get_week_number(date_obj):
    return (date_obj.day - 1) // 7 + 1

# --- 4. MENU DATA ---
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

# --- 5. ALARM LINK GENERATOR ---
def create_google_calendar_link(title, start_hour, start_min, duration_hours=1):
    base = "https://www.google.com/calendar/render?action=TEMPLATE"
    start_utc_h = start_hour - 5
    start_utc_m = start_min - 30
    if start_utc_m < 0:
        start_utc_m += 60
        start_utc_h -= 1
        
    start_str = f"20250101T{start_utc_h:02}{start_utc_m:02}00Z"
    end_utc_h = start_utc_h + duration_hours
    end_str = f"20250101T{end_utc_h:02}{start_utc_m:02}00Z"
    
    details = f"text=HRI {title}&dates={start_str}/{end_str}&recur=RRULE:FREQ=DAILY&details=Daily Mess Reminder"
    return f"{base}&{details}"

# --- 6. DATA PARSER ---
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

def display_menu_items(day_name, week_num, highlight=False, time_obj=None):
    if day_name in menu_data:
        day_menu = menu_data[day_name]
        
        active = None
        if highlight and time_obj:
            current_hour = time_obj.hour
            current_min = time_obj.minute
            now_val = current_hour + (current_min/60)
            
            if 7.5 <= now_val < 10.5: active = "Breakfast"
            elif 12.5 <= now_val < 15.5: active = "Lunch"
            elif 16.5 <= now_val < 18.5: active = "Tiffin"
            elif 19.5 <= now_val < 22.0: active = "Dinner"
            
            if active:
                st.success(f"🔔 NOW SERVING: **{active}**")
            else:
                st.info("🕒 Kitchen Closed")

        for meal in ["Breakfast", "Lunch", "Tiffin", "Dinner"]:
            raw = day_menu.get(meal, "Not Available")
            final_item = parse_smart_menu(raw, week_num)
            
            is_expanded = (meal == active) if highlight else False
            with st.expander(f"{meal}", expanded=is_expanded):
                st.markdown(f"**{final_item}**")
    else:
        st.error("Menu unavailable.")

# --- 7. UI LAYOUT ---
now_india = get_india_time()
today_name = now_india.strftime("%A")
today_week = get_week_number(now_india)
date_str = now_india.strftime("%d %b %Y")

tomorrow_date = now_india + datetime.timedelta(days=1)
tomorrow_name = tomorrow_date.strftime("%A")
tomorrow_week = get_week_number(tomorrow_date)
tomorrow_date_str = tomorrow_date.strftime("%d %b")

# SIDEBAR
with st.sidebar:
    st.header("HRI Mess App")
    st.markdown("Created by Kunal Raj")
    st.divider()
    st.markdown("### 👥 Visitor Count")
    st.markdown("![Visitors](https://api.visitorbadge.io/api/visitors?path=https%3A%2F%2Fgithub.com%2FKunal-Raj-hub%2Fhri-mess-app&label=TOTAL+VIEWS&countColor=%23263759&style=flat)")
    st.divider()
    st.info("💡 **Tip:** Go to 'Set Alarms' for daily reminders!")

# MAIN PAGE
st.title("🍛 HRI Mess App")
st.caption(f"📅 {date_str} | **{today_name}** (Week {today_week})")

# TABS
tab1, tab2, tab3, tab4 = st.tabs(["🍽️ Today", "🔮 Tomorrow", "🔔 Set Alarms", "🗳️ Vote"])

# TAB 1: TODAY
with tab1:
    display_menu_items(today_name, today_week, highlight=True, time_obj=now_india)

# TAB 2: TOMORROW
with tab2:
    st.header(f"Tomorrow: {tomorrow_name}")
    st.caption(f"📅 {tomorrow_date_str} | Week {tomorrow_week}")
    display_menu_items(tomorrow_name, tomorrow_week, highlight=False)

# TAB 3: ALARMS
with tab3:
    st.header("🔔 Set Daily Reminders")
    st.write("Never miss a meal! Click below to add permanent daily alarms to your **Google Calendar**.")
    
    b_link = create_google_calendar_link("Breakfast", 7, 30)
    st.markdown(f"[➕ Add **Breakfast Alarm** (7:30 AM)]({b_link})", unsafe_allow_html=True)
    
    l_link = create_google_calendar_link("Lunch", 12, 30)
    st.markdown(f"[➕ Add **Lunch Alarm** (12:30 PM)]({l_link})", unsafe_allow_html=True)

    s_link = create_google_calendar_link("Snacks", 16, 30)
    st.markdown(f"[➕ Add **Snacks Alarm** (4:30 PM)]({s_link})", unsafe_allow_html=True)
    
    d_link = create_google_calendar_link("Dinner", 19, 30)
    st.markdown(f"[➕ Add **Dinner Alarm** (7:30 PM)]({d_link})", unsafe_allow_html=True)

# TAB 4: VOTING (Using your Google Form)
with tab4:
    st.header("🗳️ Feedback & Voting")
    st.write("Rate the food and report issues directly here:")
    
    # 1. Provide a direct link button (Safest method for mobile)
    form_url = "https://forms.gle/7CDLZP1DVzXRrpRs8"
    st.link_button("📝 Open Feedback Form (New Tab)", form_url)
    
    st.divider()
    
    # 2. Try to embed it inside the app
    st.caption("Or fill it out below:")
    # Using the 'embedded=true' version of the link usually works better
    st.components.v1.iframe(form_url, height=800, scrolling=True)
