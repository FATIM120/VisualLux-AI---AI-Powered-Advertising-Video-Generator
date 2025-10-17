# VisualLux AI - AI-Powered Advertising Video Generator

<div align="center">

![VisualLux AI](https://img.shields.io/badge/VisualLux-AI%20Video%20Generator-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![Flask](https://img.shields.io/badge/Flask-2.0+-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Transform static images into dynamic advertising videos with the power of Generative AI**

[Features](#features) • [Demo](#demo) • [Installation](#installation) • [Usage](#usage) • [Technologies](#technologies) • [Contact](#contact)

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Technologies Used](#technologies-used)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage Guide](#usage-guide)
- [API Documentation](#api-documentation)
- [Performance Metrics](#performance-metrics)
- [Limitations](#limitations)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## 🎯 Overview

**VisualLux AI** is an innovative web application that leverages cutting-edge Generative AI technologies to automatically create professional advertising videos from static images and text descriptions. Built as a Master's project at INSEA (Institut National de Statistique et d'Économie Appliquée), this system democratizes video content creation by making it accessible to non-technical users.

The application combines multiple AI models in a seamless pipeline:
- **Stable Video Diffusion XT (SVD-XT)** for transforming static images into dynamic video sequences
- **Google Gemini API** for intelligent script enhancement and optimization
- **Google Text-to-Speech (gTTS)** for high-quality voice narration
- **MoviePy** for professional video assembly and synchronization

---

## ✨ Key Features

### 🎬 **Automated Video Generation**
- Upload 1-10 images (JPEG/PNG format)
- Automatic transformation of static images into fluid video sequences
- Professional transitions and animations

### 📝 **AI-Powered Script Enhancement**
- Input simple product descriptions
- Gemini API automatically enriches and structures advertising scripts
- Multi-language support (English, Spanish, French, and more)

### 🎙️ **Professional Voice Synthesis**
- High-quality text-to-speech narration
- Natural-sounding voices in multiple languages
- Perfect synchronization with visual content

### 🖥️ **Intuitive User Interface**
- Drag-and-drop image upload
- Real-time progress tracking
- Instant video preview and download
- Mobile-responsive design

### ⚡ **Efficient Processing**
- Optimized pipeline reducing production time from weeks to minutes
- Real-time feedback on generation progress
- Automatic resource management and cleanup

---

## 🏗️ System Architecture
```
┌─────────────────┐
│  User Interface │  (HTML/CSS/JavaScript)
│   (Frontend)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Flask Backend  │  (Python)
│   API Server    │
└────────┬────────┘
         │
    ┌────┴─────────────────────┐
    │                          │
    ▼                          ▼
┌──────────┐          ┌─────────────────┐
│ Gemini   │          │  Stable Video   │
│   API    │          │   Diffusion XT  │
│(Script)  │          │  (SVD-XT 1.7B)  │
└──────────┘          └─────────────────┘
    │                          │
    ▼                          ▼
┌──────────┐          ┌─────────────────┐
│  gTTS    │          │    MoviePy      │
│ (Voice)  │──────────│  (Assembly)     │
└──────────┘          └─────────────────┘
                              │
                              ▼
                      ┌─────────────────┐
                      │  Final MP4      │
                      │  Video Output   │
                      └─────────────────┘
```

### **Processing Pipeline:**

1. **Input Stage**: User uploads images and provides text description
2. **Script Enhancement**: Gemini API optimizes and structures the advertising script
3. **Voice Synthesis**: gTTS converts script to professional narration audio
4. **Video Generation**: SVD-XT transforms each image into animated sequences
5. **Assembly**: MoviePy synchronizes audio with video, applies transitions
6. **Output**: Final MP4 video ready for download

---

## 🛠️ Technologies Used

### **Frontend Technologies**

| Technology | Version | Purpose |
|------------|---------|---------|
| **HTML5** | - | Semantic structure and content organization |
| **CSS3** | - | Modern styling with Flexbox/Grid layouts |
| **JavaScript (ES6+)** | - | Dynamic interactions and async operations |
| **FileReader API** | - | Client-side image preview and validation |

### **Backend Technologies**

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.8+ | Core programming language |
| **Flask** | 2.0+ | Lightweight web framework and REST API |
| **Flask-CORS** | - | Cross-Origin Resource Sharing handling |

### **AI & Machine Learning**

| Technology | Parameters | Purpose |
|------------|-----------|---------|
| **Stable Video Diffusion XT** | 1.7B | Image-to-video generation engine |
| **Google Gemini API** | - | Script enhancement and optimization |
| **Google Text-to-Speech (gTTS)** | - | High-quality voice synthesis |
| **Hugging Face Transformers** | - | Model loading and inference |

### **Video Processing**

| Library | Purpose |
|---------|---------|
| **MoviePy** | Video assembly, audio synchronization, transitions |
| **OpenCV** | Image processing and manipulation |
| **Pillow (PIL)** | Image format handling and preprocessing |

### **Development & Deployment**

| Tool | Purpose |
|------|---------|
| **Git** | Version control |
| **pip** | Python package management |
| **dotenv** | Environment variable management |

---

## 📁 Project Structure
```
VisualLux-AI/
│
├── 📂 output/                    # Generated video output directory
│   └── video_généré.mp4         # Example generated video
│
├── 📂 photos/                    # User uploaded images storage
│   ├── image1.jpg
│   ├── image2.png
│   └── ...
│
├── 📂 static/                    # Static assets
│   ├── 📂 css/
│   │   └── styles.css           # Main stylesheet
│   ├── 📂 js/
│   │   └── main.js              # Frontend JavaScript logic
│   └── 📂 images/
│       └── logo.png
│
├── 📂 templates/                 # HTML templates
│   ├── index.html               # Main application interface
│   ├── progress.html            # Progress tracking page
│   ├── faq.html                 # FAQ section
│   └── testimonials.html        # User reviews section
│
├── 📄 .env                       # Environment variables (API keys)
├── 📄 ad_generator.py            # Core video generation logic
├── 📄 app.py                     # Flask application entry point
├── 📄 chatbot.py                 # AI chatbot integration
├── 📄 requirements.txt           # Python dependencies
├── 📄 README.md                  # This file
└── 📄 LICENSE                    # MIT License
```

---

## 🚀 Installation

### **Prerequisites**

- **Python 3.8+** installed
- **CUDA-compatible GPU** (12GB+ VRAM recommended for optimal performance)
- **Git** for cloning the repository
- **API Keys**: Google Gemini API key

### **Step 1: Clone the Repository**
```bash
git clone https://github.com/yourusername/visuallux-ai.git
cd visuallux-ai
```

### **Step 2: Create Virtual Environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### **Step 3: Install Dependencies**
```bash
pip install -r requirements.txt
```

**Key Dependencies:**
```txt
flask==2.3.0
flask-cors==4.0.0
torch==2.0.1
transformers==4.30.0
diffusers==0.18.0
moviepy==1.0.3
gtts==2.3.2
google-generativeai==0.3.0
pillow==9.5.0
opencv-python==4.8.0
python-dotenv==1.0.0
```

### **Step 4: Configure Environment Variables**

Create a `.env` file in the project root:
```env
# Google Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your_secret_key_here

# Model Configuration
MODEL_PATH=stabilityai/stable-video-diffusion-img2vid-xt
MAX_IMAGES=10
VIDEO_RESOLUTION=1024x576
VIDEO_FPS=24

# Storage Paths
UPLOAD_FOLDER=photos
OUTPUT_FOLDER=output
```

### **Step 5: Download AI Models**

The application will automatically download required models on first run. Ensure you have:
- **~8GB free disk space** for SVD-XT model
- **Stable internet connection** for initial model download

---

## ⚙️ Configuration

### **GPU Configuration**

For optimal performance with CUDA:
```python
# In ad_generator.py
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
torch.backends.cudnn.benchmark = True
```

### **Memory Optimization**

For systems with limited GPU memory:
```python
# Enable model offloading
pipe = StableVideoDiffusionPipeline.from_pretrained(
    "stabilityai/stable-video-diffusion-img2vid-xt",
    torch_dtype=torch.float16,
    variant="fp16"
)
pipe.enable_model_cpu_offload()
```

---

## 📖 Usage Guide

### **Starting the Application**
```bash
python app.py
```

The application will start on `http://localhost:5000`

### **Creating Your First Video**

1. **Upload Images** (1-10 images)
   - Drag and drop images into the upload zone
   - Or click to select files from your computer
   - Supported formats: JPEG, PNG
   - Recommended resolution: 512x512 to 1024x1024 pixels

2. **Enter Description**
   - Describe your product or service
   - Example: *"Promote Brande, a Spanish skincare brand using natural flower oils to hydrate and enhance skin"*
   - Be specific about target audience and key benefits

3. **Select Language**
   - Choose narration language from dropdown
   - Available: English, Spanish, French, German, etc.

4. **Generate Video**
   - Click "Generate Video" button
   - Monitor real-time progress through visual indicators
   - Typical generation time: 8-15 minutes for 30-second video

5. **Preview & Download**
   - Preview generated video in browser
   - Download MP4 file for use across platforms

### **Example Use Case: Skincare Brand "Brande"**

**Input:**
- **Images**: 5 photos (product bottle, flower ingredient, woman applying product, oil texture, elegant packaging)
- **Description**: "Brande, una marca española de cuidado de la piel que utiliza aceites florales naturales para hidratar y realzar la piel"
- **Language**: Spanish

**Output:**
- 30-second professional video
- Spanish voice-over narration
- Smooth transitions between product shots
- Background music and visual effects
- Ready-to-publish MP4 format

---

## 🔌 API Documentation

### **Endpoint: Generate Video**
```http
POST /api/generate-video
```

**Request:**
```json
{
  "images": ["base64_encoded_image_1", "base64_encoded_image_2"],
  "description": "Product description text",
  "language": "en"
}
```

**Response:**
```json
{
  "status": "success",
  "video_url": "/output/video_12345.mp4",
  "duration": 30,
  "generation_time": 512
}
```

**Status Codes:**
- `200`: Video generated successfully
- `400`: Invalid input parameters
- `500`: Server error during generation

---

## 📊 Performance Metrics

### **Generation Time Breakdown**

| Stage | Duration | Percentage |
|-------|----------|-----------|
| Script Enhancement (Gemini) | 10-15s | 3% |
| Voice Synthesis (gTTS) | 10-15s | 3% |
| Video Generation (SVD-XT) | 30-60s/image | 85% |
| Video Assembly (MoviePy) | 20-30s | 9% |

**Total Average**: 8.5 minutes for 30-second video (5 images)

### **Hardware Requirements**

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **GPU** | NVIDIA GTX 1660 (6GB) | NVIDIA RTX 4060 (12GB+) |
| **RAM** | 16GB | 32GB |
| **Storage** | 20GB free | 50GB+ SSD |
| **CPU** | 4 cores | 8+ cores |

---

## ⚠️ Limitations

1. **Computational Requirements**: Requires GPU with 12GB+ VRAM for optimal performance
2. **Generation Time**: 8-15 minutes per video may be too long for real-time applications
3. **Input Quality Dependency**: Output quality heavily depends on input image quality and description precision
4. **Synchronization**: Occasional audio-video sync issues with variable-length scripts
5. **Creative Control**: Limited fine-tuning of specific visual styles and transitions
6. **Language Support**: Voice quality varies across languages (best for English, Spanish, French)

---

## 🔮 Future Enhancements

### **Short-term (3-6 months)**
- [ ] Parallel processing for multiple images
- [ ] Model quantization for reduced GPU memory usage
- [ ] Enhanced caching system for similar generations
- [ ] Real-time parameter preview
- [ ] Industry-specific templates (automotive, fashion, food, etc.)

### **Medium-term (6-12 months)**
- [ ] Advanced multimodal capabilities
- [ ] Automatic style adaptation from reference images
- [ ] Platform-specific optimization (Instagram, YouTube, TikTok)
- [ ] Multiple video variations from single input
- [ ] Cloud-native architecture with serverless deployment

### **Long-term (12+ months)**
- [ ] Conversational AI assistant for creative guidance
- [ ] Sector-specific AI models (trained on industry data)
- [ ] Advanced audio processing (background music, sound effects)
- [ ] Collaborative editing features
- [ ] Enterprise API with usage analytics

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### **Development Guidelines**
- Follow PEP 8 style guide for Python code
- Add unit tests for new features
- Update documentation for API changes
- Ensure all tests pass before submitting PR

---




## 📧 Contact

**Fatima Zohra KAJJOUT**  
Master's Student - Information Systems & Intelligent Systems  
Institut National de Statistique et d'Économie Appliquée (INSEA)

📧 **Email**: [fatimazohrakajjout@gmail.com](mailto:fatimazohrakajjout@gmail.com)  
🔗 **LinkedIn**: [Your LinkedIn Profile](https://www.linkedin.com/in/fatima-zohra-kajjout-71b1a5281/)  
🐙 **GitHub**: [Your GitHub Profile](https://github.com/FATIM120)

**Supervisor**: Dr. Ikram EL KARFI  
**Institution**: INSEA - Morocco  
**Academic Year**: 2025-2026

---

## 🙏 Acknowledgments

Special thanks to:
- **Dr. Ikram EL KARFI** for exceptional guidance and supervision
- **INSEA** for providing the academic framework and resources
- **Stability AI** for Stable Video Diffusion model
- **Google** for Gemini API and gTTS services
- **Open-source community** for Flask, MoviePy, and other libraries

---

## 📚 References

1. Blattmann, A., et al. (2023). Stable Video Diffusion: Scaling Latent Video Diffusion Models to Large Datasets
2. Rombach, R., et al. (2022). High-Resolution Image Synthesis with Latent Diffusion Models
3. Ho, J., et al. (2020). Denoising Diffusion Probabilistic Models
4. Google DeepMind (2023). Gemini: The Next Generation of Large Language Models

---

<div align="center">

**Made with ❤️ by Fatima Zohra KAJJOUT**

⭐ Star this repo if you find it helpful!

</div>
