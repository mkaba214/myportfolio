# RAG with Amazon Bedrock Knowledge Bases Lab

## 🎯 Overview

This lab demonstrates the implementation of Retrieval-Augmented Generation (RAG) using Amazon Bedrock Knowledge Bases. The solution combines the power of large language models with enterprise knowledge bases to create intelligent question-answering systems that provide accurate, contextual responses based on proprietary data.

## 🛠️ Skills Demonstrated

### **AI/ML & Generative AI**
- **Retrieval-Augmented Generation (RAG)**: Advanced AI pattern implementation
- **Amazon Bedrock**: Fully managed foundation model service
- **Knowledge Bases**: Vector database integration and management
- **Embedding Models**: Text vectorization for semantic search
- **Large Language Models**: Integration with Claude, Titan, and other FMs

### **Vector Search & Information Retrieval**
- **Vector Databases**: Semantic similarity search implementation
- **Document Processing**: Automated text extraction and chunking
- **Embedding Generation**: Text-to-vector conversion optimization
- **Search Optimization**: Query processing and result ranking
- **Context Retrieval**: Relevant information extraction for LLM prompts

### **Cloud Architecture & Integration**
- **Serverless Architecture**: Event-driven processing with Lambda
- **Document Storage**: S3-based document management
- **API Development**: RESTful API design for Q&A systems
- **Security Implementation**: IAM roles and access control
- **Monitoring & Logging**: CloudWatch integration for observability

### **Enterprise Knowledge Management**
- **Document Ingestion**: Multi-format document processing
- **Knowledge Organization**: Structured information architecture
- **Query Processing**: Natural language query understanding
- **Response Generation**: Contextual answer creation
- **Quality Assurance**: Accuracy validation and improvement

## 📋 Implementation Steps

### **Step 1: Amazon Bedrock Foundation Model Setup**
1. **Service Enablement**
   - Enable Amazon Bedrock service in AWS Console
   - Request access to foundation models (Claude, Titan, etc.)
   - Configure service quotas and limits

2. **Foundation Model Selection**
   - Evaluate available embedding models
   - Choose appropriate LLM for response generation
   - Configure model parameters and settings

### **Step 2: Knowledge Base Creation**
1. **Vector Store Configuration**
   - Set up vector database (OpenSearch Serverless)
   - Configure index settings and mappings
   - Optimize for semantic search performance

2. **Data Source Integration**
   - Connect S3 bucket as data source
   - Configure document formats and filters
   - Set up automated ingestion triggers

### **Step 3: Document Processing Pipeline**
1. **Document Ingestion**
   - Upload documents to S3 bucket
   - Implement document validation and preprocessing
   - Configure chunking strategies for optimal retrieval

2. **Embedding Generation**
   - Process documents through embedding models
   - Store vectors in knowledge base
   - Optimize chunk size and overlap for accuracy

### **Step 4: RAG System Implementation**
1. **Query Processing**
   - Implement natural language query parsing
   - Configure semantic search parameters
   - Optimize retrieval accuracy and relevance

2. **Response Generation**
   - Integrate retrieved context with LLM prompts
   - Implement prompt engineering best practices
   - Configure response formatting and validation

### **Step 5: Testing & Optimization**
1. **Query Testing**
   - Test various query types and complexities
   - Validate response accuracy and relevance
   - Implement evaluation metrics and benchmarks

2. **Performance Tuning**
   - Optimize vector search parameters
   - Fine-tune chunking strategies
   - Improve response latency and quality

### **Step 6: Production Deployment**
1. **API Development**
   - Create RESTful API endpoints
   - Implement authentication and authorization
   - Add rate limiting and error handling

2. **Monitoring & Analytics**
   - Set up performance monitoring
   - Implement usage analytics
   - Configure alerting for system health

## 🖼️ Lab Screenshots

*Note: Screenshots are stored in the `/screenshots` directory for organized documentation*

### Architecture & Setup
- **System Architecture**: Complete RAG implementation architecture
- **Bedrock Configuration**: Foundation model setup and configuration
- **Knowledge Base Setup**: Vector store creation and configuration

### Document Processing
- **Document Ingestion**: File upload and processing interface
- **Embedding Generation**: Vector creation and storage process
- **Index Configuration**: Search optimization settings

### Query & Response Testing
- **Query Interface**: Testing framework for various question types
- **Response Evaluation**: Accuracy testing and validation results
- **Performance Metrics**: Latency and quality measurements

## 💻 Core Implementation

### RAG Query Processing
```python
import boto3
import json

class RAGProcessor:
    def __init__(self, knowledge_base_id, model_arn):
        self.bedrock_agent = boto3.client('bedrock-agent-runtime')
        self.bedrock_runtime = boto3.client('bedrock-runtime')
        self.kb_id = knowledge_base_id
        self.model_arn = model_arn

    def retrieve_and_generate(self, query, max_results=5):
        """
        Implement RAG pattern: Retrieve relevant context and generate response
        """
        # Step 1: Retrieve relevant documents
        retrieval_response = self.bedrock_agent.retrieve(
            knowledgeBaseId=self.kb_id,
            retrievalQuery={'text': query},
            retrievalConfiguration={
                'vectorSearchConfiguration': {
                    'numberOfResults': max_results
                }
            }
        )

        # Step 2: Extract context from retrieved documents
        context = self._build_context(retrieval_response['retrievalResults'])

        # Step 3: Generate response using LLM with context
        prompt = self._build_prompt(query, context)

        response = self.bedrock_runtime.invoke_model(
            modelId=self.model_arn,
            body=json.dumps({
                'prompt': prompt,
                'max_tokens': 500,
                'temperature': 0.7
            })
        )

        return json.loads(response['body'].read())

    def _build_context(self, retrieval_results):
        """Extract and format context from retrieved documents"""
        context_chunks = []
        for result in retrieval_results:
            chunk_text = result['content']['text']
            source = result['location']['s3Location']['uri']
            context_chunks.append(f"Source: {source}\nContent: {chunk_text}")

        return "\n\n---\n\n".join(context_chunks)

    def _build_prompt(self, query, context):
        """Create optimized prompt for LLM"""
        return f"""
        Based on the following context, please answer the question accurately and concisely.

        Context:
        {context}

        Question: {query}

        Answer: Please provide a detailed answer based only on the information in the context above.
        """
```

### Knowledge Base Configuration
```python
def create_knowledge_base():
    """Set up knowledge base with optimal configuration"""
    bedrock_agent = boto3.client('bedrock-agent')

    kb_config = {
        'name': 'enterprise-knowledge-base',
        'description': 'RAG-enabled enterprise document search',
        'roleArn': 'arn:aws:iam::account:role/BedrockKBRole',
        'knowledgeBaseConfiguration': {
            'type': 'VECTOR',
            'vectorKnowledgeBaseConfiguration': {
                'embeddingModelArn': 'arn:aws:bedrock:region::foundation-model/amazon.titan-embed-text-v1'
            }
        },
        'storageConfiguration': {
            'type': 'OPENSEARCH_SERVERLESS',
            'opensearchServerlessConfiguration': {
                'collectionArn': 'arn:aws:aoss:region:account:collection/kb-collection',
                'vectorIndexName': 'enterprise-index',
                'fieldMapping': {
                    'vectorField': 'vector',
                    'textField': 'text',
                    'metadataField': 'metadata'
                }
            }
        }
    }

    response = bedrock_agent.create_knowledge_base(**kb_config)
    return response['knowledgeBase']
```

## 🚀 Business Impact & Applications

### **Enterprise Knowledge Management**
- **Instant Information Access**: Rapid retrieval of relevant information from vast document repositories
- **Consistent Responses**: Standardized answers based on authoritative sources
- **Knowledge Democratization**: Easy access to specialized information across organizations

### **Customer Support Enhancement**
- **Automated Support**: AI-powered customer service with accurate product information
- **Reduced Resolution Time**: Instant access to troubleshooting guides and solutions
- **24/7 Availability**: Round-the-clock intelligent assistance

### **Research & Development**
- **Literature Review**: Rapid analysis of research papers and technical documentation
- **Patent Analysis**: Intelligent search through patent databases
- **Technical Documentation**: Easy access to engineering specifications and standards

### **Compliance & Legal**
- **Regulatory Guidance**: Quick access to compliance requirements and regulations
- **Policy Interpretation**: Intelligent analysis of legal documents and policies
- **Audit Support**: Rapid retrieval of compliance documentation

## 📁 File Structure

```
rag-bedrock-lab/
├── README.md                    # This comprehensive documentation
├── rag-bedrock.html            # Lab presentation page
├── style.css                   # Custom styling for presentation
├── code/                        # Complete source code directory
│   └── rag_implementation.py    # Full RAG system implementation with Bedrock
└── screenshots/                 # Visual documentation directory
    ├── README.md               # Screenshots organization guide
    └── [screenshot-files]      # Implementation screenshots
```

## 💻 Source Code

The complete RAG implementation is available in the [`code/`](code/) directory:

- **[`rag_implementation.py`](code/rag_implementation.py)** - Production-ready RAG system with Amazon Bedrock Knowledge Bases, including advanced query processing, context building, response generation, and knowledge base management utilities

## 🔧 Technical Requirements

- **AWS Account** with Amazon Bedrock access
- **Foundation Model Access**: Enabled access to embedding and LLM models
- **S3 Bucket**: Document storage and management
- **OpenSearch Serverless**: Vector database for embeddings
- **IAM Roles**: Appropriate permissions for Bedrock services
- **Development Environment**: Python SDK and testing framework

## 📈 Performance Metrics

### **Retrieval Accuracy**
- **Precision**: Percentage of relevant documents retrieved
- **Recall**: Percentage of all relevant documents found
- **F1 Score**: Balanced measure of precision and recall
- **MRR (Mean Reciprocal Rank)**: Quality of ranking algorithm

### **Response Quality**
- **Factual Accuracy**: Correctness of generated responses
- **Relevance Score**: Alignment with user query intent
- **Completeness**: Coverage of question requirements
- **Consistency**: Uniform quality across different queries

### **System Performance**
- **Query Latency**: Average response time for queries
- **Throughput**: Queries processed per second
- **Availability**: System uptime and reliability
- **Cost Efficiency**: Cost per query optimization

## 🔍 Advanced Features

1. **Multi-Modal Support**: Integration with image and document analysis
2. **Real-Time Updates**: Dynamic knowledge base updates
3. **Custom Embeddings**: Domain-specific embedding fine-tuning
4. **Query Analytics**: Comprehensive usage and performance analytics
5. **A/B Testing**: Response quality comparison and optimization

## 🎯 Use Case Examples

### **Technical Documentation Q&A**
- Query: "How do I configure SSL certificates for the load balancer?"
- Response: Context-aware technical guidance with step-by-step instructions

### **Product Information Retrieval**
- Query: "What are the specifications for Model X-2000?"
- Response: Detailed product specifications from official documentation

### **Policy and Procedure Guidance**
- Query: "What is the approval process for expense reports over $1000?"
- Response: Accurate policy information with relevant procedures

---

*This lab demonstrates cutting-edge AI implementation skills essential for building intelligent enterprise applications that leverage organizational knowledge effectively.*