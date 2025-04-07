FinOps Dashboard
A Streamlit-based dashboard for monitoring Google Cloud Platform (GCP) resources including VM instances, GCS buckets, and unused persistent disks.

🚀 Features
🔍 Displays list of VM instances with their status, machine type, and zone

🪣 Shows GCS bucket sizes and creation dates

🧹 Identifies unused disks along with their size and status

🔐 Uses Google Cloud Service Account for authentication

📊 Responsive UI with a clean, tabbed interface

📈 Summary statistics for each resource type

📋 Prerequisites
Python 3.8 or above

An active Google Cloud Platform project

A Service Account with the following roles:

roles/compute.viewer – Compute Engine Viewer

roles/storage.objectViewer – Storage Viewer

Enable the following GCP APIs:

Compute Engine API

Cloud Storage API

🛠 Installation
Clone the repository:

bash
Copy
Edit
git clone https://github.com/deepakkumar-m/FinOps-Dashboard.git
cd FinOps-Dashboard
Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Create and configure your service account:

In the Google Cloud Console, create a Service Account with the required roles.

Download the JSON key file for this account.

Set the environment variable to authenticate:

bash
Copy
Edit
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/keyfile.json"

▶️ Running the App
Start the Streamlit dashboard:

bash
Copy
Edit
streamlit run app.py
📁 Project Structure
graphql
Copy
Edit
FinOps-Dashboard/
│
├── app.py                   # Main Streamlit app
├── requirements.txt         # Python dependencies
├── utils/
│   ├── gcp_vm.py            # GCP VM data logic
│   ├── gcp_storage.py       # GCS bucket data logic
│   └── gcp_disks.py         # Unused disk logic
├── data/
│   └── sample_output.csv    # Optional sample outputs
└── README.md                # You're here!
📌 Notes
Make sure your GCP billing account is active and that the APIs are enabled.

Use a secure way to store and access your credentials (e.g., Secret Manager or CI/CD secrets in production).

📄 License
This project is licensed under the MIT License.

