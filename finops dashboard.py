import streamlit as st
from google.cloud import compute_v1
from google.cloud import storage
import pandas as pd
from google.oauth2 import service_account
from concurrent.futures import ThreadPoolExecutor, as_completed

# Streamlit page configuration
st.set_page_config(page_title="FinOps Dashboard - All Zones", layout="wide")

# Cache the client initialization
@st.cache_resource
def initialize_gcp_clients(service_account_file):
    credentials = service_account.Credentials.from_service_account_file(service_account_file)
    compute_client = compute_v1.InstancesClient(credentials=credentials)
    storage_client = storage.Client(credentials=credentials)
    disks_client = compute_v1.DisksClient(credentials=credentials)
    region_client = compute_v1.ZonesClient(credentials=credentials)
    return compute_client, storage_client, disks_client, region_client

# Cache zones list with unhashable param fix
@st.cache_data(ttl=3600)
def get_all_zones(_region_client, project_id):
    zones = []
    try:
        for zone in _region_client.list(project=project_id):
            zones.append(zone.name)
        return zones
    except Exception as e:
        st.error(f"Error fetching zones: {str(e)}")
        return []

# Function to get VM list for a single zone
def get_vms_for_zone(_compute_client, project_id, zone):
    vm_list = []
    try:
        instances = _compute_client.list(project=project_id, zone=zone)
        for instance in instances:
            vm_list.append({
                'Name': instance.name,
                'Status': instance.status,
                'Machine Type': instance.machine_type.split('/')[-1],
                'Zone': zone,
                'Creation Time': instance.creation_timestamp
            })
        return vm_list
    except Exception as e:
        st.error(f"Error fetching VMs for zone {zone}: {str(e)}")
        return []

# Parallel VM collection
def get_all_vms(_compute_client, project_id, zones):
    vm_list = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_zone = {executor.submit(get_vms_for_zone, _compute_client, project_id, zone): zone 
                         for zone in zones}
        
        for i, future in enumerate(as_completed(future_to_zone)):
            vm_list.extend(future.result())
            progress = (i + 1) / len(zones)
            progress_bar.progress(progress)
            status_text.text(f"Fetching VMs: {int(progress * 100)}% complete")
    
    progress_bar.empty()
    status_text.empty()
    return pd.DataFrame(vm_list)

# Optimized bucket size calculation with sampling
def get_bucket_size(bucket, sample_size=1000):
    total_size = 0
    blob_count = 0
    try:
        blobs = list(bucket.list_blobs(max_results=sample_size))
        if blobs:
            for blob in blobs:
                total_size += blob.size
                blob_count += 1
            # Estimate total size if we have more objects
            total_blobs = bucket.get_blob_count() if hasattr(bucket, 'get_blob_count') else blob_count
            if total_blobs > sample_size:
                total_size = total_size * (total_blobs / sample_size)
        return {
            'Bucket Name': bucket.name,
            'Size (GB)': round(total_size / (1024**3), 2),
            'Creation Time': bucket.time_created,
            'Location': bucket.location,
            'Object Count': total_blobs
        }
    except Exception as e:
        st.error(f"Error processing bucket {bucket.name}: {str(e)}")
        return None

# Parallel bucket processing with unhashable param fix
@st.cache_data(ttl=3600)
def get_bucket_sizes(_storage_client, _project_id):
    bucket_data = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    buckets = list(_storage_client.list_buckets())
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_bucket = {executor.submit(get_bucket_size, bucket): bucket 
                          for bucket in buckets}
        
        for i, future in enumerate(as_completed(future_to_bucket)):
            result = future.result()
            if result:
                bucket_data.append(result)
            progress = (i + 1) / len(buckets)
            progress_bar.progress(progress)
            status_text.text(f"Fetching bucket sizes: {int(progress * 100)}% complete")
    
    progress_bar.empty()
    status_text.empty()
    return pd.DataFrame(bucket_data)

# Function to get unused disks for a single zone
def get_unused_disks_for_zone(_disks_client, project_id, zone):
    disk_list = []
    try:
        disks = _disks_client.list(project=project_id, zone=zone)
        for disk in disks:
            if not disk.users:
                disk_list.append({
                    'Disk Name': disk.name,
                    'Size (GB)': disk.size_gb,
                    'Status': disk.status,
                    'Zone': zone,
                    'Creation Time': disk.creation_timestamp
                })
        return disk_list
    except Exception as e:
        st.error(f"Error fetching disks for zone {zone}: {str(e)}")
        return []

# Parallel disk collection
def get_all_unused_disks(_disks_client, project_id, zones):
    disk_list = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_zone = {executor.submit(get_unused_disks_for_zone, _disks_client, project_id, zone): zone 
                         for zone in zones}
        
        for i, future in enumerate(as_completed(future_to_zone)):
            disk_list.extend(future.result())
            progress = (i + 1) / len(zones)
            progress_bar.progress(progress)
            status_text.text(f"Fetching unused disks: {int(progress * 100)}% complete")
    
    progress_bar.empty()
    status_text.empty()
    return pd.DataFrame(disk_list)

def main():
    st.title("FinOps Dashboard - All Zones")
    
    st.sidebar.header("Configuration")
    service_account_file = st.sidebar.file_uploader("Upload Service Account JSON", type=['json'])
    project_id = st.sidebar.text_input("GCP Project ID")
    
    if service_account_file and project_id:
        with open("temp_service_account.json", "wb") as f:
            f.write(service_account_file.getvalue())
        
        compute_client, storage_client, disks_client, region_client = initialize_gcp_clients("temp_service_account.json")
        zones = get_all_zones(region_client, project_id)
        st.sidebar.write(f"Found {len(zones)} zones")
        
        tab1, tab2, tab3 = st.tabs(["VM Instances", "GCS Buckets", "Unused Disks"])
        
        with tab1:
            st.subheader("Virtual Machine Instances (All Zones)")
            vm_df = get_all_vms(compute_client, project_id, zones)
            if not vm_df.empty:
                st.dataframe(vm_df, use_container_width=True)
                col1, col2, col3 = st.columns(3)
                col1.metric("Total VMs", len(vm_df))
                col2.metric("Running VMs", len(vm_df[vm_df['Status'] == 'RUNNING']))
                col3.metric("Zones Covered", len(vm_df['Zone'].unique()))
        
        with tab2:
            st.subheader("GCS Buckets")
            bucket_df = get_bucket_sizes(storage_client, project_id)
            if not bucket_df.empty:
                st.dataframe(bucket_df, use_container_width=True)
                col1, col2 = st.columns(2)
                col1.metric("Total Buckets", len(bucket_df))
                col2.metric("Total Size (GB)", f"{bucket_df['Size (GB)'].sum():.2f}")
        
        with tab3:
            st.subheader("Unused Disks (All Zones)")
            unused_disks_df = get_all_unused_disks(disks_client, project_id, zones)
            if not unused_disks_df.empty:
                st.dataframe(unused_disks_df, use_container_width=True)
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Unused Disks", len(unused_disks_df))
                col2.metric("Total Size (GB)", unused_disks_df['Size (GB)'].sum())
                col3.metric("Zones Covered", len(unused_disks_df['Zone'].unique()))
    else:
        st.warning("Please upload a service account JSON file and enter Project ID to proceed.")

if __name__ == "__main__":
    main()
