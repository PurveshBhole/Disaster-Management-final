import streamlit as st
import requests
from groq import Groq

# Set page configuration
st.set_page_config(page_title="Disaster Response Chatbot")

# OpenWeather API setup
OPENWEATHER_API_KEY = "078b7ce730ccb542a4d91ab8438f69da"
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"

# Custom CSS to set the background image, overlay, and chat icons
page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] {{
background-image: url("imh.avif");
background-size: cover;
background-position: center;
background-attachment: fixed;
}}

[data-testid="stAppViewContainer"]::before {{
content: "";
position: absolute;
top: 0;
left: 0;
width: 100%;
height: 100%;
background-color: rgba(0, 0, 0, 0.1);  /* This creates the semi-transparent overlay */
z-index: -1;
}}

[data-testid="stSidebar"] {{
background-color: rgba(255, 255, 255, 0.8);
}}

[data-testid="stHeader"] {{
background-color: rgba(255, 255, 255, 0.8);
}}

/* Style for user and bot icons */
.chat-container {{
  display: flex;
  align-items: flex-start;
  margin-bottom: 10px;
}}

.chat-container .icon {{
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin-right: 10px;
}}

.chat-container .user-icon {{
  background-image: url("https://uxwing.com/wp-content/themes/uxwing/download/peoples-avatars/man-user-circle-icon.png");
  background-size: cover;
}}

.chat-container .bot-icon {{
  background-image: url("https://cdn-icons-png.flaticon.com/512/13330/13330989.png");
  background-size: cover;
}}

/* Black chat bubbles */
.chat-container .message {{
  background-color: #000;  /* Black background for chat bubbles */
  color: #fff;  /* White text color for contrast */
  padding: 10px;
  border-radius: 10px;
  max-width: 80%;
  word-wrap: break-word;
}}

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
    system_prompt = f"""
    You are a smart assistant for a disaster response platform designed to provide crucial information and solve queries related to natural and human-made disasters. Your task is to assist users with information about disaster preparedness, response, recovery, risk assessment, and mitigation strategies.

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

# Fetch weather from OpenWeather API
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

# Streamlit app
def main():
    st.title("Disaster Response Chatbot")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you today?"}]

    conversation_str = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.messages])
    
    # Display messages with custom icons
    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            st.markdown(f'''
            <div class="chat-container">
                <div class="icon bot-icon"></div>
                <div class="message">{msg["content"]}</div>
            </div>
            ''', unsafe_allow_html=True)
        elif msg["role"] == "user":
            st.markdown(f'''
            <div class="chat-container">
                <div class="icon user-icon"></div>
                <div class="message">{msg["content"]}</div>
            </div>
            ''', unsafe_allow_html=True)

    user_input = st.chat_input("Enter your question or response:")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display user input
        st.markdown(f'''
        <div class="chat-container">
            <div class="icon user-icon"></div>
            <div class="message">{user_input}</div>
        </div>
        ''', unsafe_allow_html=True)

        # Initialize Groq client
        client_groq = initialize_groq_client("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")
        if client_groq is None:
            st.error("Failed to initialize the Groq client. Please check your API key.")
            st.stop()

        # Check if the user asked for weather
        if "weather" in user_input.lower():
            # Extract the city (assuming it's in the format "weather in city")
            city = user_input.split("in")[-1].strip()
            weather_response = get_weather(city)
            st.session_state.messages.append({"role": "assistant", "content": weather_response})
            
            # Display assistant response
            st.markdown(f'''
            <div class="chat-container">
                <div class="icon bot-icon"></div>
                <div class="message">{weather_response}</div>
            </div>
            ''', unsafe_allow_html=True)
        else:
            context = conversation_str
            try:
                full_response = windy_assistant_response(client_groq, user_input, context=context)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
                # Display assistant response
                st.markdown(f'''
                <div class="chat-container">
                    <div class="icon bot-icon"></div>
                    <div class="message">{full_response}</div>
                </div>
                ''', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"An error occurred while generating the response: {e}")

if __name__ == "__main__":
    main()
