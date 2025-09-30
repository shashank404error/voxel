# Voxel: AI Talking Avatar Generation Pipeline

Voxel is an advanced AI-powered pipeline for generating realistic talking avatars from a single image and audio input. By combining state-of-the-art voice cloning and diffusion models, Voxel creates lifelike animations with synchronized lip movements and natural expressions.

## Example of videos generated on my 24Gib VRAM GPU with CPU offloading and fp8.
<p float="left">
  <video src="assets/demo_hindi.mp4" controls width="24%" title="Me talking about hyperchaos in hindi. 512 resolution."></video>
  <video src="assets/upsc_hindi.mp4" controls width="24%" title="A teacher teaching a topic to his students. 512 resolution"></video>
  <video src="assets/demo_english.mp4" controls width="24%" title="Me talking about voxel. 256 resolution."></video>
  <video src="assets/engg_topic_hindi.mp4" controls width="24%" title="A teacher talking about capabilities of voxel. 256 resolution."></video>
</p>

## Key Features

- **Voice Cloning**: Clone any voice from a short audio sample
- **Talking Head Generation**: Create lightweight talking head animations
- **Full Body Animation**: Generate complete body animations with natural movements
- **Streaming Capability**: Process and generate content in real-time
- **Speech Variation**: Add realistic variations to cloned voices
- **Efficient Processing**: Chunk and process videos to reduce computational costs and generate videos above 30 mins.

## AI Models

Voxel integrates multiple cutting-edge AI models:

- **Chatterbox**: Voice cloning model with added streaming capability
- **Ditto Talking Head**: Lightweight model for generating talking head animations
- **Wan2.2**: Advanced diffusion model for full-body animation generation

## Custom Capabilities

### Streaming Voice Cloning

The standard Chatterbox model has been enhanced with streaming capabilities, allowing for real-time voice cloning and processing. This significantly reduces latency and enables interactive applications.

### Voice Speech Variation

A custom speech variation system has been implemented to make cloned voices sound more natural and less robotic. This system introduces subtle variations in tone, pitch, and rhythm to create more human-like speech patterns.

### Chunking for Efficient Processing

To keep computational costs low while maintaining high-quality output, Voxel implements a chunking system that breaks down longer videos into manageable segments. These segments are processed individually using diffusion models and then seamlessly combined into a final output.

## Getting Started

### Prerequisites

- Python 3.8+
- CUDA-compatible GPU (for optimal performance)
- Redquired depenencies (see requirements.txt in each model directory)

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/voxel.git
   cd voxel
   ```
### Use Speech Variation Capabilities locally

1. ```cd chatterbox-streaming```
2. Setup environemnt for chatterbox-streaming using `requirement.txt`
3. Run gradio server using `multilingual_app.py`
4. Run `speech_variation_parallel.py` with speech_variation_schema path, reference_audio path and an output tag.
5. The results will be stored in speech_variation folder (under unique run name).

Note: Use this prompt to get the `speech_variation_schema` for now, it will be integrated to the pipeline in the next update.

```
You are a speech expression annotator for TTS.  
I will give you a paragraph of text.  
Do NOT rewrite or paraphrase the text. Keep every word exactly as it is.  

Your task:  
- Split the paragraph into sentences and then into smaller expressive chunks (phrases, clauses, or impactful words).  
- Where a natural pause is needed, insert a special silence chunk:  
  {
    "text": "...",
    "exaggeration": 0.0,
    "cfg": 0.0,
    "duration_ms": <integer milliseconds of silence>
  }

Schema for output:  
[
  {
    "text": <exact text chunk from the original paragraph OR "..." if pause>,
    "exaggeration": <float between 0.25 and 2.0 OR 0.0 for silence>,
    "cfg": <float between 0.2 and 1.0 OR 0.0 for silence>,
    "duration_ms": <integer duration in milliseconds, only used if "text" is "...", otherwise omit>
  }
]

Guidelines:
- Use `"..."` only where a meaningful pause or breath would naturally occur.  
- Suggested silence durations:  
  • Short phrase break → 200–400ms  
  • Sentence end → 500–800ms  
  • Dramatic/emphatic beat → 700–1200ms  
  • Whisper/soft reflection → 400–600ms  
- Voice tone scaling:  
  • Calm/narrative → exaggeration 0.5–0.7, cfg 0.4–0.6  
  • Confident/clear → exaggeration 0.8–1.0, cfg 0.6–0.8  
  • Energetic → exaggeration 1.2–1.6, cfg 0.7–0.9  
  • Dramatic/emphatic → exaggeration 1.4–1.8, cfg 0.6–0.8  
  • Soft/whispering → exaggeration 0.7–0.9, cfg 0.3–0.4  
  • Questioning → exaggeration 0.8–1.1, cfg 0.5–0.7  

Rules:  
- Always preserve the exact words from the input paragraph.  
- Insert `"..."` only for meaningful pauses, not after every chunk.  
- Return **only the JSON array**, nothing else.  

Example:  

Input Paragraph:  
"Good morning, friends. Today, I want to share a story. At first, everything was calm and steady, like the slow rhythm of a peaceful walk. But suddenly—things began to move faster, brighter, more exciting, almost as if the world itself had doubled in energy!"

Output JSON:  
[
  {"text": "Good morning,", "exaggeration": 0.6, "cfg": 0.45}, 
  {"text": "friends.", "exaggeration": 0.8, "cfg": 0.6}, 
  {"text": "...", "exaggeration": 0.0, "cfg": 0.0, "duration_ms": 600},

  {"text": "Today,", "exaggeration": 0.7, "cfg": 0.5}, 
  {"text": "I want to share a story.", "exaggeration": 0.9, "cfg": 0.65}, 
  {"text": "...", "exaggeration": 0.0, "cfg": 0.0, "duration_ms": 500},

  {"text": "At first,", "exaggeration": 0.6, "cfg": 0.4}, 
  {"text": "everything was calm and steady,", "exaggeration": 0.5, "cfg": 0.35}, 
  {"text": "like the slow rhythm", "exaggeration": 0.7, "cfg": 0.45}, 
  {"text": "of a peaceful walk.", "exaggeration": 0.8, "cfg": 0.5}, 
  {"text": "...", "exaggeration": 0.0, "cfg": 0.0, "duration_ms": 800}, 

  {"text": "But suddenly—", "exaggeration": 1.6, "cfg": 0.85}, 
  {"text": "things began to move faster,", "exaggeration": 1.5, "cfg": 0.8}, 
  {"text": "brighter,", "exaggeration": 1.4, "cfg": 0.75}, 
  {"text": "more exciting,", "exaggeration": 1.6, "cfg": 0.85}, 
  {"text": "almost as if the world itself had doubled in energy!", "exaggeration": 1.5, "cfg": 0.9}
]


input: "सन 2002 में एलन मस्क ने स्पेसएक्स की स्थापना की, जिसका सपना था अंतरिक्ष यात्रा को सस्ता, भरोसेमंद और सभी के लिए सुलभ बनाना। शुरुआत फाल्कन 1 से हुई, लेकिन असली पहचान फाल्कन 9 और फाल्कन हेवी जैसे रॉकेट्स से मिली, जो बार-बार इस्तेमाल किए जा सकते हैं और इसी वजह से अंतरिक्ष यात्रा की लागत कई गुना कम हो गई। स्पेसएक्स का ड्रैगन कैप्सूल आज न केवल माल बल्कि अंतरिक्ष यात्रियों को भी इंटरनेशनल स्पेस स्टेशन तक ले जाता है और नासा भी इस पर भरोसा करता है। अब कंपनी का अगला बड़ा कदम है स्टारशिप, जो अब तक का सबसे शक्तिशाली रॉकेट है और इसे इंसानों को चाँद और मंगल तक ले जाने के लिए तैयार किया जा रहा है। स्पेसएक्स केवल रॉकेट बनाने वाली कंपनी नहीं है, बल्कि मानवता को सितारों तक पहुँचाने के मिशन का प्रतीक है।"
```

### Use WAN2.2 diffusion model for video generation (s2v)
1. Prepare the audio file before running the model
   - run `run_voxel.sh` with the audio generated in the above step to convert it into chunks of 5 sec and generate a driver csv file for the model.
2. `cd HunyuanVideo-Avatar-voxel`
3. Setup HunyuanVideo-Avatar-voxel using conda.
4. run using scripts as applicable to your GPU availibility.
   - Off load the computation to CPU if GPU poor.
   - Try reducing the resolution and generation steps if get GPU OOM error.

## 📝 License

Each component has its own license. Please refer to the LICENSE files in each subdirectory.

## 🙏 Acknowledgements

This project builds upon several open-source AI models and has been enhanced with custom capabilities to create a comprehensive talking avatar generation pipeline.