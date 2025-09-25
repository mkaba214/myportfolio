"""
Amazon Textract & Polly Integration Lambda Function
==================================================

This Lambda function demonstrates the integration of Amazon Textract and Amazon Polly
for automated document processing and text-to-speech conversion.

Author: Mohamed Adama Kaba
Purpose: Extract text from documents and convert to audio files
Services: AWS Lambda, Amazon Textract, Amazon Polly, Amazon S3

Workflow:
1. Extract text from image documents using Amazon Textract
2. Process and concatenate extracted text lines
3. Convert text to speech using Amazon Polly's neural engine
4. Store resulting audio file in S3 bucket

Environment Variables Required:
- BUCKET_NAME: S3 bucket for input documents and output audio files
"""

import boto3
import os
import json
import logging
from botocore.exceptions import ClientError, BotoCoreError
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configuration
S3_BUCKET = os.environ.get('BUCKET_NAME')
SAMPLE_FILE = os.environ.get('SAMPLE_FILE', 'textract_sample.jpeg')
VOICE_ID = os.environ.get('VOICE_ID', 'Amy')
OUTPUT_FORMAT = os.environ.get('OUTPUT_FORMAT', 'mp3')
ENGINE = os.environ.get('ENGINE', 'neural')


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler function for document text extraction and speech synthesis.

    Args:
        event: Lambda event data (can contain S3 event triggers)
        context: Lambda context object with runtime information

    Returns:
        Dict containing status code, message, and processing details
    """

    try:
        logger.info("Starting document processing workflow")

        # Extract document filename from event if provided
        document_key = extract_document_key(event)
        if not document_key:
            document_key = SAMPLE_FILE

        logger.info(f"Processing document: {document_key}")

        # Step 1: Extract text using Amazon Textract
        extracted_text = extract_text_from_document(document_key)

        if not extracted_text:
            logger.warning("No text extracted from document")
            return create_response(400, "No text found in document")

        logger.info(f"Extracted text length: {len(extracted_text)} characters")

        # Step 2: Convert text to speech using Amazon Polly
        synthesis_task_id = convert_text_to_speech(extracted_text, document_key)

        if synthesis_task_id:
            logger.info(f"Speech synthesis task started: {synthesis_task_id}")
            return create_response(200, "Document processing completed successfully", {
                "document": document_key,
                "text_length": len(extracted_text),
                "synthesis_task_id": synthesis_task_id,
                "extracted_text_preview": extracted_text[:100] + "..." if len(extracted_text) > 100 else extracted_text
            })
        else:
            return create_response(500, "Failed to start speech synthesis")

    except Exception as e:
        logger.error(f"Error in document processing: {str(e)}")
        return create_response(500, f"Processing error: {str(e)}")


def extract_document_key(event: Dict[str, Any]) -> Optional[str]:
    """
    Extract document key from S3 event trigger or use default.

    Args:
        event: Lambda event data

    Returns:
        Document key string or None if not found
    """

    try:
        # Check if event contains S3 trigger information
        if 'Records' in event:
            for record in event['Records']:
                if record.get('eventSource') == 'aws:s3':
                    return record['s3']['object']['key']

        # Check for direct document specification
        if 'document_key' in event:
            return event['document_key']

        return None

    except (KeyError, TypeError) as e:
        logger.warning(f"Could not extract document key from event: {e}")
        return None


def extract_text_from_document(document_key: str) -> str:
    """
    Extract text from a document using Amazon Textract.

    Args:
        document_key: S3 object key for the document to process

    Returns:
        Concatenated text from all detected text lines

    Raises:
        ClientError: If Textract API call fails
        ValueError: If document format is not supported
    """

    try:
        # Initialize Textract client
        textract_client = boto3.client('textract')

        logger.info(f"Starting text extraction for document: {document_key}")

        # Perform document text detection
        response = textract_client.detect_document_text(
            Document={
                'S3Object': {
                    'Bucket': S3_BUCKET,
                    'Name': document_key
                }
            }
        )

        # Process response and extract text
        extracted_lines = []
        block_count = len(response.get("Blocks", []))

        logger.info(f"Processing {block_count} blocks from Textract response")

        for block in response["Blocks"]:
            if block["BlockType"] == "LINE":
                text_content = block.get("Text", "").strip()
                if text_content:
                    extracted_lines.append(text_content)

        # Combine all text lines
        full_text = ' '.join(extracted_lines)

        logger.info(f"Successfully extracted {len(extracted_lines)} text lines")
        logger.info(f"Text preview: {full_text[:200]}...")

        return full_text

    except ClientError as e:
        error_code = e.response['Error']['Code']
        logger.error(f"Textract API error [{error_code}]: {e}")
        raise

    except Exception as e:
        logger.error(f"Unexpected error in text extraction: {e}")
        raise


def convert_text_to_speech(text: str, source_document: str) -> Optional[str]:
    """
    Convert extracted text to speech using Amazon Polly.

    Args:
        text: Text content to convert to speech
        source_document: Original document name for output file naming

    Returns:
        Synthesis task ID if successful, None otherwise

    Raises:
        ClientError: If Polly API call fails
    """

    try:
        # Initialize Polly client
        polly_client = boto3.client('polly')

        # Validate text content
        if not text or len(text.strip()) == 0:
            logger.warning("Empty text provided for speech synthesis")
            return None

        # Truncate text if too long (Polly has character limits)
        max_chars = 100000  # Polly limit for neural voices
        if len(text) > max_chars:
            text = text[:max_chars]
            logger.warning(f"Text truncated to {max_chars} characters for Polly processing")

        # Generate output filename based on source document
        output_prefix = f"audio/{source_document.split('.')[0]}"

        logger.info(f"Starting speech synthesis with voice: {VOICE_ID}")
        logger.info(f"Output location: s3://{S3_BUCKET}/{output_prefix}")

        # Start speech synthesis task
        response = polly_client.start_speech_synthesis_task(
            VoiceId=VOICE_ID,
            OutputFormat=OUTPUT_FORMAT,
            OutputS3BucketName=S3_BUCKET,
            OutputS3KeyPrefix=output_prefix,
            Text=text,
            Engine=ENGINE,
            LanguageCode='en-US',  # Explicitly set language
            TextType='text'        # Specify text type
        )

        task_id = response['SynthesisTask']['TaskId']
        logger.info(f"Speech synthesis task created successfully: {task_id}")

        return task_id

    except ClientError as e:
        error_code = e.response['Error']['Code']
        logger.error(f"Polly API error [{error_code}]: {e}")
        raise

    except Exception as e:
        logger.error(f"Unexpected error in speech synthesis: {e}")
        raise


def create_response(status_code: int, message: str, data: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Create standardized Lambda response.

    Args:
        status_code: HTTP status code
        message: Response message
        data: Optional additional data

    Returns:
        Formatted response dictionary
    """

    response = {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'message': message,
            'timestamp': context.aws_request_id if 'context' in globals() else 'N/A',
            'data': data or {}
        })
    }

    return response


# Additional utility functions for monitoring and debugging

def get_synthesis_task_status(task_id: str) -> Dict[str, Any]:
    """
    Check the status of a Polly synthesis task.

    Args:
        task_id: Polly synthesis task ID

    Returns:
        Task status information
    """

    try:
        polly_client = boto3.client('polly')
        response = polly_client.get_speech_synthesis_task(TaskId=task_id)
        return response['SynthesisTask']

    except ClientError as e:
        logger.error(f"Error checking synthesis task status: {e}")
        return {}


def validate_environment() -> bool:
    """
    Validate required environment variables and AWS permissions.

    Returns:
        True if environment is properly configured
    """

    if not S3_BUCKET:
        logger.error("BUCKET_NAME environment variable not set")
        return False

    try:
        # Test S3 access
        s3_client = boto3.client('s3')
        s3_client.head_bucket(Bucket=S3_BUCKET)

        # Test Textract access
        textract_client = boto3.client('textract')

        # Test Polly access
        polly_client = boto3.client('polly')
        polly_client.describe_voices(MaxItems=1)

        logger.info("Environment validation successful")
        return True

    except Exception as e:
        logger.error(f"Environment validation failed: {e}")
        return False