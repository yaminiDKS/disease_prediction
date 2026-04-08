import streamlit as st
from groq import Groq
import base64

# Initialize Groq client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.title("🌿 AgriDiagnoX")

# Language selection
selected_language = st.selectbox(
    "Select Output Language",
    ["English", "Tamil"]
)

# Image input
input_method = st.radio(
    "Select Image Input Method",
    ("Upload Image", "Capture Image")
)

image_data = None

# Upload image
if input_method == "Upload Image":
    uploaded_file = st.file_uploader(
        "Upload Image",
        type=["png", "jpg", "jpeg", "webp"]
    )

    if uploaded_file:
        image_data = uploaded_file.read()
        st.image(uploaded_file, use_column_width=True)

# Camera capture
else:
    captured = st.camera_input("Capture Image")
    if captured:
        image_data = captured.getvalue()
        st.image(captured, use_column_width=True)

# Analyze
if image_data:

    base64_image = base64.b64encode(image_data).decode("utf-8")

    system_prompt = f"""
You are an expert agricultural diagnostician.

Analyze the crop image carefully.

Provide:
1. Observations
2. Disease Name
3. Cause
4. Treatment
5. Prevention

Respond completely in {selected_language}.
Do not ask follow-up questions.
"""

    if st.button("Analyze Image"):

        with st.spinner("Analyzing crop..."):

            completion = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                temperature=0.6,
                max_completion_tokens=4096,
                top_p=0.95,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this plant image"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
            )

            response = completion.choices[0].message.content
            st.chat_message("assistant").write(response)
