import streamlit as st
import datetime
import re

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="HRI Smart Mess", page_icon="🍛")

# --- 2. BACKGROUND IMAGE ---
bg_url = "https://images.unsplash.com/photo-1543353071-873f1753ade2?q=80&w=2070&auto=format&fit=crop"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("{bg_url}");
        background-attachment: fixed;
        background-size: cover;
    }}
    .stExpander, .stTextInput, .stMarkdown, .stTab, .stHeader, .stCaption, .stInfo, .stSuccess {{
        background-color: rgba(0, 0, 0, 0.7);
        border-radius: 10px;
        padding: 10px;
    }}
    h1, h2, h3, p, div, label, span {{
        color: white !important;
    }}
    /* Fix for text area and input text color */
    .stTextArea textarea, .stTextInput input {{
        color: white !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- 3. TIME CALCULATION ---
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

# --- 4. MENU DATA (JANUARY 2026) ---
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

# --- 5. SIDEBAR ---
with st.sidebar:
    st.header("HRI Mess App")
    st.markdown("Created by Kunal Raj")
    st.divider()
    st.markdown("![Visitors](https://api.visitorbadge.io/api/visitors?path=https%3A%2F%2Fgithub.com%2FKunal-Raj-hub%2Fhri-mess-app&label=TOTAL+VIEWS&countColor=%23263759&style=flat)")
    st.divider()
    st.info("💡 **Update:** Jan 2026 Menu Added!")

# --- 6. MAIN APP ---
st.title("🍛 HRI Mess App")
st.caption(f"📅 {today_date_str} | **{today_name}** (Week {today_week_num})")

tab1, tab2, tab3, tab4 = st.tabs(["🍽️ Today", "🔮 Tomorrow", "🔔 Set Alarms", "🗳️ Feedback"])

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
    
    st.markdown("[➕ **Breakfast Alarm** (7:30 AM)](https://www.google.com/calendar/render?action=TEMPLATE&text=HRI+Breakfast&dates=20260101T020000Z/20260101T030000Z&recur=RRULE:FREQ=DAILY&details=Mess+Reminder)")
    st.markdown("[➕ **Lunch Alarm** (12:30 PM)](https://www.google.com/calendar/render?action=TEMPLATE&text=HRI+Lunch&dates=20260101T070000Z/20260101T080000Z&recur=RRULE:FREQ=DAILY&details=Mess+Reminder)")
    st.markdown("[➕ **Tiffin Alarm** (4:30 PM)](https://www.google.com/calendar/render?action=TEMPLATE&text=HRI+Tiffin&dates=20260101T110000Z/20260101T120000Z&recur=RRULE:FREQ=DAILY&details=Mess+Reminder)")
    st.markdown("[➕ **Dinner Alarm** (7:30 PM)](https://www.google.com/calendar/render?action=TEMPLATE&text=HRI+Dinner&dates=20260101T140000Z/20260101T150000Z&recur=RRULE:FREQ=DAILY&details=Mess+Reminder)")

# TAB 4: WHATSAPP FEEDBACK
with tab4:
    st.header("🗳️ Feedback & Rating")
    st.write("Rate today's food and generate a report for the WhatsApp group.")
    
    st.divider()
    
    # 1. Star Rating
    rating = st.slider("How was the food?", 1, 5, 3)
    if rating >= 4:
        st.success("Great! 😋")
    elif rating <= 2:
        st.error("Needs improvement 😞")

    # 2. Issues Tickbox
    st.write("Which meal needs improvement?")
    col1, col2 = st.columns(2)
    with col1:
        issue_b = st.checkbox("Breakfast")
        issue_l = st.checkbox("Lunch")
    with col2:
        issue_t = st.checkbox("Tiffin")
        issue_d = st.checkbox("Dinner")
        
    issues = []
    if issue_b: issues.append("Breakfast")
    if issue_l: issues.append("Lunch")
    if issue_t: issues.append("Tiffin")
    if issue_d: issues.append("Dinner")
    
    issues_str = ", ".join(issues) if issues else "None"

    # 3. Comment
    comment = st.text_area("Any specific complaint?")

    # 4. Generate Button
    if st.button("📝 Generate WhatsApp Report"):
        report_text = (
            f"*HRI Mess Feedback ({today_date_str})*\n"
            f"-----------------------------\n"
            f"⭐ Rating: {rating}/5\n"
            f"⚠️ Needs Improvement: {issues_str}\n"
            f"💬 Comment: {comment}\n"
            f"-----------------------------"
        )
        st.code(report_text, language="markdown")
        st.success("✅ Copied! You can now paste this in the HRI WhatsApp group.")
