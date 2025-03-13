# Animation Generator

A Python script that uses Google's Gemini 2.0 Flash API to generate animated GIFs from text prompts.

![Sample Animation](animation.gif)

## Description

This script utilizes Google's Gemini AI to create animation frames based on a text prompt. It then combines these frames into a GIF animation using ffmpeg. The example animation shows "a seed growing into a plant and then blooming into a flower in an 8-bit pixel art style."

## Features

- Generates multiple animation frames using Google's Gemini 2.0 Flash model
- Implements retry logic to ensure multiple frames are generated
- Automatically assembles frames into a smooth GIF animation
- Configurable animation parameters (framerate, scaling)

## Requirements

- Python 3.x
- ffmpeg (must be installed and available in your PATH)
- Google Gemini API key

## Installation

1. Clone this repository
2. Create a virtual environment:

```
python3 -m venv venv
source venv/bin/activate
```

3. Install required packages:

```
pip install Pillow google-genai loguru
```

4. Edit the script to add your Gemini API key
```python
GEMINI_API_KEY = "YOUR_KEY_HERE"
```

## Usage
Run the script with:

```
python generate.py
```

To customize the animation, modify the following variables in the script:
* `subject`: What the animation should depict (e.g., "a seed growing into a plant and then blooming into a flower")
* `style`: Visual style for the animation (e.g., "in an 8-bit pixel art style")

## How It Works

1. The script sends a prompt to Gemini 2.0 Flash requesting multiple animation frames
2. If insufficient frames are returned, it retries with an enhanced prompt
3. Frames are saved as temporary PNG files
4. ffmpeg combines these frames into a GIF animation
5. The final animation is saved with a unique filename and displayed
