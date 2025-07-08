# Customer 360 Dashboard - Demo Version

## 🎯 Overview
This is a **demonstration version** of the Customer 360 Dashboard that uses sample data instead of connecting to OpenSearch. Perfect for showcasing the dashboard's capabilities to stakeholders without requiring backend infrastructure.

## ✨ Features
- **📊 Interactive Gantt Chart**: Professional timeline visualization with hierarchical task structure
- **🗂️ Hierarchical Navigation**: Expand/collapse task hierarchy with immediate Gantt chart updates
- **📈 Summary Metrics**: Real-time statistics on tickets, status, and RAG indicators
- **📥 Export Options**: Download PNG charts and CSV data
- **🎨 Professional UI**: Clean, modern interface with responsive design

## 🚀 Quick Start

### Local Development
```bash
# Install dependencies
pip install -r demo_requirements.txt

# Run the demo
streamlit run customer360_dashboard_demo.py --server.port 8503
```

### Cloud Deployment (Streamlit Cloud)

1. **Upload to GitHub**:
   - Create a new repository
   - Upload these files:
     - `customer360_dashboard_demo.py`
     - `sample_data.py`
     - `demo_requirements.txt`
     - `DEMO_README.md`

2. **Deploy to Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select your repository
   - Set main file: `customer360_dashboard_demo.py`
   - Deploy!

## 📋 Sample Data Structure
The demo includes realistic sample data representing:
- **3 Epics**: Main project initiatives
- **Multiple hierarchy levels**: Up to 4 levels deep
- **Various statuses**: TO DO, In Progress, Done
- **RAG indicators**: Green, Amber, Red status tracking
- **Realistic timelines**: Spanning several months

## 🛠️ Technical Details

### Key Components
- **`sample_data.py`**: Generates realistic Jira ticket data
- **`customer360_dashboard_demo.py`**: Main dashboard application
- **Hierarchical Navigation**: Expand/collapse functionality with session state
- **Matplotlib Integration**: Professional Gantt chart generation
- **Export Functionality**: PNG and CSV download capabilities

### Architecture
```
Demo Dashboard
├── Sample Data Generator
├── Streamlit UI Components
├── Hierarchical Navigation Logic
├── Matplotlib Gantt Chart
└── Export Functionality
```

## 🎨 UI Features

### Dashboard Sections
1. **Summary Metrics**: Total tickets, epics, children, completion stats
2. **Status Breakdown**: TO DO, In Progress, Done counts
3. **RAG Status**: Green, Amber, Red indicators
4. **Hierarchical Navigation**: Interactive task tree
5. **Gantt Chart**: Professional timeline visualization
6. **Export Options**: Download capabilities

### Interactive Elements
- **▶/▼ Expand/Collapse**: Navigate task hierarchy
- **Real-time Updates**: Gantt chart updates immediately on expansion
- **Professional Formatting**: "CX-44 | Task Summary" ticket display
- **Multi-level Support**: Handle complex nested structures

## 🔄 Differences from Production Version

| Feature | Demo Version | Production Version |
|---------|-------------|-------------------|
| Data Source | Sample data | OpenSearch/Jira API |
| Real-time Updates | Static sample | Live data sync |
| Data Volume | 15 sample tickets | Unlimited tickets |
| Authentication | None | OpenSearch auth |
| Deployment | Streamlit Cloud | Docker containers |

## 🌐 Deployment URLs

After deployment, your dashboard will be available at:
- **Streamlit Cloud**: `https://your-app-name.streamlit.app`
- **Local**: `http://localhost:8503`

## 📞 Support

For questions about the demo version:
1. Check the sample data in `sample_data.py`
2. Review the dashboard code in `customer360_dashboard_demo.py`
3. Test locally before cloud deployment

## 🎯 Next Steps

To convert this demo to production:
1. Replace `sample_data.py` with OpenSearch connection
2. Add authentication mechanisms
3. Implement real-time data refresh
4. Add more comprehensive error handling
5. Scale for larger datasets

---

**Demo Version** - Perfect for stakeholder presentations and feature demonstrations! 