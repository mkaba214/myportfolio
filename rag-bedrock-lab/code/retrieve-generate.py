import os
import boto3
import json
import sys

boto3_session = boto3.session.Session()
region = boto3_session.region_name

bedrock_agent_runtime_client = boto3.client('bedrock-agent-runtime', region_name='us-east-1')

# Define the Knowledge Base ID and Model ID for the Bedrock Agent Runtime service
kb_id = "<FMI-1>"
print ('kb_id =' + kb_id)
model_id = "<FMI-2>"
model_arn = f'arn:aws:bedrock:us-east-1::foundation-model/{model_id}'
sessionId=""

def retrieveAndGenerate(input_value, kbId, model_arn, sessionId):
    """
    Function to retrieve and generate text using the Bedrock Agent Runtime service.

    Args:
        input_value (str): The input text for the Bedrock Agent Runtime service.
        kbId (str): The Knowledge Base ID for the Bedrock Agent Runtime service.
        model_arn (str): The Amazon Resource Name (ARN) of the model to be used by the Bedrock Agent Runtime service.
        sessionId (str): The session ID for the Bedrock Agent Runtime service (optional).

    This function does not return a value. Instead, it prints the following:
        1. The input values (input_value, kbId, model_arn, sessionId).
        2. A message indicating whether the sessionId is empty or not.
        3. The response from the Bedrock Agent Runtime service's retrieve_and_generate method.
           If a sessionId is provided, it prints the raw response object.
           If no sessionId is provided, it prints the response object in a formatted JSON string.
    """
    print(input_value, kbId, model_arn, sessionId)
    # If a session ID is provided, use the retrieve_and_generate method with the session ID
    if sessionId != "":
        print('sessionId is not empty')
        result = bedrock_agent_runtime_client.retrieve_and_generate(
            input=input_value,
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': kbId,
                    'modelArn': model_arn
                }
            },
            sessionId=sessionId
        )
        print(result)
    else:
        print('sessionId is empty')
        # If no session ID is provided, use the retrieve_and_generate method without a session ID
        result=bedrock_agent_runtime_client.retrieve_and_generate(
            input={
                'text': input_value
            },
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': kbId,
                    'modelArn': model_arn
                }
            }
        )
        print(json.dumps(result, indent=4, default=str))

# Check if the input value is provided
if len(sys.argv) < 2:
    print("Please provide an input value as a command-line argument.")
    sys.exit(1)

# Get the input value from the command line
input_value = sys.argv[1]

# Call the retrieveAndGenerate function with the input value, Knowledge Base ID, Model ARN, and session ID
retrieveAndGenerate(input_value, kb_id, model_arn, sessionId)
