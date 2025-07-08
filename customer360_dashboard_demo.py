import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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
    .expand-button {
        background-color: #1f77b4;
        color: white;
        border: none;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        cursor: pointer;
        font-size: 0.8rem;
    }
    .demo-notice {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
    }
    .task-row {
        padding: 0.5rem;
        margin: 0.2rem 0;
        border-left: 3px solid #1f77b4;
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

def safe_date_format(date_val):
    """Safely format a date value, handling NaT and None."""
    if date_val is None:
        return 'No date'
    
    date_str = str(date_val)
    if 'NaT' in date_str:
        return 'No date'
    
    try:
        if hasattr(date_val, 'year'):
            return f"{date_val.year}-{date_val.month:02d}-{date_val.day:02d}"
        else:
            return 'No date'
    except:
        return 'No date'

def get_visible_tickets(df, expanded_items):
    """Get tickets that should be visible based on expanded items."""
    visible_tickets = []
    
    def add_ticket_and_children(ticket_id, level=0):
        # Add the ticket itself
        ticket_row = df[df['ticket_id'] == ticket_id]
        if not ticket_row.empty:
            visible_tickets.append(ticket_id)
            
            # If this ticket is expanded, add its children
            if ticket_id in expanded_items:
                children = df[df['parent'].astype(str) == str(ticket_id)]
                for _, child in children.iterrows():
                    add_ticket_and_children(child['ticket_id'], level + 1)
    
    # Start with epics (tickets with no parent)
    epics = df[df['parent'] == '']
    for _, epic in epics.iterrows():
        add_ticket_and_children(epic['ticket_id'])
    
    return visible_tickets

def create_gantt_chart(df_filtered):
    """Create a Gantt chart using Plotly."""
    if df_filtered.empty:
        st.warning("No data to display. Expand items in the navigation to see the Gantt chart.")
        return None
    
    # Filter out rows with invalid dates
    valid_rows = []
    for idx, row in df_filtered.iterrows():
        start_date = row['start_date']
        due_date = row['due_date']
        
        # Check if start date is valid
        if start_date is None or str(start_date) == 'NaT':
            continue
            
        # If due date is invalid, use start date + 1 day
        if due_date is None or str(due_date) == 'NaT':
            due_date = start_date + timedelta(days=1)
        
        valid_rows.append({
            'ticket_id': row['ticket_id'],
            'summary': row['summary'],
            'status': row['status'],
            'hierarchy_level': row['hierarchy_level'],
            'start_date': start_date,
            'due_date': due_date
        })
    
    if not valid_rows:
        st.info("No tickets with valid dates to display in Gantt chart.")
        return None
    
    # Sort by hierarchy level and start date
    valid_rows.sort(key=lambda x: (x['hierarchy_level'], x['start_date']))
    
    # Color mapping for different levels
    level_colors = {
        0: '#1f77b4',  # Epic - Blue
        1: '#ff7f0e',  # Level 1 - Orange
        2: '#2ca02c',  # Level 2 - Green
        3: '#d62728',  # Level 3 - Red
        4: '#9467bd'   # Level 4 - Purple
    }
    
    # Create Plotly Gantt chart
    fig = go.Figure()
    
    # Add bars for each task
    for row in valid_rows:
        color = level_colors.get(row['hierarchy_level'], '#1f77b4')
        indent = "  " * row['hierarchy_level']
        task_label = f"{indent}{row['ticket_id']} | {row['summary']}"
        
        # Format dates safely for hover
        start_str = safe_date_format(row['start_date'])
        end_str = safe_date_format(row['due_date'])
        
        fig.add_trace(go.Bar(
            name=task_label,
            x=[row['due_date'] - row['start_date']],
            y=[task_label],
            base=row['start_date'],
            orientation='h',
            marker=dict(color=color, opacity=0.7),
            text=row['status'],
            textposition='middle center',
            hovertemplate=f"<b>{row['ticket_id']}</b><br>" +
                         f"Start: {start_str}<br>" +
                         f"End: {end_str}<br>" +
                         f"Status: {row['status']}<br>" +
                         f"Level: {row['hierarchy_level']}<extra></extra>",
            showlegend=False
        ))
    
    # Update layout
    fig.update_layout(
        title={
            'text': "Project Gantt Chart - Hierarchical View",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title="Timeline",
        yaxis_title="Tasks",
        height=max(600, len(valid_rows) * 30),
        xaxis=dict(type='date'),
        yaxis=dict(
            autorange='reversed',
            tickfont={'size': 10}
        ),
        margin=dict(l=300, r=50, t=80, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    # Add grid
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    
    return fig

def main():
    # Demo notice
    st.markdown("""
    <div class="demo-notice">
        <h3>📋 Demo Version</h3>
        <p><strong>Note:</strong> This is a demonstration version with sample data. 
        The actual dashboard connects to live Jira data through OpenSearch.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown('<h1 class="main-header">Customer 360 Dashboard</h1>', unsafe_allow_html=True)
    
    # Load sample data
    try:
        df, summary_data = generate_sample_data()
        st.success(f"✅ Loaded {len(df)} sample tickets successfully!")
    except Exception as e:
        st.error(f"❌ Error loading sample data: {str(e)}")
        return
    
    # Initialize session state for expanded items
    if 'expanded_items' not in st.session_state:
        st.session_state.expanded_items = set()
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_tickets = len(df)
        st.metric("Total Tickets", total_tickets)
    
    with col2:
        epics_count = len(df[df['parent'] == ''])
        st.metric("Epics", epics_count)
    
    with col3:
        status_counts = df['status'].value_counts()
        completed = status_counts.get('Done', 0)
        st.metric("Completed", completed)
    
    with col4:
        in_progress = status_counts.get('In Progress', 0)
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
        # RAG Status
        rag_summary = df['rag'].value_counts()
        st.write("**RAG Status:**")
        for rag, count in rag_summary.items():
            if rag and rag.strip():  # Only show non-empty RAG values
                color = {'Green': '🟢', 'Amber': '🟡', 'Red': '🔴'}.get(rag, '⚪')
                st.write(f"• {color} {rag}: {count}")
    
    # Create two columns for navigation and Gantt chart
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("🗂️ Project Navigation")
        
        # Hierarchical navigation
        def render_hierarchy(parent_id='', level=0):
            if parent_id == '':
                children = df[df['parent'] == '']
            else:
                children = df[df['parent'].astype(str) == str(parent_id)]
            
            for _, child in children.iterrows():
                ticket_id = child['ticket_id']
                summary = child['summary']
                status = child['status']
                
                # Check if this ticket has children
                has_children = len(df[df['parent'].astype(str) == str(ticket_id)]) > 0
                
                # Create indentation
                indent = "  " * level
                
                if has_children:
                    # Expandable item
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
                    
                    # Show children if expanded
                    if is_expanded:
                        render_hierarchy(ticket_id, level + 1)
                else:
                    # Leaf item
                    status_emoji = {"Done": "✅", "In Progress": "🔄", "TO DO": "📋"}.get(status, "📋")
                    st.write(f"{indent}  {status_emoji} **{ticket_id}** | {summary}")
        
        render_hierarchy()
    
    with col2:
        st.subheader("📈 Gantt Chart")
        
        # Get visible tickets based on expanded items
        visible_ticket_ids = get_visible_tickets(df, st.session_state.expanded_items)
        df_filtered = df[df['ticket_id'].isin(visible_ticket_ids)]
        
        if not df_filtered.empty:
            # Create and display Gantt chart
            fig = create_gantt_chart(df_filtered)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Expand items in the navigation to see the Gantt chart.")
    
    # Data table view
    st.subheader("📋 Detailed View")
    if not df_filtered.empty:
        # Show filtered data in a table
        display_df = df_filtered[['ticket_id', 'summary', 'status', 'rag', 'start_date', 'due_date', 'hierarchy_level']].copy()
        
        # Format dates safely
        display_df['start_date'] = display_df['start_date'].apply(safe_date_format)
        display_df['due_date'] = display_df['due_date'].apply(safe_date_format)
        
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("Expand items in the navigation to see detailed data.")

if __name__ == "__main__":
    main()
