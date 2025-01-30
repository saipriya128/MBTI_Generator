from typing import Dict
import random
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PersonalityAnalyzer:
    def __init__(self):
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("MISTRAL_API_KEY not found in environment variables")
        self.client = MistralClient(api_key=api_key)
        
    def generate_analysis_prompt(self, answers: Dict[int, str], questions) -> str:
        """Generate a prompt for Mistral AI based on user's answers."""
        prompt = """Analyze these quiz responses and give us a personality deep-dive! Mix professional MBTI insights with relatable examples.

        1. Core MBTI Analysis:
        - Break down their type preferences (E/I, S/N, T/F, J/P)
        - Show how their answers reveal their type (like "choosing 'Netflix marathon' over 'spontaneous road trip' gives us introverted vibes")
        - Explain their cognitive function stack (like Ni-Fe-Ti-Se) and how it shows up in their answers
        - Connect their answers to famous people/characters with the same type

        2. Deep Personality Insights:
        - Their energy style (how they recharge and what drains them)
        - Decision-making approach (what their answers reveal about how they solve problems)
        - Social style (their unique way of connecting with others)
        - Stress patterns (how they handle pressure, based on their answers)
        - Communication preferences (their natural way of expressing themselves)

        3. Real-Life Applications:
        - How their type shows up in friendships
        - Their likely work/study style
        - Their approach to challenges
        - Natural talents and potential blind spots

        Format your response like this:
        TITLE: [A creative nickname that captures their essence]
        TYPE: [MBTI type with a clear, relatable explanation of why]
        EMOJI: [A spot-on emoji for their vibe]
        DESCRIPTION: [A thorough analysis that mixes MBTI theory with real-world examples from their answers. Make it engaging - like a friend who really gets MBTI explaining things over coffee. Minimum 300 words.]
        TRAITS: [Key personality traits with specific examples from their answers]
        STRENGTHS: [Their superpowers, based on their type and answers]
        GROWTH_AREAS: [Gentle suggestions for development, explained in a supportive way]

        Here are their responses:\n"""
        
        for question_num, answer in answers.items():
            prompt += f"Question: {questions[question_num]['text']}\n"
            prompt += f"Answer: {answer}\n\n"
        
        prompt += "\nGive us a balanced analysis that's both insightful and relatable. Mix some casual language with proper MBTI insights!"
        
        return prompt

    def analyze_responses(self, answers: Dict[int, str], questions) -> dict:
        """Use Mistral AI to analyze quiz responses and generate a personality profile."""
        try:
            if not os.getenv("MISTRAL_API_KEY"):
                print("No API key found! Please check your .env file")
                return self._get_fallback_analysis(answers)
            
            prompt = self.generate_analysis_prompt(answers, questions)
            
            messages = [
                ChatMessage(
                    role="system", 
                    content="""You are a personality analyst who deeply understands MBTI theory while keeping things relatable. 
                    For each analysis:
                    - Break down cognitive functions in a way that makes sense (like explaining how Fe users are the friends who always know when someone's upset)
                    - Use specific examples from their answers to support your type assessment
                    - Mix professional insights with casual observations
                    - Explain MBTI concepts clearly without getting too technical
                    - Connect their type to real-world behaviors and tendencies
                    - Keep it balanced between formal MBTI theory and friendly chat
                    """
                ),
                ChatMessage(role="user", content=prompt)
            ]
            
            try:
                response = self.client.chat(
                    model="mistral-medium",
                    messages=messages,
                    temperature=0.9,
                    max_tokens=1500
                )
                
                # The response structure has changed - let's handle it correctly
                if not response or not response.choices:
                    print("Empty response from Mistral API")
                    return self._get_fallback_analysis(answers)
                
                # Get the message content from the first choice
                message_content = response.choices[0].message.content
                if not message_content:
                    print("Empty message content from API")
                    return self._get_fallback_analysis(answers)
                    
                result = self._parse_mistral_response(message_content)
                return result
                
            except Exception as api_error:
                print(f"API Error: {str(api_error)}")
                return self._get_fallback_analysis(answers)
            
        except Exception as e:
            print(f"General Error: {str(e)}")
            return self._get_fallback_analysis(answers)
    
    def _parse_mistral_response(self, response_text: str) -> dict:
        """Parse the Mistral AI response into structured format."""
        try:
            sections = {
                "title": "",
                "type": "",
                "emoji": "",
                "description": [],
                "traits": [],
                "strengths": [],
                "growth_areas": []
            }
            
            current_section = None
            lines = response_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith("TITLE:"):
                    current_section = "title"
                    sections["title"] = line.replace("TITLE:", "").strip()
                elif line.startswith("TYPE:"):
                    current_section = "type"
                    sections["type"] = line.replace("TYPE:", "").strip()
                elif line.startswith("EMOJI:"):
                    sections["emoji"] = line.replace("EMOJI:", "").strip()
                elif line.startswith("DESCRIPTION:"):
                    current_section = "description"
                elif line.startswith("TRAITS:"):
                    current_section = "traits"
                    traits = line.replace("TRAITS:", "").strip()
                    if traits and ',' in traits:
                        sections["traits"] = [t.strip() for t in traits.split(",")]
                    else:
                        sections["traits"] = [traits] if traits else []
                elif line.startswith("STRENGTHS:"):
                    current_section = "strengths"
                    strengths = line.replace("STRENGTHS:", "").strip()
                    if strengths and ',' in strengths:
                        sections["strengths"] = [s.strip() for s in strengths.split(",")]
                    else:
                        sections["strengths"] = [strengths] if strengths else []
                elif line.startswith("GROWTH_AREAS:"):
                    current_section = "growth_areas"
                    areas = line.replace("GROWTH_AREAS:", "").strip()
                    if areas and ',' in areas:
                        sections["growth_areas"] = [a.strip() for a in areas.split(",")]
                    else:
                        sections["growth_areas"] = [areas] if areas else []
                elif current_section == "description":
                    sections["description"].append(line)
                elif current_section == "traits" and line and not line.startswith("-"):
                    sections["traits"].append(line)
                elif current_section == "strengths" and line and not line.startswith("-"):
                    sections["strengths"].append(line)
                elif current_section == "growth_areas" and line and not line.startswith("-"):
                    sections["growth_areas"].append(line)
            
            # Clean up lists - remove any empty strings
            sections["traits"] = [t for t in sections["traits"] if t]
            sections["strengths"] = [s for s in sections["strengths"] if s]
            sections["growth_areas"] = [a for a in sections["growth_areas"] if a]
            
            # Handle bullet points if present
            for key in ["traits", "strengths", "growth_areas"]:
                new_items = []
                for item in sections[key]:
                    if item.startswith("- "):
                        new_items.append(item[2:])
                    elif item.startswith("• "):
                        new_items.append(item[2:])
                    else:
                        new_items.append(item)
                sections[key] = new_items
            
            return {
                "title": sections["title"] or "The Personality Explorer",
                "type": sections["type"] or "Personality Type Analysis",
                "emoji": sections["emoji"] or "✨",
                "description": "\n\n".join(sections["description"]),
                "traits": sections["traits"] or ["Unique", "Complex", "Multifaceted"],
                "strengths": sections["strengths"] or ["Adaptability", "Insight", "Growth Mindset"],
                "growth_areas": sections["growth_areas"] or ["Continuing to explore", "Embracing change", "Self-discovery"]
            }
        except Exception as e:
            print(f"Error parsing AI response: {str(e)}")
            return self._get_fallback_analysis(answers)
    
    def _get_fallback_analysis(self, answers: Dict[int, str]) -> dict:
        """Provide a fallback analysis based on actual answers."""
        # Analyze answers for personality tendencies
        answers_text = ' '.join(answers.values()).lower()
        
        # Simple keyword analysis
        keywords = {
            'E': ['out', 'social', 'friends', 'party', 'people', 'group'],
            'I': ['alone', 'quiet', 'few', 'home', 'individual'],
            'S': ['detail', 'fact', 'practical', 'present', 'reality'],
            'N': ['future', 'possibility', 'imagine', 'theory', 'abstract'],
            'T': ['logic', 'analyze', 'think', 'pros and cons', 'objective'],
            'F': ['feel', 'value', 'harmony', 'emotion', 'care'],
            'J': ['plan', 'organize', 'structure', 'decide', 'control'],
            'P': ['flexible', 'adapt', 'spontaneous', 'flow', 'explore']
        }
        
        # Count occurrences
        scores = {letter: sum(answers_text.count(word) for word in words) 
                 for letter, words in keywords.items()}
        
        # Determine type
        mbti = ''
        mbti += 'E' if scores['E'] > scores['I'] else 'I'
        mbti += 'N' if scores['N'] > scores['S'] else 'S'
        mbti += 'T' if scores['T'] > scores['F'] else 'F'
        mbti += 'J' if scores['J'] > scores['P'] else 'P'
        
        return {
            "title": f"The {mbti} Explorer",
            "type": mbti,
            "emoji": "✨",
            "description": "Analysis unavailable at the moment. Please try again later.",
            "traits": ["Analytical", "Adaptable", "Thoughtful"],
            "strengths": ["Problem solving", "Communication", "Creativity"],
            "growth_areas": ["Balance", "Patience", "Self-reflection"]
        }

def analyze_personality(answers: Dict[int, str], questions) -> dict:
    """
    Wrapper function to analyze quiz responses using the PersonalityAnalyzer.
    """
    analyzer = PersonalityAnalyzer()
    return analyzer.analyze_responses(answers, questions)

def get_mistral_analysis(text: str) -> str:
    """Get raw analysis from Mistral AI."""
    try:
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("MISTRAL_API_KEY not found in environment variables")
            
        client = MistralClient(api_key=api_key)
        messages = [
            ChatMessage(role="system", content="You are an insightful personality analyst."),
            ChatMessage(role="user", content=text)
        ]
        
        response = client.chat(
            model="mistral-medium",  # Changed from tiny to medium for better analysis
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in raw analysis: {str(e)}")
        return "Unable to generate analysis at this time." 