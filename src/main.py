import streamlit as st
from travel_assistant import TravelAssistant

from dotenv import load_dotenv

load_dotenv()

def main():
    st.title("Travel Assistant")
    st.write("Расскажите мне о своих планах путешествия, и я помогу вам открыть для себя удивительные места!")

    # Initialize assistant
    assistant = TravelAssistant()

    # Get user query
    user_query = st.text_input(
        "Какие у вас планы на поездку?",
        placeholder="Пример: Я планирую посетить Лондон в следующем месяце. Какие места мне стоит посетить?"
    )

    if user_query:
        with st.spinner('Анализируем ваш запрос и готовим рекомендации...'):
            try:
                response, aviasales_url = assistant.process_query(user_query)
                st.markdown(response, unsafe_allow_html=True)
                st.image('images/screenshot.png')
                # button_html = f"""
                # <a href="{aviasales_url}" target="_blank" style="text-decoration: none;">
                #     <button style="padding: 10px 20px; font-size: 16px;">Перейти на сайт</button>
                # </a>
                # """
                # st.markdown(button_html, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()