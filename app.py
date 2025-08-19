import streamlit as st
import json

# Initialize session state to track current scenario
if 'scenario' not in st.session_state:
    st.session_state.scenario = '1'

#Load scenarios from JSON file
def load_scenarios():
    try:
        with open('scenarios.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        st.error("scenarios.json not found!")
        return {"scenarios": []}

#Get current scenario by ID
def get_scenario(scenarios, scenario_id):
    for scenario in scenarios.get("scenarios", []):
        if scenario.get("id") == scenario_id:
            return scenario
    return None



#Main app logic
def main():
    st.title("IT Help Desk Cybersecurity Simulator")

    #Load scenarios
    scenarios = load_scenarios()
    if not scenarios['scenarios']:
        st.stop()
    
    #Get current scenarios
    current_scenario = get_scenario(scenarios, st.session_state.scenario)
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
                st.session_state.scenario = selected['next_id']
                st.rerun() #refresh to show new scenario
            else:
                st.write("End of scenario. Thank you for playing! Restart to try again!")
                if st.button('Restart'):
                    st.session_state.scenario = '1'
                    st.rerun()
        else:
            st.warning("Please select a choice before submitting.")

if __name__ == "__main__":
    main()
