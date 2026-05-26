  GNU nano 8.4                                                                        app.py                                                                                  
import streamlit as st
import os
from simulacra_v2 import run_simulation

warehouse_mode = True

TITLE = "Simulacra Warehouse Mode"
SUBTITLE = "Testing robot coordination before deployment."


st.title(TITLE)
st.caption(SUBTITLE)

left, center, right = st.columns([1.2, 3, 1])

with left:
    st.header("Controls")

    run = st.button("Run Simulation")    
    
    mode = st.radio(
        "Coordination policy",
        ["Free routing", "Balanced routing", "Strict routing"]
    )

    if mode == "Free routing":
        edge_penalty = 0.0
    elif mode == "Balanced routing":
        edge_penalty = 3.5
    else:
        edge_penalty = 6.0


with center:
    st.header("Simulation")

    if run:
        with st.spinner("Running simulation..."):
            gif_path, metrics = run_simulation(edge_penalty=edge_penalty)
        st.image(gif_path,use_container_width=True)
    else:
        st.info("Choose a demo mode, then click Run Simulation.")



                                                                              [ Read 66 lines ]
^G Help          ^O Write Out     ^F Where Is      ^K Cut           ^T Execute       ^C Location      M-U Undo         M-A Set Mark     M-] To Bracket   M-B Previous
^X Exit          ^R Read File     ^\ Replace       ^U Paste         ^J Justify       ^/ Go To Line    M-E Redo         M-6 Copy         ^B Where Was     M-F Next
