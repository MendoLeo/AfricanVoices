import streamlit as st
from audio_recorder_streamlit import audio_recorder
import requests
import base64
import tempfile


st.set_page_config(page_title="TTS + S2ST", layout="wide")
API_URL = "https://olamemend-african-voice.hf.space"

st.markdown("##### **🗣️ UNLOCK AFRICAN VOICES**")

st.markdown("""
This app demonstrates both **Text-to-Speech** (TTS) and **Speech-to-Speech** (S2ST).  
AFRICAN VOICES demo: type text or upload audio, choose the language, and get speech output!
""")

# Onglets
tabs = st.tabs(["📝 Text to Speech", "🎤 Speech to Speech"])

# ---------------------- TTS ----------------------
# ---------------------- TTS ----------------------
with tabs[0]:
    st.subheader("📝 -> 🗣️ Text to Speech")

    col1, col2 = st.columns([1.5, 1])

    with col1:
        with st.form("tts_form"):
            # Zone de texte liée à session_state
            tts_text = st.text_area(
                "Enter text",
                height=80,
                label_visibility="collapsed",
                value=st.session_state.get("tts_text", "")
            )

            # Upload fichier (non concerné par le bouton Clear)
            tts_file = st.file_uploader("Or upload a .txt file", type=["txt"])

            # Sélection de langue
            tts_lang = st.selectbox(
                "TTS language",
                ["Ewondo (ewo)", "Bulu (bum)", "Bafia (ksf)"],
            )
            tts_lang_code = tts_lang.split("(")[-1].strip(")")

            # Boutons côte à côte
            btn_cols = st.columns([1, 1], gap="medium")
            with btn_cols[0]:
                submit_tts = st.form_submit_button("🎤 Generate Speech", use_container_width=True)
            with btn_cols[1]:
                clear_tts = st.form_submit_button("🧹 Clear", use_container_width=True)

        # Action Clear
        if clear_tts:
            st.session_state["tts_text"] = ""
            st.rerun()
        else:
            st.session_state["tts_text"] = tts_text

        # Action Submit
        if submit_tts:
            if not tts_text and not tts_file:
                st.warning("Enter text or upload a file.")
            else:
                with col2:
                    st.markdown("**🔊 TTS Output will appear here**")
                    with st.spinner("Generating audio..."):
                        try:
                            files = {"file": tts_file} if tts_file else None
                            data = {"lang": tts_lang_code.lower(), "text": tts_text} if not tts_file else {"lang": tts_lang_code.lower()}

                            response = requests.post(f"{API_URL}/tts/", data=data, files=files)

                            if response.status_code == 200:
                                audio_base64 = base64.b64encode(response.content).decode()
                                audio_html = f"""
                                <div style="background-color:#111827;padding:20px;border-radius:10px;">
                                  <audio controls style="width:100%;">
                                    <source src="data:audio/wav;base64,{audio_base64}" type="audio/wav">
                                    Your browser does not support the audio element.
                                  </audio>
                                </div>
                                """
                                st.markdown(audio_html, unsafe_allow_html=True)
                            else:
                                st.error(f"❌ Error: {response.status_code} - {response.text}")
                        except Exception as e:
                            st.error(f"Connection error: {e}")

    #with col2:
        #st.markdown("**🔊 TTS Output will appear here**")


# ---------------------- S2ST ----------------------
with tabs[1]:
    st.subheader("🎤 -> 🎙️ Speech to Speech")

    input_col, output_col = st.columns([1.2, 1])

    # --------- COLONNE GAUCHE : Upload & Record ---------
    with input_col:
        st.markdown("##### 🎧 Audio Input")
        with st.container(border=True):
            up_col, rec_col = st.columns([5, 1])

            with up_col:
                audio_file = st.file_uploader(
                    "Drop or upload audio",
                    type=["wav", "mp3", "m4a","opus"],
                    label_visibility="collapsed"
                )
                if audio_file is not None:
                    st.session_state["audio_data"] = audio_file.read()
                    st.session_state["audio_source"] = "uploaded"

            with rec_col:
                st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
                recorded_audio = audio_recorder(
                    text="🎙️",
                    recording_color="#e10000",
                    neutral_color="#6aa36f",
                    icon_size="2x",
                    energy_threshold=(-1.0, 1.0),
                    pause_threshold=180.0,  # Enregistrement fixe de 3 minutes
                    sample_rate=16000,
                                )
                
                st.markdown("</div>", unsafe_allow_html=True)
                if recorded_audio is not None:
                    st.session_state["audio_data"] = recorded_audio
                    st.session_state["audio_source"] = "recorded"

            # Aperçu audio (gauche)
            if "audio_data" in st.session_state:
                label = "🔊 Preview (uploaded):" if st.session_state.get("audio_source") == "uploaded" else "🔊 Preview (recorded):"
                st.markdown(label)
                st.audio(st.session_state["audio_data"], format="audio/wav")

    # --------- COLONNE DROITE : Output Audio + Form ---------
    with output_col:
        #st.markdown("##### 🎧 Output Audio")

        # ---- Formulaire avec langue + boutons ----
        with st.form("s2s_submit_form"):
            st.markdown("##### 🌍 Languages", help="Choose the target language and trigger translation.")

            s2s_lang = st.selectbox(
                "Source language", [
                        "français (fr)",
                        "anglais (en)",
                        "chinois (zh)",
                        "espagnol (es)",
                        "arabe (ar)",
                        "hindi (hi)",
                        "portugais (pt)",
                        "russe (ru)",
                        "coréen (ko)",
                        "allemand (de)"
                        ],
                label_visibility="collapsed",
            )
            s2s_lang_code = s2s_lang.split("(")[-1].strip(")")

            btn_cols = st.columns([1, 1], gap="medium")
            with btn_cols[0]:
                submit_s2s = st.form_submit_button("🔁 Translate & Clone", use_container_width=True)
            with btn_cols[1]:
                clear = st.form_submit_button("🧹 Clear", use_container_width=True)
        st.markdown("##### 🎧 Output Audio")

        # --------- ACTIONS ---------
        if clear:
            for key in ["audio_data", "audio_source", "output_audio_base64"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

        if submit_s2s:
            if "audio_data" not in st.session_state:
                st.warning("❗ Please upload or record audio first.")
                st.stop()

            with st.spinner("Translating and cloning..."):
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp:
                        temp.write(st.session_state["audio_data"])
                        temp.flush()
                        files = {"source_audio": open(temp.name, "rb")}
                        data = {"lang": s2s_lang_code}

                        response = requests.post(f"{API_URL}/speech-to-speech/", data=data, files=files)

                        if response.status_code == 200:
                            audio_base64 = base64.b64encode(response.content).decode()
                            st.session_state["output_audio_base64"] = audio_base64
                            #st.success("✅ Output audio ready!")

                            # Affichage direct sans attendre rerun
                            audio_html = f"""
                            <div style="background-color:#111827;padding:20px;border-radius:10px;">
                              <audio controls style="width:100%;">
                                <source src="data:audio/wav;base64,{audio_base64}" type="audio/wav">
                                Your browser does not support the audio element.
                              </audio>
                            </div>
                            """
                            output_col.markdown(audio_html, unsafe_allow_html=True)
                        else:
                            st.error(f"❌ Error: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"Connection error: {e}")

        # Affichage persistant après rechargement
        elif "output_audio_base64" in st.session_state:
            audio_html = f"""
            <div style="background-color:#111827;padding:20px;border-radius:10px;">
              <audio controls style="width:100%;">
                <source src="data:audio/wav;base64,{st.session_state['output_audio_base64']}" type="audio/wav">
                Your browser does not support the audio element.
              </audio>
            </div>
            """
            output_col.markdown(audio_html, unsafe_allow_html=True)
