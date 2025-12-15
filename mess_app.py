import streamlit as st
import datetime
import re

# --- 1. APP CONFIG ---
st.set_page_config(page_title="HRI Smart Mess", page_icon="🍛")

# --- 2. TIME LOGIC ---
def get_india_time():
    """Returns the current time in India (UTC+5:30)"""
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    india_tz = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    return utc_now.astimezone(india_tz)

def get_week_number(date_obj):
    return (date_obj.day - 1) // 7 + 1

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

# --- 4. DATA PARSER ---
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
        
        # Highlight Logic
        active = None
        if highlight and time_obj:
            current_hour = time_obj.hour
            if current_hour < 10: active = "Breakfast"
            elif current_hour < 14: active = "Lunch"
            elif current_hour < 18: active = "Tiffin"
            else: active = "Dinner"
            st.info(f"⚡ Currently serving: **{active}**")

        for meal in ["Breakfast", "Lunch", "Tiffin", "Dinner"]:
            raw = day_menu.get(meal, "Not Available")
            final_item = parse_smart_menu(raw, week_num)
            
            # If highlighting, open the active meal
            is_expanded = (meal == active) if highlight else False
            
            with st.expander(f"{meal}", expanded=is_expanded):
                st.markdown(f"**{final_item}**")
    else:
        st.error("Menu unavailable.")

# --- 5. UI LAYOUT ---
now_india = get_india_time()
today_name = now_india.strftime("%A")
today_week = get_week_number(now_india)
date_str = now_india.strftime("%d %b %Y")

# Calculate Tomorrow
tomorrow_date = now_india + datetime.timedelta(days=1)
tomorrow_name = tomorrow_date.strftime("%A")
tomorrow_week = get_week_number(tomorrow_date)
tomorrow_date_str = tomorrow_date.strftime("%d %b")

# --- SIDEBAR (VISITOR COUNTER) ---
with st.sidebar:
    st.header("HRI Mess App")
    st.markdown("Created by Kunal Raj")
    st.divider()
    # This badge auto-counts unique visitors to your GitHub repo link
    st.markdown("### 👥 Visitor Count")
    st.markdown("![Visitors](https://api.visitorbadge.io/api/visitors?path=https%3A%2F%2Fgithub.com%2FKunal-Raj-hub%2Fhri-mess-app&label=TOTAL+VIEWS&countColor=%23263759&style=flat)")
    st.caption("Live counter")

# --- MAIN PAGE ---
st.title("🍛 HRI Mess App")
st.caption(f"📅 {date_str} | **{today_name}** (Week {today_week})")

# TABS
tab1, tab2, tab3 = st.tabs(["🍽️ Today", "🔮 Tomorrow", "🗳️ Vote & Report"])

# TAB 1: TODAY
with tab1:
    display_menu_items(today_name, today_week, highlight=True, time_obj=now_india)

# TAB 2: TOMORROW
with tab2:
    st.header(f"Tomorrow: {tomorrow_name}")
    st.caption(f"📅 {tomorrow_date_str} | Week {tomorrow_week}")
    st.info("Plan your meals for tomorrow 👇")
    display_menu_items(tomorrow_name, tomorrow_week, highlight=False)

# TAB 3: VOTING & FEEDBACK
with tab3:
    st.header("🗳️ Feedback Dashboard")
    st.write("Help improve the Mess by reporting issues.")
    
    st.divider()
    
    # 1. Star Rating
    st.subheader("1. Rate Today's Food")
    rating = st.slider("Select Stars:", 1, 5, 3)
    
    if rating == 5:
        st.success("Excellent! ⭐⭐⭐⭐⭐")
    elif rating == 1:
        st.error("Terrible 😞")
    else:
        st.info(f"You rated it {rating}/5")

    st.divider()

    # 2. What needs improvement?
    st.subheader("2. What needs improvement?")
    st.caption("Tick the meals that were not up to the mark:")
    
    col1, col2 = st.columns(2)
    with col1:
        issue_b = st.checkbox("Breakfast")
        issue_l = st.checkbox("Lunch")
    with col2:
        issue_t = st.checkbox("Tiffin")
        issue_d = st.checkbox("Dinner")
        
    # Build list of issues
    issues = []
    if issue_b: issues.append("Breakfast")
    if issue_l: issues.append("Lunch")
    if issue_t: issues.append("Tiffin")
    if issue_d: issues.append("Dinner")
    
    issues_str = ", ".join(issues) if issues else "None"

    st.divider()

    # 3. Comment
    st.subheader("3. Specific Complaint")
    comment = st.text_area("Write details (e.g., 'Rice was undercooked', 'Too much oil')")

    # 4. Action Button
    st.markdown("### 🚀 Take Action")
    if st.button("📝 Generate WhatsApp Report"):
        # Format the message for WhatsApp
        report_text = (
            f"*HRI Mess Feedback ({date_str})*\n"
            f"-----------------------------\n"
            f"⭐ Rating: {rating}/5\n"
            f"⚠️ Needs Improvement: {issues_str}\n"
            f"💬 Details: {comment}\n"
            f"-----------------------------"
        )
        
        st.code(report_text, language="markdown")
        st.success("✅ Report Generated! Copy the text above and paste it in the Mess Group.")
