# Graduate Project - AI-Powered Interview System

This project is a comprehensive AI-powered interview and candidate evaluation system built with FastAPI. It includes multiple agents for different aspects of the hiring process, leveraging advanced AI models for resume analysis, question generation, interview evaluation, and cheating detection.

## Features

- **CV Agent**: Upload and analyze resumes using Pinecone vector database, automatically select best candidates
- **Exam Generation Agent**: Generate technical questions tailored to specific job requirements
- **Interview Agent**: Transcribe audio recordings and provide detailed technical evaluation of candidate responses
- **Proctor Agent**: Real-time video analysis for cheating detection using YOLO and MediaPipe


## Video 
you can find our video in this link
[![Watch the video](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAP8AAADGCAMAAAAqo6adAAAABlBMVEUAAAAORKmU5gWIAAAA3klEQVR4nO3PAQEAAAjDoNu/tEEYDdjN1t/W39bf1t/W39bf1t/W39bf1t/W39bf1t/W39bf1t/W39bf1t/W39bf1t/W39bf1t/W39bf1t/W39bf1t/W39bf1t/W39bf1t/W39bf1t/W39bf1t/W39bf1t/W39bf1t/W39bf1t/W39bf1t/W39bf1t/W39bf1t/W39bf1t/W39bf1t/W39bf1t/W39bf1t/W39bf1t/W39bf1t/W39bf1t/W39bf1t/W39bf1t/W39bf1t/W39bf1t/W39bf1t/W34b/H769AMf5McvaAAAAAElFTkSuQmCC)](https://nileuniversity-my.sharepoint.com/:v:/g/personal/s_aboalyazeed2141_nu_edu_eg/EdV6ruQeebNIgy6Ibr9lPn4Bo98JCHLa_MxmgGxEKWjAQg?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=x6X2hd)



## Prerequisites

- Python 3.8 or higher
- Conda (Anaconda or Miniconda)
- OpenAI API key
- Pinecone API key

## Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <your-repository-url>
   cd <repository-name>
   ```

2. **Create and activate the conda environment**:
   ```bash
   conda env create -f environment.yml
   conda activate grad-project
   ```

3. **Set up API keys**:
   - Configure your OpenAI and Pinecone API keys in the respective modules
   - Required for CV agent and Interview agent functionality

## Running the Application

1. **Start the FastAPI server**:
   ```bash
   python app.py
   ```

2. **Access the application**:
   - The server will start on `http://localhost:8000`
   - Interactive API documentation is available at `http://localhost:8000/docs`
   - Alternative docs at `http://localhost:8000/redoc`

## API Endpoints

### CV Agent (`/cv-agent`)

#### 1. Upload Resume to Pinecone
**Endpoint:** `POST /cv-agent/upload-resume_to_pinecone/`

**Purpose:** Upload a PDF resume and index it in Pinecone vector database for semantic search.

**Parameters:**
- `file` (form-data): PDF file containing the resume
- `id_key` (form-data): Unique identifier for the candidate

**Request Example:**
```bash
curl -X POST "http://localhost:8000/cv-agent/upload-resume_to_pinecone/" \
     -F "file=@john_doe_resume.pdf" \
     -F "id_key=candidate_001"
```

**Response:**
```json
{
  "message": "Resume uploaded and indexed successfully.",
  "pinecone_id": "candidate_001"
}
```

**Features:**
- Extracts text from PDF using advanced parsing
- Validates PDF format and text content
- Indexes resume content in Pinecone for semantic search
- Temporary file handling with automatic cleanup

#### 2. Choose Best Resume
**Endpoint:** `POST /cv-agent/choose_best_resume/`

**Purpose:** Analyze job description and return the best matching candidate from indexed resumes.

**Request Body:**
```json
{
  "job_description": "We are looking for a Python developer with 3+ years of experience in web development, familiar with FastAPI, PostgreSQL, and cloud deployment."
}
```

**Request Example:**
```bash
curl -X POST "http://localhost:8000/cv-agent/choose_best_resume/" \
     -H "Content-Type: application/json" \
     -d '{"job_description": "Python developer with FastAPI experience"}'
```

**Response:**
```json
{
  "best_candidate_id": "candidate_001",
  "best_candidate_name": "John Doe",
  "reason": "Strong match with 4 years Python experience, extensive FastAPI knowledge, and proven cloud deployment skills with AWS. Educational background in Computer Science aligns perfectly with technical requirements."
}
```

**Features:**
- Uses GPT-4 for intelligent candidate matching
- Performs semantic search across all indexed resumes
- Provides detailed reasoning for candidate selection
- Considers skills, experience, and educational background
#### 3. Generate Job Details
**Endpoint:** `POST /cv-agent/generate_job_details/`

**Purpose:** Generate comprehensive job descriptions and requirements based on basic job information.

**Request Body:**
```json
{
  "job_title": "Data Engineer",
  "department": "Engineering",
  "employment_type": "Full-time",
  "experience_level": "Mid-level"
}
```

**Request Example:**
```bash
curl -X POST "http://localhost:8000/cv-agent/generate_job_details/" \
     -H "Content-Type: application/json" \
     -d '{
       "job_title": "Data Engineer",
       "department": "Engineering",
       "employment_type": "Full-time",
       "experience_level": "Mid-level"
     }'
```

**Response:**
```json
{
  "job_description": "We are seeking a skilled Mid-level Data Engineer to join our Engineering team...",
  "responsibilities": [
    "Design, build, and maintain robust, scalable data pipelines",
    "Develop and optimize ETL processes",
    "Collaborate with data scientists and analysts"
  ],
  "requirements": "Bachelor's degree in Computer Science, Engineering...",
}
```

**Features:**
- AI-powered job description generation
- Detailed responsibility mapping
- Customizable requirements based on experience level
- Industry-specific skill recommendations

### Exam Generation Agent (`/exam-generation-agent`)

#### Generate Questions
**Endpoint:** `POST /exam-generation-agent/generate-questions`

**Purpose:** Generate technical interview questions tailored to specific job requirements and difficulty levels.

**Request Body:**
```json
{
  "job_description": "Senior Python Developer",
  "num_questions": 5,
}
```

**Request Example:**
```bash
curl -X POST "http://localhost:8000/exam-generation-agent/generate-questions" \
     -H "Content-Type: application/json" \
     -d '{
       "job_description": "Python Developer with Django experience",
       "num_questions": 3
     }'
```

**Response:**
```json
{
  "questions": [
    "Explain the difference between asyncio and threading in Python",
    "How would you optimize a slow database query?"
  ],
  "answers": [
    "asyncio is for I/O-bound concurrency using coroutines and event loops, while threading uses OS threads for parallel execution",
    "Use indexes, query optimization, connection pooling, and caching strategies"
  ],
  "types": [
        "coding",
        "essay",
        "true_false"
    ],
    "difficulties": [
        "hard",
        "hard",
        "medium"
    ],
    "domains": [
        "Deep Learning",
        "machine learning",
        "AI Ethics"
    ]
}
```

### Interview Agent (`/interview-agent`)

#### 1. Transcribe Audio
**Endpoint:** `POST /interview-agent/transcribe-audio`

**Purpose:** Convert audio recordings of interviews to text using advanced speech-to-text technology.

**Parameters:**
- `file` (form-data): Audio file (.mp3, .wav, .m4a formats supported)
- `candidate_id` (form-data): Unique identifier for the candidate

**Request Example:**
```bash
curl -X POST "http://localhost:8000/interview-agent/transcribe-audio" \
     -F "file=@interview_recording.m4a" \
     -F "candidate_id=candidate_001"
```

**Response:**
```json
{
  "transcription": "123 TEST."
}
```

#### 2. Evaluate Interview
**Endpoint:** `POST /interview-agent/evaluate-exam`

**Purpose:** Provide comprehensive technical evaluation of candidate responses using AI analysis.

**Request Body:**
```json
{
  "questions": [
    "Explain the difference between asyncio and threading in Python",
    "How would you optimize a slow database query?"
  ],
  "golden_answers": [
    "asyncio is for I/O-bound concurrency using coroutines and event loops, while threading uses OS threads for parallel execution",
    "Use indexes, query optimization, connection pooling, and caching strategies"
  ],
  "candidate_answers": [
    "asyncio lets you write concurrent code with coroutines and the event loop",
    "Indexes speed up queries and you can use connection pooling"
  ]
}
```

**Response:**
```json
{
  "questions_evaluated": 
    { 
            "question": "questions[i]",
            "golden_answer": "golden_answers[i]",
            "candidate_answer": "candidate_answers[i]",
            "evaluation" : "explanation[i]"
        }
      ,
    
  
  "exam_summary": "Candidate demonstrates solid foundational knowledge with room for deeper technical understanding. Strong in basic concepts but needs improvement in comparative analysis.",
  "final_grade": 75.5,
  "recommendation": "Consider for junior-mid level position with mentoring"
}
```

**Features:**
- Individual question evaluation with detailed feedback
- Overall exam summary and grading
- Identifies strengths and improvement areas
- Provides hiring recommendations

#### 3. emaraty part (interview analysis)

### Proctor Agent (`/proctor-agent`)

#### Check Cheating
**Endpoint:** `POST /proctor-agent/check-cheating/`

**Purpose:** Analyze video recordings to detect potential cheating behaviors during exams using computer vision.

**Parameters:**
- `file` (form-data): Video file of the exam session
- `candidate_name` (form-data): Name of the candidate being monitored

**Request Example:**
```bash
curl -X POST "http://localhost:8000/proctor-agent/check-cheating/" \
     -F "file=@exam_session.mp4" \
     -F "candidate_name=john_doe"
```

**Response:**
```json
{
    "Candidate": "ss",
    "Phone usage detected": 2,
    "Frames with phone detection": [
        "frame_0007.jpg",
        "frame_0008.jpg"
    ],
    "People detected (more than 1)": 0,
    "Frames with multiple people detection": [],
    "People count changes detected": 0,
    "Total frames processed": 10
}
```

**Detection Features:**
- **Head Pose Estimation**: Tracks unusual head movements and orientations
- **Device Detection**: Identifies phones, tablets, and other electronic devices
- **Gaze Analysis**: Monitors eye movement patterns
- **Multiple Person Detection**: Alerts if additional people enter the frame
- **Audio Analysis**: Detects unusual sounds or conversations

**Supported Formats:**
- Video: .mp4, .mov, .avi, .mkv
- Resolution: Up to 4K
- Duration: Up to 2 hours per session

## Project Structure

```
├── app.py                          # Main FastAPI application with router integration
├── environment.yml                 # Conda environment configuration with all dependencies
├── phone.mp4                       # Sample video for testing cheating detection
├── WIN_20250502_18_19_02_Pro.mp4  # Additional test video
├── yolov8l.pt                      # Pre-trained YOLO model for object detection
│
├── candiate_eval/                  # CV processing and candidate evaluation
│   ├── agent.py                    # Core AI agent for resume analysis
│   ├── app.py                      # FastAPI router for CV endpoints
│   ├── cv_processor.py             # PDF processing and Pinecone integration
│   └── uploads/                    # Temporary storage for uploaded files
│
├── question_and_answer_agent/      # Intelligent question generation system
│   └── app.py                      # FastAPI router for question generation
│
├── interview_agent/                # Interview processing and evaluation
│   ├── app.py                      # FastAPI router for interview endpoints
│   ├── speech_to_text.py           # Audio transcription functionality
│   ├── technical_depth_analysis.py # AI-powered answer evaluation
│   ├── exam_results.json           # Sample evaluation results
│   ├── qa_pairs.json               # Question-answer pairs database
│   └── Recording.m4a               # Sample audio file
│
├── Test_Cheating_Detection/        # Advanced video-based proctoring system
│   ├── app.py                      # FastAPI router for proctoring
│   └── README.md                   # Detailed documentation for cheating detection
│
└── grad_project/                   # Research and development resources
    ├── data_prep_for_medical_question_training.ipynb
    ├── fake_cv_detection.py        # CV authenticity verification
    ├── lora_finetune.ipynb         # Model fine-tuning experiments
    ├── prompt_eng.py               # Prompt engineering utilities
    └── stt.py                      # Speech-to-text experimentation
```

## Usage Examples

### Complete Interview Workflow

1. **Upload candidate resumes:**
```bash
curl -X POST "http://localhost:8000/cv-agent/upload-resume_to_pinecone/" \
     -F "file=@candidate1.pdf" -F "id_key=cand_001"
```

2. **Find best candidate:**
```bash
curl -X POST "http://localhost:8000/cv-agent/choose_best_resume/" \
     -H "Content-Type: application/json" \
     -d '{"job_description": "Senior Python Developer with 5+ years experience"}'
```

3. **Generate interview questions:**
```bash
curl -X POST "http://localhost:8000/exam-generation-agent/generate-questions" \
     -H "Content-Type: application/json" \
     -d '{"job_description": "Senior Python Developer", "num_questions": 5}'
```

4. **Transcribe interview audio:**
```bash
curl -X POST "http://localhost:8000/interview-agent/transcribe-audio" \
     -F "file=@interview.m4a" -F "candidate_id=cand_001"
```

5. **Evaluate responses:**
```bash
curl -X POST "http://localhost:8000/interview-agent/evaluate" \
     -H "Content-Type: application/json" \
     -d '{"questions": ["..."], "golden_answers": ["..."], "candidate_answers": ["..."]}'
```

6. **Monitor for cheating:**
```bash
curl -X POST "http://localhost:8000/proctor-agent/check-cheating/" \
     -F "file=@exam_video.mp4" -F "candidate_name=john_doe"
```

## Technical Specifications

### AI Models Used
- **OpenAI GPT-4**: For resume analysis and answer evaluation
- **YOLO v8**: For object detection in video streams
- **MediaPipe**: For pose estimation and facial analysis
- **Pinecone**: Vector database for semantic resume search

### Performance Metrics
- **Resume Processing**: ~2-3 seconds per PDF
- **Question Generation**: ~5-10 seconds for 5 questions
- **Audio Transcription**: Real-time (1x speed)
- **Video Analysis**: ~0.5x speed (2-minute video takes ~4 minutes)

### Rate Limiting
- Some endpoints implement 2-3 second delays to prevent API abuse
- Concurrent request handling with FastAPI's async capabilities

## Development

### Running Individual Modules
```bash
# CV Agent only
cd candiate_eval && python app.py

# Question Generator only
cd question_and_answer_agent && python app.py

# Interview Agent only
cd interview_agent && python app.py

# Proctoring Agent only
cd Test_Cheating_Detection && python app.py
```



## Troubleshooting

### Common Issues

1. **Environment Setup**
   ```bash
   # If conda environment creation fails
   conda clean --all
   conda env create -f environment.yml --force
   ```







## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

For detailed information about individual components, check the respective module directories and their documentation.