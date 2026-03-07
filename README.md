# 🎓 Ganithamithura

## A Multi-Sensory Learning Solution for Overcoming Early Mathematical Difficulties

An innovative educational platform that combines AI, Augmented Reality, and adaptive learning to help primary school students (Grades 1–4) master fundamental mathematical concepts through engaging, hands-on experiences.

---

## 👥 Team Members

| Student ID | Name | Component |
|------------|------|-----------|
| IT22602596 | Imalshika A.B.E | Number Identification, Reading & Writing |
| IT21208812 | Jayarathna H.D.N.K | Symbols & Arithmetic Facts Component |
| IT22626110 | Thilakarathna HMSD | AR Measurement (Length, Area, Capacity, Weight) |
| IT22599872 | Kumara H.P.K.D | Shapes and Game Patterns |

---

## 🌟 System Overview

Ganithamithura is a comprehensive mobile-based educational platform designed specifically for primary school children aged 6–9 years who experience mathematical learning difficulties. The system leverages cutting-edge technologies including Augmented Reality (AR), Machine Learning, Computer Vision, and Retrieval-Augmented Generation (RAG) to create an immersive, personalized learning environment. 

By combining visual, auditory, and kinesthetic learning methods, the app addresses diverse learning styles and helps students develop confidence in mathematics through interactive games, real-world object interaction, and AI-powered adaptive instruction. The platform continuously monitors student progress and adjusts difficulty levels to ensure optimal learning outcomes.

---

## 🎯 Problem Statement

Traditional mathematics education often fails to engage young learners, particularly those with learning difficulties. Abstract concepts presented through static textbooks and worksheets lack the hands-on interaction necessary for deep understanding. Students struggle to connect mathematical theories to real-world applications, leading to disengagement and poor performance.

Current educational tools are unable to:
- Adapt to individual learning paces and styles
- Provide immediate, personalized feedback
- Bridge the gap between abstract concepts and concrete experiences
- Identify and address specific learning difficulties in real-time

Ganithamithura addresses these challenges by creating an interactive, multi-sensory learning environment that makes mathematics tangible, engaging, and accessible to all learners.

---

## 📊 System Architecture

![System Architecture Diagram](./docs/system-diagram.png)
*Comprehensive system architecture showing the integration of AR, ML, and adaptive learning components*

---

## 🧩 Core Components

### 1️⃣ Number Identification, Reading & Writing
A multisensory AI-based system that helps children master number recognition, writing, and counting through image processing and gamification. This component uses machine learning to identify student difficulties in number formation and provides targeted interventions with real-time feedback. Interactive exercises adapt to each child's learning style, building confidence through progressive skill development and engaging visual and auditory cues.

### 2️⃣ Symbols & Arithmetic Facts Component
An AI-driven adaptive learning module focused on mathematical symbols, fact fluency, and arithmetic computation for early-grade students. Using Large Language Models (LLMs) and neural networks, the system generates contextual questions with visual explanations and voice-guided instruction. The component employs a closed-loop architecture with parallel processing to continuously evaluate performance, classify learners, and adapt content delivery, ensuring personalized, curriculum-aligned instruction that emphasizes conceptual understanding over rote memorization.

### 3️⃣ AR Measurement (Length, Area, Capacity, Weight)
An Augmented Reality-powered measurement learning platform that allows students to interact with real-world objects and practice measurement concepts hands-on. Using AR Foundation, object detection (YOLOv8), and RAG-based question generation, students can measure physical items like desks and bottles with virtual tools. The AI tutor provides personalized feedback and adjusts difficulty based on performance, making abstract measurement concepts tangible and engaging through immersive AR experiences.

### 4️⃣ Shapes and Game Patterns
An interactive learning module that teaches shape recognition and pattern building through puzzles, games, and spatial reasoning activities. Students explore geometric concepts through engaging challenges that develop logical thinking and visual-spatial intelligence. The component uses Flutter for seamless cross-platform delivery and FastAPI for real-time data processing, creating an enjoyable learning experience that strengthens foundational geometry skills through play-based learning.

---

## 🛠️ Technology Stack

### **Frontend** 🌐
- **Framework**: React.js ⚛️
- **Mobile Development**: Flutter
- **Styling**: Tailwind CSS
- **Libraries**: Axios, React Router, React Icons

### **Backend** 🔧
- **API Framework**: FastAPI (Python)
- **Authentication**: JWT
- **API Documentation**: Swagger/OpenAPI

### **Database** 🗄️
- **Primary Database**: MongoDB 🍃
- **ODM**: Mongoose
- **Caching**: Redis (optional)

### **Machine Learning & AI** 🤖
- **Deep Learning**: TensorFlow, PyTorch
- **ML Libraries**: Scikit-learn, Pandas, NumPy
- **Computer Vision**: OpenCV
- **Object Detection**: YOLOv8, ML Kit
- **NLP**: Large Language Models (LLMs)
- **Speech**: Text-to-Speech (TTS), Speech Recognition (ASR)

### **Augmented Reality** 🥽
- **AR Framework**: AR Foundation (Unity)
- **Mobile AR**: ARCore (Android), ARKit (iOS)

### **Other Tools** 🧰
- **Containerization**: Docker 🐳
- **Version Control**: Git & GitHub
- **CI/CD**: GitHub Actions
- **Image Processing**: OpenCV
- **Model Serving**: TensorFlow Serving

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.10+** — backend services
- **Flutter SDK** — mobile app
- **MongoDB** (Atlas URI or local) — database
- **Ngrok** — public tunneling
- **GitHub Personal Access Token** — Gist updates

### Quick Setup (First Time / Fresh Clone)

> 📖 **Full instructions:** See [`SETUP_GUIDE.md`](./SETUP_GUIDE.md)

```bash
# 1. Clone the repository
git clone https://github.com/cynos28/ganithamithura
cd ganithamithura

# 2. Set up your environment files
#    - Copy and fill in: ganithamithura/.env  (GITHUB_TOKEN)
#    - Copy and fill in: auth_service/.env    (MONGODB_URL, DB_NAME)
#    - Copy and fill in: unit-rag-service/.env (OPENAI_API_KEY, MONGODB_URL)

# 3. Run the setup & start script (installs deps + starts all services)
chmod +x setup_and_start.sh
./setup_and_start.sh
```

The script will:
1. Create virtual environments for each service
2. Install all Python dependencies automatically
3. Start all 6 backend services
4. Open a Ngrok tunnel and update the GitHub Gist so the Flutter app finds the backend

### Daily Use (After First Setup)
```bash
# Just start everything (skips install)
./start_all.sh
```

### Flutter App
```bash
cd ../gmfrontend
flutter run
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Contact

For questions or support, please reach out to the development team or open an issue in the repository.

---

<div align="center">
  <p>Made with ❤️ by the Ganithamithura Team</p>
  <p>Empowering young minds through innovative mathematics education</p>
</div>
