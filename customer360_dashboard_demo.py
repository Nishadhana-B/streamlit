import streamlit as st
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for Streamlit Cloud
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import datetime, timedelta
import io
import base64
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
</style>
""", unsafe_allow_html=True)

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

def create_matplotlib_gantt(df_filtered):
    """Create a professional Gantt chart using matplotlib."""
    if df_filtered.empty:
        st.warning("No data to display in Gantt chart.")
        return None
    
    # Sort by hierarchy level and start date
    df_sorted = df_filtered.sort_values(['hierarchy_level', 'start_date'])
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(16, max(8, len(df_sorted) * 0.8)))
    
    # Color mapping for different levels and statuses
    level_colors = {
        0: '#1f77b4',  # Epic - Blue
        1: '#ff7f0e',  # Level 1 - Orange
        2: '#2ca02c',  # Level 2 - Green
        3: '#d62728',  # Level 3 - Red
        4: '#9467bd'   # Level 4 - Purple
    }
    
    status_alpha = {
        'Done': 0.9,
        'In Progress': 0.7,
        'TO DO': 0.5
    }
    
    # Calculate date range
    min_date = df_sorted['start_date'].min()
    max_date = df_sorted['due_date'].max()
    
    # Add some padding to the date range
    padding = timedelta(days=7)
    min_date -= padding
    max_date += padding
    
    y_positions = {}
    current_y = 0
    
    for idx, row in df_sorted.iterrows():
        # Calculate position and duration
        start_date = row['start_date']
        due_date = row['due_date']
        duration = (due_date - start_date).days
        
        # Get color and alpha based on level and status
        color = level_colors.get(row['hierarchy_level'], '#1f77b4')
        alpha = status_alpha.get(row['status'], 0.7)
        
        # Create bar
        bar_height = 0.6
        y_pos = current_y
        y_positions[row['ticket_id']] = y_pos
        
        # Add background shading for hierarchy levels
        if row['hierarchy_level'] > 0:
            ax.axhspan(y_pos - bar_height/2, y_pos + bar_height/2, 
                      alpha=0.1, color='gray', zorder=0)
        
        # Main task bar
        rect = patches.Rectangle(
            (start_date, y_pos - bar_height/2),
            due_date - start_date,
            bar_height,
            facecolor=color,
            alpha=alpha,
            edgecolor='black',
            linewidth=0.5
        )
        ax.add_patch(rect)
        
        # Add connecting lines to parent
        if row['parent'] and row['parent'] in y_positions:
            parent_y = y_positions[row['parent']]
            ax.plot([start_date, start_date], [parent_y, y_pos], 
                   'k--', alpha=0.3, linewidth=1)
        
        # Add task label
        indent = "  " * row['hierarchy_level']
        task_label = f"{indent}{row['ticket_id']} | {row['summary']}"
        ax.text(min_date + timedelta(days=1), y_pos, task_label,
                va='center', ha='left', fontsize=9, weight='bold')
        
        # Add status indicator
        status_color = {'Done': 'green', 'In Progress': 'orange', 'TO DO': 'red'}
        ax.text(max_date - timedelta(days=1), y_pos, row['status'],
                va='center', ha='right', fontsize=8, 
                color=status_color.get(row['status'], 'black'))
        
        current_y += 1
    
    # Formatting
    ax.set_ylim(-0.5, current_y - 0.5)
    ax.set_xlim(min_date, max_date)
    ax.set_xlabel('Timeline', fontsize=12, weight='bold')
    ax.set_ylabel('Tasks', fontsize=12, weight='bold')
    ax.set_title('Project Gantt Chart - Hierarchical View', fontsize=16, weight='bold', pad=20)
    
    # Format x-axis
    ax.xaxis.set_major_locator(plt.matplotlib.dates.MonthLocator())
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m'))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    # Remove y-axis ticks
    ax.set_yticks([])
    
    # Add grid
    ax.grid(True, alpha=0.3, axis='x')
    
    # Add legend
    legend_elements = [
        patches.Patch(color=level_colors[0], label='Epic'),
        patches.Patch(color=level_colors[1], label='Level 1'),
        patches.Patch(color=level_colors[2], label='Level 2'),
        patches.Patch(color=level_colors[3], label='Level 3'),
        patches.Patch(color=level_colors[4], label='Level 4')
    ]
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1, 1))
    
    plt.tight_layout()
    return fig

def main():
    # Demo notice
    st.markdown("""
    <div class="demo-notice">
        <h3>📋 Demo Version</h3>
        <p>This is a demonstration version using sample data. The full version connects to OpenSearch for real-time Jira data.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">Customer 360 Dashboard</h1>', unsafe_allow_html=True)
    
    # Load sample data
    with st.spinner("Loading sample data..."):
        df, summary_data = generate_sample_data()
    
    # Summary metrics
    st.subheader("📊 Summary Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tickets", summary_data['total_tickets'])
    with col2:
        st.metric("Epics", summary_data['epics'])
    with col3:
        st.metric("Children", summary_data['children'])
    with col4:
        st.metric("With Dates", summary_data['with_dates']['both_dates'])
    
    # Status breakdown
    st.subheader("📈 Status Breakdown")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("TO DO", summary_data['by_status']['TO DO'])
    with col2:
        st.metric("In Progress", summary_data['by_status']['In Progress'])
    with col3:
        st.metric("Done", summary_data['by_status']['Done'])
    
    # RAG status
    st.subheader("🚦 RAG Status")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🟢 Green", summary_data['by_rag']['Green'])
    with col2:
        st.metric("🟡 Amber", summary_data['by_rag']['Amber'])
    with col3:
        st.metric("🔴 Red", summary_data['by_rag']['Red'])
    
    st.markdown("---")
    
    # Hierarchical navigation and Gantt chart
    st.subheader("🗂️ Hierarchical Task Navigation & Gantt Chart")
    
    # Initialize session state for expanded items
    if 'expanded_items' not in st.session_state:
        st.session_state.expanded_items = set()
    
    # Create two columns
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("**Task Hierarchy**")
        
        def render_hierarchy(parent_id='', level=0):
            children = df[df['parent'] == parent_id].sort_values('ticket_id')
            
            for _, row in children.iterrows():
                ticket_id = row['ticket_id']
                has_children = len(df[df['parent'] == ticket_id]) > 0
                is_expanded = ticket_id in st.session_state.expanded_items
                
                # Create indentation
                indent = "  " * level
                
                # Create expand/collapse button for parents
                if has_children:
                    expand_symbol = "▼" if is_expanded else "▶"
                    button_key = f"expand_{ticket_id}"
                    
                    if st.button(f"{indent}{expand_symbol} {ticket_id} | {row['summary']}", 
                               key=button_key, help=f"Status: {row['status']}, RAG: {row['rag']}"):
                        if is_expanded:
                            st.session_state.expanded_items.discard(ticket_id)
                        else:
                            st.session_state.expanded_items.add(ticket_id)
                        st.rerun()
                else:
                    # Regular item without expand button
                    st.write(f"{indent}• {ticket_id} | {row['summary']}")
                    st.caption(f"{indent}  Status: {row['status']}, RAG: {row['rag']}")
                
                # If expanded, show children
                if is_expanded and has_children:
                    render_hierarchy(ticket_id, level + 1)
        
        # Render hierarchy starting from epics
        render_hierarchy()
    
    with col2:
        st.markdown("**Gantt Chart**")
        
        # Get visible tickets based on expanded items (exactly like your local version)
        visible_ticket_ids = get_visible_tickets(df, st.session_state.expanded_items)
        df_filtered = df[df['ticket_id'].isin(visible_ticket_ids)]
        
        if not df_filtered.empty:
            # Create Gantt chart
            fig = create_matplotlib_gantt(df_filtered)
            
            if fig:
                st.pyplot(fig)
                
                # Export functionality
                st.markdown("### 📥 Export Options")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📊 Export PNG"):
                        buf = io.BytesIO()
                        fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
                        buf.seek(0)
                        
                        b64 = base64.b64encode(buf.read()).decode()
                        href = f'<a href="data:image/png;base64,{b64}" download="gantt_chart.png">Download PNG</a>'
                        st.markdown(href, unsafe_allow_html=True)
                
                with col2:
                    if st.button("📋 Export CSV"):
                        csv = df_filtered.to_csv(index=False)
                        b64 = base64.b64encode(csv.encode()).decode()
                        href = f'<a href="data:file/csv;base64,{b64}" download="project_data.csv">Download CSV</a>'
                        st.markdown(href, unsafe_allow_html=True)
        else:
            st.info("Expand items in the hierarchy to see them in the Gantt chart.")
    
    # Footer
    st.markdown("---")
    st.markdown(f"**Last Updated:** {summary_data['extraction_timestamp']}")
    st.markdown("*Demo version with sample data*")

if __name__ == "__main__":
    main() 
