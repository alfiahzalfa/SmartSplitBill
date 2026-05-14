import os
from dataclasses import dataclass, field

import streamlit as st
from babel.numbers import get_currency_name

from modules.data import session_data
from modules.models.loader import ModelNames
from modules.utils import CURRENCY_LIST


@dataclass
class SettingsData:
    currency: str = field(default_factory=session_data.currency.get)
    model_name: ModelNames = field(default_factory=session_data.model_name.get)
    gemini_api_key: str = field(
        default_factory=lambda: os.environ.get("GOOGLE_API_KEY", "")
    )
    groq_api_key: str = field(
        default_factory=lambda: os.environ.get("GROQ_API_KEY", "")
    )

    def apply(self) -> None:
        session_data.currency.set(self.currency)
        if self.model_name != session_data.model_name.get():
            session_data.model.reset()
        session_data.model_name.set(self.model_name)
        if self.gemini_api_key:
            os.environ["GOOGLE_API_KEY"] = self.gemini_api_key
        if self.groq_api_key:
            os.environ["GROQ_API_KEY"] = self.groq_api_key


def currency_settings_view(settings: SettingsData) -> SettingsData:
    currencies = list(CURRENCY_LIST.keys())
    current_idx = currencies.index(settings.currency) if settings.currency in currencies else 0
    selected = st.selectbox(
        "Mata Uang",
        currencies,
        format_func=lambda x: f"{x}: {get_currency_name(x)}",
        index=current_idx,
    )
    settings.currency = selected
    return settings


def model_selection_view(settings: SettingsData) -> SettingsData:
    options = list(ModelNames)
    current_idx = options.index(settings.model_name) if settings.model_name in options else 0
    selected = st.selectbox(
        "Model AI",
        options,
        format_func=lambda x: x.value,
        index=current_idx,
    )

    if selected == ModelNames.GEMINI:
        st.info("Membutuhkan Google API Key dari https://aistudio.google.com")
        key = st.text_input(
            "Google API Key",
            type="password",
            value=settings.gemini_api_key,
        )
        settings.gemini_api_key = key

    elif selected == ModelNames.GROQ:
        st.info(
            "Alternatif gratis jika Gemini kena limit. "
            "Daftar & ambil API key di https://console.groq.com"
        )
        key = st.text_input(
            "Groq API Key",
            type="password",
            value=settings.groq_api_key,
        )
        settings.groq_api_key = key

    elif selected == ModelNames.DONUT:
        st.warning(
            "⚠️ Donut berjalan secara lokal di CPU/GPU. "
            "Proses bisa memakan waktu 45–90 detik di CPU. "
            "Akurasi lebih rendah untuk receipt Indonesia. "
            "Tidak bisa mengekstrak pajak/service charge otomatis."
        )

    settings.model_name = selected
    return settings


@st.dialog("Settings")
def controller(error_msg: str | None = None) -> None:
    if error_msg is not None:
        st.error(error_msg)
    settings = SettingsData()
    settings = currency_settings_view(settings)
    settings = model_selection_view(settings)
    if st.button("Simpan", key="settings_apply_button"):
        settings.apply()
        st.rerun()