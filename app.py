import streamlit as st
import requests
from utils.image import convert_image_bytes_to_base64
import time


## Change this to True if you want to use the live APIs
isProd = False


BACKEND_URL = "https://insect-identifier.vercel.app/chat" if isProd else "http://localhost:8000/chat"

BACKEND_URL_IMAGE = "https://insect-identifier.vercel.app/image" if isProd else "http://localhost:8000/image"


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
    AAA = """
 "Imagine there is an insect named Humanoid Insect. Generate random thoughts about that insect and return the result in the following format. The name should always be Humanoid Insect.
For this task, return the details in this exact format:
{format_instructions}
Here is an example return type: {api_result} (Do not use this data directly, it's just an example)."
    
    
    """



    DEFAULT_IMAGE_PROMPT = """

                     "Using the following iNaturalist API result, identify any insects or bug-like creatures present:\n{api_result}\n\n"
                     "For this task, consider all of the following as 'insects' (even if they are not scientifically insects):\n"
                     "Ants, Beetles, Flies, Mosquitoes, Butterflies, Moths, Bees, Wasps, Dragonflies, Grasshoppers, Crickets, "
                     "Cockroaches, Termites, Spiders, Ticks, Fleas, Lice, Mites, Earwigs, Silverfish, Centipedes, Millipedes, "
                     "Aphids, Stink Bugs, Ladybugs, Caterpillars, Locusts, Crane Flies, Fireflies, Bedbugs, and other similar small arthropods.\n\n"
                     "✅ Treat anything small and bug-like as an insect for this task.\n\n"
                     "If such a creature is detected, return the details in this exact format:\n{format_instructions}\n\n"
                     "Include if available:\n"
                     "Name, Scientific name, Habitat, Diet, Lifespan, Color, Behavior, Description, "
                     "(Optional) Danger level, (Optional) Rarity.\n\n"
                     "⚠️ If no insect or bug-like creature is found, respond exactly with:\n"
                     "`This image does not contain an insect.`"


    """

    GOOGLEAI = "google"
    OPENAI = "openai"
    GROQ = "groq"



    st.markdown("""
        <div style="text-align: center;">
            <h1 style="margin-bottom: 0;">🪲 Insect Identifying Bot</h1>
            <p style="font-size: 1.1rem; color: gray;">
                Chat with AI agents to identify insects using image + text New Base64 updated.
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
        old_fetching_style = st.radio("Old Style", [True, False], index=1, horizontal=True)

        st.markdown("### 🔎 Example Prompts")
        st.code(IMAGE_CONVERSATION)
        st.code(CHAT_CONVERSATION)
        st.code(CHAT_CONVERSATION2)
        st.code(RANDOM_CONVERSATION)
        st.code(PREV_CONVERSATION_CHECKER)
        st.code(PREV_CONVERSATION_CHECKER2)
        st.code(AAA)

    with main_col:
        st.subheader("💬 Your Query")
        # Initialize session state for user_query if not already
        if "user_query" not in st.session_state:
            st.session_state.user_query = DEFAULT_IMAGE_PROMPT

        # Layout for text area and clear button
        text_col, clear_col = st.columns([10, 1])
        with text_col:
            user_query = st.text_area(
                "What do you want to ask?",
                value=st.session_state.user_query,
                height=180,
                placeholder="Describe the insect, behavior, or ask anything related..."
            )
            st.session_state.user_query = user_query  # update state with current value
        with clear_col:
            if st.button("❌", help="Clear prompt"):
                st.session_state.user_query = ""

        button_col1, button_col2 = st.columns([1, 1])
        ask_button = button_col1.button("🚀 Ask Agent", use_container_width=True)
        attach_image_button = button_col2.button("📎 Attach Image", use_container_width=True)

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
            # if not user_query.strip():
            #     st.warning("Please enter your query.")
            # else:
                st.info("Sending your request to the agent...")

                is_image_search = bool(image_url or base64_image)


                def handle_response(response, elapsed_time, endpoint_used):
                    try:
                        response.raise_for_status()
                        data = response.json()
                        if "error" in data:
                            st.error(f"❌ {data['error']}")
                        else:
                            st.success("✅ Agent replied!")
                            st.markdown("### 🤖 Agent's Answer")
                            st.write(data)
                            st.info(f"🌐 Endpoint used: `{endpoint_used}`")
                            st.info(f"⏱️ Response time: {elapsed_time:.2f} seconds")
                    except requests.RequestException as e:
                        st.error(f"❗ Network Error: {e}")


                # Prepare payload and endpoint
                if is_image_search:
                    if old_fetching_style:
                        payload = {
                            "query": user_query,
                            "model_name": selected_model,
                            "model_provider": providers,
                            "image_url": image_url,
                            "base64_image": base64_image,
                            "just_last_message": not is_detailed,
                            "thread_id": thread_id,
                            "isTest": False
                        }
                        endpoint = BACKEND_URL
                    else:
                        payload = {
                            "model_name": selected_model,
                            "model_provider": providers,
                            "image_url": image_url,
                            "base64_image": base64_image,
                            "thread_id": thread_id,
                            "image_prompt": user_query,
                        }
                        endpoint = BACKEND_URL_IMAGE
                else:
                    payload = {
                        "query": user_query,
                        "model_name": selected_model,
                        "model_provider": providers,
                        "image_url": image_url,
                        "base64_image": base64_image,
                        "just_last_message": not is_detailed,
                        "thread_id": thread_id,
                        "isTest": False
                    }
                    endpoint = BACKEND_URL

                # Measure response time
                start_time = time.time()
                response = requests.post(endpoint, json=payload)
                end_time = time.time()

                handle_response(response, end_time - start_time, endpoint)
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
