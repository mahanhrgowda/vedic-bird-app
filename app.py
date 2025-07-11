import streamlit as st
import math
import datetime
import zoneinfo
import random

# Julian Date calculation
def julian_date(year, month, day, hour=0, minute=0, second=0):
    if month == 1 or month == 2:
        yearp = year - 1
        monthp = month + 12
    else:
        yearp = year
        monthp = month
    
    if year < 1582 or (year == 1582 and (month < 10 or (month == 10 and day < 15))):
        B = 0
    else:
        A = math.floor(yearp / 100)
        B = 2 - A + math.floor(A / 4)
    
    C = math.floor(365.25 * (yearp + 4716))
    D = math.floor(30.6001 * (monthp + 1))
    jd = B + day + C + D - 1524.5
    jd += (hour + minute / 60.0 + second / 3600.0) / 24.0
    return jd

# Calculate Sun's ecliptic longitude
def calculate_sun_longitude(d):
    w = 282.9404 + 4.70935e-5 * d
    e = 0.016709 - 1.151e-9 * d
    M = (356.0470 + 0.9856002585 * d) % 360
    Mrad = math.radians(M)
    E = M + math.degrees(e * math.sin(Mrad) * (1.0 + e * math.cos(Mrad)))
    Erad = math.radians(E)
    xv = math.cos(Erad) - e
    yv = math.sin(Erad) * math.sqrt(1.0 - e*e)
    v = math.degrees(math.atan2(yv, xv))
    lonsun = (v + w) % 360
    return lonsun

# Calculate Moon's ecliptic longitude with perturbations
def calculate_moon_longitude(d):
    N = (125.1228 - 0.0529538083 * d) % 360
    i = 5.1454
    w = (318.0634 + 0.1643573223 * d) % 360
    a = 60.2666  # Earth radii
    e = 0.054900
    M = (115.3654 + 13.0649929509 * d) % 360  # Mm
    Mrad = math.radians(M)
    E = M + math.degrees(e * math.sin(Mrad) * (1.0 + e * math.cos(Mrad)))
    Erad = math.radians(E)
    xv = a * (math.cos(Erad) - e)
    yv = a * (math.sqrt(1.0 - e*e) * math.sin(Erad))
    v = math.degrees(math.atan2(yv, xv))
    r = math.sqrt(xv*xv + yv*yv)
    Nr = math.radians(N)
    vr = math.radians(v + w)
    ir = math.radians(i)
    xh = r * (math.cos(Nr) * math.cos(vr) - math.sin(Nr) * math.sin(vr) * math.cos(ir))
    yh = r * (math.sin(Nr) * math.cos(vr) + math.cos(Nr) * math.sin(vr) * math.cos(ir))
    lonecl = math.degrees(math.atan2(yh, xh)) % 360
    
    # Perturbations
    Ms = (356.0470 + 0.9856002585 * d) % 360
    Msr = math.radians(Ms)
    Nm = (125.1228 - 0.0529538083 * d) % 360
    ws = 282.9404 + 4.70935e-5 * d
    Ls = (Ms + ws) % 360
    Lm = (M + w + N) % 360
    Dr = math.radians(Lm - Ls)
    Fr = math.radians(Lm - Nm)
    Mr = math.radians(M)
    E_pert = -1.274 * math.sin(Mr - 2*Dr)  # degrees
    E_pert += 0.658 * math.sin(2*Dr)
    E_pert -= 0.186 * math.sin(Msr)
    E_pert -= 0.059 * math.sin(2*Mr - 2*Dr)
    E_pert -= 0.057 * math.sin(Mr - 2*Dr + Msr)
    E_pert += 0.053 * math.sin(Mr + 2*Dr)
    E_pert += 0.046 * math.sin(2*Dr - Msr)
    E_pert += 0.041 * math.sin(Mr - Msr)
    E_pert -= 0.035 * math.sin(Dr)
    E_pert -= 0.031 * math.sin(Mr + Msr)
    E_pert -= 0.015 * math.sin(2*Fr - 2*Dr)
    E_pert += 0.011 * math.sin(Mr - 4*Dr)
    lonecl = (lonecl + E_pert) % 360
    return lonecl

# Lahiri Ayanamsa approximation
def calculate_ayanamsa(jd):
    base_ayan = 23.853  # for J2000
    rate_per_year = 50.2719 / 3600  # degrees per year
    years = (jd - 2451545.0) / 365.25
    ayan = base_ayan + years * rate_per_year
    return ayan

# Main app
st.title("Vedic Astrology Fun Descriptor")

birth_date = st.date_input("Birth Date", min_value=datetime.date(1900, 1, 1), max_value=datetime.date(2100, 12, 31))
birth_time = st.time_input("Birth Time (Local)")
timezones = sorted(zoneinfo.available_timezones())
timezone = st.selectbox("Timezone", timezones, index=timezones.index("UTC") if "UTC" in timezones else 0)

if st.button("Generate Description"):
    local_dt = datetime.datetime.combine(birth_date, birth_time)
    local_tz = zoneinfo.ZoneInfo(timezone)
    local_dt = local_dt.replace(tzinfo=local_tz)
    utc_dt = local_dt.astimezone(zoneinfo.ZoneInfo("UTC"))
    year, month, day = utc_dt.year, utc_dt.month, utc_dt.day
    hour, minute = utc_dt.hour, utc_dt.minute
    jd = julian_date(year, month, day, hour, minute)
    d = jd - 2451545.0
    
    sun_long = calculate_sun_longitude(d)
    moon_long = calculate_moon_longitude(d)
    ayan = calculate_ayanamsa(jd)
    
    sid_moon = (moon_long - ayan) % 360
    
    nak_num = math.floor(sid_moon / (360 / 27))
    nak_rem = sid_moon % (360 / 27)
    pada = math.floor(nak_rem / (360 / 108)) + 1
    
    rashi_num = math.floor(sid_moon / 30)
    
    elong = (moon_long - sun_long) % 360
    paksha = "Shukla" if elong < 180 else "Krishna"
    
    nakshatras = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purvaphalguni", "Uttaraphalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshta", "Mula", "Purvashada", "Uttarashada", "Shravana", "Dhanishta", "Shatabhisha", "Purvabhadra", "Uttarabhadra", "Revati"]
    nak_name = nakshatras[nak_num]
    
    rashis = ["Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya", "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena"]
    rashi_name = rashis[rashi_num]
    
    rashi_elements = {
        "Mesha": "Fire", "Vrishabha": "Earth", "Mithuna": "Air", "Karka": "Water",
        "Simha": "Fire", "Kanya": "Earth", "Tula": "Air", "Vrishchika": "Water",
        "Dhanu": "Fire", "Makara": "Earth", "Kumbha": "Air", "Meena": "Water"
    }
    
    shukla_birds = {
        "Vulture": ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira"],
        "Owl": ["Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purvaphalguni"],
        "Crow": ["Uttaraphalguni", "Hasta", "Chitra", "Swati", "Vishakha"],
        "Cock": ["Anuradha", "Jyeshta", "Mula", "Purvashada", "Uttarashada"],
        "Peacock": ["Shravana", "Dhanishta", "Shatabhisha", "Purvabhadra", "Uttarabhadra", "Revati"]
    }
    krishna_birds = {
        "Peacock": ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira"],
        "Cock": ["Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purvaphalguni"],
        "Crow": ["Uttaraphalguni", "Hasta", "Chitra", "Swati", "Vishakha"],
        "Owl": ["Anuradha", "Jyeshta", "Mula", "Purvashada", "Uttarashada"],
        "Vulture": ["Shravana", "Dhanishta", "Shatabhisha", "Purvabhadra", "Uttarabhadra", "Revati"]
    }
    
    ruling_bird = None
    if paksha == "Shukla":
        for bird, naks in shukla_birds.items():
            if nak_name in naks:
                ruling_bird = bird
                break
    else:
        for bird, naks in krishna_birds.items():
            if nak_name in naks:
                ruling_bird = bird
                break
    
    bird_to_sanskrit = {
        "Vulture": "Gṛdhra",
        "Owl": "Ulūka",
        "Crow": "Kāka",
        "Cock": "Kukkuṭa",
        "Peacock": "Mayūra"
    }
    
    bird_to_element = {
        "Vulture": "Fire",
        "Owl": "Water",
        "Crow": "Earth",
        "Cock": "Air",
        "Peacock": "Ether"
    }
    element_to_string = {
        "Fire": "Type I",
        "Water": "Type IIA",
        "Air": "Type IIB",
        "Earth": "Heterotic SO(32)",
        "Ether": "Heterotic E8×E8"
    }
    
    bird_descriptions = {
        "Vulture": "In Pancha Pakshi Shastra, the Vulture (Gṛdhra) symbolizes Fire 🔥, representing transformation, power, and leadership. Mythically linked to Garuda, Vishnu's vehicle, it embodies swift action and protection. It engages in activities like Ruling (strongest) to Dying (weakest), influencing auspicious timings. Linked to Type I strings, it vibrates with dynamic, open-closed modes, enhancing fiery Rashis like Mesha with passionate drive! 🦅⚡",
        "Owl": "The Owl (Ulūka) in Pancha Pakshi stands for Water 💧, signifying intuition, wisdom, and adaptability. Associated with Lakshmi's night vigilance, it's a harbinger of deep knowledge. Cycles through Eating, Walking, etc., for daily predictions. Tied to Type IIA strings, it flows in balanced, non-chiral dimensions, amplifying watery traits in Nakshatras like Pushya with emotional depth! 🦉🌊🔮",
        "Crow": "Crow (Kāka) represents Earth 🌍, denoting practicality, intelligence, and ancestral connections. As Shani's messenger, it signifies resourcefulness and caution. Its states (Ruling to Sleeping) guide mundane tasks. Connected to Heterotic SO(32) strings, grounding hybrid symmetries, it stabilizes earthy Kanya Rashi with wise, analytical energy! 🐦🌿🧠",
        "Cock": "The Cock (Kukkuṭa) embodies Air 🌬️, symbolizing alertness, courage, and communication. Linked to dawn and warriors like Kartikeya, it crows awakening and vigilance. Activities cycle for timing battles or starts. Aligned with Type IIB strings, chiral and self-dual, it boosts airy Mithuna with swift, intellectual winds! 🐔☁️🏹",
        "Peacock": "Peacock (Mayūra) signifies Ether ✨, illustrating expansion, beauty, and spirituality. Vehicle of Kartikeya, it dances in royal harmony, representing boundless space. From Ruling (peak creativity) to Dying, it aids spiritual pursuits. Mapped to Heterotic E8×E8 strings, unifying grand symmetries, it elevates ethereal Meena with cosmic visions! 🦚🌌💫"
    }
    
    rashi_traits = {
        "Mesha": "energetic pioneer 🔥🚀",
        "Vrishabha": "patient builder 🌱🏰",
        "Mithuna": "curious communicator 🗣️🌟",
        "Karka": "nurturing protector 🏡❤️",
        "Simha": "confident leader 👑🌞",
        "Kanya": "analytical perfectionist 📊🔍",
        "Tula": "diplomatic harmonizer ⚖️💕",
        "Vrishchika": "intense transformer 🦂🔥",
        "Dhanu": "adventurous philosopher 🏹📜",
        "Makara": "disciplined achiever 🏔️🏆",
        "Kumbha": "innovative visionary 💡🌐",
        "Meena": "compassionate dreamer 🌊✨"
    }
    
    nak_traits = {
        "Ashwini": "swift healer 🏇💨",
        "Bharani": "creative warrior ⚔️🎨",
        "Krittika": "fiery critic 🔥🗡️",
        "Rohini": "artistic nurturer 🌸🍼",
        "Mrigashira": "curious explorer 🦌🔎",
        "Ardra": "stormy intellectual 🌩️🧠",
        "Punarvasu": "renewing archer 🏹🔄",
        "Pushya": "protective guru 🌟🛡️",
        "Ashlesha": "intuitive serpent 🐍🔮",
        "Magha": "regal ancestor 👑🕊️",
        "Purvaphalguni": "loving performer ❤️🎭",
        "Uttaraphalguni": "helpful analyst 🤝📈",
        "Hasta": "skillful artisan 🖐️🛠️",
        "Chitra": "charismatic architect 🌟🏗️",
        "Swati": "independent diplomat ⚖️🌬️",
        "Vishakha": "ambitious goal-setter 🏆🔥",
        "Anuradha": "devoted friend 🤝❤️",
        "Jyeshta": "protective elder 🛡️👴",
        "Mula": "truth-seeking root 🌿🔍",
        "Purvashada": "invincible optimist 🏹😊",
        "Uttarashada": "enduring victor 🏆💪",
        "Shravana": "learning listener 👂📚",
        "Dhanishta": "musical networker 🎶🤝",
        "Shatabhisha": "healing mystic 🌟🧙",
        "Purvabhadra": "spiritual warrior ⚔️🙏",
        "Uttarabhadra": "wise supporter 🧠🤝",
        "Revati": "compassionate guide 🐟❤️"
    }
    
    fun_phrases = {
        "Fire": ["ignite passions like a blazing star! 🔥🌟🦅", "transform challenges into victories with fiery zeal! ⚡🏆🔥", "soar high with unstoppable energy! 🚀🔥🕊️"],
        "Water": ["flow through life with deep intuition! 💧🌊🦉", "adapt and nurture like ocean waves! 🌊❤️💙", "dive into emotions with graceful wisdom! 🏊‍♂️🔮💧"],
        "Earth": ["build stable foundations with earthy wisdom! 🌍🏗️🐦", "grow steadily like ancient trees! 🌳💪🟫", "caw out practical solutions grounded in reality! 🐦🛠️🌿"],
        "Air": ["dance freely with intellectual winds! 🌬️💃🐔", "crow ideas that soar through the skies! 🐔☁️🧠", "breeze through challenges with swift agility! 🌪️🏃‍♂️🌬️"],
        "Ether": ["expand infinitely like cosmic space! ✨🌌🦚", "harmonize universes with ethereal grace! 🔮💫🌠", "peacock your boundless potential! 🦚🌈✨"]
    }
    
    element = bird_to_element.get(ruling_bird, "Unknown")
    string_type = element_to_string.get(element, "Unknown")
    sanskrit_name = bird_to_sanskrit.get(ruling_bird, "Unknown")
    bird_desc = bird_descriptions.get(ruling_bird, "This bird embodies cosmic mysteries! 🌌")
    r_trait = rashi_traits.get(rashi_name, "mysterious soul 🌌")
    n_trait = nak_traits.get(nak_name, "cosmic wanderer ⭐")
    fun_phrase = random.choice(fun_phrases.get(element, ["embody the universe's mysteries! 🌌🔮✨"]))
    
    dynamic_desc = f"You are a {r_trait} infused with {n_trait} in Pada {pada} precision ⏳, guided by {ruling_bird} ({sanskrit_name}) of {element} vibes like {string_type} strings vibrating through reality! {fun_phrase}"
    
    st.write(f"🌟 **Your Vedic Astrology Snapshot:** 🌟")
    st.write(f"- **Rashi:** {rashi_name} (Element: {rashi_elements.get(rashi_name, 'Unknown')})")
    st.write(f"- **Nakshatra:** {nak_name}, Pada {pada}")
    st.write(f"- **Paksha:** {paksha}")
    st.write(f"- **Ruling Bird (Panchabhuta):** {ruling_bird} ({sanskrit_name}) ({element})")
    st.write(f"- **Linked String Type:** {string_type}")
    st.write(f"**Dynamic Fun Description:** {dynamic_desc}")
    st.write(f"**Bird Meaning in Context:** {bird_desc}")
    
    with st.expander("Meanings of All Birds in Pancha Pakshi Shastra"):
        for bird, desc in bird_descriptions.items():
            st.write(f"- **{bird}:** {desc}")
