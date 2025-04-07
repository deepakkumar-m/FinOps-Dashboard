import streamlit as st
from google.cloud import compute_v1
from google.cloud import storage
import pandas as pd
from google.oauth2 import service_account

# Streamlit page configuration
st.set_page_config(page_title="FinOps Dashboard", layout="wide")

# Function to initialize GCP clients with service account
def initialize_gcp_clients(service_account_file):
    credentials = service_account.Credentials.from_service_account_file(service_account_file)
    
    compute_client = compute_v1.InstancesClient(credentials=credentials)
    storage_client = storage.Client(credentials=credentials)
    disks_client = compute_v1.DisksClient(credentials=credentials)
    
    return compute_client, storage_client, disks_client

# Function to get VM list with status
def get_vm_list(compute_client, project_id, zone):
    vm_list = []
    try:
        instances = compute_client.list(project=project_id, zone=zone)
        for instance in instances:
            vm_list.append({
                'Name': instance.name,
                'Status': instance.status,
                'Machine Type': instance.machine_type.split('/')[-1],
                'Zone': instance.zone.split('/')[-1]
            })
        return pd.DataFrame(vm_list)
    except Exception as e:
        st.error(f"Error fetching VM list: {str(e)}")
        return pd.DataFrame()

# Function to get GCS bucket sizes
def get_bucket_sizes(storage_client):
    bucket_data = []
    try:
        buckets = storage_client.list_buckets()
        for bucket in buckets:
            total_size = 0
            for blob in bucket.list_blobs():
                total_size += blob.size
            bucket_data.append({
                'Bucket Name': bucket.name,
                'Size (GB)': round(total_size / (1024**3), 2),
                'Creation Time': bucket.time_created
            })
        return pd.DataFrame(bucket_data)
    except Exception as e:
        st.error(f"Error fetching bucket sizes: {str(e)}")
        return pd.DataFrame()

# Function to get unused disks
def get_unused_disks(disks_client, project_id, zone):
    disk_list = []
    try:
        disks = disks_client.list(project=project_id, zone=zone)
        for disk in disks:
            if not disk.users:
                disk_list.append({
                    'Disk Name': disk.name,
                    'Size (GB)': disk.size_gb,
                    'Status': disk.status,
                    'Creation Time': disk.creation_timestamp
                })
        return pd.DataFrame(disk_list)
    except Exception as e:
        st.error(f"Error fetching unused disks: {str(e)}")
        return pd.DataFrame()

def main():
    st.title("FinOps Dashboard")
    
    # Sidebar configuration
    st.sidebar.header("Configuration")
    service_account_file = st.sidebar.file_uploader("Upload Service Account JSON", type=['json'])
    project_id = st.sidebar.text_input("GCP Project ID")
    zone = st.sidebar.text_input("Zone", value="us-central1-a")
    
    if service_account_file and project_id:
        # Save uploaded file temporarily
        with open("temp_service_account.json", "wb") as f:
            f.write(service_account_file.getvalue())
        
        # Initialize clients
        compute_client, storage_client, disks_client = initialize_gcp_clients("temp_service_account.json")
        
        # Create tabs for different sections
        tab1, tab2, tab3 = st.tabs(["VM Instances", "GCS Buckets", "Unused Disks"])
        
        # VM Instances Tab
        with tab1:
            st.subheader("Virtual Machine Instances")
            vm_df = get_vm_list(compute_client, project_id, zone)
            if not vm_df.empty:
                st.dataframe(vm_df, use_container_width=True)
                st.write(f"Total VMs: {len(vm_df)}")
                st.write(f"Running VMs: {len(vm_df[vm_df['Status'] == 'RUNNING'])}")
        
        # GCS Buckets Tab
        with tab2:
            st.subheader("GCS Bucket Sizes")
            bucket_df = get_bucket_sizes(storage_client)
            if not bucket_df.empty:
                st.dataframe(bucket_df, use_container_width=True)
                st.write(f"Total Buckets: {len(bucket_df)}")
                st.write(f"Total Size: {bucket_df['Size (GB)'].sum():.2f} GB")
        
        # Unused Disks Tab
        with tab3:
            st.subheader("Unused Disks")
            unused_disks_df = get_unused_disks(disks_client, project_id, zone)
            if not unused_disks_df.empty:
                st.dataframe(unused_disks_df, use_container_width=True)
                st.write(f"Total Unused Disks: {len(unused_disks_df)}")
                st.write(f"Total Unused Size: {unused_disks_df['Size (GB)'].sum()} GB")
    else:
        st.warning("Please upload a service account JSON file and enter Project ID to proceed.")

if __name__ == "__main__":
    main()