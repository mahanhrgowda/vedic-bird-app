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

# Improved Moon's ecliptic longitude calculation
def calculate_moon_longitude(d):
    T = d / 36525.0
    L0 = 218.31617 + 481267.88088 * T - 4.06 * T**2 / 3600.0
    M = 134.96292 + 477198.86753 * T + 33.25 * T**2 / 3600.0
    MSun = 357.52543 + 35999.04944 * T - 0.58 * T**2 / 3600.0
    F = 93.27283 + 483202.01873 * T - 11.56 * T**2 / 3600.0
    D = 297.85027 + 445267.11135 * T - 5.15 * T**2 / 3600.0

    Delta = (22640 * math.sin(math.radians(M)) 
             + 769 * math.sin(math.radians(2 * M)) 
             - 4586 * math.sin(math.radians(M - 2 * D)) 
             + 2370 * math.sin(math.radians(2 * D)) 
             - 668 * math.sin(math.radians(MSun)) 
             - 412 * math.sin(math.radians(2 * F)) 
             - 125 * math.sin(math.radians(D)) 
             - 212 * math.sin(math.radians(2 * M - 2 * D)) 
             - 206 * math.sin(math.radians(M + MSun - 2 * D)) 
             + 192 * math.sin(math.radians(M + 2 * D)) 
             - 165 * math.sin(math.radians(MSun - 2 * D)) 
             + 148 * math.sin(math.radians(L0 - MSun)) 
             - 110 * math.sin(math.radians(M + MSun)) 
             - 55 * math.sin(math.radians(2 * F - 2 * D))) / 3600.0

    lonecl = (L0 + Delta) % 360
    return lonecl

# Lahiri Ayanamsa approximation
def calculate_ayanamsa(jd):
    base_ayan = 23.853  # for J2000
    rate_per_year = 50.2719 / 3600  # degrees per year
    years = (jd - 2451545.0) / 365.25
    ayan = base_ayan + years * rate_per_year
    return ayan

# List of Nakshatras (consistent across both apps)
nakshatras = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purvaphalguni", "Uttaraphalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshta", "Mula", "Purvashada", "Uttarashada", "Shravana", "Dhanishta", "Shatabhisha", "Purvabhadra", "Uttarabhadra", "Revati"]

# Original Pancha Pakshi bird mapping
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

# Siddha Force mapping (from second app, fixed for Revati)
def get_siddha_force(nak_name, paksha):
    nak_index = nakshatras.index(nak_name)
    if paksha == "Shukla":
        if 0 <= nak_index <= 4:
            return "Vulture-Ether 🦅🌌"
        elif 5 <= nak_index <= 10:
            return "Owl-Air 🦉💨"
        elif 11 <= nak_index <= 15:
            return "Crow-Fire 🐦‍⬛🔥"
        elif 16 <= nak_index <= 20:
            return "Cock-Water 🐓🌊"
        else:  # 21-26
            return "Peacock-Earth 🦚🌍"
    else:  # Krishna
        if 0 <= nak_index <= 4:
            return "Peacock-Earth 🦚🌍"
        elif 5 <= nak_index <= 10:
            return "Cock-Water 🐓🌊"
        elif 11 <= nak_index <= 15:
            return "Crow-Fire 🐦‍⬛🔥"
        elif 16 <= nak_index <= 20:
            return "Owl-Air 🦉💨"
        else:  # 21-26
            return "Vulture-Ether 🦅🌌"

# Siddha Force descriptions (from second app)
descriptions = {
    "Vulture-Ether 🦅🌌": "🌟 As the Vulture-Ether force governs your essence 🦅🌌, you embody profound intuition and spiritual detachment, soaring high above earthly concerns like a vulture circling the skies. 🦅✨ Your life path is marked by visionary insights and a deep connection to the cosmos, allowing you to perceive hidden truths that others miss. 🌌🔮 In challenges, you rise with resilience, transforming obstacles into opportunities for growth. 💪🌱 Your personality radiates a mysterious aura, drawing people to your wisdom, yet you maintain independence, avoiding superficial bonds. 🤝🚫 Relationships flourish when you embrace vulnerability, balancing your ethereal nature with grounded emotions. ❤️🌍 Career-wise, fields like spirituality, research, or aviation suit you, where your broad perspectives shine. ✈️📚 Health may involve occasional detachment from physical needs, so prioritize meditation and etheric practices like yoga to stay balanced. 🧘‍♂️🍃 Karmically, past lives of exploration grant you current-life gifts in foresight, but beware of isolation—engage with community for fulfillment. 👥🌟 Auspicious times align when your force is in Ruling state, empowering bold decisions. ⏰👑 Overall, embrace your soaring spirit to manifest dreams, turning the intangible into reality with grace and power. 🦅💫 This divination reveals a journey of enlightenment, where ether's vastness fuels your eternal quest for truth and freedom. 🌌🕊️ Lengthy paths await, filled with cosmic wonders and self-discovery. 🚀📖",
    "Owl-Air 🦉💨": "🌟 Guided by the Owl-Air force 🦉💨, your core vibrates with intellectual wisdom and adaptable winds of change, much like an owl navigating the night with silent wings. 🦉🌬️ You possess sharp analytical skills and a thirst for knowledge, making you a natural learner and communicator in all realms. 📚🗣️ Life's winds may shift directions, but your flexibility turns them into advantages, fostering innovation and quick adaptations. 🔄💡 Personality-wise, you're witty and curious, enchanting others with your insights, though restlessness can lead to scattered energies—focus is key. 🎯🤔 In love, air's flow brings dynamic partnerships; nurture stability to avoid fleeting connections. ❤️🏠 Careers in writing, teaching, or technology harness your airy intellect for success. 💻🖋️ Health benefits from breathing exercises and fresh air, countering any nervous tendencies. 🌬️🧘 Karmic threads from past intellectual pursuits gift you eloquence, but learn patience to avoid superficiality. ⏳👥 Favorable periods emerge in Harmonizing states, ideal for collaborations and ideas. 🤝⏰ This Siddha force propels you toward enlightened adaptability, where air's freedom unlocks boundless potentials. 💨🕊️ Your divination unfolds as a whirlwind of discoveries, blending wisdom with whimsy for a fulfilling existence. 🌪️📖 Profound transformations await as you ride the currents of destiny with grace. 🚀✨",
    "Crow-Fire 🐦‍⬛🔥": "🌟 The Crow-Fire force ignites your being 🐦‍⬛🔥, symbolizing vigilant transformation and communal energy, akin to a crow's clever spark amid flames. 🐦‍⬛🕯️ You exude passion and leadership, driving change with fiery determination and sharp observation. 🔥👀 Life's trials forge you stronger, turning adversity into triumphs through resourcefulness. ⚒️🏆 Your personality is energetic and social, thriving in groups where your charisma shines, but temper impulsiveness to build lasting alliances. 👥😊 Relationships burn brightly; channel fire's warmth for deep bonds, avoiding conflicts. ❤️🔥 Ideal careers include management, activism, or arts, where your fire fuels creativity. 🎨📈 Health requires cooling practices like hydration and calm activities to balance heat. 💧🧘 Karmically, past communal roles endow you with networking prowess, but resolve old rivalries. 🤝🕰️ Optimal times in Observing states enhance vigilance for opportunities. 👁️⏰ This force divines a path of passionate evolution, where fire's light illuminates success and connections. 🔥🌟 Your journey is a blazing trail of achievements, embroidered with transformative experiences and joyful camaraderie. 🚀📖 Embrace the flames to forge a legacy of inspiration and warmth. 🐦‍⬛💫",
    "Cock-Water 🐓🌊": "🌟 Under the Cock-Water force's influence 🐓🌊, you reflect alertness and emotional renewal, like a rooster heralding dawn over flowing waters. 🐓💦 Your essence is protective and fluid, navigating life's currents with intuition and resilience. 🌊🛡️ You excel in empathy and healing, offering support that refreshes souls around you. 🤗💙 Challenges dissolve in your adaptable flow, emerging stronger through emotional depths. 🌊💪 Personality radiates charm and vigilance, fostering nurturing environments, though over-sensitivity needs boundaries. 🛡️😌 Love thrives in watery depths; seek partners who match your depth for harmonious unions. ❤️🌊 Careers in counseling, healthcare, or marine fields align with your watery vigilance. 🩺🚢 Health flourishes with water-based activities and emotional release practices. 🏊🧘 Karmic echoes from protective pasts grant intuitive gifts, but release fears for growth. 🕊️🕰️ Prime moments in Querying states aid insightful decisions and healings. ❓⏰ This divination promises a refreshing voyage, where water's flow carries you to emotional fulfillment and prosperity. 🌊🌟 Waves of opportunity and serenity define your path, enriched with profound connections and renewals. 🚀📖 Let the waters guide your vigilant spirit to shores of abundance. 🐓💫",
    "Peacock-Earth 🦚🌍": "🌟 The Peacock-Earth force grounds your soul 🦚🌍, embodying beauty, stability, and manifestation, as a peacock displays splendor on solid ground. 🦚🌳 You manifest creativity and reliability, building lasting foundations with artistic flair. 🎨🛠️ Life's beauty unfolds through your efforts, turning visions into tangible realities. 🌍💎 Your personality is grounded yet vibrant, attracting admiration with poise, but avoid rigidity by embracing change. 😊🔄 Relationships bloom in stable soils; cultivate openness for colorful unions. ❤️🌿 Careers in design, agriculture, or business leverage your earthly grace for success. 🏗️🌱 Health stabilizes with nature walks and balanced diets, rooting your vitality. 🌳🍎 Karmic roots from creative lifetimes bestow manifestation powers, but humility tempers pride. 🌟🕰️ Auspicious phases in Remediating states foster healing and growth. 🛠️⏰ This force foretells a grounded odyssey, where earth's bounty yields beauty and security. 🌍🦚 Your divination is a tapestry of achievements, woven with elegance, stability, and joyous expressions. 🚀📖 Dance through life with peacock's allure, creating a world of enduring wonder. 💫🌟"
}

# Original elements and mappings
rashi_elements = {
    "Mesha": "Fire", "Vrishabha": "Earth", "Mithuna": "Air", "Karka": "Water",
    "Simha": "Fire", "Kanya": "Earth", "Tula": "Air", "Vrishchika": "Water",
    "Dhanu": "Fire", "Makara": "Earth", "Kumbha": "Air", "Meena": "Water"
}

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

# Main app
st.title("Divination by Mahaan 🔮🦅🌟")

st.write("Enter your birth details to receive a combined Vedic Astrology fun descriptor and Siddha Pakshi Prasna divination. Birth time is local; select timezone for accurate UTC conversion. Place is for reference in divination output.")

birth_date = st.date_input("Birth Date 📅", min_value=datetime.date(1900, 1, 1), max_value=datetime.date(2100, 12, 31))
birth_time = st.time_input("Birth Time (Local) ⏰", step=datetime.timedelta(minutes=1))
timezones = sorted(zoneinfo.available_timezones())
timezone = st.selectbox("Timezone 🌍", timezones, index=timezones.index("UTC") if "UTC" in timezones else 0)
place = st.text_input("Place of Birth 🏙️ (Optional)")

if st.button("Generate Insights ✨"):
    if birth_date and birth_time:
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
        
        nak_name = nakshatras[nak_num]
        
        rashis = ["Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya", "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena"]
        rashi_name = rashis[rashi_num]
        
        # Original ruling bird calculation
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
        
        element = bird_to_element.get(ruling_bird, "Unknown")
        string_type = element_to_string.get(element, "Unknown")
        sanskrit_name = bird_to_sanskrit.get(ruling_bird, "Unknown")
        bird_desc = bird_descriptions.get(ruling_bird, "This bird embodies cosmic mysteries! 🌌")
        r_trait = rashi_traits.get(rashi_name, "mysterious soul 🌌")
        n_trait = nak_traits.get(nak_name, "cosmic wanderer ⭐")
        fun_phrase = random.choice(fun_phrases.get(element, ["embody the universe's mysteries! 🌌🔮✨"]))
        
        dynamic_desc = f"You are a {r_trait} infused with {n_trait} in Pada {pada} precision ⏳, guided by {ruling_bird} ({sanskrit_name}) of {element} vibes like {string_type} strings vibrating through reality! {fun_phrase}"
        
        # Siddha Force calculation
        siddha_force = get_siddha_force(nak_name, paksha)
        divination_desc = descriptions.get(siddha_force, "Mysterious forces guide your path! 🌌")
        
        # Output
        st.subheader(f"🌟 Your Combined Vedic & Siddha Insights for {place or 'Unknown Place'} 🌟")
        st.write(f"- **Rashi:** {rashi_name} (Element: {rashi_elements.get(rashi_name, 'Unknown')})")
        st.write(f"- **Nakshatra:** {nak_name}, Pada {pada}")
        st.write(f"- **Paksha:** {paksha}")
        st.write(f"- **Pancha Pakshi Ruling Bird (Panchabhuta):** {ruling_bird} ({sanskrit_name}) ({element})")
        st.write(f"- **Linked String Type:** {string_type}")
        st.write(f"- **Siddha Pakshi Force:** {siddha_force}")
        st.write(f"**Dynamic Fun Description:** {dynamic_desc}")
        st.write(f"**Bird Meaning in Context:** {bird_desc}")
        st.write(f"**Siddha Pakshi Prasna Divination:** {divination_desc}")
        
        with st.expander("Meanings of All Birds in Pancha Pakshi Shastra"):
            for bird, desc in bird_descriptions.items():
                st.write(f"- **{bird}:** {desc}")
        
        with st.expander("Meanings of All Siddha Forces"):
            for force, desc in descriptions.items():
                st.write(f"- **{force}:** {desc}")
    else:
        st.warning("Please enter birth date and time. ⚠️")
