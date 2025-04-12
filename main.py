import os
import streamlit as st
import google.generativeai as genai

# Configure the API key
os.environ["GEMINI_API_KEY"] = "YOUR_API_KEY_HERE"  # Replace with your actual API key
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Function to upload file to Gemini
def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini."""
    file = genai.upload_file(path, mime_type=mime_type)
    st.write(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

# Streamlit UI
st.title("AgriDiagnoX")

# Language selection for output
selected_language = st.selectbox("Select Output Language", ["English", "Tamil"])

# Option to choose image input method
input_method = st.radio("Select Image Input Method", ("Upload Image", "Capture Image"))

image_data = None
temp_filename = "temp_image.webp"

if input_method == "Upload Image":
    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg", "webp"])
    if uploaded_file is not None:
        image_data = uploaded_file.read()
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
elif input_method == "Capture Image":
    # Option to choose camera (front or back)
    camera_choice = st.selectbox("Select Camera", ["Front Camera", "Back Camera"])
    # Map to a camera ID; front camera is usually 0 and back camera is usually 1
    camera_id = 0 if camera_choice == "Front Camera" else 1
    captured_image = st.camera_input("Capture an image", camera_id=camera_id)
    if captured_image is not None:
        image_data = captured_image.getvalue()
        st.image(captured_image, caption="Captured Image", use_column_width=True)

if image_data is not None:
    # Save the image data to a temporary file
    with open(temp_filename, "wb") as f:
        f.write(image_data)

    # Upload the image to Gemini (using image/webp mime type; adjust as needed)
    image_file = upload_to_gemini(temp_filename, mime_type="image/webp")

    # Build refined system instruction including the selected language
    system_instruction = (
        "You are an expert agricultural diagnostician. Analyze the input image thoroughly for any disease "
        "symptoms in plants or animals. Provide a detailed diagnosis including observations and recommended "
        "treatments, and output your response entirely in {}. Do not ask any follow-up questions."
    ).format(selected_language)

    # Configure generation parameters
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 16384,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
        system_instruction=system_instruction,
    )

    # Initialize chat session history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Button to analyze image
    if st.button("Analyze Image"):
        user_message = "Please analyze the uploaded image for disease symptoms and suggest a cure."
        st.session_state.chat_history.append({"role": "user", "content": user_message})

        # Start the chat session by sending the uploaded image as the first message
        chat_session = model.start_chat(
            history=[{"role": "user", "parts": [image_file]}],
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
