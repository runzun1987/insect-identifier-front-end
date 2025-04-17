import streamlit as st
import requests
from utils.image import convert_image_bytes_to_base64

# Password setup
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["app_password"]:
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password
        st.text_input("Enter password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Enter password", type="password", on_change=password_entered, key="password")
        st.error("😬 Incorrect password.")
        return False
    else:
        return True

# Run password check before showing the app
if check_password():

    # ------------- your app content goes here ---------------

    st.set_page_config(page_title="Insect Identifier", layout="wide")

    IMAGE_CONVERSATION = "Please analyze the image and identify the insect. Based on the details in the image, what insect do you think this is?"
    CHAT_CONVERSATION = "How many insects are there in this world?"
    CHAT_CONVERSATION2 = "what is butterfly doing?"
    RANDOM_CONVERSATION = "Hi, what's the weather like today?"

    PREV_CONVERSATION_CHECKER = "I want to know more about that insect that i have previously provided please check"
    PREV_CONVERSATION_CHECKER2 = "give more info about this "

    GOOGLEAI = "google"
    OPENAI = "openai"
    GROQ = "groq"

    BACKEND_URL = "https://insect-identifier.vercel.app/chat"

    st.markdown("""
        <div style="text-align: center;">
            <h1 style="margin-bottom: 0;">🪲 Insect Identifying Bot</h1>
            <p style="font-size: 1.1rem; color: gray;">
                Chat with AI agents to identify insects using image + text.
            </p>
        </div>
    """, unsafe_allow_html=True)

    settings_col, main_col = st.columns([1.2, 2.8])

    with settings_col:
        st.subheader("⚙️ Agent Settings")

        thread_id = st.text_input("Thread ID", placeholder="Optional thread reference")
        providers = st.selectbox("AI Provider", [GOOGLEAI, OPENAI, GROQ])

        MODEL_OPTIONS = {
            GROQ: [
                "llama-3.3-70b-versatile",
                "deepseek-r1-distill-qwen-32b",
                "deepseek-r1-distill-llama-70b",
                "mistral-saba-24b",
                "llama-3.2-11b-vision-preview"
            ],
            OPENAI: ["gpt-4o-mini"],
            GOOGLEAI: ["gemini-1.5-flash", "gemini-2.0-flash"]
        }
        selected_model = st.selectbox("Select Model", MODEL_OPTIONS[providers])

        is_detailed = st.radio("Response Detail", [True, False], index=1, horizontal=True)

        st.markdown("### 🔎 Example Prompts")
        st.code(IMAGE_CONVERSATION)
        st.code(CHAT_CONVERSATION)
        st.code(CHAT_CONVERSATION2)
        st.code(RANDOM_CONVERSATION)
        st.code(PREV_CONVERSATION_CHECKER)
        st.code(PREV_CONVERSATION_CHECKER2)

    with main_col:
        st.subheader("💬 Your Query")
        user_query = st.text_area("What do you want to ask?", height=180,
                                  placeholder="Describe the insect, behavior, or ask anything related...")

        button_col1, button_col2 = st.columns([1, 1])
        ask_button = button_col1.button("🚀 Ask Agent", use_container_width=True)
        attach_image_button = button_col2.button("📎 Next", use_container_width=True)

        if "show_image_input" not in st.session_state:
            st.session_state.show_image_input = False
        if attach_image_button:
            st.session_state.show_image_input = not st.session_state.show_image_input

        base64_image = None
        image_url = ""
        if st.session_state.show_image_input:
            image_url = st.text_input("Paste image URL (optional)")
            uploaded_file = st.file_uploader("Upload an image (JPG, PNG):", type=["jpg", "jpeg", "png"])
            if uploaded_file:
                image_bytes = uploaded_file.read()
                st.image(image_bytes, caption="Uploaded Image", use_column_width=True)
                base64_image = convert_image_bytes_to_base64(image_bytes)

        if ask_button:
            if not user_query.strip():
                st.warning("Please enter your query.")
            else:
                st.info("Sending your request to the agent...")
                payload = {
                    "query": user_query,
                    "model_name": selected_model,
                    "model_provider": providers,
                    "image_url": image_url,
                    "base64_image": base64_image,
                    "just_last_message": not is_detailed,
                    "thread_id": thread_id
                }

                try:
                    response = requests.post(BACKEND_URL, json=payload)
                    response.raise_for_status()
                    data = response.json()
                    if "error" in data:
                        st.error(f"❌ {data['error']}")
                    else:
                        st.success("✅ Agent replied!")
                        st.markdown("### 🤖 Agent's Answer")
                        st.write(data)
                except requests.RequestException as e:
                    st.error(f"❗ Network Error: {e}")

        st.markdown("### 📸 Image Gallery (Copy Image URLs)")
        image_urls = [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Sunflower_from_Silesia2.jpg/1280px-Sunflower_from_Silesia2.jpg",
            "https://tinyjpg.com/images/social/website.jpg",
            "https://t3.ftcdn.net/jpg/04/99/62/42/360_F_499624241_YyIdlEqyGZEvmJ5aW5e9MWcxayvLlODz.jpg",
            "https://images.pexels.com/photos/950327/pexels-photo-950327.jpeg",
            "https://i.pinimg.com/736x/2b/27/cc/2b27cc3463a73dc2d87895ce40d0b700.jpg",
            "https://images.pexels.com/photos/121472/ladybug-beetle-coccinellidae-insect-121472.jpeg"
        ]
        for i in range(0, len(image_urls), 3):
            cols = st.columns(3)
            for col, url in zip(cols, image_urls[i:i + 3]):
                with col:
                    st.image(url, use_container_width=True)
                    st.code(url, language="text")
