"""
RAG with Amazon Bedrock Knowledge Bases Implementation
=====================================================

This module demonstrates a complete Retrieval-Augmented Generation (RAG)
system using Amazon Bedrock Knowledge Bases for enterprise question-answering.

Author: Mohamed Adama Kaba
Purpose: Intelligent document search and response generation
Services: Amazon Bedrock, Knowledge Bases, OpenSearch Serverless, S3

Features:
- Vector-based semantic search
- Context-aware response generation
- Multi-document knowledge integration
- Query optimization and ranking
"""

import boto3
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    """Data class for query results."""
    query: str
    response: str
    sources: List[str]
    confidence_score: float
    retrieval_count: int
    processing_time: float


class RAGProcessor:
    """
    Advanced RAG implementation using Amazon Bedrock Knowledge Bases.

    This class provides comprehensive functionality for document retrieval
    and response generation using foundation models.
    """

    def __init__(
        self,
        knowledge_base_id: str,
        model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0",
        region_name: str = "us-east-1"
    ):
        """
        Initialize RAG processor with Bedrock services.

        Args:
            knowledge_base_id: ID of the Bedrock Knowledge Base
            model_id: Foundation model ID for response generation
            region_name: AWS region for Bedrock services
        """
        self.knowledge_base_id = knowledge_base_id
        self.model_id = model_id
        self.region_name = region_name

        # Initialize Bedrock clients
        self.bedrock_agent = boto3.client('bedrock-agent-runtime', region_name=region_name)
        self.bedrock_runtime = boto3.client('bedrock-runtime', region_name=region_name)

        logger.info(f"RAG Processor initialized with KB: {knowledge_base_id}")

    def query_knowledge_base(
        self,
        query: str,
        max_results: int = 5,
        confidence_threshold: float = 0.7
    ) -> QueryResult:
        """
        Execute end-to-end RAG query with retrieval and generation.

        Args:
            query: Natural language question
            max_results: Maximum number of documents to retrieve
            confidence_threshold: Minimum confidence score for results

        Returns:
            QueryResult object with response and metadata
        """
        start_time = datetime.now()

        try:
            logger.info(f"Processing query: {query[:100]}...")

            # Step 1: Retrieve relevant documents
            retrieval_results = self._retrieve_documents(query, max_results)

            # Step 2: Filter by confidence threshold
            filtered_results = [
                result for result in retrieval_results
                if result.get('score', 0) >= confidence_threshold
            ]

            if not filtered_results:
                logger.warning(f"No results above confidence threshold {confidence_threshold}")
                return self._create_fallback_response(query, start_time)

            # Step 3: Build context from retrieved documents
            context = self._build_context(filtered_results)

            # Step 4: Generate response using foundation model
            response = self._generate_response(query, context)

            # Step 5: Extract source information
            sources = self._extract_sources(filtered_results)

            processing_time = (datetime.now() - start_time).total_seconds()

            return QueryResult(
                query=query,
                response=response,
                sources=sources,
                confidence_score=max(r.get('score', 0) for r in filtered_results),
                retrieval_count=len(filtered_results),
                processing_time=processing_time
            )

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            raise

    def _retrieve_documents(self, query: str, max_results: int) -> List[Dict]:
        """
        Retrieve relevant documents using vector search.

        Args:
            query: Search query
            max_results: Maximum documents to retrieve

        Returns:
            List of retrieved document chunks with metadata
        """
        try:
            response = self.bedrock_agent.retrieve(
                knowledgeBaseId=self.knowledge_base_id,
                retrievalQuery={'text': query},
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': max_results,
                        'overrideSearchType': 'HYBRID'  # Combines vector and keyword search
                    }
                }
            )

            results = response.get('retrievalResults', [])
            logger.info(f"Retrieved {len(results)} documents")

            return results

        except Exception as e:
            logger.error(f"Document retrieval failed: {e}")
            raise

    def _build_context(self, retrieval_results: List[Dict]) -> str:
        """
        Build context string from retrieved documents.

        Args:
            retrieval_results: List of document chunks from knowledge base

        Returns:
            Formatted context string for LLM prompt
        """
        context_chunks = []

        for idx, result in enumerate(retrieval_results, 1):
            # Extract content and metadata
            content = result['content']['text']
            score = result.get('score', 0)

            # Get source information
            location = result.get('location', {})
            source_uri = ""
            if 's3Location' in location:
                bucket = location['s3Location'].get('uri', '')
                source_uri = bucket

            # Format chunk with metadata
            chunk_header = f"[Document {idx} | Relevance: {score:.2f} | Source: {source_uri}]"
            context_chunks.append(f"{chunk_header}\n{content}\n")

        context = "\n" + "="*50 + "\n".join(context_chunks)

        logger.info(f"Built context from {len(context_chunks)} chunks ({len(context)} characters)")
        return context

    def _generate_response(self, query: str, context: str) -> str:
        """
        Generate response using foundation model with retrieved context.

        Args:
            query: Original user question
            context: Retrieved document context

        Returns:
            Generated response text
        """
        # Create optimized prompt for Claude
        prompt = self._create_rag_prompt(query, context)

        try:
            # Prepare request body for Claude
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "temperature": 0.1,
                "top_p": 0.9,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }

            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )

            response_body = json.loads(response['body'].read())
            generated_text = response_body['content'][0]['text']

            logger.info(f"Generated response ({len(generated_text)} characters)")
            return generated_text

        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            raise

    def _create_rag_prompt(self, query: str, context: str) -> str:
        """
        Create optimized RAG prompt for foundation model.

        Args:
            query: User question
            context: Retrieved document context

        Returns:
            Formatted prompt string
        """
        prompt = f"""You are an expert assistant that provides accurate, helpful answers based on the provided context documents.

**Context Documents:**
{context}

**User Question:** {query}

**Instructions:**
1. Answer the question based ONLY on the information provided in the context documents
2. If the context doesn't contain enough information to fully answer the question, clearly state what information is missing
3. Include specific references to the source documents when possible
4. Provide a comprehensive but concise answer
5. If there are conflicting information in the sources, acknowledge this and explain the differences

**Answer:**"""

        return prompt

    def _extract_sources(self, retrieval_results: List[Dict]) -> List[str]:
        """
        Extract source document information from retrieval results.

        Args:
            retrieval_results: List of retrieved document chunks

        Returns:
            List of source identifiers
        """
        sources = []

        for result in retrieval_results:
            location = result.get('location', {})

            if 's3Location' in location:
                s3_uri = location['s3Location'].get('uri', '')
                if s3_uri and s3_uri not in sources:
                    sources.append(s3_uri)

        return sources

    def _create_fallback_response(self, query: str, start_time: datetime) -> QueryResult:
        """
        Create fallback response when no relevant documents found.

        Args:
            query: Original user question
            start_time: Query start time

        Returns:
            QueryResult with fallback response
        """
        processing_time = (datetime.now() - start_time).total_seconds()

        return QueryResult(
            query=query,
            response="I'm sorry, but I couldn't find relevant information in the knowledge base to answer your question. Please try rephrasing your question or contact support for assistance.",
            sources=[],
            confidence_score=0.0,
            retrieval_count=0,
            processing_time=processing_time
        )


class KnowledgeBaseManager:
    """
    Manager class for Knowledge Base operations and maintenance.
    """

    def __init__(self, region_name: str = "us-east-1"):
        """Initialize Knowledge Base manager."""
        self.bedrock_agent = boto3.client('bedrock-agent', region_name=region_name)
        self.s3_client = boto3.client('s3', region_name=region_name)

    def create_knowledge_base(
        self,
        name: str,
        description: str,
        role_arn: str,
        embedding_model_arn: str,
        collection_arn: str,
        vector_index_name: str
    ) -> str:
        """
        Create a new Knowledge Base with OpenSearch Serverless.

        Args:
            name: Knowledge base name
            description: Knowledge base description
            role_arn: IAM role for Knowledge Base
            embedding_model_arn: ARN of embedding model
            collection_arn: OpenSearch Serverless collection ARN
            vector_index_name: Name of vector index

        Returns:
            Knowledge Base ID
        """
        try:
            response = self.bedrock_agent.create_knowledge_base(
                name=name,
                description=description,
                roleArn=role_arn,
                knowledgeBaseConfiguration={
                    'type': 'VECTOR',
                    'vectorKnowledgeBaseConfiguration': {
                        'embeddingModelArn': embedding_model_arn
                    }
                },
                storageConfiguration={
                    'type': 'OPENSEARCH_SERVERLESS',
                    'opensearchServerlessConfiguration': {
                        'collectionArn': collection_arn,
                        'vectorIndexName': vector_index_name,
                        'fieldMapping': {
                            'vectorField': 'vector',
                            'textField': 'text',
                            'metadataField': 'metadata'
                        }
                    }
                }
            )

            kb_id = response['knowledgeBase']['knowledgeBaseId']
            logger.info(f"Created Knowledge Base: {kb_id}")
            return kb_id

        except Exception as e:
            logger.error(f"Failed to create Knowledge Base: {e}")
            raise

    def add_data_source(
        self,
        knowledge_base_id: str,
        data_source_name: str,
        bucket_arn: str,
        inclusion_prefixes: List[str] = None
    ) -> str:
        """
        Add S3 data source to Knowledge Base.

        Args:
            knowledge_base_id: Target Knowledge Base ID
            data_source_name: Name for the data source
            bucket_arn: S3 bucket ARN containing documents
            inclusion_prefixes: List of S3 prefixes to include

        Returns:
            Data source ID
        """
        try:
            data_source_config = {
                'name': data_source_name,
                'knowledgeBaseId': knowledge_base_id,
                'dataSourceConfiguration': {
                    'type': 'S3',
                    's3Configuration': {
                        'bucketArn': bucket_arn
                    }
                }
            }

            if inclusion_prefixes:
                data_source_config['dataSourceConfiguration']['s3Configuration']['inclusionPrefixes'] = inclusion_prefixes

            response = self.bedrock_agent.create_data_source(**data_source_config)

            data_source_id = response['dataSource']['dataSourceId']
            logger.info(f"Created data source: {data_source_id}")
            return data_source_id

        except Exception as e:
            logger.error(f"Failed to create data source: {e}")
            raise

    def start_ingestion_job(self, knowledge_base_id: str, data_source_id: str) -> str:
        """
        Start document ingestion job for data source.

        Args:
            knowledge_base_id: Knowledge Base ID
            data_source_id: Data source ID

        Returns:
            Ingestion job ID
        """
        try:
            response = self.bedrock_agent.start_ingestion_job(
                knowledgeBaseId=knowledge_base_id,
                dataSourceId=data_source_id
            )

            job_id = response['ingestionJob']['ingestionJobId']
            logger.info(f"Started ingestion job: {job_id}")
            return job_id

        except Exception as e:
            logger.error(f"Failed to start ingestion job: {e}")
            raise


# Example usage and testing functions

def example_rag_usage():
    """
    Example demonstrating RAG system usage.
    """
    # Initialize RAG processor
    rag = RAGProcessor(
        knowledge_base_id="YOUR_KB_ID",
        model_id="anthropic.claude-3-sonnet-20240229-v1:0"
    )

    # Example queries
    queries = [
        "What are the benefits of using microservices architecture?",
        "How do I configure SSL certificates for load balancers?",
        "What is the recommended approach for database migrations?",
        "Explain the differences between REST and GraphQL APIs"
    ]

    for query in queries:
        try:
            result = rag.query_knowledge_base(query)

            print(f"\n{'='*60}")
            print(f"Query: {result.query}")
            print(f"Confidence: {result.confidence_score:.2f}")
            print(f"Sources: {len(result.sources)}")
            print(f"Processing Time: {result.processing_time:.2f}s")
            print(f"\nResponse:\n{result.response}")
            print(f"\nSources:\n{chr(10).join(result.sources)}")

        except Exception as e:
            print(f"Error processing query '{query}': {e}")


if __name__ == "__main__":
    # Run example usage
    example_rag_usage()