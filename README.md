# MoodBeats 🎵🛍️

MoodBeats is an AI-powered web application that recommends songs and products based on the user’s real-time emotions. It uses facial emotion detection to personalize the user experience and integrates music recommendations with product suggestions into a single platform.

## Features

- Emotion-based song recommendations
- Product recommendations based on detected mood
- Facial emotion detection
- Music personalization experience
- E-commerce product suggestions
- Interactive web interface
- Mood-based user engagement through AI recommendations

## Tech Stack

- Python
- Flask
- HTML
- CSS
- JavaScript
- SQLite

## Project Structure

- `run.py` – Entry point of the application
- `app/routes.py` – Application routes
- `app/emotion_detect.py` – Emotion detection logic
- `app/database.py` – Database handling
- `app/templates/` – HTML templates
- `app/static/` – CSS, JS, images
- `moodbeats.db` – SQLite database file

## How It Works

1. The user interacts with the MoodBeats web application.
2. The system detects the user's emotion using facial emotion detection.
3. Based on the detected emotion, the application recommends suitable songs.
4. It also suggests related products to enhance the user experience.
5. The platform combines entertainment and shopping in one personalized interface.

## Installation and Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/shreyaa2408/moodbeats.git
   ```

2. Move into the project folder:

   ```bash
   cd moodbeats
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:

   ```bash
   python run.py
   ```

5. Open the local server URL in your browser.

## Future Scope

- Real-time webcam-based emotion detection
- Improved music recommendation engine
- Better product recommendation system
- User authentication and personalized profiles
- Integration with music streaming APIs
- Enhanced UI/UX for a more immersive experience

## Author

**Shreya**
