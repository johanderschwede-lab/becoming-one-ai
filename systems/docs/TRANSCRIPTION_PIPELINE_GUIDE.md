# 🎵 Becoming One™ Transcription Pipeline

## Complete Audio/Video → Text → INBOX → Knowledge Base Workflow

**Your Question**: "What is the pipeline for recordings and transcription - is it Whisper? Can this be done without such a service?"

**Answer**: You have **3 flexible options** - from cloud-based to completely local and free!

---

## 🎯 **The Complete Pipeline**

```
Recording → Transcription → INBOX → AI Processing → Knowledge Base
    ↓            ↓           ↓         ↓              ↓
  .mp4/.mp3 → Whisper API → .txt → Content Curation → Searchable Knowledge
```

---

## 📊 **Your 3 Transcription Options**

### **1. OpenAI Whisper API (Recommended - Default)**
```bash
# Highest quality, easiest setup
python transcribe_media.py workshop.mp4 --inbox /path/to/inbox
```

**✅ Pros:**
- **Highest quality** transcription available
- **No setup required** - works immediately  
- **Fast processing** - typically 2-5x faster than real-time
- **Multi-language support** - auto-detects language
- **Handles accents** and background noise well
- **Timestamped segments** for precise editing

**❌ Cons:**
- **Cost**: ~$0.006 per minute (~$0.36/hour)
- **Internet required** - files uploaded to OpenAI
- **Privacy consideration** - content sent to third party
- **25MB file limit** per request

**Best for**: High-quality workshops, important content, when you want the best results

### **2. Local Whisper (Completely Free & Private)**
```bash
# One-time setup
pip install openai-whisper
brew install ffmpeg  # Mac
# or: apt install ffmpeg  # Linux

# Use local processing
python transcribe_media.py workshop.mp4 --method local --inbox /path/to/inbox
```

**✅ Pros:**
- **Completely free** - no ongoing costs
- **Full privacy** - nothing sent to cloud
- **Works offline** - no internet needed
- **No file size limits** - process hours of content
- **Your hardware, your control**

**❌ Cons:**
- **Setup required** - install Whisper + FFmpeg
- **Slower processing** - typically 0.5-1x real-time speed
- **Uses your CPU/GPU** - may slow down other work
- **Slightly lower quality** than API version
- **Model downloads** required (1-3GB first time)

**Best for**: Large volumes of content, privacy-sensitive recordings, cost savings

### **3. Hybrid (Smart Choice)**
```bash
# Automatically chooses best method per file
python transcribe_media.py recordings/ --batch --method hybrid --inbox /path/to/inbox
```

**✅ Pros:**
- **Intelligent routing** - API for small files, local for large
- **Cost optimization** - uses free local for big files
- **Quality optimization** - uses API for important content
- **Flexibility** - adapts to your needs

**Best for**: Mixed workload, cost-conscious with quality needs

---

## 🚀 **Quick Start Guide**

### **Step 1: Choose Your Method**
```bash
# See all options and cost estimates
python transcribe_media.py --show-options

# Estimate costs before processing
python transcribe_media.py workshop.mp4 --estimate-cost
```

### **Step 2: Process Your Content**

**Single File:**
```bash
# Basic transcription (saves .txt file)
python transcribe_media.py recording.mp4

# Transcribe and auto-send to INBOX
python transcribe_media.py recording.mp4 --inbox /Volumes/NAS/BecomingOne/INBOX
```

**Batch Processing:**
```bash
# Process entire folder
python transcribe_media.py recordings/ --batch --inbox /path/to/inbox

# Use local method for cost savings
python transcribe_media.py recordings/ --batch --method local
```

### **Step 3: Automatic INBOX Processing**
Once transcripts hit your INBOX, the AI processor automatically:
- Identifies Johan vs Marianne vs participants
- Extracts teaching content → Knowledge base
- Stores community content separately
- Generates social media suggestions

---

## 📁 **Supported File Formats**

### **Audio Files**
- `.mp3` - Most common audio format
- `.wav` - High quality uncompressed
- `.m4a` - Apple/iPhone recordings  
- `.flac` - Lossless compression
- `.ogg` - Open source format

### **Video Files** (audio extracted automatically)
- `.mp4` - Most common video format
- `.mov` - Apple/iPhone videos
- `.avi` - Windows video format
- `.mkv` - High quality container
- `.webm` - Web video format

### **What Happens to Video Files**
1. **FFmpeg extracts audio** (16kHz mono for optimal Whisper processing)
2. **Audio gets transcribed** using chosen method
3. **Temporary audio file deleted** after processing
4. **Original video preserved** unchanged

---

## 💰 **Cost Analysis**

### **OpenAI Whisper API Pricing**
- **Rate**: $0.006 per minute
- **Examples**:
  - 1-hour workshop: $0.36
  - 30-min interview: $0.18
  - 3-hour event: $1.08
  - 10 hours/month: $3.60

### **Local Whisper Costs**
- **Setup**: Free (one-time software installation)
- **Processing**: Free forever
- **Electricity**: Minimal (~$0.01/hour on typical laptop)

### **Break-Even Analysis**
- If you process **>10 hours/month**: Local saves money
- If you process **<5 hours/month**: API is cost-effective
- **Hybrid approach**: Best of both worlds

---

## ⚙️ **Setup Instructions**

### **For API Method (Easiest)**
```bash
# Already set up if you have OpenAI API key in config/live.env
# Just run:
python transcribe_media.py your_recording.mp4
```

### **For Local Method**
```bash
# 1. Install Whisper
pip install openai-whisper

# 2. Install FFmpeg
# Mac:
brew install ffmpeg

# Linux:
sudo apt install ffmpeg

# Windows:
# Download from https://ffmpeg.org/download.html

# 3. Test installation
whisper --help
ffmpeg -version

# 4. Use local method
python transcribe_media.py recording.mp4 --method local
```

### **First-Time Local Usage**
```bash
# First run downloads model (1-3GB)
python transcribe_media.py test_audio.mp3 --method local

# Models downloaded to:
# ~/.cache/whisper/ (Linux/Mac)
# %USERPROFILE%\.cache\whisper\ (Windows)
```

---

## 🔄 **Complete Workflow Examples**

### **Workshop Recording Workflow**
```bash
# 1. Record workshop (iPhone, Zoom, etc.) → workshop_2025_01_15.mp4

# 2. Transcribe with API (highest quality)
python transcribe_media.py workshop_2025_01_15.mp4 --inbox /Volumes/NAS/INBOX

# 3. INBOX processor automatically:
#    - Identifies Johan/Marianne teaching segments
#    - Extracts participant questions/feedback  
#    - Uploads teaching content to knowledge base
#    - Generates social media content suggestions

# 4. Check results in organized folders
```

### **Batch Processing Workflow**
```bash
# 1. Drop multiple recordings in folder:
recordings/
├── workshop_part1.mp4
├── interview_expert.mp3
├── q_and_a_session.wav
└── presentation.mov

# 2. Batch transcribe (cost-effective with local)
python transcribe_media.py recordings/ --batch --method local --inbox /path/to/inbox

# 3. All transcripts automatically processed by INBOX system
```

### **Privacy-Focused Workflow**
```bash
# For sensitive content - everything stays local
python transcribe_media.py sensitive_recording.mp4 --method local

# Transcript saved locally, then manually review before INBOX
```

---

## 📊 **Output Format**

### **Generated Transcript File**
```markdown
# Transcript: workshop_emotional_anchors.mp4

**Transcribed**: 2025-01-15 14:30:22
**Method**: openai_whisper_api  
**Duration**: 67.3 minutes
**Language**: en
**Cost**: $0.404

---

## Timestamped Transcript

**00:00**: Welcome everyone to today's workshop on emotional anchors...

**00:45**: So the first thing to understand about anchors is that they're not...

**02:30**: Marianne, would you like to share your perspective on this?

**02:35**: Absolutely Johan. What I've found in my work is that when people...

[continues with full timestamped transcript]
```

### **Batch Processing Summary**
```json
{
  "processed_at": "2025-01-15T14:30:22",
  "method_used": "openai_whisper_api",
  "total_files": 5,
  "successful": 5,
  "failed": 0,
  "total_duration_minutes": 234.7,
  "total_cost_estimate": 1.408,
  "results": [
    {
      "file": "workshop_part1.mp4",
      "success": true,
      "duration_minutes": 67.3,
      "transcript_length": 12847,
      "cost_estimate": 0.404
    }
  ]
}
```

---

## 🛠️ **Advanced Features**

### **Quality Optimization**
```bash
# Use different Whisper models for local processing
whisper recording.mp3 --model medium  # Better quality, slower
whisper recording.mp3 --model large   # Best quality, slowest
```

### **Language Specification**
```bash
# Specify language for better accuracy
python transcribe_media.py german_workshop.mp4 --language de
```

### **Custom Processing**
```bash
# Process with custom settings
whisper recording.wav --language en --model base --output_format txt --verbose False
```

---

## 🔧 **Troubleshooting**

### **Common Issues**

**"FFmpeg not found"**
```bash
# Install FFmpeg
brew install ffmpeg  # Mac
sudo apt install ffmpeg  # Linux
# Windows: Download from https://ffmpeg.org/
```

**"File too large for API"**
```bash
# Use local method for files >25MB
python transcribe_media.py large_file.mp4 --method local
```

**"Whisper command not found"**
```bash
# Install Whisper
pip install openai-whisper
# Or upgrade: pip install --upgrade openai-whisper
```

**"Poor transcription quality"**
- Check audio quality (clear speech, minimal background noise)
- Use API method for highest quality
- Specify correct language
- Try different Whisper model sizes for local processing

### **Performance Tips**

**For API Method:**
- Split very long files (>2 hours) into segments
- Use good audio quality for best results
- Batch process during off-peak hours

**For Local Method:**
- Use GPU if available (install torch with CUDA)
- Close other applications during processing
- Use smaller models (base/small) for faster processing
- Process overnight for large batches

---

## 🎯 **Recommendations by Use Case**

### **Small Team (You + Marianne)**
- **Method**: OpenAI API
- **Workflow**: Individual files → API → INBOX
- **Cost**: ~$5-20/month depending on content volume

### **High Volume Content Creation**
- **Method**: Local Whisper
- **Workflow**: Batch folders → Local processing → INBOX
- **Setup**: One-time installation, unlimited processing

### **Mixed Content (Public + Private)**
- **Method**: Hybrid
- **Workflow**: Sensitive content → Local, Public workshops → API
- **Benefits**: Privacy + Quality optimization

### **Budget Conscious**
- **Method**: Local Whisper
- **One-time setup**: 30 minutes
- **Ongoing cost**: $0

---

## 🚀 **Integration with Your Existing Workflow**

### **Current State**
```
Recording → Manual transcription → Manual processing → Knowledge base
```

### **New Automated Pipeline**
```
Recording → Auto-transcription → Auto-INBOX → Auto-processing → Knowledge base + Social content
```

### **What Changes for You**
1. **Record as usual** (any device, any format)
2. **Run one command** to transcribe
3. **Everything else is automatic**

### **Time Savings**
- **Manual transcription**: 4-6 hours per hour of content
- **Automated pipeline**: 5-10 minutes per hour of content
- **ROI**: Pays for itself after first workshop transcription

---

**Your complete recording-to-knowledge pipeline is ready!** 🎵 → 📝 → 🤖 → 📚

Choose your transcription method, process your recordings, and watch them automatically become searchable knowledge and engaging social content.

---

*System Status: Ready for Audio/Video Processing*  
*Next Step: Choose your transcription method and process your first recording!*
