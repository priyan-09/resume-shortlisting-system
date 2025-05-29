import boto3
from botocore.exceptions import ClientError
from datetime import datetime
from app.config import Config
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_s3_client():
    """Create and return an S3 client with error handling"""
    try:
        return boto3.client(
            's3',
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
            region_name=Config.S3_REGION
        )
    except Exception as e:
        logger.error(f"Error creating S3 client: {e}")
        return None

def upload_to_s3(file, filename):
    """Upload file to S3 bucket with enhanced error handling"""
    s3_client = get_s3_client()
    if not s3_client:
        return None

    try:
        file_key = f"resumes/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
        
        # Verify bucket exists first
        s3_client.head_bucket(Bucket=Config.S3_BUCKET_NAME)
        
        # Upload file
        s3_client.upload_fileobj(
            file,
            Config.S3_BUCKET_NAME,
            file_key
        )
        logger.info(f"Successfully uploaded {filename} to S3")
        return file_key
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '403':
            logger.error("Access Denied - Check your AWS credentials and permissions")
        elif error_code == '404':
            logger.error("Bucket not found - Verify bucket name and region")
        else:
            logger.error(f"S3 upload error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during S3 upload: {e}")
        return None

def get_s3_url(file_key):
    """Generate proper S3 URL for the file"""
    if not file_key:
        logger.error("No file key provided")
        return None
    
    if not all([Config.S3_BUCKET_NAME, Config.S3_REGION]):
        logger.error("Missing S3 configuration")
        return None
    
    # Use virtual-hosted style URL (recommended)
    return f"https://{Config.S3_BUCKET_NAME}.s3.{Config.S3_REGION}.amazonaws.com/{file_key}"