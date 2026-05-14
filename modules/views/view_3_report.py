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
            f"###### Subtotal item: "
            f"{format_number_to_currency(participant_report.purchased_subtotal)}"
        )

        # Rincian biaya tambahan proporsional
        if participant_report.charges_breakdown:
            st.markdown("###### Biaya tambahan (proporsional):")
            for name, amount in participant_report.charges_breakdown:
                st.markdown(f"- {name}: {format_number_to_currency(amount)}")

        # Total biaya tambahan
        st.markdown(
            f"###### Total biaya tambahan\\*: "
            f"{format_number_to_currency(participant_report.purchased_others)}"
        )


def controller(report: ReportData | None) -> bool:
    """Controller halaman 3: tampilkan report split bill."""
    if report is None:
        st.error("Belum ada report. Selesaikan assignment terlebih dahulu!")
        return False

    # Ringkasan
    grand_total = sum(p.purchased_total for p in report.participants_reports)
    st.markdown(
        f"### 📊 Ringkasan — Grand Total: {format_number_to_currency(grand_total)}"
    )
    st.caption(
        "Biaya tambahan (pajak, service charge, dll) dibagi proporsional "
        "sesuai jumlah belanja masing-masing orang."
    )
    st.divider()

    for participant_report in report.participants_reports:
        participant_view(participant_report)

    st.markdown("*\\*pajak, service charge, diskon, dll.*")
    return False
