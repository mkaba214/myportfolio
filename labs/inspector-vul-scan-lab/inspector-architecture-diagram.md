# Amazon Inspector Vulnerability Scanning Architecture

## System Architecture Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              AWS Account Environment                                 │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────┐                    ┌─────────────────┐                       │
│  │   AWS Lambda    │                    │    Amazon EC2   │                       │
│  │   Functions     │                    │   Instances     │                       │
│  │                 │                    │                 │                       │
│  │ ┌─────────────┐ │                    │ ┌─────────────┐ │                       │
│  │ │get-request  │ │                    │ │dev-instance │ │                       │
│  │ │function     │ │                    │ │             │ │                       │
│  │ │             │ │                    │ │SSM Agent   │ │                       │
│  │ │requests==   │ │                    │ │v3.x.x       │ │                       │
│  │ │2.20.0       │ │                    │ │             │ │                       │
│  │ │(vulnerable) │ │                    │ │Applications:│ │                       │
│  │ └─────────────┘ │                    │ │- Python     │ │                       │
│  └─────────────────┘                    │ │- Node.js    │ │                       │
│           │                             │ │- etc.       │ │                       │
│           │                             │ └─────────────┘ │                       │
│           │                             │                 │                       │
│           │                             │ ┌─────────────┐ │                       │
│           │                             │ │Security     │ │                       │
│           │                             │ │Groups       │ │                       │
│           │                             │ │             │ │                       │
│           │                             │ │Port 22: SSH │ │                       │
│           │                             │ │(Internet    │ │                       │
│           │                             │ │Gateway)     │ │                       │
│           │                             │ └─────────────┘ │                       │
│           │                             └─────────────────┘                       │
│           │                                      │                                │
│           │                                      │                                │
│           ▼                                      ▼                                │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                        Amazon Inspector                                     │ │
│  │                     Vulnerability Management                                │ │
│  │                                                                             │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐            │ │
│  │  │   Lambda Code   │  │   Lambda Std    │  │   EC2 Agent     │            │ │
│  │  │   Scanning      │  │   Scanning      │  │   Scanning      │            │ │
│  │  │                 │  │                 │  │                 │            │ │
│  │  │ • Code analysis │  │ • Package scan  │  │ • Package scan  │            │ │
│  │  │ • Dependencies  │  │ • CVE detection │  │ • CVE detection │            │ │
│  │  │ • Runtime scan  │  │ • Version check │  │ • Network scan  │            │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘            │ │
│  │           │                     │                     │                    │ │
│  │           └─────────────────────┼─────────────────────┘                    │ │
│  │                                 ▼                                          │ │
│  │  ┌─────────────────────────────────────────────────────────────────────┐  │ │
│  │  │                    Findings Analysis Engine                         │  │ │
│  │  │                                                                     │  │ │
│  │  │ • CVE Database Integration (NIST NVD)                              │  │ │
│  │  │ • CVSS Score Calculation                                           │  │ │
│  │  │ • Severity Assessment (Critical/High/Medium/Low)                   │  │ │
│  │  │ • Network Reachability Analysis                                    │  │ │
│  │  │ • Vulnerability Correlation                                        │  │ │
│  │  └─────────────────────────────────────────────────────────────────────┘  │ │
│  │                                 │                                          │ │
│  └─────────────────────────────────┼──────────────────────────────────────────┘ │
│                                    ▼                                            │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                           Findings Dashboard                                 │ │
│  │                                                                             │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐            │ │
│  │  │   Active        │  │   Suppressed    │  │     Closed      │            │ │
│  │  │   Findings      │  │   Findings      │  │   Findings      │            │ │
│  │  │                 │  │                 │  │                 │            │ │
│  │  │ CVE-2023-32681  │  │ Port 22 SSH     │  │ CVE-2023-32681  │            │ │
│  │  │ requests        │  │ (Suppressed     │  │ requests        │            │ │
│  │  │ (High)          │  │ by rule)        │  │ (Remediated)    │            │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘            │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                            │
│                                    ▼                                            │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                       Remediation Workflows                                 │ │
│  │                                                                             │ │
│  │  ┌─────────────────┐              ┌─────────────────┐                      │ │
│  │  │   Automated     │              │     Manual      │                      │ │
│  │  │  Remediation    │              │   Remediation   │                      │ │
│  │  │                 │              │                 │                      │ │
│  │  │ • Lambda Deploy │              │ • Code Updates  │                      │ │
│  │  │ • SSM Patching  │              │ • Config Changes│                      │ │
│  │  │ • Auto-scaling  │              │ • Suppression   │                      │ │
│  │  └─────────────────┘              └─────────────────┘                      │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                            Integration Services                                      │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐  │
│  │ AWS Systems     │  │   Amazon SNS    │  │   CloudWatch    │  │   AWS Config  │  │
│  │ Manager         │  │                 │  │                 │  │               │  │
│  │                 │  │ • Notifications │  │ • Metrics       │  │ • Compliance  │  │
│  │ • Fleet Manager │  │ • Alerts        │  │ • Logging       │  │ • Rules       │  │
│  │ • Patch Manager │  │ • Reporting     │  │ • Dashboards    │  │ • Auditing    │  │
│  │ • Inventory     │  │                 │  │                 │  │               │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └───────────────┘  │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                            External References                                       │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────┐              ┌─────────────────┐                              │
│  │   NIST NVD      │              │   CVE Database  │                              │
│  │   Database      │              │                 │                              │
│  │                 │              │ • CVE Details   │                              │
│  │ • Vulnerability │              │ • CVSS Scores   │                              │
│  │   Details       │              │ • Remediation   │                              │
│  │ • Scoring       │              │   Guidance      │                              │
│  └─────────────────┘              └─────────────────┘                              │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## Vulnerability Scanning Workflow

### 1. Resource Discovery
- **EC2 Instances**: Automatically discovered via SSM Agent
- **Lambda Functions**: Automatically discovered via service integration
- **ECR Images**: Container image scanning (deactivated in this lab)

### 2. Scanning Types
- **Lambda Standard Scanning**: Package vulnerability detection
- **Lambda Code Scanning**: Static code analysis for vulnerabilities
- **EC2 Agent Scanning**: Package and configuration vulnerability scanning
- **Network Reachability**: Security group and network configuration analysis

### 3. Findings Analysis
- **CVE Integration**: Cross-reference with NIST National Vulnerability Database
- **Severity Scoring**: CVSS-based risk assessment
- **Impact Analysis**: Business and security impact evaluation
- **Remediation Guidance**: Automated recommendations for vulnerability resolution

### 4. Remediation Actions
- **Automated**: Lambda redeployment, SSM patch management
- **Manual**: Code updates, configuration changes, suppression rules
- **Validation**: Continuous scanning to verify remediation effectiveness

This architecture demonstrates a complete vulnerability management lifecycle from discovery through remediation, showcasing enterprise-grade security automation capabilities.