# FinOps Dashboard

A Streamlit-based dashboard for monitoring Google Cloud Platform (GCP) resources including VM instances, GCS buckets, and unused persistent disks.

## 🚀 Features
- 🔍 Displays list of VM instances with their status, machine type, and zone
- 🪣 Shows GCS bucket sizes and creation dates
- 🧹 Identifies unused disks along with their size and status
- 🔐 Uses Google Cloud Service Account for authentication
- 📊 Responsive UI with a clean, tabbed interface
- 📈 Summary statistics for each resource type

## 📋 Prerequisites
- Python 3.8 or above
- An active Google Cloud Platform project
- A Service Account with the following roles:
  - `roles/compute.viewer` – Compute Engine Viewer
  - `roles/storage.objectViewer` – Storage Viewer

Enable the following GCP APIs:
- Compute Engine API
- Cloud Storage API

## 🛠 Installation
Clone the repository:
```bash
git clone https://github.com/deepakkumar-m/FinOps-Dashboard.git
cd FinOps-Dashboard

Install dependencies:

pip install -r requirements.txt

Create and configure your service account:

In the Google Cloud Console, create a Service Account with the required roles.
Download the JSON key file for this account.

Set the environment variable to authenticate:
bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/keyfile.json"

▶️ Running the App
Start the Streamlit dashboard:
bash
streamlit run app.py
