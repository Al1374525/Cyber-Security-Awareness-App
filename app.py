
import streamlit as st
import json
import random
import os
from openai import OpenAI



def load_scenarios():
    try:
        with open('scenarios.json', 'r') as file:
            data = json.load(file)
            if not isinstance(data, dict) or 'scenarios' not in data:
                raise KeyError("Missing 'scenarios' key in JSON")
            return data
    except FileNotFoundError:
        st.error("scenarios.json not found in project directory!")
        return {"scenarios": []}
    except json.JSONDecodeError:
        st.error("Invalid JSON format in scenarios.json!")
        return {"scenarios": []}
    except PermissionError:
        st.error("Permission denied accessing scenarios.json!")
        return {"scenarios": []}

# Initialize session state to track current scenario
if 'current_scenario_id' not in st.session_state:
    st.session_state.current_scenario_id = random.choice(['1', '4']) #added this for a random choice berween these scenarios
if 'scenarios' not in st.session_state:
    loaded_data = load_scenarios()
    try:
        st.session_state.scenarios = loaded_data['scenarios']
    except KeyError as e:
        st.error("Invalid structure in scenarios.json: Missing 'scenarios' key.")
        st.session_state.scenarios = []


#Get current scenario by ID
def get_scenario(scenarios, scenario_id):
    for scenario in scenarios:
        if scenario['id'] == scenario_id:
            return scenario
    return None

#Generate new scenario via xAI API key
def generate_ai_scenario():
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        st.error("XAI_API_KEY environment variable not set. Visit https://x.ai/api.")
        return None
    client = OpenAI(base_url="https://api.x.ai/v1/chat/completions", api_key=api_key)
    prompt = """
    Generate a single IT Help Desk cybersecurity scenario in JSON format:
    {
        "description": "A brief scenario description (1-2 sentences).",
        "choices": [
            {"text": "Choice 1", "is_correct": true, "feedback": "Correct feedback.", "next_id": null},
            {"text": "Choice 2", "is_correct": false, "feedback": "Wrong feedback.", "next_id": null},
            {"text": "Choice 3", "is_correct": false, "feedback": "Wrong feedback.", "next_id": null}
        ]
    }
    Focus on realistic help desk tasks like phishing, passwords, or malware. Make one choice correct.
    """
    try:
        response = client.chat.completions.create(
            model="grok-3-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300
        )
        ai_json = response.choices[0].message.content.strip()
        if not ai_json:
            st.error("API returned empty response. Check network or API key.")
            return None
        if ai_json.startswith('```json'):
            ai_json = ai_json[7:].rstrip('```').strip()
        try:
            new_scenario = json.loads(ai_json)
            if not isinstance(new_scenario, dict) or 'description' not in new_scenario or 'choices' not in new_scenario:
                st.error(f"API response missing required fields (description, choices). Raw response: {ai_json}")
                return None
            new_scenario['id'] = f"ai_{len(st.session_state.scenarios) + 1}"
            st.session_state.scenarios.append(new_scenario)
            return new_scenario['id']
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON from API: {str(e)}. Raw response: {ai_json}")
            return None
    except Exception as e:
        error_msg = f"API request failed: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            error_msg += f" (HTTP {e.response.status_code})"
        st.error(f"{error_msg}. Check key or network.")
        return None

    



#Main app logic
def main():
    st.title("IT Help Desk Cybersecurity Simulator")

    #Load scenarios
    if not st.session_state.scenarios:
        st.stop()
    
    #Button to generate AI scenario
    if st.button("Generate New Scenario via AI"):
        new_id = generate_ai_scenario()
        if new_id:
            st.session_state.current_scenario_id = new_id()
            st.rerun()
    
    #Get current scenarios
    current_scenario = get_scenario(st.session_state.scenarios, st.session_state.current_scenario_id)
    if not current_scenario:
        st.error("Scenario not found!")
        st.stop()
    
    #Display scenario description
    st.write(current_scenario['description'])

    #Display choices as radio buttons
    choice = st.radio("What do you do?", [c['text'] for c in current_scenario['choices']], key="choice")

    #Submit button
    if st.button("Submit"):
        if choice:
            #Find selected choice
            selected = next(c for c in current_scenario['choices'] if c['text'] == choice )

            #show  and correct answer feedback
            if selected['is_correct']:
                st.markdown("**Correct!**")
            else:
                st.markdown("**Wrong**")
            st.write(f"**Feedback**: {selected['feedback']}")

            #Update to next scenario
            if selected['next_id']:
                st.session_state.current_scenario_id = selected['next_id']
                st.rerun() #refresh to show new scenario
            else:
                st.write("End of scenario. Thank you for playing! Restart to try again!")
                if st.button('Restart'):
                    st.session_state.current_scenario_id = random.choice(['1', '4']) #reset to a random scenario
                    st.rerun()
        else:
            st.warning("Please select a choice before submitting.")

if __name__ == "__main__":
    main()
