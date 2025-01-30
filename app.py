import streamlit as st
from datetime import datetime, timedelta
import time
from quiz_agent import analyze_personality, get_mistral_analysis
import plotly.graph_objects as go

# Quiz Configuration
TIMER_DURATION = 30  # seconds per question

# Quiz questions and options
QUESTIONS = [
    {
        "text": "Your friend just spilled a huge secret. You...",
        "options": [
            "Can't help but tell someone else",
            "Take it to the grave",
            "Tell only if someone really needs to know",
            "Forget about it immediately"
        ]
    },
    {
        "text": "It's Friday night and your phone's buzzing with plans. You're most likely to...",
        "options": [
            "Already be out somewhere",
            "Make up an excuse to stay in",
            "Join if your best friend is going",
            "Suggest a smaller hangout instead"
        ]
    },
    {
        "text": "Your brain at 3 AM usually...",
        "options": [
            "Replays embarrassing moments from 2015",
            "Plans your next big life move",
            "Thinks about random facts",
            "Actually sleeps like a normal person"
        ]
    },
    {
        "text": "Someone disagrees with you in the group chat. You...",
        "options": [
            "Write a whole essay with sources cited",
            "Send a meme and change the subject",
            "Start a friendly debate",
            "Leave them on read"
        ]
    },
    {
        "text": "Your idea of a perfect weekend is...",
        "options": [
            "Netflix marathon in your blanket fort",
            "Spontaneous road trip with friends",
            "Trying that new thing everyone's talking about",
            "Finally organizing your life"
        ]
    },
    {
        "text": "When your friend is going through it, you typically...",
        "options": [
            "Offer practical solutions",
            "Just listen and validate",
            "Share your own similar experience",
            "Distract them with fun activities"
        ]
    },
    {
        "text": "Your camera roll is full of...",
        "options": [
            "Aesthetic shots that never make it to Instagram",
            "Screenshots you'll never look at again",
            "Memes to send at the perfect moment",
            "Photos of things you need to remember"
        ]
    },
    {
        "text": "When making big decisions, you usually...",
        "options": [
            "Go with your gut feeling",
            "Make a pros and cons list",
            "Ask everyone you know for advice",
            "Google it extensively"
        ]
    },
    {
        "text": "Your friends would describe you as the one who...",
        "options": [
            "Always has a crazy story to tell",
            "Knows everyone's secrets",
            "Comes through in a crisis",
            "Has the best recommendations"
        ]
    },
    {
        "text": "In group projects, you naturally become the...",
        "options": [
            "Ideas person with big plans",
            "One who actually gets it done",
            "Peacekeeper between strong personalities",
            "Editor who fixes everything last minute"
        ]
    }
]

def initialize_session_state():
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'answers' not in st.session_state:
        st.session_state.answers = {}
    if 'quiz_complete' not in st.session_state:
        st.session_state.quiz_complete = False
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None

def display_timer():
    if st.session_state.start_time:
        elapsed_time = datetime.now() - st.session_state.start_time
        remaining_time = max(TIMER_DURATION - elapsed_time.seconds, 0)
        progress = remaining_time / TIMER_DURATION
        st.progress(progress)
        st.write(f"⏱️ Time remaining: {remaining_time} seconds")
        return remaining_time
    return TIMER_DURATION

def handle_answer(answer):
    st.session_state.answers[st.session_state.current_question] = answer
    st.session_state.current_question += 1
    st.session_state.start_time = datetime.now()

def create_trait_radar_chart(traits, values):
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=traits,
        fill='toself',
        line=dict(color='rgb(111, 231, 219)'),
        fillcolor='rgba(111, 231, 219, 0.5)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=70, r=70, t=20, b=20)
    )
    return fig

def create_personality_bars(personality_result):
    # Create sample scores for personality dimensions
    dimensions = {
        "Introversion-Extroversion": 65,
        "Intuition-Sensing": 80,
        "Thinking-Feeling": 45,
        "Judging-Perceiving": 70
    }
    
    fig = go.Figure()
    
    for dim, score in dimensions.items():
        fig.add_trace(go.Bar(
            x=[score],
            y=[dim],
            orientation='h',
            marker=dict(
                color='rgb(111, 231, 219)',
                line=dict(color='rgb(8, 48, 107)', width=2)
            )
        ))
    
    fig.update_layout(
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=20, b=20),
        xaxis=dict(range=[0, 100])
    )
    return fig

def main():
    st.title("✨ What's Your Vibe? Personality Quiz")
    st.markdown("""
    ### Hey there! 
    Let's figure out what makes you uniquely you! No pressure, just pick whatever feels right - 
    there are no wrong answers here! 😊
    """)
    
    initialize_session_state()

    if not st.session_state.quiz_complete:
        if st.session_state.current_question < len(QUESTIONS):
            current_q = QUESTIONS[st.session_state.current_question]
            
            # Display progress
            progress = st.session_state.current_question / len(QUESTIONS)
            st.progress(progress)
            st.write(f"Question {st.session_state.current_question + 1} of {len(QUESTIONS)}")
            
            # Display question and options
            st.write(f"### {current_q['text']}")
            
            for option in current_q['options']:
                if st.button(option, key=option, use_container_width=True):
                    handle_answer(option)
                    st.rerun()
                
        else:
            st.session_state.quiz_complete = True
            st.rerun()
    
    else:
        # Display results with a more casual loading message
        with st.spinner("✨ Analyzing your vibes..."):
            personality_result = analyze_personality(st.session_state.answers, QUESTIONS)
            
        st.success("The results are in! 🎉")
        st.balloons()
        
        # Create tabs for different sections of the results
        tab1, tab2 = st.tabs(["The Scoop", "The Details"])
        
        with tab1:
            st.markdown(f"## {personality_result['title']}")
            st.markdown(f"# {personality_result['emoji']}")
            
            # Display personality type with custom styling
            st.markdown(
                f"""
                <div style='background-color: rgba(111, 231, 219, 0.1); 
                           padding: 20px; 
                           border-radius: 10px; 
                           border: 2px solid rgba(111, 231, 219, 0.5);'>
                    <h3 style='text-align: center;'>{personality_result['type']}</h3>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            # Display main description
            st.markdown("### Here's Your Personality Breakdown")
            st.markdown(personality_result['description'])
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### ✨ What Makes You, You")
                for trait in personality_result['traits']:
                    st.markdown(
                        f"""
                        <div style='background-color: rgba(111, 231, 219, 0.1); 
                                   padding: 10px; 
                                   margin: 5px 0; 
                                   border-radius: 5px;'>
                            ✦ {trait}
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
            
            with col2:
                st.markdown("### 🌟 Your Superpowers")
                for strength in personality_result['strengths']:
                    st.markdown(
                        f"""
                        <div style='background-color: rgba(111, 231, 219, 0.1); 
                                   padding: 10px; 
                                   margin: 5px 0; 
                                   border-radius: 5px;'>
                            • {strength}
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
        
        # Add a download button for full report
        st.download_button(
            label="Save Your Results ✨",
            data=f"""
            Your Personality Scoop! ✨
            
            You're a: {personality_result['type']}
            
            The Full Story:
            {personality_result['description']}
            
            Your Superpowers:
            {', '.join(personality_result['strengths'])}
            
            What Makes You Special:
            {', '.join(personality_result['traits'])}
            """,
            file_name="my_personality_scoop.txt",
            mime="text/plain",
        )
        
        if st.button("Take the Quiz Again!", use_container_width=True):
            st.session_state.clear()
            st.rerun()

if __name__ == "__main__":
    main() 