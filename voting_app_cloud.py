from dataclasses import dataclass
import streamlit as st
import os
import json
from web3 import Web3
from pathlib import Path
import pandas as pd
import plotly.express as px
from google.cloud import firestore


##################  CONFIGURE PAGE ####################

st.set_page_config(page_title = "Voting dApp", page_icon = "🗳️") # add title and emoji to tab in browser

################  INITIALIZE SESSION STATES ################

# PAGES - allows us to control which 'page' the user is on base on the steps they've completed
if 'verified' not in st.session_state:
    st.session_state.verified = False 

if 'voted' not in st.session_state:
    st.session_state.voted = False

if 'view_results' not in st.session_state:
    st.session_state.view_results = False

# THINGS - important variable to remember and recall while using the app
if 'address' not in st.session_state:
    st.session_state.address = "no address"

if 'name' not in st.session_state:
    st.session_state.name = "no name"

if 'location' not in st.session_state:
    st.session_state.location = 0

if 'vote' not in st.session_state:
    st.session_state.vote = 0


##################  INITIALIZE FIRESTORE  ####################

# Connect to Firestore client - authenticate with json file
db = firestore.Client.from_service_account_json("firestore_key.json") 

# Read Database - Covert to Dataframe
votes = list(db.collection(u'voting_app').stream()) # stream data and store in votes
votes_dict = list(map(lambda x: x.to_dict(), votes))  # convert votes to a dictionary
df = pd.DataFrame(votes_dict) # convert dictionary to a dataframe

# Define function to write voter entries as 'documents'
def write_to_db(address, name, location, proposal):
    doc_ref = db.collection("voting_app").document(address)
    doc_ref.set({
        "address": address,
        "name": name,
        "location": location,
        "vote": proposal
    })

# Create a reference to the Google post.
   #doc_ref = db.collection("voting_app").document("votes")
# Then get the data at that reference.
   #doc = doc_ref.get()
# Let's see what we got!
   #st.write("The id is: ", doc.id)
   #st.write("The contents are: ", doc.to_dict())


################ INITIALIZE VARIABLES ################

# Lists
address_list = ["0x5E3c0ae41B4B8c70D10b376517C0CC7e4d37150c" , "0x658B07936e2f349C7c8E025d9F6ECeB8848BC2CE" , "0x5F2c48AFE1BeF0F1394BefBDB0D7822e1d583B02" , "0x9f801f9Fc343D2782D3c276361A3157FD036DC57" , "0x9eD64EBc9b06DF5f2dEb83b2E00fF12F1B6AAc05" , "0xee2bd6BeEe24f22c0253A5a2b2f27c6F40e44C37" , "0x90c6cBA31ECf29Acf5C439fa7AbD72a638B85Fb8" , "0x2F9002cb4d6C5b8A3f28A54390CFE8cA82E61813" , "0x7e517EA68A81F516ad44804844a9CbA305242197" , "0xFDC9DA12f141037181Ca5Bd29939068944A69cfD"]
location_list = ["Center City Philly" , "South Philly" , "North Philly" , "West Philly" , "Greater Philadelphia" , "Outside Philadelphia Area"]
proposals_list = ["P1 - Harm Reduction Program", "P2 - After School Program", "P3 - Clean Up"]

########################  MAIN BODY HEADER  ###########################

st.image("images/dao_or_die_grey.png")  # Main title image
st.image("images/serve_community_blue.png")  # Subtitle image
st.write("______________________")  # a line


########################  VIEW FIRESTORE DATAFRAME  ############################

#st.write(df)
#st.write("______________________")  # a line


########################  PAGES  ###########################

####  VERIFY ADDRESS - Page 1  ###
if st.session_state.verified == False: # check session state, if session state is false all nested code will be run/displayed
    st.write("### Verify Your Address") # Title
    address = st.text_input("Input your wallet address to verify your are eligible to vote") # Create the variable 'address' and saves the text input from the user in it
    ss_verified = st.button("Verify Address") # Initialize the Verify button
    if ss_verified: # If button pushed, then...
        if address in address_list: # If the address is in the address list, then...
            st.session_state.verified = True # Update verified session state to True
            st.session_state.address = address # save address to session state
            st.experimental_rerun() # Rerun the whole app to guarentee everything displayed is up to date
        else:
            st.error("This wallet address is not eligible to vote.") # error message if your address is not verified


#### VOTE - Page 2  ###
elif st.session_state.voted == False:  # check session state, if session state is false all nested code will be run/displayed
    st.write("### Cast Your Vote") # Title
    st.info(f"This address is registered to vote : {st.session_state.address}") # success message displaying the address to the user
    st.markdown("##")
    location = st.selectbox("Choose your co-op location", options=location_list) # location drop down menu
    vote = st.selectbox("Vote for a proposal", options=proposals_list)  # proposal drop down menu
    name = st.text_input("Optional: Enter your name / nickname (Allows you to see your vote in the dataframe)")
    st.session_state.location = location
    st.session_state.vote = vote  # save the list index of the proposal in the session state
    st.session_state.name = name

    ss_voted = st.button("Vote") # Initialize the Vote button 
    if ss_voted:  # If the Vote button is pushed, then...
        st.session_state.voted = True
        st.experimental_rerun()


### CONFIRMATION - Page 3  ###
elif st.session_state.view_results == False: # check session state, if session state is false all nested code will be run/displayed
    
    # Can't Vote Again
    if st.session_state.address in df.values:
        b1, c1, b2 = st.columns([1,5,1]) # columns
        with c1: # middle column
            st.write("## You can't vote again") # text
            st.image("images/no.gif") # Danny DeVito gif 
            st.error("Nope. You cannot vote because you already voted.")  # error message
            st.markdown("#") # spacer
            ss_view_results = st.button("View Results") # view results button
            if ss_view_results: # if button is pushed, then...
                st.session_state.view_results = True # set session state to True
                st.experimental_rerun() # rerun the whole app so the display is updated
    
    # Successful Vote
    else:
        write_to_db(st.session_state.address, st.session_state.name, st.session_state.location, st.session_state.vote)
        b1, c1, b2 = st.columns([1,5,1]) # columns
        with c1: # middle columns
            st.write("## Your vote has been submitted!") # title
            st.image("images/yes.gif") # Zach Galifianakis gif
            st.info(f"Your vote for {st.session_state.vote} has been submitted") # message displaying which proposal was submitted
            st.markdown("#") # spacer
            #st.experimental_rerun() # rerun the whole app so the display is updated

        b1, c1, b2 = st.columns([1,5,1]) # columns
        with c1: # middle column
            ss_view_results = st.button("View Results") # view results button
            if ss_view_results: # if button is pushed, then...
                st.session_state.view_results = True # set session state to True
                st.experimental_rerun() # rerun the whole app so the display is updated

### VIEW RESULTS - Page 4 ###
else: # check session state, if session state is false all nested code will be run/displayed
    
    # DATAFRAME - groupby proposal
    gb_vote_df = df.groupby('vote').size().reset_index()
    gb_vote_df.columns = ['Proposal' , 'Votes']

    # DATAFRAME - groupby location
    gb_location_df = df.groupby('location').size().reset_index()
    #st.write(gb_location_df)
    gb_location_df.columns = ['Location' , 'Votes']   

    # DATAFRAME - groupby proposal & location
    sunburst_df = df.groupby(['vote' , 'location']).size().reset_index()
    sunburst_df.columns = ['Proposal' , 'Location' , "Votes"]

    # BAR CHART - STACKED
    st.markdown("### Votes by Proposal (Subdivided by Location)")
    sunburst_df = df.groupby(['vote' , 'location']).size().reset_index()
    sunburst_df.columns = ['Proposal' , 'Location' , "Votes"]
    stacked_bar_fig = px.bar(sunburst_df, x="Proposal", y="Votes", color="Location", height=600,  text_auto=True)
    st.plotly_chart(stacked_bar_fig, use_container_width=True) # disply the bar graph
    st.write("______________________")

    # PIE CHART - SUNBURST
    st.markdown("### Votes by Proposal (Subdivided by Location)")
    st.write("Hover and click in interact with pie chart")
    sunburst_fig = px.sunburst(sunburst_df, path=['Proposal', 'Location'], values='Votes')
    st.plotly_chart(sunburst_fig, ) # disply the bar graph use_container_width=True
    st.write("______________________")


    # Bar Chart - Total Vote by Proposal
    st.markdown("### Votes by Location")

    bar_fig = px.bar(x=gb_location_df.Location, y=gb_location_df.Votes, color=gb_location_df.Location) # initialize the bar graph
    bar_fig.update_yaxes(title="Votes") # y axis title
    bar_fig.update_xaxes(title="") # x axis title
    st.plotly_chart(bar_fig, use_container_width=True) # disply the bar graph
    st.write("______")
    #st.write(gb_vote_df)


    st.markdown("### Raw Dataframe")
    st.write(df)
    st.markdown("#")


    # Button to start over
    start_over_1 = st.button("Start Over")  # a start over button
    if start_over_1:  # if the button is pushed, then....
        st.session_state.voted = False  # update session state to false
        st.session_state.verified = False  # update session state to false
        st.session_state.view_results = False  # update session state to false
        st.experimental_rerun() # rerun the whole app so the display is updated




    # Pie Chart
    #pie_fig = px.pie(df, values='Votes', names='Proposal')  # initialize the pie graph
    #st.plotly_chart(pie_fig, use_container_width=True) # display the pie graph
    #st.write("______________________") # a line


















########################  Sidebar ###########################

#IMAGES
st.sidebar.image("images/voting_dapp_image.png")  # title image
st.sidebar.title("ABOUT")  # title

# How to Use this Dapp
with st.sidebar.expander("How to use this Dapp ", expanded=False):
    st.write("STEP 1: In the 'About the Proposals' section below, familiarize yourself with the proposals and choose which one you'd like to vote for.")
    st.write("STEP 2: In the 'Verify your Address' section to the right, enter the verified wallet address you are permitted to vote with.  Click 'Verify Address' ")
    st.write("STEP 3: Once your address is verified the 'Vote' section will appear.  Choose the proposal you want to vote for and the Co-Op you are assocated with.  Then click the 'Vote' button. ")

# About 'DAO or DIE'
with st.sidebar.expander("About 'DAO or DIE' ", expanded=False):
    st.write("For its work in the community, DAO or Die has received a grant of $25,000 to spend on a community service project of its choosing.  The DAO members vote to decide how to spend the funds.  See the proposals below.")

# About the Proposals
with st.sidebar.expander("About the Proposals", expanded=False):
    proposal_info = st.selectbox("", options = proposals_list)
    if proposal_info == proposals_list[0]:
        st.write("### Harm Reduction Project:")
        st.write("Fund overdose prevention programs, syringe access implementation programs, and expenses for training and capacity facilities.")
    elif proposal_info == proposals_list[1]:
        st.write("### After School Programs:")
        st.write("Fund after school programs for Low Income Schools.  This includes staff and supplies for after school activites related to arts, music, and sports.")
    elif proposal_info == proposals_list[2]:
        st.write("### Clean Up:")
        st.write("Fund expenses related to organizing and executing a nationwide clean-up initiative across the US")
    else:
        st.empty()

# Button to start over
st.sidebar.write("______")
c1, c2, c3 = st.sidebar.columns([1, 2, 1])

with c2:
    start_over_sidebar = st.button("> Start Over <")  # a start over button
    if start_over_sidebar:  # if the button is pushed, then....
        st.session_state.voted = False  # update session state to false
        st.session_state.verified = False  # update session state to false
        st.session_state.view_results = False  # update session state to false
        st.experimental_rerun() # rerun the whole app so the display is updated


###### SESSION STATE TRACKER ####### 
# This section displays the status of the various session states which is useful during development)

#st.sidebar.write("# State")
#st.sidebar.write(f"Address Verified: " , st.session_state.verified)
#st.sidebar.write(f"Voted :" , st.session_state.voted)
#st.sidebar.write(f"Viewed Results:" , st.session_state.view_results)

#st.sidebar.write("__")
#st.sidebar.write(f"Address :" , st.session_state.address)
#st.sidebar.write(f"Name :" , st.session_state.name)
#st.sidebar.write(f"Location:" , st.session_state.location)
#st.sidebar.write(f"Vote:" , st.session_state.vote)





