import streamlit as st

from modules.data import session_data
from modules.data.assignment_data import (
    AssignedItemData,
    GroupData,
    ParticipantData,
    SplitManager,
)
from modules.utils import format_number_to_currency


def controller() -> bool:
    st.markdown("### 👥 Assign Participants")
    st.info("💡 Tambahkan nama terlebih dahulu, lalu pada setiap item, pilih siapa saja yang akan ikut membayar.")
    
    manager = session_data.split_manager.get()
    if manager is None:
        receipt = session_data.receipt_data.get()
        if receipt is None:
            st.error("Upload a receipt first...")
            return False
        group_data = session_data.group_data.get()
        manager = SplitManager(group_data, receipt)
        session_data.split_manager.set(manager)

    st.markdown("---")
    
    st.markdown("#### 1. Participants")
    col1, col2 = st.columns([7, 3])
    with col1:
        new_name = st.text_input(
            "Name", label_visibility="collapsed", placeholder="Ketik nama di sini..."
        )
    with col2:
        if st.button("➕ Add Person", type="primary", use_container_width=True) and new_name:
            manager.group_data.add(name=new_name)
            st.rerun()

    participants = manager.get_all_participants()
    if not participants:
        st.warning("⚠️ Masukan minimal 1 nama untuk memulai.")
        return False
        
    st.markdown("**Active Participants:**")
    p_cols = st.columns(min(len(participants), 4))
    for i, p in enumerate(participants):
        with p_cols[i % 4]:
            if st.button(f"❌ {p.name}", key=f"del_p_{p.id}", use_container_width=True):
                manager.remove_participant(p.id)
                st.rerun()

    st.markdown("---")

    st.markdown("#### 2. Items")
    manager.participant_assignments.clear()
    
    items = manager.get_all_items()
    all_assigned = True
    
    for item in items:
        state_key = f"item_share_{item.id}"
        
        with st.container(border=True):
            st.markdown(
                f"##### 🍽️ {item.name} "
                f"<span style='color: #64748B; font-size: 0.9em;'>(Qty: {item.count} — {format_number_to_currency(item.total_price)})</span>",
                unsafe_allow_html=True
            )
            
            selected_p_ids = st.multiselect(
                "Shared by:",
                options=[p.id for p in participants],
                format_func=lambda pid: manager.group_data.participants[pid].name,
                key=state_key,
                placeholder="Pilih siapa saja yang ikut makan/minum ini..."
            )
            
            if not selected_p_ids:
                st.markdown("<span style='color: #EF4444; font-size: 0.85em;'>⚠️ Belum ada yang ditugaskan untuk item ini!</span>", unsafe_allow_html=True)
                all_assigned = False
            else:
                split_count = item.count / len(selected_p_ids)
                for pid in selected_p_ids:
                    if pid not in manager.participant_assignments:
                        manager.participant_assignments[pid] = []
                    manager.participant_assignments[pid].append(
                        AssignedItemData(item=item, assigned_count=split_count)
                    )
                
                if len(selected_p_ids) > 1:
                    st.markdown(f"<span style='color: #10B981; font-size: 0.85em;'>✅ Dibagi rata ke {len(selected_p_ids)} orang (masing-masing bayar {format_number_to_currency(item.total_price / len(selected_p_ids))})</span>", unsafe_allow_html=True)

    st.markdown("---")
    
    # --- 3. SUBMIT ---
    if not all_assigned:
        st.warning("⚠️ Pastikan semua item sudah dipilih!")
        
    return st.button("🚀 Calculate Split Bill", type="primary", disabled=not all_assigned, use_container_width=True)