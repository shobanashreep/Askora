# 🧠 Askora – AI-Powered Student Doubt Solver

## Overview

Askora is an AI-powered educational assistant designed to help students instantly understand academic questions from images. By combining OCR, AI tutoring, personalized practice generation, and quiz creation, Askora transforms a simple question image into an interactive learning experience.

Students can upload a photo of a question, receive a detailed step-by-step explanation, generate similar practice problems, create quizzes for self-assessment, and export their learning history as a PDF notebook.

---

## Problem Statement

Students often face challenges when studying independently:

* Difficulty understanding textbook and assignment questions.
* Lack of immediate academic support outside classroom hours.
* Limited access to personalized practice material.
* Inefficient methods for revising and tracking solved doubts.

Existing solutions typically focus on providing answers rather than helping students understand concepts deeply.

---

## Solution

Askora acts as a personal AI tutor that:

1. Reads academic questions directly from uploaded images.
2. Identifies the subject automatically.
3. Provides clear step-by-step explanations.
4. Generates similar practice problems for reinforcement.
5. Creates personalized quizzes for self-evaluation.
6. Exports learning sessions into a downloadable PDF notebook.

This enables students to learn concepts independently while improving problem-solving skills.

---

## Key Features

### AI-Powered Question Recognition

* Upload question images in PNG, JPG, or JPEG format.
* Automatic extraction of question content using Gemini Vision capabilities.

### Automatic Subject Detection

* Identifies the academic subject of the uploaded question.
* Supports Mathematics, Science, Physics, Chemistry, Biology, Aptitude, and more.

### Personalized AI Tutoring

* Generates detailed step-by-step explanations.
* Uses student-friendly language.
* Focuses on concept understanding rather than answer memorization.

### Practice Problem Generator

* Creates similar problems based on the current topic.
* Encourages active learning and skill reinforcement.

### Quiz Generation

* Generates multiple-choice quizzes from the explained concept.
* Helps students evaluate their understanding instantly.

### Follow-Up Doubt Solving

* Supports conversational learning.
* Students can ask additional questions related to the topic.

### PDF Notebook Export

* Saves learning sessions into a downloadable PDF.
* Useful for revision and exam preparation.

### Optimized AI Pipeline

* Combines OCR, subject detection, explanation generation, and practice problem creation into a single AI request.
* Reduces API usage and improves response speed.

---

## Technology Stack

### Frontend

* Streamlit

### AI & Machine Learning

* Google Gemini 2.5 Flash
* Gemini Vision for image understanding

### Image Processing

* Pillow (PIL)

### PDF Generation

* FPDF

### Environment Management

* Python Dotenv

### Programming Language

* Python 3.11+

---

## System Architecture

```text
Student Uploads Image
          │
          ▼
    Gemini Vision OCR
          │
          ▼
   Subject Identification
          │
          ▼
 Step-by-Step Explanation
          │
          ▼
 Practice Problem Creation
          │
          ▼
    Quiz Generation
          │
          ▼
      PDF Export
```

---

## Installation

### Clone Repository

```bash
git clone <repository-url>
cd Askora
```

### Create Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

### Run Application

```bash
streamlit run app.py
```

---

## Project Structure

```text
Askora/
│
├── app.py
├── .env
├── requirements.txt
│
├── utils/
│   ├── llm_utils.py
│   └── pdf_utils.py
│
└── assets/
```

---

## Future Enhancements

* Multi-language support
* Voice-based doubt solving
* Adaptive learning recommendations
* Student progress analytics dashboard
* Topic-wise performance tracking
* AI-generated study plans
* Teacher and classroom integration

---

## Use Cases

* School students
* College students
* Competitive exam aspirants
* Self-learners
* Online education platforms
* Academic tutoring systems

---

## Innovation Highlights

* AI-powered image-to-explanation workflow
* Automated subject identification
* Personalized practice generation
* Dynamic quiz creation
* Downloadable revision notebook
* Optimized single-request AI architecture

---

## Impact

Askora empowers students with instant academic assistance, personalized learning support, and continuous practice opportunities. By combining AI tutoring, assessment, and revision tools into one platform, it helps learners build confidence, improve understanding, and study more effectively.

