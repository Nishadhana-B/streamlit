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
    .gantt-container {
        background-color: white;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
    }
    .gantt-row {
        display: flex;
        align-items: center;
        margin: 3px 0;
        padding: 2px 0;
        border-bottom: 1px solid #f0f0f0;
    }
    .gantt-task-name {
        width: 300px;
        font-size: 12px;
        padding: 5px;
        text-align: left;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .gantt-timeline {
        flex: 1;
        height: 25px;
        position: relative;
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
    }
    .gantt-bar {
        position: absolute;
        height: 20px;
        top: 2px;
        border-radius: 3px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 10px;
        font-weight: bold;
        color: white;
        text-overflow: ellipsis;
        overflow: hidden;
        white-space: nowrap;
        min-width: 2px;
    }
    .gantt-done { background-color: #28a745; }
    .gantt-inprogress { background-color: #ffc107; color: black; }
    .gantt-todo { background-color: #dc3545; }
    .task-level-0 { font-weight: bold; color: #0052CC; }
    .task-level-1 { padding-left: 20px; color: #2E7D32; }
    .task-level-2 { padding-left: 40px; color: #1976D2; }
    .task-level-3 { padding-left: 60px; color: #F57C00; }
    .gantt-header {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
        padding: 5px 0;
        border-bottom: 2px solid #ddd;
        font-weight: bold;
    }
    .gantt-task-header {
        width: 300px;
        padding: 5px;
    }
    .gantt-timeline-header {
        flex: 1;
        text-align: center;
        padding: 5px;
    }
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

def build_hierarchy_tree(df):
    """Build hierarchy tree with proper levels."""
    df_with_hierarchy = df.copy()
    df_with_hierarchy['hierarchy_level'] = 0
    
    def set_hierarchy_level(parent_id, level):
        children = df_with_hierarchy[df_with_hierarchy['parent'].astype(str) == str(parent_id)]
        for idx, child in children.iterrows():
            df_with_hierarchy.at[idx, 'hierarchy_level'] = level
            set_hierarchy_level(child['ticket_id'], level + 1)
    
    # Set hierarchy levels starting from epics (level 0)
    epics = df_with_hierarchy[df_with_hierarchy['parent'] == '']
    for _, epic in epics.iterrows():
        set_hierarchy_level(epic['ticket_id'], 1)
    
    return df_with_hierarchy

def create_professional_gantt_chart(df_filtered):
    """Create a professional Gantt chart matching the image format."""
    if df_filtered.empty:
        st.warning("No data to display for Gantt chart.")
        return
    
    st.markdown("### 📊 Gantt Chart")
    st.markdown(f"Displaying {len(df_filtered)} tickets based on navigation")
    
    # Build hierarchy
    df_hierarchy = build_hierarchy_tree(df_filtered)
    
    # Sort by hierarchy and natural order
    df_sorted = df_hierarchy.sort_values(['hierarchy_level', 'ticket_id']).reset_index(drop=True)
    
    # Find date range
    all_dates = []
    for _, row in df_sorted.iterrows():
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
    
    # Create Gantt chart container
    gantt_html = f"""
    <div class="gantt-container">
        <div class="gantt-header">
            <div class="gantt-task-header">Task Name</div>
            <div class="gantt-timeline-header">Timeline ({min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')})</div>
        </div>
    """
    
    # Create rows for each task
    for _, row in df_sorted.iterrows():
        start_date = row['start_date'] if not pd.isna(row['start_date']) else datetime.now()
        due_date = row['due_date'] if not pd.isna(row['due_date']) else start_date + timedelta(days=30)
        
        start_offset = (start_date - min_date).days
        duration = (due_date - start_date).days
        
        if duration <= 0:
            duration = 1
        
        left_percent = (start_offset / total_days) * 100
        width_percent = (duration / total_days) * 100
        
        # Ensure minimum width for visibility
        if width_percent < 1:
            width_percent = 1
        
        status_class = {
            'Done': 'gantt-done',
            'In Progress': 'gantt-inprogress',
            'TO DO': 'gantt-todo'
        }.get(row['status'], 'gantt-todo')
        
        # Task name with hierarchy
        level = row.get('hierarchy_level', 0)
        task_class = f"task-level-{min(level, 3)}"
        
        # Format task name based on hierarchy
        if level == 0:
            task_display = f"▶ {row['ticket_id']} | {row['summary'][:40]}"
        else:
            indent = "  " * level
            task_display = f"{indent}{row['ticket_id']} | {row['summary'][:35]}"
        
        # Bar content (show ticket ID if bar is wide enough)
        bar_content = row['ticket_id'] if width_percent > 5 else ""
        
        gantt_html += f"""
        <div class="gantt-row">
            <div class="gantt-task-name {task_class}" title="{row['summary']}">{task_display}</div>
            <div class="gantt-timeline">
                <div class="gantt-bar {status_class}" 
                     style="left: {left_percent}%; width: {width_percent}%;"
                     title="{row['ticket_id']}: {start_date.strftime('%Y-%m-%d')} to {due_date.strftime('%Y-%m-%d')} ({duration} days)">
                    {bar_content}
                </div>
            </div>
        </div>
        """
    
    gantt_html += "</div>"
    
    st.markdown(gantt_html, unsafe_allow_html=True)
    
    # Add legend
    st.markdown("""
    **Legend:** 🟢 Done | 🟡 In Progress | 🔴 To Do
    """)

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
    
    # Create navigation and Gantt chart
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("🗂️ Ticket Navigation")
        
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
        
        # Add expand/collapse all buttons
        col_exp, col_col = st.columns(2)
        with col_exp:
            if st.button("🔽 Expand All"):
                parent_ids = set(df['parent'].dropna().unique())
                st.session_state.expanded_items = set(df[df['ticket_id'].isin(parent_ids)]['ticket_id'].tolist())
                st.rerun()
        
        with col_col:
            if st.button("🔼 Collapse All"):
                st.session_state.expanded_items = set()
                st.rerun()
    
    with col2:
        # Get visible tickets based on expanded items
        visible_ticket_ids = get_visible_tickets(df, st.session_state.expanded_items)
        df_filtered = df[df['ticket_id'].isin(visible_ticket_ids)]
        
        # Professional Gantt Chart
        create_professional_gantt_chart(df_filtered)
    
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
