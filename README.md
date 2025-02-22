# Data Backup & Restore for AWS EC2 Volumes

Hi! In this project, I created a few python scripts to automate the backup, cleanup, and restoration of AWS EC2 volumes. I leveraged Python and the Boto3 library to interact with AWS services.

## What I Did

1.  **EC2 Volume Backup:** I wrote a Python script that automatically creates snapshots of EC2 volumes.
    *   **Suggested Picture:** A screenshot of the AWS console showing the created snapshots.

2.  **Old Snapshot Cleanup:** I developed another Python script that identifies and removes old EC2 volume snapshots to manage storage.
    *   **Suggested Picture:** A before-and-after screenshot of the AWS console showing the snapshot list, or a graph depicting storage space over time.

3.  **EC2 Volume Restoration:** I created a Python script to restore EC2 volumes from the created backups.
    *   **Suggested Picture:** A screenshot of the AWS console showing a successfully restored volume, or the output of the script showing the restoration process.
```