from typing import Callable

import streamlit as st
from PIL import Image

from modules.data import session_data
from modules.data.receipt_data import AdditionalCharge, ReceiptData
from modules.utils import format_number_to_currency

IMAGE_DISPLAY_HEIGHT = 480


def get_items_columns_config() -> dict:
    return {
        "name": "Nama Item",
        "count": "Jumlah",
        "total_price": st.column_config.NumberColumn("Total Harga", format="accounting"),
        "id": None,
    }


def get_charges_columns_config() -> dict:
    return {
        "name": "Keterangan",
        "amount": st.column_config.NumberColumn("Jumlah", format="accounting"),
    }


def resize_to_height(image: Image.Image, target_height: int) -> Image.Image:
    width, height = image.size
    new_width = int(target_height * (width / height))
    return image.resize((new_width, target_height), Image.Resampling.LANCZOS)


def image_input_view() -> Image.Image | None:
    """Widget upload gambar struk."""
    uploaded_file = st.file_uploader(
        "Upload gambar struk belanja",
        type=["jpg", "jpeg", "png"],
        on_change=lambda: session_data.reset_receipt_data(),
    )
    if uploaded_file is None:
        return session_data.image.get()
    image = Image.open(uploaded_file)
    session_data.image.set(image)
    return image


@st.dialog("Membaca struk...")
def read_receipt_view(
    receipt_reader: Callable[[Image.Image], ReceiptData],
    image: Image.Image,
) -> None:
    """Pop-up saat AI sedang membaca struk."""
    _, col, _ = st.columns([4.75, 0.5, 4.75])
    with col:
        with st.spinner(""):
            receipt = receipt_reader(image)
            session_data.view1_model_result.set(receipt)
            st.rerun()


@st.dialog("Konfirmasi Data Struk")
def receipt_read_confirmation_view(receipt: ReceiptData) -> None:
    """
    Pop-up konfirmasi hasil baca AI.
    User bisa edit data sebelum lanjut.
    """
    st.markdown("### Cek dan edit data berikut jika ada yang salah")

    # Item
    st.markdown("#### 🛒 Daftar Item")
    edited_items = st.data_editor(
        receipt.to_items_df(),
        num_rows="dynamic",
        hide_index=True,
        column_config=get_items_columns_config(),
    )
    subtotal = float(edited_items["total_price"].sum())
    st.markdown(f"**Subtotal (item saja): {format_number_to_currency(subtotal)}**")

    # Additional charges
    st.markdown("#### 🧾 Biaya Tambahan (Pajak, Service Charge, Diskon, dll)")
    st.caption("Isi amount negatif untuk diskon. Kosongkan jika tidak ada.")
    edited_charges = st.data_editor(
        receipt.to_charges_df(),
        num_rows="dynamic",
        hide_index=True,
        column_config=get_charges_columns_config(),
    )
    total_charges = float(edited_charges["amount"].sum()) if not edited_charges.empty else 0.0
    st.markdown(f"**Total biaya tambahan: {format_number_to_currency(total_charges)}**")

    # Grand total
    st.markdown("#### 💰 Total Keseluruhan")
    st.caption("Angka ini adalah total akhir yang tertera di struk.")
    edited_total = st.number_input(
        "Total", value=float(receipt.total), label_visibility="collapsed"
    )
    st.markdown(f"**Grand Total: {format_number_to_currency(edited_total)}**")

    # Tombol konfirmasi
    if st.button("✅ Konfirmasi & Lanjut", key="confirm_button"):
        charges = [
            AdditionalCharge(name=str(row["name"]), amount=float(row["amount"]))
            for _, row in edited_charges.iterrows()
            if str(row.get("name", "")).strip()
        ]
        session_data.view1_auto_next_page.set(True)
        session_data.receipt_data.set(
            ReceiptData.from_items_df(edited_items, edited_total, charges)
        )
        st.rerun()


def image_preview_view(image: Image.Image) -> None:
    st.image(resize_to_height(image, IMAGE_DISPLAY_HEIGHT), use_container_width=True)


def final_receipt_view() -> None:
    """Tampilkan data struk yang sudah dikonfirmasi."""
    receipt = session_data.receipt_data.get()
    if receipt is None:
        st.warning("Belum ada data yang terbaca...")
        return

    # Item list
    st.markdown("##### 🛒 Item")
    st.dataframe(
        receipt.to_items_df(),
        hide_index=True,
        column_config=get_items_columns_config(),
    )
    st.markdown(f"**Subtotal: {format_number_to_currency(receipt.subtotal)}**")

    # Additional charges
    if receipt.additional_charges:
        st.markdown("##### 🧾 Biaya Tambahan")
        for ch in receipt.additional_charges:
            st.markdown(f"- {ch.name}: {format_number_to_currency(ch.amount)}")
        st.markdown(
            f"**Total biaya tambahan: "
            f"{format_number_to_currency(receipt.total_additional_charges)}**"
        )

    # Grand total
    st.markdown(f"##### 💰 Total: {format_number_to_currency(receipt.total)}")


def controller(receipt_reader: Callable[[Image.Image], ReceiptData]) -> bool:
    """Controller halaman 1: upload & konfirmasi struk."""
    image = image_input_view()
    if image is None:
        return False

    if session_data.receipt_data.get() is None:
        reading_data = session_data.view1_model_result.get_once()
        if reading_data is None:
            read_receipt_view(receipt_reader, image)
        else:
            receipt_read_confirmation_view(reading_data)

    st.markdown("### Data Struk Kamu")
    col1, col2 = st.columns([3, 7])
    with col1:
        image_preview_view(image)
    with col2:
        final_receipt_view()

    return session_data.view1_auto_next_page.get_once()
