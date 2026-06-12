import streamlit as st
import requests
import uuid

# Configuration
API_URL = "http://127.0.0.1:8000"

st.title("GM Financial Agent")


# Helper function to recursively flatten and clean the response
def clean_response(data):
    """
    Cleans incoming data to remove list artifacts, nested structures,
    and character debris like brackets or quotes.
    """
    if isinstance(data, list):
        flat_list = []
        for item in data:
            if isinstance(item, list):
                flat_list.extend(item)
            else:
                flat_list.append(str(item))
        # Join into a single block of text and strip out list characters
        text = "\n".join(flat_list)
    else:
        text = str(data)

    return text.replace("[", "").replace("]", "").replace("'", "").replace('"', "")


# --- State Initialization ---
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "waiting_for_approval" not in st.session_state:
    st.session_state.waiting_for_approval = False

# --- User Input ---
question = st.text_input("Ask a question about your lease:")

if st.button("Submit"):
    payload = {"thread_id": st.session_state.thread_id, "question": question}
    try:
        response = requests.post(f"{API_URL}/start_query", json=payload).json()

        if response.get("status") == "paused":
            st.session_state.waiting_for_approval = True
            st.warning("Agent paused: Critical query detected. Human approval required.")
        else:
            st.success("Result:")
            st.write(clean_response(response.get("result", "")))
    except Exception as e:
        st.error(f"Could not connect to backend: {e}")

# --- Approval Flow ---
if st.session_state.waiting_for_approval:
    if st.button("Approve & Finalize"):
        app_payload = {"thread_id": st.session_state.thread_id, "approved": True}
        try:
            final_res = requests.post(f"{API_URL}/approve", json=app_payload).json()

            st.success("Result:")
            st.write(clean_response(final_res.get("result", "")))

            # Reset state after completion
            st.session_state.waiting_for_approval = False
        except Exception as e:
            st.error(f"Approval failed: {e}")