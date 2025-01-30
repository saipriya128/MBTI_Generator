# ✨ What's Your Vibe? - Personality Quiz App

A modern, engaging personality quiz application built with Streamlit and powered by Mistral AI. This app delivers personalized MBTI-inspired personality insights through an interactive quiz experience.

## 🌟 Features

- **Interactive Quiz Experience**: 10 personality-revealing questions with timed responses
- **AI-Powered Analysis**: Leverages Mistral AI for deep personality insights
- **Rich Visualization**: 
  - Progress tracking
  - Dynamic personality trait radar charts
  - Interactive personality dimension bars
- **Detailed Results**:
  - Personalized MBTI-style type analysis
  - Custom personality title and emoji
  - Detailed trait breakdown
  - Strengths and growth areas
- **Downloadable Results**: Save your personality analysis as a text file

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
- Mistral AI API key

### Installation

1. Clone the repository:
bash
git clone [your-repository-url]
cd personality-quiz-app
 
2. Install required packages:
bash
pip install -r requirements.txt

3. Set up your environment variables:
Create a `.env` file in the root directory and add: MISTRAL_API_KEY=your_mistral_api_key_here

### Running the App

Launch the app using Streamlit: 
bash
streamlit run app.py


## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **AI Integration**: Mistral AI
- **Data Visualization**: Plotly
- **Environment Management**: python-dotenv

## 📊 Quiz Structure

The quiz consists of 10 carefully crafted questions covering various aspects of personality:
- Social interactions
- Decision-making processes
- Communication styles
- Work preferences
- Personal habits

## 🤖 AI Analysis

The app uses Mistral AI to provide:
- MBTI-inspired personality type analysis
- Detailed personality descriptions
- Personalized traits and strengths
- Growth area suggestions

## 🎨 Customization

You can modify the quiz by adjusting:
- `QUESTIONS` list in `app.py` for different questions
- `TIMER_DURATION` for question time limits
- Visualization styles in the plotting functions

## ✨ Acknowledgments

- Powered by Mistral AI
- Built with Streamlit
- Inspired by MBTI personality theory
