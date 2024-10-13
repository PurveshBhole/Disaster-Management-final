import streamlit as st
import requests
import re
from groq import Groq

# Set page configuration
st.set_page_config(page_title="Disaster Response Chatbot")

# OpenWeather API setup
OPENWEATHER_API_KEY = "0c24cff5ec5448c093b83539240810"
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"

# Custom CSS for background, chat icons, and bubbles
page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://img.freepik.com/free-photo/amazing-beautiful-sky-with-clouds_58702-1653.jpg");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.1);
    z-index: -1;
}
.chat-container {
    display: flex;
    align-items: flex-start;
    margin-bottom: 10px;
}
.chat-container .icon {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    margin-right: 10px;
}
.user-icon {
    background-image: url("https://uxwing.com/wp-content/themes/uxwing/download/peoples-avatars/man-user-circle-icon.png");
    background-size: cover;
}
.bot-icon {
    background-image: url("https://cdn-icons-png.flaticon.com/512/13330/13330989.png");
    background-size: cover;
}
.message {
    background-color: #000;
    color: #fff;
    padding: 10px;
    border-radius: 10px;
    max-width: 80%;
    word-wrap: break-word;
}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)

def initialize_groq_client(api_key):
    try:
        return Groq(api_key=api_key)
    except Exception as e:
        st.error(f"Error initializing Groq client: {e}")
        return None

def windy_assistant_response(client, input_text, context=None):
    system_prompt = """
    You are a smart assistant for a disaster response platform designed to provide crucial information 
    and solve queries related to natural and human-made disasters. 
    Your task is to assist users with information about disaster preparedness, response, recovery, 
    risk assessment, and mitigation strategies.

    You also provide weather updates for specific locations when requested.

    Your responses should be concise, actionable, and based on reliable data.
    """

    conversation = f"{context}\nStudent: {input_text}\nAssistant:" if context else f"Student: {input_text}\nAssistant:"

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": conversation}
            ],
            model="llama3-70b-8192",
            temperature=0.5
        )
        response = chat_completion.choices[0].message.content
        return response
    except Exception as e:
        st.error(f"Error generating chat completion: {e}")
        return "An error occurred while generating the response."

def get_weather(city):
    try:
        response = requests.get(f"{WEATHER_API_URL}?q={city}&appid={OPENWEATHER_API_KEY}&units=metric")
        data = response.json()

        if response.status_code == 200:
            weather_description = data['weather'][0]['description']
            temperature = data['main']['temp']
            humidity = data['main']['humidity']
            return f"The current weather in {city} is {weather_description} with a temperature of {temperature}°C and humidity of {humidity}%."
        else:
            return f"Could not fetch weather for {city}. Please try again."
    except Exception as e:
        return f"Error fetching weather data: {e}"

def extract_city_from_input(user_input):
    match = re.search(r"weather in (\w+)", user_input, re.IGNORECASE)
    return match.group(1) if match else None

def main():
    st.title("Disaster Response Chatbot")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you today?"}]

    # Display all messages in session state with appropriate icons
    for msg in st.session_state.messages:
        icon_class = "bot-icon" if msg["role"] == "assistant" else "user-icon"
        st.markdown(f'''
        <div class="chat-container">
            <div class="icon {icon_class}"></div>
            <div class="message">{msg["content"]}</div>
        </div>
        ''', unsafe_allow_html=True)

    user_input = st.chat_input("Enter your question or response:")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        client_groq = initialize_groq_client("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")
        if client_groq is None:
            st.error("Failed to initialize the Groq client.")
            return

        if "weather" in user_input.lower():
            city = extract_city_from_input(user_input)
            weather_response = get_weather(city) if city else "Please specify a valid city."
            st.session_state.messages.append({"role": "assistant", "content": weather_response})
        else:
            context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
            response = windy_assistant_response(client_groq, user_input, context=context)
            st.session_state.messages.append({"role": "assistant", "content": response})

        # Re-render all messages after appending the new one
        for msg in st.session_state.messages:
            icon_class = "bot-icon" if msg["role"] == "assistant" else "user-icon"
            st.markdown(f'''
            <div class="chat-container">
                <div class="icon {icon_class}"></div>
                <div class="message">{msg["content"]}</div>
            </div>
            ''', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
