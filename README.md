# FinOps Dashboard

A Streamlit-based dashboard for monitoring Google Cloud Platform resources including VM instances, GCS buckets, and unused disks.

## Features
- Displays list of VM instances with their status, machine type, and zone
- Shows GCS bucket sizes and creation dates
- Identifies unused disks with their sizes and status
- Uses Google Cloud service account for authentication
- Responsive UI with tabbed interface
- Summary statistics for each resource type

## Prerequisites
- Python 3.8+
- Google Cloud Platform project
- Service account with appropriate permissions
- Required APIs enabled (Compute Engine, Storage)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/deepakkumar-m/FinOps-Dashboard.git
cd FinOps-Dashboard
