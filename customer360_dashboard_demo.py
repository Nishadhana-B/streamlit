import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from sample_data import generate_sample_data

# Set page config
st.set_page_config(
    page_title="Customer 360 Dashboard - Demo",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5rem;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .demo-notice {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
    }
    .gantt-bar {
        height: 20px;
        margin: 2px 0;
        border-radius: 3px;
        display: flex;
        align-items: center;
        padding: 0 8px;
        font-size: 12px;
        color: white;
        font-weight: bold;
    }
    .gantt-done { background-color: #2ca02c; }
    .gantt-inprogress { background-color: #ff7f0e; }
    .gantt-todo { background-color: #d62728; }
</style>
""", unsafe_allow_html=True)

def get_visible_tickets(df, expanded_items):
    """Get tickets that should be visible based on expanded items."""
    visible_tickets = []
    
    def add_ticket_and_children(ticket_id, level=0):
        ticket_row = df[df['ticket_id'] == ticket_id]
        if not ticket_row.empty:
            visible_tickets.append(ticket_id)
            
            if ticket_id in expanded_items:
                children = df[df['parent'].astype(str) == str(ticket_id)]
                for _, child in children.iterrows():
                    add_ticket_and_children(child['ticket_id'], level + 1)
    
    epics = df[df['parent'] == '']
    for _, epic in epics.iterrows():
        add_ticket_and_children(epic['ticket_id'])
    
    return visible_tickets

def create_simple_gantt_chart(df_filtered):
    """Create a simple Gantt chart using Streamlit components."""
    if df_filtered.empty:
        st.warning("No data to display for Gantt chart.")
        return
    
    st.markdown("### 📊 Project Gantt Chart")
    
    # Find date range
    all_dates = []
    for _, row in df_filtered.iterrows():
        start_date = row['start_date'] if not pd.isna(row['start_date']) else datetime.now()
        due_date = row['due_date'] if not pd.isna(row['due_date']) else start_date + timedelta(days=30)
        all_dates.extend([start_date, due_date])
    
    if not all_dates:
        st.warning("No valid dates found for Gantt chart.")
        return
    
    min_date = min(all_dates)
    max_date = max(all_dates)
    total_days = (max_date - min_date).days
    
    if total_days <= 0:
        total_days = 30
    
    # Create Gantt chart
    for _, row in df_filtered.iterrows():
        start_date = row['start_date'] if not pd.isna(row['start_date']) else datetime.now()
        due_date = row['due_date'] if not pd.isna(row['due_date']) else start_date + timedelta(days=30)
        
        start_offset = (start_date - min_date).days
        duration = (due_date - start_date).days
        
        if duration <= 0:
            duration = 1
        
        left_percent = (start_offset / total_days) * 100
        width_percent = (duration / total_days) * 100
        
        status_class = {
            'Done': 'gantt-done',
            'In Progress': 'gantt-inprogress',
            'TO DO': 'gantt-todo'
        }.get(row['status'], 'gantt-todo')
        
        task_name = f"{row['ticket_id']} - {row['summary'][:30]}{'...' if len(row['summary']) > 30 else ''}"
        
        st.markdown(f"""
        <div style="position: relative; width: 100%; height: 30px; background-color: #f0f0f0; margin: 5px 0; border-radius: 3px;">
            <div class="gantt-bar {status_class}" style="position: absolute; left: {left_percent}%; width: {width_percent}%; height: 20px; top: 5px;">
                {task_name}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.caption(f"📅 {start_date.strftime('%Y-%m-%d')} → {due_date.strftime('%Y-%m-%d')} ({duration} days)")

def format_date_column(series):
    """Format a datetime series to string, handling NaT values."""
    return series.apply(lambda x: x.strftime('%Y-%m-%d') if not pd.isna(x) else 'No date')

def main():
    st.markdown("""
    <div class="demo-notice">
        <h3>📋 Demo Version</h3>
        <p><strong>Note:</strong> This is a demonstration version with sample data. 
        The actual dashboard connects to live Jira data through OpenSearch.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-header">Customer 360 Dashboard</h1>', unsafe_allow_html=True)
    
    try:
        df, summary_data = generate_sample_data()
        st.success(f"✅ Loaded {len(df)} sample tickets successfully!")
    except Exception as e:
        st.error(f"❌ Error loading sample data: {str(e)}")
        return
    
    if 'expanded_items' not in st.session_state:
        st.session_state.expanded_items = set()
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tickets", len(df))
    
    with col2:
        st.metric("Epics", len(df[df['parent'] == '']))
    
    with col3:
        completed = len(df[df['status'] == 'Done'])
        st.metric("Completed", completed)
    
    with col4:
        in_progress = len(df[df['status'] == 'In Progress'])
        st.metric("In Progress", in_progress)
    
    # Status breakdown
    st.subheader("📊 Status Overview")
    status_summary = df['status'].value_counts()
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Status Distribution:**")
        for status, count in status_summary.items():
            st.write(f"• {status}: {count}")
    
    with col2:
        rag_summary = df['rag'].value_counts()
        st.write("**RAG Status:**")
        for rag, count in rag_summary.items():
            color = {'Green': '🟢', 'Amber': '🟡', 'Red': '🔴'}.get(rag, '⚪')
            st.write(f"• {color} {rag}: {count}")
    
    # Create navigation and timeline
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("🗂️ Project Navigation")
        
        def render_hierarchy(parent_id='', level=0):
            if parent_id == '':
                children = df[df['parent'] == '']
            else:
                children = df[df['parent'].astype(str) == str(parent_id)]
            
            for _, child in children.iterrows():
                ticket_id = child['ticket_id']
                summary = child['summary']
                status = child['status']
                
                has_children = len(df[df['parent'].astype(str) == str(ticket_id)]) > 0
                indent = "  " * level
                
                if has_children:
                    is_expanded = ticket_id in st.session_state.expanded_items
                    button_text = "▼" if is_expanded else "▶"
                    
                    col_btn, col_text = st.columns([0.1, 0.9])
                    with col_btn:
                        if st.button(button_text, key=f"btn_{ticket_id}"):
                            if is_expanded:
                                st.session_state.expanded_items.discard(ticket_id)
                            else:
                                st.session_state.expanded_items.add(ticket_id)
                            st.rerun()
                    
                    with col_text:
                        status_emoji = {"Done": "✅", "In Progress": "🔄", "TO DO": "📋"}.get(status, "📋")
                        st.write(f"{indent}{status_emoji} **{ticket_id}** | {summary}")
                    
                    if is_expanded:
                        render_hierarchy(ticket_id, level + 1)
                else:
                    status_emoji = {"Done": "✅", "In Progress": "🔄", "TO DO": "📋"}.get(status, "📋")
                    st.write(f"{indent}  {status_emoji} **{ticket_id}** | {summary}")
        
        render_hierarchy()
    
    with col2:
        st.subheader("📈 Project Timeline")
        
        visible_ticket_ids = get_visible_tickets(df, st.session_state.expanded_items)
        df_filtered = df[df['ticket_id'].isin(visible_ticket_ids)]
        
        if not df_filtered.empty:
            # Show timeline
            for _, row in df_filtered.iterrows():
                indent = "  " * row.get('hierarchy_level', 0)
                status_emoji = {"Done": "✅", "In Progress": "🔄", "TO DO": "📋"}.get(row['status'], "📋")
                rag_emoji = {"Green": "🟢", "Amber": "🟡", "Red": "🔴"}.get(row['rag'], "⚪")
                
                start_date = row['start_date'].strftime('%Y-%m-%d') if not pd.isna(row['start_date']) else 'No start date'
                due_date = row['due_date'].strftime('%Y-%m-%d') if not pd.isna(row['due_date']) else 'No due date'
                
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{indent}{row['ticket_id']}** | {row['summary']}")
                    
                    with col2:
                        st.markdown(f"{status_emoji} {row['status']}")
                    
                    with col3:
                        st.markdown(f"{rag_emoji} {row['rag']}")
                    
                    st.caption(f"{indent}📅 {start_date} → {due_date}")
                    st.markdown("---")
        else:
            st.info("Expand items in the navigation to see the project timeline.")
    
    # Gantt Chart
    st.subheader("📊 Gantt Chart")
    if not df_filtered.empty:
        create_simple_gantt_chart(df_filtered)
    else:
        st.info("Expand items in the navigation to see the Gantt chart.")
    
    # Data table
    st.subheader("📋 Detailed View")
    if not df_filtered.empty:
        display_df = df_filtered[['ticket_id', 'summary', 'status', 'rag', 'start_date', 'due_date']].copy()
        display_df['start_date'] = format_date_column(display_df['start_date'])
        display_df['due_date'] = format_date_column(display_df['due_date'])
        
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("Expand items in the navigation to see detailed data.")

if __name__ == "__main__":
    main()
