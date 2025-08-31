# TransVox

> Record your speech, convert it to text, and display it in real-time.

---

## Overview
**TransVox** is an experimental project that allows users to record speech from the browser and send it to a backend for transcription.  
The backend uses **AssemblyAI** to convert audio into text, which is then displayed in the UI textbox.  


---

## Features

- ✅ **Record Speech** from the browser using MediaRecorder  
- ✅ **Speech-to-Text (STT)** via AssemblyAI  
- 🚧 **Text Translation** (powered by Murf AI)  
- 🚧 **Text-to-Speech Playback** using Murf AI voices  
- ⚡ **Modern UI** built with React + Tailwind CSS

---

## Tech Stack

| Layer                | Technology                       |
|-----------------------|----------------------------------|
| **Frontend**          | React, Tailwind CSS, Vite        |
| **Backend**           | Flask (Python)                  |
| **Speech-to-Text**    | AssemblyAI                      |
| **Translation**| Murf AI Translation API          |
| **Text-to-Speech** | Murf AI TTS API             |
| **Audio Handling**    | pydub + FFmpeg                  |


---

## Getting Started

### Prerequisites
- Node.js & npm (for frontend)  
- Python 3.8+ (for backend)  
- FFmpeg installed (for audio processing)  
- API keys:  
  - AssemblyAI (for STT)  
  - Murf AI (for Translation + TTS) 

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
- Frontend runs at http://localhost:3000

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows

python app.py
```

- Backend runs at http://localhost:5000

## Acknowledgements

-Built as part of the Murf AI Hackathon/Contest 🏆

-Thanks to Murf AI for their Translation & Text-to-Speech APIs

-Uses AssemblyAI for transcription
