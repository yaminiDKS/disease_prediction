import os
import streamlit as st
from groq import Groq
import base64

# Set your Groq API key
os.environ["GROQ_API_KEY"] = "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"
client = Groq(api_key=os.environ["GROQ_API_KEY"])

st.title("AgriDiagnoX")

# Language selection
selected_language = st.selectbox(
    "Select Output Language",
    ["English", "Tamil"]
)

# Image input method
input_method = st.radio(
    "Select Image Input Method",
    ("Upload Image", "Capture Image")
)

image_data = None

if input_method == "Upload Image":
    uploaded_file = st.file_uploader(
        "Upload an image",
        type=["png", "jpg", "jpeg", "webp"]
    )

    if uploaded_file is not None:
        image_data = uploaded_file.read()
        st.image(uploaded_file, caption="Uploaded Image")

elif input_method == "Capture Image":
    st.info("Allow camera permission")

    captured_image = st.camera_input("Capture Image")

    if captured_image is not None:
        image_data = captured_image.getvalue()
        st.image(captured_image, caption="Captured Image")

# ---------- AI ANALYSIS ----------
if image_data is not None:

    # Convert image to base64
    base64_image = base64.b64encode(image_data).decode("utf-8")

    system_prompt = f"""
You are an expert agricultural diagnostician.

Analyze plant or animal disease symptoms from the image.

Provide:
- Observations
- Disease name
- Cause
- Treatment
- Prevention

Respond completely in {selected_language}.
Do not ask follow up questions.
"""

    if st.button("Analyze Image"):

        with st.spinner("Analyzing..."):

            completion = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                temperature=1,
                max_completion_tokens=4096,
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
                                "text": "Analyze this agricultural image for disease"
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
