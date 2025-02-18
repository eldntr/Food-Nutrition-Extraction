import streamlit as st
import requests
import base64
import json
from PIL import Image, ImageDraw, ImageFont
import os

# Define prompt templates outside the functions for easy customization
FOOD_INFO_PROMPT_TEMPLATE = """
Extract only the food-related information from this image. 
Focus on identifying the main ingredients, portion size, and any other relevant details about the food.
Specifically:
- Identify the number of main components (e.g., main dish, side dishes, garnishes).
- Describe each component in detail, including its type, estimated quantity, and notable ingredients.
"""
NUTRITION_INFO_PROMPT_TEMPLATE = """
Provide a detailed TOTAL nutritional breakdown for the ENTIRE dish described below. 
Include ONLY the total values for macronutrients like calories, carbohydrates, fats, proteins, etc.
Do not include per-serving information. Ensure the output is clear, concise, and well-organized.
{text}
"""

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_food_info(image_path, api_key):
    base64_image = encode_image_to_base64(image_path)
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json",
    }
    data = {
        "model": "google/gemini-pro-vision",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": FOOD_INFO_PROMPT_TEMPLATE  # Use the external prompt template
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
    }
    response = requests.post(url=url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.status_code}"

def extract_nutrition_info(text, api_key):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json",
    }
    data = {
        "model": "mistralai/mistral-small-24b-instruct-2501",
        "messages": [
            {
                "role": "user",
                "content": NUTRITION_INFO_PROMPT_TEMPLATE.format(text=text)  # Use the external prompt template
            }
        ],
    }
    response = requests.post(url=url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.status_code}"

def add_text_to_image(image_path, text):
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font = ImageFont.load_default()
    text_position = (10, 10)
    draw.text(text_position, text, fill="red", font=font)
    return img

# Streamlit App
st.title("Food Information Extractor")

# Input for API Key
api_key = st.text_input("Enter your OpenRouter API Key:", type="password")
if not api_key:
    st.warning("Please enter your API Key to proceed.")
    st.stop()

uploaded_file = st.file_uploader("Choose an image...", type="jpg")
if uploaded_file is not None:
    image_path = "uploaded_image.jpg"
    with open(image_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.image(image_path, caption='Uploaded Image.', use_column_width=True)
    st.write("")
    st.write("Extracting food information...")
    
    food_info = extract_food_info(image_path, api_key)
    st.write("Food Information:")
    st.write(food_info)
    
    nutrition_info = extract_nutrition_info(food_info, api_key)
    st.write("Nutrition Information:")
    st.write(nutrition_info)