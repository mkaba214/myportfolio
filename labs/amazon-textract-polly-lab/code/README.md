# Code Documentation - Amazon Textract & Polly Integration

## 📁 Code Structure

This directory contains the complete source code and deployment configurations for the Amazon Textract & Polly document processing solution.

### 📄 File Overview

| File | Purpose | Description |
|------|---------|-------------|
| `lambda_function.py` | Original Implementation | Basic Lambda function from the lab |
| `lambda_function_enhanced.py` | Production-Ready Version | Enhanced with error handling, logging, and documentation |
| `requirements.txt` | Dependencies | Python package requirements for deployment |
| `deployment.yaml` | Infrastructure | AWS SAM template for automated deployment |
| `README.md` | Documentation | This file - comprehensive code documentation |

## 🔧 Core Implementation

### Lambda Function Features

#### **Original Implementation (`lambda_function.py`)**
- ✅ Basic text extraction from images using Textract
- ✅ Simple text-to-speech conversion with Polly
- ✅ S3 integration for input and output
- ⚠️ Minimal error handling
- ⚠️ Basic logging

#### **Enhanced Implementation (`lambda_function_enhanced.py`)**
- ✅ Comprehensive error handling and validation
- ✅ Structured logging with detailed information
- ✅ Type hints for better code documentation
- ✅ Configurable via environment variables
- ✅ Support for S3 event triggers
- ✅ Text truncation for Polly limits
- ✅ Standardized response format
- ✅ Monitoring and debugging utilities

## 🚀 Deployment Instructions

### **Method 1: AWS SAM Deployment**

1. **Prerequisites**
   ```bash
   # Install AWS SAM CLI
   pip install aws-sam-cli

   # Configure AWS credentials
   aws configure
   ```

2. **Deploy the application**
   ```bash
   # Build the application
   sam build

   # Deploy with guided setup
   sam deploy --guided

   # For subsequent deployments
   sam deploy
   ```

### **Method 2: Manual Lambda Deployment**

1. **Package the function**
   ```bash
   # Create deployment package
   zip -r textract-polly-function.zip lambda_function.py
   ```

2. **Create Lambda function**
   ```bash
   aws lambda create-function \
     --function-name textract-polly-processor \
     --runtime python3.9 \
     --role arn:aws:iam::ACCOUNT:role/lambda-execution-role \
     --handler lambda_function.lambda_handler \
     --zip-file fileb://textract-polly-function.zip
   ```

3. **Set environment variables**
   ```bash
   aws lambda update-function-configuration \
     --function-name textract-polly-processor \
     --environment Variables='{BUCKET_NAME=your-bucket-name,VOICE_ID=Amy}'
   ```

## 🔐 Required IAM Permissions

### **Lambda Execution Role**

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": "arn:aws:s3:::your-bucket-name/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "textract:DetectDocumentText",
                "textract:AnalyzeDocument"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "polly:StartSpeechSynthesisTask",
                "polly:GetSpeechSynthesisTask"
            ],
            "Resource": "*"
        }
    ]
}
```

## ⚙️ Configuration

### **Environment Variables**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BUCKET_NAME` | ✅ Yes | - | S3 bucket for documents and audio output |
| `SAMPLE_FILE` | ❌ No | `textract_sample.jpeg` | Default document to process |
| `VOICE_ID` | ❌ No | `Amy` | Amazon Polly voice for speech synthesis |
| `OUTPUT_FORMAT` | ❌ No | `mp3` | Audio output format |
| `ENGINE` | ❌ No | `neural` | Polly synthesis engine |

### **Supported File Formats**

#### **Input Documents (Textract)**
- JPEG (.jpg, .jpeg)
- PNG (.png)
- PDF (.pdf) - Single page
- TIFF (.tiff, .tif)

#### **Output Audio (Polly)**
- MP3 (.mp3) - Recommended
- OGG (.ogg)
- PCM (.pcm)

## 🧪 Testing

### **Manual Testing**

1. **Upload test document**
   ```bash
   aws s3 cp test-document.jpg s3://your-bucket-name/
   ```

2. **Invoke function directly**
   ```bash
   aws lambda invoke \
     --function-name textract-polly-processor \
     --payload '{"document_key": "test-document.jpg"}' \
     response.json
   ```

3. **Check output**
   ```bash
   aws s3 ls s3://your-bucket-name/audio/
   ```

### **Automated Testing**

```python
import boto3
import json

# Test function
def test_lambda_function():
    lambda_client = boto3.client('lambda')

    test_payload = {
        "document_key": "test-document.jpg"
    }

    response = lambda_client.invoke(
        FunctionName='textract-polly-processor',
        Payload=json.dumps(test_payload)
    )

    result = json.loads(response['Payload'].read())
    assert result['statusCode'] == 200
```

## 📊 Monitoring & Logging

### **CloudWatch Metrics**

The function automatically generates metrics for:
- ✅ Function duration and memory usage
- ✅ Error rates and success rates
- ✅ Textract API call latency
- ✅ Polly synthesis task completion

### **Custom Logging**

```python
# Example log analysis
aws logs filter-log-events \
  --log-group-name /aws/lambda/textract-polly-processor \
  --filter-pattern "ERROR" \
  --start-time 1640995200000
```

## 🔧 Troubleshooting

### **Common Issues**

1. **Text extraction fails**
   - ✅ Verify document format is supported
   - ✅ Check S3 bucket permissions
   - ✅ Ensure document is not corrupted

2. **Speech synthesis fails**
   - ✅ Check text length (max 100,000 characters)
   - ✅ Verify Polly service quotas
   - ✅ Ensure voice ID is valid

3. **Permission errors**
   - ✅ Verify IAM role has required permissions
   - ✅ Check S3 bucket policies
   - ✅ Ensure services are available in region

### **Debug Mode**

Enable detailed logging by setting log level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🚀 Performance Optimization

### **Best Practices**

1. **Memory Configuration**
   - Recommended: 512MB for average documents
   - Large documents: 1024MB
   - Adjust based on document size

2. **Timeout Settings**
   - Recommended: 300 seconds (5 minutes)
   - Adjust based on document complexity

3. **Batch Processing**
   - Process multiple documents in parallel
   - Use SQS for queuing large batches

## 🔮 Future Enhancements

- [ ] Multi-language support
- [ ] Custom vocabulary for domain-specific terms
- [ ] Real-time streaming synthesis
- [ ] Document format conversion
- [ ] AI-powered content summarization
- [ ] Voice customization and SSML support

---

*This code demonstrates production-ready AWS service integration with comprehensive error handling, monitoring, and deployment automation.*