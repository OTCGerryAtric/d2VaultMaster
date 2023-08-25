import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from typing import Any

# Set Page Config
st.set_page_config(page_title="Destiny 2 Vault Tool", page_icon=None, layout="wide", initial_sidebar_state="expanded", menu_items=None)

# Define Session State
class SessionState:
    def __init__(self, **kwargs: Any):
        self.__dict__.update(kwargs)

# Import Manifest
from csv_processing import load_manifest_data
weapon_manifest_file = load_manifest_data('data/Master Weapon Manifest.csv')

# Define Navigation Bar
def navigation():
    st.sidebar.title('Navigation')
    selection = st.sidebar.selectbox("Go to", ['Home', 'Vault Summary', 'Weapon Analysis', 'Weapon Comparison', 'Weapon Perks', 'Build Tool'])
    return selection

def weapon_type_filter(df, selected_tier):
    if len(selected_tier) > 0:
        df = sorted(df[df['Weapon Tier'].isin(selected_tier)]['Weapon Type'].unique())
    else:
        df = sorted(df['Weapon Type'].unique())
    return df

def weapon_archetype_filter(df, selected_tier, selected_type):
    if len(selected_tier) > 0 and selected_type != 'Select all':
        df = sorted(df[(df['Weapon Tier'].isin(selected_tier)) & (df['Weapon Type'] == selected_type)]['Weapon Archetype'].unique())
    elif len(selected_tier) > 0:
        df = sorted(
            df[df['Weapon Tier'].isin(selected_tier)]['Weapon Archetype'].unique())
    elif selected_type != 'Select all':
        df = sorted(
            df[df['Weapon Type'] == selected_type]['Weapon Archetype'].unique())
    else:
        df = sorted(df['Weapon Archetype'].unique())
    return df

def weapon_slot_filter(df, selected_tier, selected_type, selected_archetype):
    if len(selected_tier) > 0 and selected_type != 'Select all' and selected_archetype != 'Select all':
        df = sorted(df[(df['Weapon Tier'].isin(selected_tier)) & (df['Weapon Type'] == selected_type) & (df['Weapon Archetype'] == selected_archetype)]['Weapon Slot'].unique())
    elif len(selected_tier) > 0 and selected_type != 'Select all':
        df = sorted(df[(df['Weapon Tier'].isin(selected_tier)) & (df['Weapon Type'] == selected_type)]['Weapon Slot'].unique())
    elif len(selected_tier) > 0 and selected_archetype != 'Select all':
        df = sorted(df[(df['Weapon Tier'].isin(selected_tier)) & (df['Weapon Archetype'] == selected_archetype)]['Weapon Slot'].unique())
    elif selected_type != 'Select all' and selected_archetype != 'Select all':
        df = sorted(df[(df['Weapon Type'] == selected_type) & (df['Weapon Archetype'] == selected_archetype)]['Weapon Slot'].unique())
    elif selected_type != 'Select all':
        df = sorted(df[df['Weapon Type'] == selected_type]['Weapon Slot'].unique())
    elif selected_archetype != 'Select all':
        df = sorted(
            df[df['Weapon Archetype'] == selected_archetype]['Weapon Slot'].unique())
    elif len(selected_tier) > 0:
        df = sorted(
            df[df['Weapon Tier'].isin(selected_tier)]['Weapon Slot'].unique())
    else:
        df = sorted(df['Weapon Slot'].unique())
    return df

def weapon_element_filter(df, selected_tier, selected_type, selected_archetype, selected_slot):
    if len(selected_tier) > 0:
        df = df[df['Weapon Tier'].isin(selected_tier)]
    else:
        df = df.copy()
    if selected_type != 'Select all':
        df = df.loc[df['Weapon Type'] == selected_type]
    if selected_archetype != 'Select all':
        df = df.loc[df['Weapon Archetype'] == selected_archetype]
    if selected_slot != 'Select all':
        df = df.loc[df['Weapon Slot'] == selected_slot]
    df = sorted(df['Weapon Element'].unique())
    return df

# Define Filters
def apply_all_filters(df, selected_tier, selected_type, selected_archetype, selected_slot, selected_element, selected_sunset):
    # Apply filters here
    if len(selected_tier) > 0:
        df = df.loc[df['Weapon Tier'].isin(selected_tier)]
    if selected_type != 'Select all':
        df = df.loc[df['Weapon Type'] == selected_type]
    if selected_archetype != 'Select all':
        df = df.loc[df['Weapon Archetype'] == selected_archetype]
    if selected_slot != 'Select all':
        df = df.loc[df['Weapon Slot'] == selected_slot]
    if selected_element != 'Select all':
        df = df.loc[df['Weapon Element'] == selected_element]
    if selected_sunset == 'Yes':
        df = df.loc[df['Is Sunset'] == 'No']
    if selected_sunset == 'Yes':
        df = df.loc[df['Is Sunset'] == 'No']
    return df

def apply_reduced_filters(df, selected_tier, selected_sunset):
    # Apply filters here
    if len(selected_tier) > 0:
        df = df.loc[df['Weapon Tier'].isin(selected_tier)]
    if selected_sunset == 'Yes':
        df = df.loc[df['Is Sunset'] == 'No']
    return df

def sidebar():
    # Set Up Unique Non Dependant Lists
    unique_tier = ['Exotic', 'Legendary', 'Rare', 'Common', 'Basic']  # Free Choice
    selected_tier = st.sidebar.multiselect('Select Tiers', unique_tier, default=unique_tier[1], help='Select the Tiers to Look At. Can Select Multiple. Select None For All')

    unique_type = weapon_type_filter(weapon_manifest_file, selected_tier)
    unique_type.insert(0, 'Select all')
    selected_type = st.sidebar.selectbox('Select a Type', unique_type, help="Select the Weapon Type. Can Only Select One As The Stats Categories by Weapon Type. 'Select All' To See Full Weapon List")

    unique_archetype = weapon_archetype_filter(weapon_manifest_file, selected_tier, selected_type)
    unique_archetype.insert(0, 'Select all')
    selected_archetype = st.sidebar.selectbox('Select an Archetype', unique_archetype, help='Select Weapon Archetype')

    unique_slot = weapon_slot_filter(weapon_manifest_file, selected_tier, selected_type, selected_archetype)
    unique_slot.insert(0, 'Select all')
    selected_slot = st.sidebar.selectbox('Select a Weapon Slot', unique_slot, help="Select the Weapon Slot")

    unique_element = weapon_element_filter(weapon_manifest_file, selected_tier, selected_type, selected_archetype, selected_slot)
    unique_element.insert(0, 'Select all')
    selected_element = st.sidebar.selectbox('Select an Element', unique_element, help='Select the Elements to Look At. Can Select Multiple. Select None For All')

    exclude_sunset = ['Yes', 'No']
    selected_sunset = st.sidebar.selectbox('Exclude Sunset Weapons', exclude_sunset, index=0, help='Include or Exclude Sunset Weapons')

    return selected_tier, selected_type, selected_archetype, selected_slot, selected_element, selected_sunset

def main():
    # Setup DIM Uploads
    try:
        from csv_processing import load_dim_weapon_data, load_dim_armour_data
        from data_preperation import weapon_type_count, weapon_type_element_count, weapon_type_output_without_dim, weapon_type_output_with_dim, owned_counted_list, not_owned_list, owned_weapons_perk_list
        from data_preperation import load_weapon_type_data, create_grid_table, create_hyperlinks_v1, create_hyperlinks_v2
    except ImportError:
        pass

    # Setup Session States
    session_state = SessionState(dim_weapon_data=None, dim_armour_data=None, owned_weapons_perk_list=None)

    # Setup DIM Uploads
    with st.expander('DIM File Uploader', expanded=False):
        col1, col2 = st.columns([1, 1])
        uploaded_weapon_file = col1.file_uploader("DIM Weapon Uploader", type="csv")
        if uploaded_weapon_file is not None:
            session_state.dim_weapon_data = load_dim_weapon_data(uploaded_weapon_file, weapon_manifest_file)
            weapon_type_count = weapon_type_count(session_state.dim_weapon_data)
            weapon_type_element_count = weapon_type_element_count(session_state.dim_weapon_data)
            weapon_type_output_without_dim = weapon_type_output_without_dim(session_state.dim_weapon_data)
            weapon_type_output_with_dim = weapon_type_output_with_dim(weapon_manifest_file, session_state.dim_weapon_data)
            owned_counted_list = owned_counted_list(session_state.dim_weapon_data)
            not_owned_list = not_owned_list(weapon_manifest_file, session_state.dim_weapon_data)
            owned_weapons_perk_list = owned_weapons_perk_list(weapon_manifest_file, session_state.dim_weapon_data)
        uploaded_armour_file = col2.file_uploader("DIM armour Uploader", type="csv")
        if uploaded_armour_file is not None:
            session_state.dim_armour_data = load_dim_armour_data(uploaded_armour_file)

    # Determine the selected page based on navigation
    selection = navigation()

    # Add a Filter Title in the Sidebar
    st.sidebar.title('Filters')

    # Setup Sidebar Filters
    selected_tier, selected_type, selected_archetype, selected_slot, selected_element, selected_sunset = sidebar()

    # Define the page functions
    def home_page(session_state, weapon_manifest_file, selected_tier, selected_type, selected_archetype, selected_slot,
                  selected_element, selected_sunset):
        st.title('Home Page')

        # Set up columns for multiselect
        col1, col2, col3, col4, col5 = st.columns(5)

        # Create hyperlink for DIM
        selected_url_1 = "https://www.bungie.net/7/en/Destiny"
        link_text_1 = "Register with Bungie (if you haven't already)"
        # Use st.write to display the formatted hyperlink text
        col1.write(f'<a href="{selected_url_1}" target="_blank">{link_text_1}</a>', unsafe_allow_html=True)

        # Create hyperlink for DIM
        selected_url_2 = "https://app.destinyitemmanager.com/settings"
        link_text_2 = 'Where to download DIM Data'
        # Use st.write to display the formatted hyperlink text
        col2.write(f'<a href="{selected_url_2}" target="_blank">{link_text_2}</a>', unsafe_allow_html=True)

        # Create hyperlink for DIM Beta
        selected_url_3 = "https://beta.destinyitemmanager.com/settings"
        link_text_3 = 'Where to download DIM Data (BETA)'
        # Use st.write to display the formatted hyperlink text
        col3.write(f'<a href="{selected_url_3}" target="_blank">{link_text_3}</a>', unsafe_allow_html=True)

        # Create hyperlink for DIM Beta
        selected_url_4 = "https://www.light.gg/"
        link_text_4 = 'Light.gg'
        # Use st.write to display the formatted hyperlink text
        col4.write(f'<a href="{selected_url_4}" target="_blank">{link_text_4}</a>', unsafe_allow_html=True)

        # Create hyperlink for DIM Beta
        selected_url_5 = "https://d2foundry.gg/"
        link_text_5 = 'D2Foundry'
        # Use st.write to display the formatted hyperlink text
        col5.write(f'<a href="{selected_url_5}" target="_blank">{link_text_5}</a>', unsafe_allow_html=True)

    def vault_summary(session_state, manifest_weapon_data, selected_tier, selected_type, selected_archetype, selected_slot, selected_element, selected_sunset):
        st.title('Vault Summary')

    def weapon_analysis(session_state, manifest_weapon_data, selected_tier, selected_type, selected_archetype, selected_slot, selected_element, selected_sunset):
        st.title('Weapon Analysis')

    def weapon_comparison(session_state, manifest_weapon_data, selected_tier, selected_type, selected_archetype, selected_slot, selected_element, selected_sunset):
        st.title('Weapon Comparison')

    def weapon_perks(session_state, manifest_weapon_data, selected_tier, selected_type, selected_archetype, selected_slot, selected_element, selected_sunset):
        st.title('Weapon Perks')

    def build_tool(session_state, manifest_weapon_data, selected_tier, selected_type, selected_archetype, selected_slot, selected_element, selected_sunset):
        st.title('Build Tool')

# Call the selected page function
    page = {
        'Home': lambda: home_page(session_state, weapon_manifest_file, selected_tier, selected_type, selected_archetype,
                                  selected_slot, selected_element, selected_sunset),
        'Vault Summary': lambda: vault_summary(session_state, weapon_manifest_file, selected_tier, selected_type,
                                               selected_archetype, selected_slot, selected_element, selected_sunset),
        'Weapon Analysis': lambda: weapon_analysis(session_state, weapon_manifest_file, selected_tier, selected_type,
                                                   selected_archetype, selected_slot, selected_element, selected_sunset),
        'Weapon Comparison': lambda: weapon_comparison(session_state, weapon_manifest_file, selected_tier,
                                                       selected_type, selected_archetype, selected_slot,
                                                       selected_element, selected_sunset),
        'Weapon Perks': lambda: weapon_perks(session_state, weapon_manifest_file, selected_tier, selected_type,
                                             selected_archetype, selected_slot, selected_element, selected_sunset),
        'Build Tool': lambda: build_tool(session_state, weapon_manifest_file, selected_tier, selected_type,
                                         selected_archetype, selected_slot, selected_element, selected_sunset),
    }[selection]

    page()

if __name__ == '__main__':
    main()