import os
import streamlit as st
import google.generativeai as genai

# Configure the API key
os.environ["GEMINI_API_KEY"] = "AIzaSyDfcuVWz7b43riDEn3LTbAlK84ry2lzx6o"
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Function to upload file to Gemini
def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini."""
    file = genai.upload_file(path, mime_type=mime_type)
    st.write(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

# Streamlit UI
st.title("AgriDiagnoX")

uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg", "webp"])

if uploaded_file is not None:
    # Display the uploaded image
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

    # Save the uploaded image to a temporary location
    with open("temp_image.webp", "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Upload the image to Gemini
    image_file = upload_to_gemini("temp_image.webp", mime_type="image/webp")

    # Configure the model
    generation_config = {
        "temperature": 0,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 16384,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
        system_instruction="evaluate the disease and symptoms in plants and animals using the input image\n",
    )

    # Initialize chat session history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display the chat-like interface
   
    # Request the model to analyze the image
    if st.button("Analyze Image"):
        user_message = "Analyze the uploaded image for disease symptoms and suggest a cure."
        st.session_state.chat_history.append({"role": "user", "content": user_message})

        # Start the chat session with the image
        chat_session = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                        image_file,
                    ],
                },
            ]
        )

        response = chat_session.send_message(user_message)
        st.session_state.chat_history.append({"role": "assistant", "content": response.text})

    # Display the chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])
