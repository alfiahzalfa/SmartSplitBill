import streamlit as st

from modules.data.report_data import ParticipantReportData, ReportData
from modules.utils import format_number_to_currency


def participant_view(participant_report: ParticipantReportData) -> None:
    """Tampilan report untuk satu peserta."""
    with st.container(border=True):
        col_name, col_label, col_total = st.columns([7, 1, 2])
        with col_name:
            st.markdown(f"##### 👤 {participant_report.name}")
        with col_label:
            st.markdown("##### Total:")
        with col_total:
            st.markdown(
                f"##### {format_number_to_currency(int(participant_report.purchased_total))}"
            )

        # Tabel item yang dibeli
        st.table(participant_report.to_dataframe_display())

        # Subtotal item
        st.markdown(
            f"###### Item Subtotal: "
            f"{format_number_to_currency(participant_report.purchased_subtotal)}"
        )

        # Rincian biaya tambahan proporsional
        if participant_report.charges_breakdown:
            st.markdown("###### Additional Charges (Proportional):")
            for name, amount in participant_report.charges_breakdown:
                st.markdown(f"- {name}: {format_number_to_currency(amount)}")

        # Total biaya tambahan
        st.markdown(
            f"###### Total Additional Charges\\*: "
            f"{format_number_to_currency(participant_report.purchased_others)}"
        )


def controller(report: ReportData | None) -> bool:
    """Controller halaman 3: tampilkan report split bill."""
    if report is None:
        st.error("Belum ada report. Selesaikan assignment terlebih dahulu!")
        return False

    # Ringkasan
    grand_total = sum(p.purchased_total for p in report.participants_reports)
    
    st.success("🎉 Success! The bill has been successfully split.")
    st.markdown("### 📊 Split Summary")
    
    with st.container(border=True):
        st.markdown(
            f"<h2 style='text-align: center; color: #1E3A8A;'>Grand Total: {format_number_to_currency(grand_total)}</h2>",
            unsafe_allow_html=True
        )
        st.caption(
            "<div style='text-align: center;'>Additional charges (tax, service charge, discount, etc.) are divided proportionally "
            "based on each participant's item subtotal.</div>",
            unsafe_allow_html=True
        )
        
    st.markdown("---")
    st.markdown("#### Participant Details")

    for participant_report in report.participants_reports:
        participant_view(participant_report)

    st.info("💡 **Catatan:** Pajak, service charge, diskon, dll dibagi sesuai persentase item masing-masing.")
    return False
