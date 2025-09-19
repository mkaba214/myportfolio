# Portfolio Access Control Configuration

## 🎯 Objective

Configure the portfolio repository so that main directory files remain private while lab subdirectories are publicly accessible to showcase technical work.

## 🔒 Privacy Requirements

### **Private Files (Main Directory)**
The following files should not be directly accessed by site visitors:

- `home.html` - Personal portfolio page
- `myphoto.jpeg` - Personal photo
- `style.css` / `main-style.css` - Styling files
- `template.json` - Configuration file
- `test.py` - Test scripts
- `README.md` - Project documentation
- `.nojekyll` - GitHub Pages configuration
- `backup/` - Backup directory
- `test/` - Testing directory

### **Public Access (Lab Subdirectories)**
These directories should remain publicly accessible:

- `amazon-textract-polly-lab/` - Document processing lab
- `x-ray-lab/` - Performance monitoring lab
- `rag-bedrock-lab/` - RAG implementation lab
- `capstone-project/` - DevOps capstone project

## 🛠️ Implementation Strategy

### **1. Entry Point Control**
- `index.html` - Redirects to `labs.html` instead of `home.html`
- `labs.html` - Public lab directory page with direct GitHub links
- Visitors land on lab selection page rather than personal portfolio

### **2. Search Engine Control**
- `robots.txt` - Instructs search engines to avoid indexing private files
- Allows crawling of lab subdirectories only
- Discourages indexing of main directory content

### **3. Error Handling**
- `404.html` - Custom error page redirecting to lab directories
- Provides helpful navigation if users try to access restricted content
- Professional presentation of available resources

### **4. Direct Navigation**
All lab pages link directly to GitHub subdirectories:
```html
<a href="https://github.com/mkaba214/myportfolio/tree/main/lab-name"
   target="_blank" rel="noopener noreferrer">
```

## 📋 File Structure

```
myportfolio/
├── 🔒 PRIVATE FILES (Main Directory)
│   ├── home.html                    # Personal portfolio
│   ├── myphoto.jpeg                 # Personal photo
│   ├── style.css                    # Styling
│   ├── README.md                    # Project docs
│   └── backup/, test/               # Development files
│
├── 🌐 PUBLIC ACCESS (Entry Points)
│   ├── index.html                   # Redirects to labs.html
│   ├── labs.html                    # Public lab directory
│   ├── robots.txt                   # Search engine control
│   └── 404.html                     # Error page with lab links
│
└── 📂 PUBLIC LAB SUBDIRECTORIES
    ├── amazon-textract-polly-lab/   # ✅ Public access
    ├── x-ray-lab/                   # ✅ Public access
    ├── rag-bedrock-lab/             # ✅ Public access
    └── capstone-project/            # ✅ Public access
```

## 🎯 User Experience Flow

### **Intended Navigation Path:**
1. User visits `https://mkaba214.github.io/myportfolio/`
2. `index.html` redirects to `labs.html`
3. `labs.html` displays professional lab directory
4. User clicks lab links → GitHub subdirectory pages
5. Access to comprehensive documentation, code, and screenshots

### **If User Tries Direct Access:**
- Main files: Redirected to lab directory via `404.html`
- Lab subdirectories: Direct access as intended
- Search engines: Follow `robots.txt` guidelines

## 🔧 Technical Implementation

### **Robots.txt Configuration**
```
User-agent: *

# Disallow main directory files
Disallow: /home.html
Disallow: /myphoto.jpeg
Disallow: /style.css
# ... other private files

# Allow lab subdirectories
Allow: /amazon-textract-polly-lab/
Allow: /x-ray-lab/
Allow: /rag-bedrock-lab/
Allow: /capstone-project/
```

### **Redirect Configuration**
```html
<!-- index.html -->
<meta http-equiv="refresh" content="0; url=labs.html">

<!-- JavaScript backup -->
setTimeout(function() {
    window.location.href = 'labs.html';
}, 100);
```

## 📊 Benefits

### **Privacy Protection**
- Personal information and development files remain private
- Professional boundary between personal portfolio and technical showcase
- Clean separation of concerns

### **Professional Presentation**
- Visitors see curated technical work immediately
- Direct access to comprehensive lab documentation
- Organized, professional first impression

### **SEO Optimization**
- Search engines index technical work, not personal files
- Lab content appears in search results
- Better discoverability of technical skills

## 🚀 Usage

### **For Site Visitors:**
- Visit main URL → Automatic redirect to lab directory
- Browse professional technical implementations
- Access detailed documentation and source code

### **For Repository Management:**
- Main directory remains functional for development
- Lab subdirectories serve as public showcase
- Clean separation between private and public content

---

*This configuration ensures that technical work is prominently displayed while maintaining privacy for personal portfolio elements.*