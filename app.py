import streamlit as st
import google.generativeai as genai
import os

# Get API key
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    st.error("""
    ⚠️ API Key not found!
    
    1. Create a file named `.env` in this folder
    2. Add: GOOGLE_API_KEY=your_key_here
    3. Get key from: https://aistudio.google.com/app/apikey
    """)
    st.stop()

# Configure
genai.configure(api_key=API_KEY)

st.title("🤖 Gemini Chat Assistant")

# First, let's discover available models
@st.cache_data
def get_available_models():
    """Get list of available models"""
    try:
        models = list(genai.list_models())
        available = []
        for model in models:
            # Only get models that support chat/generation
            if 'generateContent' in model.supported_generation_methods:
                # Extract model name
                model_name = model.name
                if '/' in model_name:
                    model_name = model_name.split('/')[-1]
                available.append(model_name)
        return available
    except Exception as e:
        st.error(f"Cannot list models: {e}")
        return []

# Get available models
available_models = get_available_models()

# Sidebar for model selection
with st.sidebar:
    st.header("⚙️ Settings")
    
    if available_models:
        selected_model = st.selectbox(
            "Select Model",
            available_models,
            index=0
        )
        st.caption(f"Using: {selected_model}")
    else:
        # Fallback to common model names
        selected_model = st.selectbox(
            "Select Model",
            ["gemini-1.0-pro", "gemini-pro-vision", "gemini-1.5-pro"],
            index=0
        )
        st.warning("Could not auto-discover models")
    
    if st.button("🔄 New Chat"):
        st.session_state.clear()
        st.rerun()

# Initialize model and chat
if "model" not in st.session_state:
    st.session_state.model = None
if "chat" not in st.session_state:
    st.session_state.chat = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize the model
if st.session_state.model is None:
    with st.spinner("Initializing model..."):
        try:
            # Try with the selected model
            st.session_state.model = genai.GenerativeModel(selected_model)
            st.session_state.chat = st.session_state.model.start_chat(history=[])
            st.success(f"✅ Model '{selected_model}' loaded!")
        except Exception as e:
            st.error(f"Failed to load '{selected_model}': {e}")
            
            # Try alternative model names
            alternative_models = ["gemini-1.0-pro", "models/gemini-pro", "gemini-pro"]
            for alt_model in alternative_models:
                try:
                    st.info(f"Trying: {alt_model}")
                    st.session_state.model = genai.GenerativeModel(alt_model)
                    st.session_state.chat = st.session_state.model.start_chat(history=[])  #******
                    st.success(f"✅ Using '{alt_model}' instead")
                    break
                except:
                    continue
            
            if st.session_state.model is None:
                st.error("❌ Could not initialize any model")
                st.stop()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Get response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.chat.send_message(prompt)    #********
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})