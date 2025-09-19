import boto3
import os

s3_bucket = os.environ['BUCKET_NAME']
sample_file = 'textract_sample.jpeg'

def lambda_handler(event, context):
    
    textract_client = boto3.client('textract')
    text2speech = ''
    
    textract_response = textract_client.detect_document_text(
     Document={
         'S3Object': {
             'Bucket': s3_bucket,
             'Name': sample_file
         }
     })
       
    for item in textract_response["Blocks"]:
        if item["BlockType"] == "LINE":
             text2speech = text2speech+' '+item["Text"]
    
    print(text2speech)
    
    # Request speech synthesis
    polly_client = boto3.client('polly')

    response = polly_client.start_speech_synthesis_task(
        VoiceId='Amy',  
        OutputFormat='mp3', 
        OutputS3BucketName=s3_bucket, 
        OutputS3KeyPrefix = 'output', 
        Text = text2speech,
        Engine='neural')