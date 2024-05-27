from PIL import Image
import io
import logging
import streamlit as st
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
import re
import trialsearch as ts
import requests

temperature = 0.9
import streamlit as st

# Power tools
power_tools = [
    {"name": "Bosch Tools on IBO", "link": "https://www.ibo.com/power-tools/c/3050"},
    {"name": "Bosch Power Tools",
     "link": "https://www.boschtools.com/us/en/power-tools-22064-ocs-c/"},
    {"name": "Bosch Measurement Tools",
     "link": "https://www.boschtools.com/us/en/measuring-and-layout-tools-23413-ocs-c/"},
    {"name": "Bosch ROS20VSC Palm Sander",
     "link": "https://www.lowes.com/pd/Bosch-2-5-Amp-Corded-5-in-Random-Orbit-Sander-with-Case/999925164"},
    {"name": "Bosch Tools on Amazon",
     "link": "https://www.amazon.in/s?k=bosch+tools&crid=1ULBPHHWWPPLG&sprefix=bosch+tool%2Caps%2C330&ref=nb_sb_noss_1"},
    {"name": "Bosch Tools on Flipkart",
     "link": "https://www.flipkart.com/search?q=bosch%20tools&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off"},
    {"name": "Stanley 16-791 Sweetheart 750 Series Socket Chisel Set",
     "link": "https://www.amazon.com/Stanley-16-791-Sweetheart-4-Piece-750/dp/B0030T1BR6"},
    {"name": "TEKTON Combination Wrench Set",
     "link": "https://www.amazon.com/TEKTON-Combination-Wrench-12-Inch-15-Piece/dp/B009QYF3QA"}
]


generation_config = {
    "temperature": temperature,
    "top_p": 0.95,
    "top_k": 1,
    "max_output_tokens": 99998,
}

st.set_page_config(page_title="Gemini Chatbot", page_icon=":gem:")

with st.sidebar:
    st.title("Gemini Setting")

    api_key = 'AIzaSyC5Mmy23tELO2hAbz0f6HNe9Nkd9KsMRyE'
    if api_key:
        genai.configure(api_key=api_key)
    else:
        if "GOOGLE_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        else:
            st.error("Missing API key.")
    select_model = st.selectbox(
        "Select model", ["powertools__new_final111"])
    temperature = 0.9

    if select_model == "gemini-pro-vision":
        uploaded_image = st.file_uploader(
            "upload image",
            label_visibility="collapsed",
            accept_multiple_files=False,
            type=["png", "jpg"],
        )
        st.caption(
            "Note: The vision model gemini-pro-vision is not optimized for multi-turn chat."
        )
        if uploaded_image:
            image_bytes = uploaded_image.read()


def get_response(messages, model="gemini-pro"):
    model = genai.GenerativeModel(model)
    res = model.generate_content(messages,
                                 generation_config=generation_config)
    return res


if "messages" not in st.session_state:
    st.session_state["messages"] = []
messages = st.session_state["messages"]

# The vision model gemini-pro-vision is not optimized for multi-turn chat.
st.header("TINKER.BOT")
st.write(
    "This is a Gemini LLM Chatbot for suggesting tools and providing steps to fix anything we want. This app is powered by Google's GEMINI Generative AI models. This app is built using Streamlit and hosted on Streamlit Share.")
st.markdown("""
    App built by ENTC-C Batch-3 Group 5
""")

# Initialize session state for chat history if it doesn't exist
if messages and select_model != "gemini-pro-vision":
    for item in messages:
        role, parts = item.values()
        if role == "user":
            st.chat_message("user").markdown(parts[0])
        elif role == "model":
            st.chat_message("assistant").markdown(parts[0])

chat_message = st.chat_input("Say something")

res = None
if chat_message:
    st.chat_message("user").markdown(chat_message)
    res_area = st.chat_message("assistant").markdown("...")

    if select_model == "gemini-pro-vision":
        if "image_bytes" in globals():
            vision_message = [chat_message,
                              Image.open(io.BytesIO(image_bytes))]
            try:
                res = get_response(vision_message, model="gemini-pro-vision")
            except google_exceptions.InvalidArgument as e:
                if "API key not valid" in str(e):
                    st.error("API key not valid. Please pass a valid API key.")
                else:
                    st.error("An error occurred. Please try again.")
            except Exception as e:
                logging.error(e)
                st.error("Error occured. Please refresh your page and try again.")
        else:
            vision_message = [{"role": "user", "parts": [chat_message]}]
            st.warning(
                "Since there is no uploaded image, the result is generated by the default gemini-pro model.")
            try:
                res = get_response(vision_message)
            except google_exceptions.InvalidArgument as e:
                if "API key not valid" in str(e):
                    st.error("API key not valid. Please pass a valid API key.")
                else:
                    st.error("An error occurred. Please try again.")
            except Exception as e:
                logging.error(e)
                st.error("Error occured. Please refresh your page and try again.")
    else:
        messages.append(
            {"role": "user", "parts": [chat_message]},
        )
        try:
            res = get_response(messages)
        except google_exceptions.InvalidArgument as e:
            if "API key not valid" in str(e):
                st.error("API key not valid. Please pass a valid API key.")
            else:
                st.error("An error occurred. Please refresh your page and try again.")
        except Exception as e:
            logging.error(e)
            st.error("Error occured. Please refresh your page and try again.")

    if res is not None:
        res_text = ""
        for chunk in res:
            if chunk.candidates:
                res_text += chunk.text
            if res_text == "":
                res_text = "unappropriate words"
                st.error("Your words violate the rules that have been set. Please try again!")
        res_area.markdown(res_text)

        st.header("Buy the Tools Now :")
        for tool in power_tools:
            st.write(f"[{tool['name']}]({tool['link']})")

    maintext = res_text

    # Split the main text into paragraphs
    textArr = maintext.split("\n\n")
    
    # Initialize materialsList as an empty list
    materialsList = []
    toolsList = []
    
    # Check if textArr has at least two paragraphs to avoid index errors
    if len(textArr) >= 2:
        # Get the second paragraph (materials)
        materials = textArr[1]
        materialsList = materials.split('\n')
    
    # Check if textArr has at least four paragraphs to avoid index errors
    if len(textArr) >= 4:
        # Get the fourth paragraph (tools)
        tools = textArr[3]
        toolsList = tools.split('\n')
    
    final_material_list = []
    final_tools_list = []
    
    # Check if the first line of the response contains the word 'material'
    if len(textArr) > 0 and 'material' in textArr[0].lower():
        # Process materials list
        for m in materialsList:
            m = re.sub(r'[^\w\s]+', '', m)
            final_material_list.append(m)
    
        # Process tools list
        for t in toolsList:
            t = re.sub(r'[^\w\s]+', '', t)
            final_material_list.append(t)

        st.header("Material images:")
        # Display images for materials
        for m in final_material_list:
            # Perform Google search for each material
            result = ts.google_search(m, ts.api_key, ts.search_engine_id)
            
            if 'items' in result:
                # Get the first search result
                image_url = result['items'][0]['link']
                try:
                    response = requests.get(image_url)
                    img = response.content
                
                    st.image(img, caption=m, width=100)
                except Exception:
                    pass
            else:
                st.write("No results found for:", m)
                
    else:
        st.write("No materials and tools found in the response.")


        if select_model != "gemini-pro-vision":
            messages.append({"role": "model", "parts": [res_text]})
