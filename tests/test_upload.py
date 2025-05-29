import os
from pathlib import Path
from app.utils.file_processor import upload_to_s3
from dotenv import load_dotenv
print(f"Loaded .env from: {os.path.abspath('.env')}")
load_dotenv()

print("DEBUG ENV VALUE:", os.getenv("S3_BUCKET_NAME"))  # Should be 'resume-storage-bucket-priyanka'

from app.config import Config

import boto3
from app.config import Config

def test_s3_connection():
    print("Testing S3 connection...")
    
    # Verify credentials are loaded
    print("\nAWS Configuration:")
    print(f"Access Key ID: {'****'+Config.AWS_ACCESS_KEY_ID[-4:] if Config.AWS_ACCESS_KEY_ID else 'Not set'}")
    print(f"Secret Key: {'****'+Config.AWS_SECRET_ACCESS_KEY[-4:] if Config.AWS_SECRET_ACCESS_KEY else 'Not set'}")
    print(f"Bucket: {Config.S3_BUCKET_NAME}")
    print(f"Region: {Config.S3_REGION}")
    
    # Test basic S3 connection
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
            region_name=Config.S3_REGION
        )
        
        # List buckets to test connection
        response = s3.list_buckets()
        print("\nSuccessfully connected to S3. Available buckets:")
        for bucket in response['Buckets']:
            print(f"- {bucket['Name']}")
            
        # Check if target bucket exists
        if Config.S3_BUCKET_NAME in [b['Name'] for b in response['Buckets']]:
            print(f"\nTarget bucket '{Config.S3_BUCKET_NAME}' exists!")
            
            # Test bucket permissions
            try:
                s3.head_bucket(Bucket=Config.S3_BUCKET_NAME)
                print("You have permission to access this bucket")


                # Test with a sample file
                with open("D:\Btech\Resume Processing System\Resumes\Resumes\Resume 4.pdf", 'rb') as f:
                    file_key = upload_to_s3(f, 'test_resume.pdf')
                    print("File uploaded to:", file_key)
            except Exception as e:
                print(f"Permission error: {e}")
        else:
            print(f"\nTarget bucket '{Config.S3_BUCKET_NAME}' NOT FOUND")
            
    except Exception as e:
        print(f"\nS3 Connection Failed: {e}")

if __name__ == "__main__":
    test_s3_connection()