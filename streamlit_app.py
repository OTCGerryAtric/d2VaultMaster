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
    return df

def apply_reduced_filters(df, selected_tier, selected_sunset):
    # Apply filters here
    if len(selected_tier) > 0:
        df = df.loc[df['Weapon Tier'].isin(selected_tier)]
    if selected_sunset == 'Yes':
        try:
            df = df.loc[df['Is Sunset'] == 'No']
        except Exception:
            pass
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

    # Setup DIM Uploads & Process Data
    with st.expander('DIM File Uploader', expanded=False):
        col1, col2 = st.columns([1, 1])
        uploaded_weapon_file = col1.file_uploader("DIM Weapon Uploader", type="csv")
        if uploaded_weapon_file is not None:
            session_state.dim_weapon_data = load_dim_weapon_data(uploaded_weapon_file, weapon_manifest_file)
            weapon_type_count = weapon_type_count(session_state.dim_weapon_data)
            weapon_type_element_count = weapon_type_element_count(session_state.dim_weapon_data)
        uploaded_armour_file = col2.file_uploader("DIM armour Uploader", type="csv")
        if uploaded_armour_file is not None:
            session_state.dim_armour_data = load_dim_armour_data(uploaded_armour_file)

    # Determine the selected page based on navigation
    selection = navigation()

    # Add a Filter Title in the Sidebar
    st.sidebar.title('Filters')

    # Setup Sidebar Filters
    selected_tier, selected_type, selected_archetype, selected_slot, selected_element, selected_sunset = sidebar()

    # Apply Filters
    weapon_manifest_file_filtered_all = apply_all_filters(weapon_manifest_file, selected_tier, selected_type, selected_archetype, selected_slot, selected_element, selected_sunset)
    weapon_manifest_file_filtered_reduced = apply_reduced_filters(weapon_manifest_file, selected_tier, selected_sunset)
    if uploaded_weapon_file is not None:
        dim_weapon_data_filtered_all = apply_all_filters(session_state.dim_weapon_data, selected_tier, selected_type, selected_archetype, selected_slot, selected_element, selected_sunset)
        dim_weapon_data_filtered_reduced = apply_reduced_filters(session_state.dim_weapon_data, selected_tier, selected_sunset)
    else:
        pass

    # Define the page functions
    def home_page(session_state, weapon_manifest_file, selected_tier, selected_type, selected_archetype, selected_slot, selected_element, selected_sunset):
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

        with st.expander('How To Use', expanded=False):
            from website_text import text_1
            text_1()

        with st.expander('About me', expanded=False):
            from website_text import text_2
            text_2()

    def vault_summary(session_state, manifest_weapon_data, selected_tier, selected_type, selected_archetype, selected_slot, selected_element, selected_sunset):
        st.title('Vault Summary')

        # Setup Overall Metrics
        col1, col2, col3, col4 = st.columns([4, 4, 4, 6])

        # Populate Col 1 Metric
        if uploaded_weapon_file is not None:
            col1.metric(label='Total Weapons Owned', value=len(session_state.dim_weapon_data), help='Count Of All Weapons Owned')
        else:
            col1.metric(label='Total Weapons Owned', value='Load DIM Data', help='Count Of All Weapons Owned')

        # Populate Col 2 Metric
        if uploaded_armour_file is not None:
            col2.metric(label='Total armour Pieces Owned', value=len(session_state.dim_armour_data), help='Count Of All armour Owned')
        else:
            col2.metric(label='Total armour Pieces Owned', value='Load DIM Data', help='Count Of All armour Owned')

        # Populate Col 3 Metric
        if uploaded_weapon_file and uploaded_armour_file is not None:
            col3.metric(label='Total Items Owned', value=len(session_state.dim_weapon_data) + len(session_state.dim_armour_data), help='Total Item Count')
        else:
            col3.metric(label='Total Items Owned', value='Load DIM Data', help='Total Item Count')

        with st.expander('Weapon Details', expanded=True):

            # Set up columns for multiselect
            col1, col2, col3 = st.columns([12, 4, 4])

            # Setup Weapon Details
            if uploaded_weapon_file is not None:
                vault_summary_table_1 = weapon_type_output_with_dim(weapon_manifest_file_filtered_reduced, dim_weapon_data_filtered_reduced)
                col1.write('Weapons Available (with owned count)')
                col1.dataframe(vault_summary_table_1, use_container_width=True)
            else:
                vault_summary_table_1 = weapon_type_output_without_dim(weapon_manifest_file_filtered_reduced)
                col1.write('Available Weapons (upload DIM file to show owned)')
                col1.dataframe(vault_summary_table_1, use_container_width=True)

            # Setup Weapon Owned
            if uploaded_weapon_file is not None:
                vault_summary_table_2 = owned_counted_list(dim_weapon_data_filtered_all)
                vault_summary_table_2 = vault_summary_table_2.reset_index(drop=True)  # Reset the index
                col2.write('Weapons Owned (with count)')
                col2.dataframe(vault_summary_table_2, use_container_width=True)
            else:
                col2.write('Upload DIM Weapon Data')

            # Setup Missing Weapon Details
            if uploaded_weapon_file is not None:
                vault_summary_table_3 = not_owned_list(weapon_manifest_file_filtered_all, dim_weapon_data_filtered_all)
                vault_summary_table_3 = pd.DataFrame(vault_summary_table_3, columns=['Weapon Name'])
                col3.write('Weapons Not Owned')
                col3.dataframe(vault_summary_table_3, use_container_width=True)
            else:
                vault_summary_table_3 = pd.DataFrame(weapon_manifest_file_filtered_all, columns=['Weapon Name'])
                col3.write('All Weapons (Upload DIM Data)')
                col3.dataframe(vault_summary_table_3, use_container_width=True)

        with st.expander('Crafted Weapons', expanded=False):
            # Import Function
            from data_preperation import crafted_weapon_list

            # Create Crafted Weapon List
            crafted_weapon_list = crafted_weapon_list(session_state.dim_weapon_data)
            crafted_weapon_list = apply_reduced_filters(crafted_weapon_list, selected_tier, selected_sunset)
            crafted_weapon_list = crafted_weapon_list.reset_index(drop=True)
            crafted_weapon_list.index += 1
            crafted_weapon_list.drop(columns=['index'], inplace=True, errors='ignore')
            st.write(crafted_weapon_list)

    def weapon_analysis(session_state, manifest_weapon_data, selected_tier, selected_type, selected_archetype, selected_slot, selected_element, selected_sunset):
        st.title('Weapon Analysis')

        # Set up Weapon Manifest counts
        unique_filtered_manifest_weapons_count = weapon_manifest_file_filtered_all[['Weapon Name', 'Weapon Power Cap']]
        unique_filtered_manifest_weapons_count = unique_filtered_manifest_weapons_count.drop_duplicates()
        unique_filtered_manifest_weapons_count = len(unique_filtered_manifest_weapons_count)

        # Set up DIM counts
        if uploaded_weapon_file is not None:
            dim_total_weapons_owned = len(dim_weapon_data_filtered_all)
            dim_total_unique_weapons_owned = dim_weapon_data_filtered_all[['Weapon Name', 'Weapon Power Cap']]
            dim_total_unique_weapons_owned = len(dim_total_unique_weapons_owned.drop_duplicates())
            dim_weapon_unique_count = dim_weapon_data_filtered_all[['Weapon Name', 'Weapon Power Cap']]
            dim_weapon_unique_count = len(dim_weapon_unique_count.drop_duplicates())
        else:
            pass

        with st.expander('Weapon Summary', expanded=True):
            # Set up columns for multiselect
            col1, col2, col3, col4, col5 = st.columns(5)

            # Set up counts
            try:
                col1.metric(label='Total Weapons Owned', value=format(dim_total_weapons_owned, ','), help='Count Of All Weapons Owned')
            except Exception:
                col1.metric(label='Total Weapons Owned', value='Upload DIM Data', help='Count Of All Weapons Owned')

            try:
                col2.metric(label='Unique Weapons Owned', value=format(dim_total_unique_weapons_owned, ','), help='Count of Unique Weapons. Excludes Duplicates Where Weapons Share Same Name And Power Cap, e.g. Dark Decider')
            except Exception:
                col2.metric(label='Unique Weapons Owned', value='Upload DIM Data', help='Count of Unique Weapons. Excludes Duplicates Where Weapons Share Same Name And Power Cap, e.g. Dark Decider')

            try:
                col3.metric(label='Unique Weapons Available (Filtered)', value=format(unique_filtered_manifest_weapons_count, ','), help='Count Of Weapons Available (Filtered)')
            except Exception:
                pass

            try:
                col4.metric(label='Unique Weapons Owned (Filtered)', value=format(dim_weapon_unique_count, ','), help='Count of Unique Weapons. Excludes Duplicates Where Weapons Share Same Name And Power Cap')
            except Exception:
                col4.metric(label='Unique Weapons Owned (Filtered)', value='Upload DIM Data', help='Count of Unique Weapons. Excludes Duplicates Where Weapons Share Same Name And Power Cap')

            try:
                col5.metric(label='% Filtered Weapons Owned', value=f"{round((dim_weapon_unique_count * 100 / unique_filtered_manifest_weapons_count), 1)}%", help='Percentage of Weapons Owned')
            except Exception:
                col5.metric(label='% Filtered Weapons Owned', value='Upload DIM Data', help='Percentage of Weapons Owned')

        with st.expander('Weapon Database', expanded=True):
            # Set up columns for multiselect
            col1, col2, col3, col4, col5 = st.columns(5)

            # Create table, based on selected weapon type
            if selected_type != 'Select all':
                weapon_analysis_table_1 = load_weapon_type_data(weapon_manifest_file_filtered_all, selected_type)
            else:
                weapon_analysis_table_1 = weapon_manifest_file_filtered_all[['Weapon Name With Season', 'Weapon Name', 'Weapon Season', 'Weapon Hash', 'Weapon Tier', 'Weapon Type', 'Weapon Archetype', 'Weapon Slot', 'Weapon Element', 'Weapon Current Version', 'Weapon Power Cap', 'Is Sunset']]

            if uploaded_weapon_file is not None:
                weapon_count = dim_weapon_data_filtered_all.groupby('Weapon Hash').size().reset_index(name='count')
                weapon_analysis_table_1 = weapon_analysis_table_1.merge(weapon_count, on='Weapon Hash', how='left')
                weapon_analysis_table_1.insert(1, 'Count', weapon_analysis_table_1.pop('count'))

            try:
                weapon_analysis_table_1 = weapon_analysis_table_1.sort_values(by=['Count', 'Weapon Name With Season'], ascending=[False, True])
            except Exception:
                weapon_analysis_table_1 = weapon_analysis_table_1.sort_values(by=['Weapon Name With Season'], ascending=[True])


            # Create table
            grid_table = create_grid_table(weapon_analysis_table_1, selected_tier, selected_type, selected_archetype, selected_slot, selected_element, selected_sunset)

            # Create hyperlinks
            create_hyperlinks_v1(weapon_analysis_table_1, grid_table, col1, col2, col3, col4, col5)

    def weapon_comparison(session_state, manifest_weapon_data, selected_tier, selected_type, selected_archetype, selected_slot, selected_element, selected_sunset):
        st.title('Weapon Comparison')

        # Set up columns for multiselect
        col1, col2, col3, col4, col5 = st.columns([2, 2, 4, 2, 2])

        # Select Season
        season_list = sorted(weapon_manifest_file_filtered_all['Weapon Season'].unique(), reverse=True)
        season_list.insert(0, 'Select all')
        selected_season = col1.selectbox('Select Season To Filter Weapons For Comparison', season_list)

        # Set up Weapon Comparator List
        if selected_season == 'Select all':
            weapon_name_list = sorted(weapon_manifest_file_filtered_all['Weapon Name With Season'].unique())
            weapon_selected_name = col2.selectbox('Select Weapon For Comparison', weapon_name_list)
        else:
            weapon_comparison_name_list = weapon_manifest_file_filtered_all.loc[weapon_manifest_file_filtered_all['Weapon Season'] == selected_season]
            weapon_name_list = sorted(weapon_comparison_name_list['Weapon Name With Season'].unique())
            weapon_selected_name = col2.selectbox('Select Weapon For Comparison', weapon_name_list)

        # Create List for Comparison
        weapon_list = sorted(weapon_manifest_file_filtered_all['Weapon Name With Season'].unique())
        if weapon_selected_name in weapon_name_list:
            weapon_list.remove(weapon_selected_name)
        weapon_comparison_list = col3.multiselect('Select Weapon To Compare', weapon_list)

        # Set Up Comparison Type
        comparison_type = col4.selectbox('Choose The Type Of Comparison', ['Absolute', 'Relative'], index=1)

        # Lookup The Weapon Type and Achetype of the Selection Comparison Weapon
        comparison_weapon_type = weapon_manifest_file_filtered_all.loc[weapon_manifest_file_filtered_all['Weapon Name With Season'] == weapon_selected_name, 'Weapon Type'].iloc[0]
        comparison_weapon_archetype = weapon_manifest_file_filtered_all.loc[weapon_manifest_file_filtered_all['Weapon Name With Season'] == weapon_selected_name, 'Weapon Archetype'].iloc[0]

        # Apply Weapon Type and Weapon Archetype Filter if a Weapon is Selected for Comparison
        selected_weapon_filtered = weapon_manifest_file_filtered_all.loc[weapon_manifest_file_filtered_all['Weapon Type'] == comparison_weapon_type]
        selected_weapon_filtered = selected_weapon_filtered.loc[selected_weapon_filtered['Weapon Archetype'] == comparison_weapon_archetype]

        # Create Selected Weapon Data for Table (So that it appears first)
        selected_weapon = weapon_manifest_file_filtered_all.loc[weapon_manifest_file_filtered_all['Weapon Name With Season'] == weapon_selected_name]

        # Add Other Weapons With That Are The Same Type And Archetype
        comparison_weapons = selected_weapon_filtered.loc[selected_weapon_filtered['Weapon Name With Season'] != weapon_selected_name]

        # Created Combined Table
        weapon_comparison_table_1 = pd.concat([selected_weapon, comparison_weapons], ignore_index=True)

        # Create table, based on selected weapon type
        if comparison_weapon_type != 'Select all':
            weapon_comparison_table_1 = load_weapon_type_data(weapon_comparison_table_1, comparison_weapon_type)
        else:
            weapon_comparison_table_1 = weapon_comparison_table_1[['Weapon Name With Season', 'Weapon Name', 'Weapon Season', 'Weapon Hash', 'Weapon Tier', 'Weapon Type', 'Weapon Archetype', 'Weapon Slot', 'Weapon Element', 'Weapon Current Version', 'Weapon Power Cap', 'Is Sunset']]

        if comparison_type == 'Relative':
            if comparison_weapon_type == 'Grenade Launcher' or selected_type == 'Rocket Launcher':
                first_index = weapon_comparison_table_1.columns.get_loc("Blast Radius")
            else:
                first_index = weapon_comparison_table_1.columns.get_loc("Impact")
            for col in weapon_comparison_table_1.iloc[:, first_index:].columns:
                # subtract the first row value from the subsequent rows and store in new column
                weapon_comparison_table_1.loc[1:, col] = weapon_comparison_table_1.loc[1:, col] - weapon_comparison_table_1.loc[0, col]
        else:
            pass

        with st.expander('Weapon Comparison', expanded=True):
            if uploaded_weapon_file is not None:
                weapon_count = session_state.dim_weapon_data.groupby('Weapon Hash').size().reset_index(name='count')
                weapon_comparison_table_1 = weapon_comparison_table_1.merge(weapon_count, on='Weapon Hash', how='left')
                weapon_comparison_table_1.insert(1, 'Count', weapon_comparison_table_1.pop('count'))

            # Create table
            grid_table = create_grid_table(weapon_comparison_table_1, selected_tier, selected_type, selected_archetype, selected_slot, selected_element, selected_sunset)

        # Create hyperlinks
        create_hyperlinks_v2(weapon_comparison_table_1, grid_table, col5)

    def weapon_perks(session_state, manifest_weapon_data, selected_tier, selected_type, selected_archetype, selected_slot, selected_element, selected_sunset):
        st.title('Weapon Perks')

        # Copy Filtered Manifest Weapon Data
        weapon_perk_filtered_df = apply_all_filters(manifest_weapon_data, selected_tier, selected_type, selected_archetype, selected_slot, selected_element, selected_sunset)

        # Set up columns for multiselect
        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])

        # Search for Slot 3 Selection
        slot3_cols = weapon_perk_filtered_df.filter(regex='^Slot 3').columns
        slot3_perks = sorted(weapon_perk_filtered_df.filter(regex='^Slot 3').stack().unique())
        slot_3 = col1.multiselect('Select Perk(s) in Slot 3', slot3_perks)
        if len(slot_3) > 0:
            slot_3_list = weapon_perk_filtered_df[slot3_cols].apply(lambda x: any(item in x.values for item in slot_3), axis=1)
            weapon_perk_filtered_df = weapon_perk_filtered_df.loc[slot_3_list]
        slot_3_count = col1.metric('Filtered Data Count', len(weapon_perk_filtered_df))

        # Search for Slot 4 Selection
        slot4_cols = weapon_perk_filtered_df.filter(regex='^Slot 4').columns
        slot4_perks = sorted(weapon_perk_filtered_df.filter(regex='^Slot 4').stack().unique())
        slot_4 = col2.multiselect('Select Perk(s) in Slot 4', slot4_perks)
        if len(slot_4) > 0:
            slot_4_list = weapon_perk_filtered_df[slot4_cols].apply(lambda x: any(item in x.values for item in slot_4), axis=1)
            weapon_perk_filtered_df = weapon_perk_filtered_df.loc[slot_4_list]
        slot_4_count = col2.metric('Filtered Data Count', len(weapon_perk_filtered_df))

        # Search for Slot 2 Selection
        slot2_cols = weapon_perk_filtered_df.filter(regex='^Slot 2').columns
        slot2_perks = sorted(weapon_perk_filtered_df.filter(regex='^Slot 2').stack().unique())
        slot_2 = col3.multiselect('Select Perk(s) in Slot 2', slot2_perks)
        if len(slot_2) > 0:
            slot_2_list = weapon_perk_filtered_df[slot2_cols].apply(lambda x: any(item in x.values for item in slot_2), axis=1)
            weapon_perk_filtered_df = weapon_perk_filtered_df.loc[slot_2_list]
        slot_2_count = col3.metric('Filtered Data Count', len(weapon_perk_filtered_df))

        # Search for Slot 1 Selection
        slot1_cols = weapon_perk_filtered_df.filter(regex='^Slot 1').columns
        slot1_perks = sorted(weapon_perk_filtered_df.filter(regex='^Slot 1').stack().unique())
        slot_1 = col4.multiselect('Select Perk(s) in Slot 1', slot1_perks)
        if len(slot_1) > 0:
            slot_1_list = weapon_perk_filtered_df[slot1_cols].apply(lambda x: any(item in x.values for item in slot_1), axis=1)
            weapon_perk_filtered_df = weapon_perk_filtered_df.loc[slot_1_list]
        slot_1_count = col4.metric('Filtered Data Count', len(weapon_perk_filtered_df))

        # Create table, based on selected weapon type
        if selected_type != 'Select all':
            weapon_perk_filtered_df = load_weapon_type_data(weapon_perk_filtered_df, selected_type)
        else:
            weapon_perk_filtered_df = weapon_perk_filtered_df[['Weapon Name With Season', 'Weapon Name', 'Weapon Season', 'Weapon Hash', 'Weapon Tier', 'Weapon Type', 'Weapon Archetype', 'Weapon Slot', 'Weapon Element', 'Weapon Current Version', 'Weapon Power Cap', 'Is Sunset']]

        # Import Functions
        from data_preperation import owned_weapons_perk_list

        if uploaded_weapon_file is not None:
            # Create List of Owned Weapon's Perks
            owned_weapons_perk_list = owned_weapons_perk_list(weapon_manifest_file_filtered_all, dim_weapon_data_filtered_all)

            # Set Up Owned Perk Count
            dfs_to_merge = []
            slots = ['Slot 1', 'Slot 2', 'Slot 3', 'Slot 4']
            slot_perks = [slot_1, slot_2, slot_3, slot_4]

            if (len(slot_1) + len(slot_2) + len(slot_3) + len(slot_4)) > 0:
                for s, perks in zip(slots, slot_perks):
                    if len(perks) > 0:
                        temp_df = owned_weapons_perk_list.loc[
                            (owned_weapons_perk_list['Slot'] == s) & (owned_weapons_perk_list['Perk'].isin(perks))]
                        dfs_to_merge.append(temp_df[['Weapon Name', 'Weapon ID']])  # Only retain the 'Weapon ID' column

                # Start with the first dataframe and successively merge with others
                owned_weapons_perk_list = dfs_to_merge[0]
                for df in dfs_to_merge[1:]:
                    owned_weapons_perk_list = pd.merge(owned_weapons_perk_list, df, on=['Weapon Name', 'Weapon ID'], how='inner')

            if (len(slot_1) + len(slot_2) + len(slot_3) + len(slot_4)) > 0:
                weapon_count = owned_weapons_perk_list.groupby('Weapon Name').size().reset_index(name='count')
                weapon_perk_filtered_df = weapon_perk_filtered_df.merge(weapon_count, on='Weapon Name', how='left')
                weapon_perk_filtered_df.insert(1, 'Count', weapon_perk_filtered_df.pop('count'))
                weapon_perk_filtered_df = weapon_perk_filtered_df.sort_values(by=['Count', 'Weapon Name With Season'], ascending=[False, True])
            else:
                weapon_count = session_state.dim_weapon_data.groupby('Weapon Hash').size().reset_index(name='count')
                weapon_perk_filtered_df = weapon_perk_filtered_df.merge(weapon_count, on='Weapon Hash', how='left')
                weapon_perk_filtered_df.insert(1, 'Count', weapon_perk_filtered_df.pop('count'))
                weapon_perk_filtered_df = weapon_perk_filtered_df.sort_values(by=['Count', 'Weapon Name With Season'], ascending=[False, True])

        with st.expander('Available Weapons', expanded=True):
            # Create table
            grid_table = create_grid_table(weapon_perk_filtered_df, selected_tier, selected_type, selected_archetype, selected_slot, selected_element, selected_sunset)

            # Create hyperlinks
            create_hyperlinks_v2(weapon_perk_filtered_df, grid_table, col5)

    def build_tool(session_state, manifest_weapon_data, selected_tier, selected_type, selected_archetype, selected_slot, selected_element, selected_sunset):
        st.title('Build Tool')
        st.write('Coming soon!')

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