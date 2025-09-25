"""
AWS X-Ray Lambda Function Implementation
=======================================

This Lambda function demonstrates AWS X-Ray tracing integration for
performance monitoring and distributed application debugging.

Author: Mohamed Adama Kaba
Purpose: Showcase X-Ray tracing capabilities in serverless applications
Services: AWS Lambda, AWS X-Ray, Amazon DynamoDB, Amazon API Gateway

Features:
- Automatic AWS service tracing
- Custom segments and subsegments
- Performance annotations and metadata
- Error tracking and debugging
"""

import json
import boto3
import time
import random
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all
from decimal import Decimal
from datetime import datetime

# Patch AWS services for automatic X-Ray tracing
patch_all()

# Initialize AWS clients (automatically traced)
dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')


@xray_recorder.capture('lambda_handler')
def lambda_handler(event, context):
    """
    Main Lambda handler with X-Ray tracing enabled.

    This function demonstrates various X-Ray tracing features:
    - Automatic service tracing
    - Custom segments and subsegments
    - Performance annotations
    - Error handling with tracing
    """

    # Add trace annotations for filtering and search
    xray_recorder.put_annotation('function_name', context.function_name)
    xray_recorder.put_annotation('request_id', context.aws_request_id)

    # Add metadata for additional context
    xray_recorder.put_metadata('event', event)
    xray_recorder.put_metadata('runtime_info', {
        'memory_limit': context.memory_limit_in_mb,
        'remaining_time': context.get_remaining_time_in_millis()
    })

    try:
        # Simulate different request types for demonstration
        request_type = event.get('request_type', 'default')
        xray_recorder.put_annotation('request_type', request_type)

        if request_type == 'database':
            result = handle_database_request(event)
        elif request_type == 'file_processing':
            result = handle_file_processing(event)
        elif request_type == 'external_api':
            result = handle_external_api_call(event)
        else:
            result = handle_default_request(event)

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'X-Trace-Id': xray_recorder.current_segment().trace_id
            },
            'body': json.dumps({
                'message': 'Request processed successfully',
                'result': result,
                'trace_id': xray_recorder.current_segment().trace_id
            })
        }

    except Exception as e:
        # Add exception to X-Ray trace
        xray_recorder.current_segment().add_exception(e)

        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'trace_id': xray_recorder.current_segment().trace_id
            })
        }


@xray_recorder.capture('database_operations')
def handle_database_request(event):
    """
    Handle database operations with detailed X-Ray tracing.
    """

    # Create custom subsegment for business logic
    subsegment = xray_recorder.begin_subsegment('data_validation')
    try:
        # Validate input data
        user_id = event.get('user_id')
        if not user_id:
            raise ValueError("Missing user_id parameter")

        subsegment.put_annotation('user_id', user_id)
        subsegment.put_metadata('validation_rules', {
            'user_id_required': True,
            'format': 'string'
        })

    finally:
        xray_recorder.end_subsegment()

    # Database operations (automatically traced)
    table = dynamodb.Table('bike-users')  # Example table from X-Ray lab

    # Add timing annotation
    start_time = time.time()

    try:
        # Get user information
        response = table.get_item(Key={'user_id': user_id})

        if 'Item' not in response:
            # Create new user record
            user_data = {
                'user_id': user_id,
                'created_at': datetime.now().isoformat(),
                'last_login': datetime.now().isoformat(),
                'login_count': 1
            }
            table.put_item(Item=user_data)
            result = {'action': 'created', 'user': user_data}
        else:
            # Update existing user
            table.update_item(
                Key={'user_id': user_id},
                UpdateExpression='SET last_login = :time, login_count = login_count + :inc',
                ExpressionAttributeValues={
                    ':time': datetime.now().isoformat(),
                    ':inc': 1
                }
            )
            result = {'action': 'updated', 'user_id': user_id}

        # Add performance annotation
        duration = time.time() - start_time
        xray_recorder.put_annotation('db_operation_duration', duration)

        return result

    except Exception as e:
        xray_recorder.put_annotation('db_error', str(e))
        raise


@xray_recorder.capture('file_processing')
def handle_file_processing(event):
    """
    Handle file processing operations with S3 integration.
    """

    bucket_name = event.get('bucket', 'bike-app-files')
    file_key = event.get('file_key', 'sample.txt')

    # Add annotations for filtering
    xray_recorder.put_annotation('bucket_name', bucket_name)
    xray_recorder.put_annotation('file_key', file_key)

    # Custom subsegment for file validation
    with xray_recorder.in_subsegment('file_validation'):
        # Simulate file validation logic
        if not file_key.endswith(('.txt', '.json', '.csv')):
            raise ValueError(f"Unsupported file type: {file_key}")

        xray_recorder.put_metadata('supported_formats', ['.txt', '.json', '.csv'])

    try:
        # Get file from S3 (automatically traced)
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        file_content = response['Body'].read().decode('utf-8')

        # Process file content
        with xray_recorder.in_subsegment('content_processing'):
            # Simulate processing time
            processing_time = random.uniform(0.1, 0.5)
            time.sleep(processing_time)

            lines = file_content.split('\n')
            word_count = sum(len(line.split()) for line in lines)

            xray_recorder.put_annotation('lines_processed', len(lines))
            xray_recorder.put_annotation('word_count', word_count)
            xray_recorder.put_annotation('processing_time', processing_time)

        return {
            'file_key': file_key,
            'lines': len(lines),
            'words': word_count,
            'processing_time': processing_time
        }

    except Exception as e:
        xray_recorder.put_annotation('file_processing_error', str(e))
        raise


@xray_recorder.capture('external_api_call')
def handle_external_api_call(event):
    """
    Simulate external API calls with X-Ray tracing.
    """

    api_endpoint = event.get('api_endpoint', 'https://api.example.com/data')
    xray_recorder.put_annotation('api_endpoint', api_endpoint)

    # Simulate external API call timing
    with xray_recorder.in_subsegment('api_request'):
        # Simulate network latency
        latency = random.uniform(0.1, 2.0)
        time.sleep(latency)

        # Simulate success/failure
        success_rate = 0.9
        if random.random() < success_rate:
            # Successful API call
            response_data = {
                'status': 'success',
                'data': {'temperature': 22, 'humidity': 45},
                'latency': latency
            }
            xray_recorder.put_annotation('api_status', 'success')
            xray_recorder.put_annotation('api_latency', latency)
        else:
            # Failed API call
            xray_recorder.put_annotation('api_status', 'error')
            raise Exception(f"API call failed after {latency:.2f}s")

    return response_data


@xray_recorder.capture('default_processing')
def handle_default_request(event):
    """
    Handle default request type with basic processing.
    """

    # Simulate some business logic
    with xray_recorder.in_subsegment('business_logic'):
        # Add custom annotations
        xray_recorder.put_annotation('operation_type', 'default')

        # Simulate processing
        processing_steps = ['validate', 'transform', 'enrich', 'respond']

        for step in processing_steps:
            with xray_recorder.in_subsegment(f'step_{step}'):
                # Simulate step processing time
                step_time = random.uniform(0.05, 0.2)
                time.sleep(step_time)
                xray_recorder.put_annotation(f'{step}_duration', step_time)

    return {
        'message': 'Default processing completed',
        'steps_completed': len(processing_steps),
        'timestamp': datetime.now().isoformat()
    }


# Utility functions for X-Ray debugging
def get_trace_context():
    """
    Get current X-Ray trace context for debugging.
    """
    segment = xray_recorder.current_segment()
    return {
        'trace_id': segment.trace_id,
        'segment_id': segment.id,
        'sampled': segment.sampled
    }


def add_custom_metric(metric_name, value, unit='Count'):
    """
    Add custom metric to X-Ray trace.
    """
    xray_recorder.put_annotation(f'metric_{metric_name}', value)
    xray_recorder.put_metadata('custom_metrics', {
        metric_name: {'value': value, 'unit': unit}
    })