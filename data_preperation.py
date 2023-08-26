import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder

@st.cache_data
def weapon_type_count(file):
    df = file.groupby('Weapon Type').agg({'Weapon Name': ['count', 'nunique']})
    df.columns = ['Total Count', 'Unique Count']
    df = df.reset_index().sort_values(by='Total Count', ascending=False)
    df.index += 1
    return df

@st.cache_data
def weapon_type_element_count(file):
    df = file.groupby(['Weapon Type', 'Weapon Element']).agg({'Weapon Name': ['count', 'nunique']})
    df.columns = ['Total Count', 'Unique Count']
    df = df.reset_index().sort_values(by=['Weapon Type', 'Weapon Element'])
    df.index += 1
    return df

@st.cache_data
def weapon_type_output_without_dim(file):
    df_1 = weapon_type_count(file)
    df_2 = weapon_type_element_count(file)

    weapon_elements = ['Kinetic', 'Stasis', 'Strand', 'Arc', 'Solar', 'Void']
    for element in weapon_elements:
        element_count_1 = df_2[df_2['Weapon Element'] == element].set_index('Weapon Type')['Unique Count']
        df_1[element] = df_1['Weapon Type'].apply(lambda x: '{}'.format(element_count_1.get(x, 0)))
    return df_1

@st.cache_data
def weapon_type_output_with_dim(manifest_weapon_data, file):
    df_1 = weapon_type_count(manifest_weapon_data)
    df_2 = weapon_type_count(file)
    df = pd.merge(df_2, df_1, on='Weapon Type', how='left')
    df = df.drop(columns=('Total Count_y'))
    df = df.rename(columns={'Total Count_x': 'Total Owned', 'Unique Count_x': 'Unique Owned', 'Unique Count_y': 'Unique Available'})
    df_3 = weapon_type_element_count(manifest_weapon_data)
    df_4 = weapon_type_element_count(file)

    weapon_elements = ['Kinetic', 'Stasis', 'Strand', 'Arc', 'Solar', 'Void']
    for element in weapon_elements:
        element_count_1 = df_4[df_4['Weapon Element'] == element].set_index('Weapon Type')['Unique Count']
        element_count_2 = df_3[df_3['Weapon Element'] == element].set_index('Weapon Type')['Unique Count']
        df[element] = df['Weapon Type'].apply(lambda x: '{} (of {})'.format(element_count_1.get(x, 0), element_count_2.get(x, 0)))
    return df

@st.cache_data
def owned_counted_list(file):
    df = file.groupby('Weapon Name').agg({'Weapon Name': ['count']})
    df.columns = ['Count']
    df = df.reset_index().sort_values(by='Count', ascending=False)
    df = df.reset_index(drop=True)
    df.index += 1
    return df

@st.cache_data
def not_owned_list(manifest_weapon_data, file):
    df_1 = file['Weapon Name'].unique()
    df = manifest_weapon_data[~manifest_weapon_data['Weapon Name'].isin(df_1)]['Weapon Name'].unique()
    df = pd.DataFrame({'Weapon Name': df})
    df = df.sort_values(by='Weapon Name')
    df = df.reset_index(drop=True)
    df.index += 1
    return df

@st.cache_data
def owned_weapons_perk_list(manifest_weapon_data, file):
    # Merge Data
    df = pd.merge(file, manifest_weapon_data, on='Weapon Hash', how='left')

    # Clean Up Columns
    columns_to_drop = df.filter(like='_y')
    df = df.drop(columns=columns_to_drop)
    df.columns = [col.rstrip('_x') if col.endswith('_x') else col for col in df.columns]

    # Define the list of columns to keep
    columns_to_keep = [
        'Weapon Name', 'Weapon Hash', 'Weapon ID', 'Perks 1', 'Perks 2', 'Perks 3', 'Perks 4', 'Perks 5', 'Perks 6', 'Perks 7', 'Perks 8',
        'Perks 9', 'Perks 10', 'Perks 11', 'Perks 12', 'Perks 13', 'Perks 14', 'Perks 15', 'Perks 16', 'Perks 17',
        'Slot 1 Perk 0', 'Slot 1 Perk 1', 'Slot 1 Perk 2', 'Slot 1 Perk 3', 'Slot 1 Perk 4', 'Slot 1 Perk 5','Slot 1 Perk 6',
        'Slot 1 Perk 7', 'Slot 1 Perk 8', 'Slot 1 Perk 9', 'Slot 1 Perk 10', 'Slot 1 Perk 11', 'Slot 1 Perk 12',
        'Slot 2 Perk 0', 'Slot 2 Perk 1', 'Slot 2 Perk 2', 'Slot 2 Perk 3', 'Slot 2 Perk 4', 'Slot 2 Perk 5','Slot 2 Perk 6',
        'Slot 2 Perk 7', 'Slot 2 Perk 8', 'Slot 2 Perk 9', 'Slot 2 Perk 10', 'Slot 2 Perk 11', 'Slot 2 Perk 12',
        'Slot 3 Perk 0', 'Slot 3 Perk 1', 'Slot 3 Perk 2', 'Slot 3 Perk 3', 'Slot 3 Perk 4', 'Slot 3 Perk 5','Slot 3 Perk 6',
        'Slot 3 Perk 7', 'Slot 3 Perk 8', 'Slot 3 Perk 9', 'Slot 3 Perk 10', 'Slot 3 Perk 11', 'Slot 3 Perk 12',
        'Slot 4 Perk 0', 'Slot 4 Perk 1', 'Slot 4 Perk 2', 'Slot 4 Perk 3', 'Slot 4 Perk 4', 'Slot 4 Perk 5','Slot 4 Perk 6',
        'Slot 4 Perk 7', 'Slot 4 Perk 8', 'Slot 4 Perk 9', 'Slot 4 Perk 10', 'Slot 4 Perk 11', 'Slot 4 Perk 12']

    # Keep only the selected columns
    df = df[columns_to_keep]

    # Select Perk Columns
    perk_columns = [col for col in file.columns if col.startswith('Perk')]

    # Iterate through each "Perk" column
    for perk_col in perk_columns:
        # Create a new column to store the results
        df[f'{perk_col}_Slot_With_Perk'] = ''

        # Iterate through each row
        for index, row in df.iterrows():
            perk_value = row[perk_col]

            # Skip the iteration if perk_value is blank
            if perk_value == '':
                continue

            # Check for Perk entry in Slot columns
            for slot_col in df.columns:
                if slot_col.startswith('Slot') and pd.notna(row[slot_col]) and pd.notna(perk_value) and str(perk_value) in str(row[slot_col]):
                    df.at[index, f'{perk_col}_Slot_With_Perk'] = slot_col

    # List of columns to explode
    columns_to_explode = [col for col in df.columns if col.endswith('Slot_With_Perk')]

    # Create a new DataFrame to store exploded rows
    df_2 = pd.DataFrame()

    # Iterate through the rows
    for idx, row in df.iterrows():
        entry_idx = 0  # Initialize the entry index

        # Iterate through the columns to explode
        for col in columns_to_explode:
            # Get the non-blank entries in the column
            entries = [entry for entry in row[col].split(', ') if entry != '']

            # Create a new row for each entry
            for entry in entries:
                new_row = row.copy()  # Copy the original row
                new_row[col] = entry  # Set the exploded entry
                new_row['Entry_Index'] = entry_idx + 1  # Add the entry index
                df_2 = pd.concat([df_2, new_row.to_frame().T], ignore_index=True)
                entry_idx += 1  # Increment the entry index

    df_2['Slot'] = ''
    df_2['Perk'] = ''

    # Find Column Numbers
    column_number_1 = df_2.columns.get_loc('Perks 1') - 1
    column_number_2 = df_2.columns.get_loc('Perks 1_Slot_With_Perk') - 1

    # Iterate through the rows
    for idx, row in df_2.iterrows():
        column_idx_1 = column_number_1 + row['Entry_Index']
        column_idx_2 = column_number_2 + row['Entry_Index']
        df_2.loc[idx, 'Perk'] = row[column_idx_1]
        df_2.loc[idx, 'Slot'] = row[column_idx_2]

    df_2['Slot'] = df_2['Slot'].str.split(n=2).str[:2].str.join(' ')

    # Reduce DataFrame
    columns_to_keep = ['Weapon Name', 'Weapon Hash', 'Weapon ID', 'Slot', 'Perk']
    df_2 = df_2[columns_to_keep]
    return df_2

def load_weapon_type_data(file, selected_type):
    # Define first_cols
    first_cols = ['Weapon Name With Season', 'Weapon Name', 'Weapon Season', 'Weapon Hash', 'Weapon Tier', 'Weapon Type', 'Weapon Archetype', 'Weapon Slot', 'Weapon Element',
                  'Weapon Current Version', 'Weapon Power Cap', 'Is Sunset']

    type_1_list = pd.DataFrame(file, columns=['Impact', 'Range', 'Stability', 'Handling', 'Reload Speed', 'Aim Assistance', 'Zoom', 'Airborne Effectiveness', 'Recoil Direction', 'Rounds Per Minute', 'Magazine'])
    type_2_list = pd.DataFrame(file, columns=['Impact', 'Accuracy', 'Stability', 'Handling', 'Reload Speed', 'Aim Assistance', 'Zoom', 'Airborne Effectiveness', 'Recoil Direction', 'Draw Time'])
    type_3_list = pd.DataFrame(file, columns=['Impact', 'Range', 'Stability', 'Handling', 'Reload Speed', 'Aim Assistance', 'Zoom', 'Airborne Effectiveness', 'Recoil Direction', 'Charge Time', 'Magazine'])
    type_4_list = pd.DataFrame(file, columns=['Blast Radius', 'Velocity', 'Stability', 'Handling', 'Reload Speed', 'Aim Assistance', 'Zoom', 'Airborne Effectiveness', 'Recoil Direction', 'Rounds Per Minute',
                                              'Magazine'])
    type_5_list = pd.DataFrame(file, columns=['Impact', 'Range', 'Shield Duration', 'Handling', 'Reload Speed', 'Aim Assistance', 'Airborne Effectiveness', 'Rounds Per Minute', 'Charge Time', 'Magazine'])
    type_6_list = pd.DataFrame(file, columns=['Impact', 'Swing Speed', 'Guard Efficiency', 'Guard Resistance', 'Charge Rate', 'Ammo Capacity'])

    # Create Additional Filters for Weapon Type
    type_map = {
        'Auto Rifle': pd.concat([pd.DataFrame(file, columns=first_cols), type_1_list], axis=1),
        'Hand Cannon': pd.concat([pd.DataFrame(file, columns=first_cols), type_1_list], axis=1),
        'Machine Gun': pd.concat([pd.DataFrame(file, columns=first_cols), type_1_list], axis=1),
        'Pulse Rifle': pd.concat([pd.DataFrame(file, columns=first_cols), type_1_list], axis=1),
        'Scout Rifle': pd.concat([pd.DataFrame(file, columns=first_cols), type_1_list], axis=1),
        'Shotgun': pd.concat([pd.DataFrame(file, columns=first_cols), type_1_list], axis=1),
        'Sidearm': pd.concat([pd.DataFrame(file, columns=first_cols), type_1_list], axis=1),
        'Sniper Rifle': pd.concat([pd.DataFrame(file, columns=first_cols), type_1_list], axis=1),
        'Submachine Gun': pd.concat([pd.DataFrame(file, columns=first_cols), type_1_list], axis=1),
        'Trace Rifle': pd.concat([pd.DataFrame(file, columns=first_cols), type_1_list], axis=1),
        'Combat Bow': pd.concat([pd.DataFrame(file, columns=first_cols), type_2_list], axis=1),
        'Fusion Rifle': pd.concat([pd.DataFrame(file, columns=first_cols), type_3_list], axis=1),
        'Linear Fusion Rifle': pd.concat([pd.DataFrame(file, columns=first_cols), type_3_list], axis=1),
        'Grenade Launcher': pd.concat([pd.DataFrame(file, columns=first_cols), type_4_list], axis=1),
        'Rocket Launcher': pd.concat([pd.DataFrame(file, columns=first_cols), type_4_list], axis=1),
        'Glaive': pd.concat([pd.DataFrame(file, columns=first_cols), type_5_list], axis=1),
        'Sword': pd.concat([pd.DataFrame(file, columns=first_cols), type_6_list], axis=1),
    }

    # Return the selected type from the type_map dictionary
    return type_map[selected_type]

def create_grid_table(file, selected_tier, selected_type, selected_archetype, selected_slot, selected_element, selected_sunset):
    # Set up the GridOptionsBuilder object
    gridOptionsBuilder = GridOptionsBuilder.from_dataframe(file)

    # Set first column as index
    gridOptionsBuilder.configure_first_column_as_index(headerText='Weapon Name (S)')

    # Add single select box
    gridOptionsBuilder.configure_selection(selection_mode='single', use_checkbox=True)

    # Hide Unneeded Columns
    gridOptionsBuilder.configure_column('Weapon Name', resizable=True, hide=True)
    gridOptionsBuilder.configure_column('Weapon Season', resizable=True, hide=True)
    gridOptionsBuilder.configure_column('Weapon Current Version', resizable=True, hide=True)
    gridOptionsBuilder.configure_column('Weapon Power Cap', resizable=True, hide=True)

    # Size Columns
    columns_to_configure = file
    for column in columns_to_configure:
        gridOptionsBuilder.configure_column(column, resizable=True, width=90)
    gridOptionsBuilder.configure_column('Weapon Name With Season', resizable=True, width=250)
    gridOptionsBuilder.configure_column('Weapon Hash', resizable=True, width=125)
    gridOptionsBuilder.configure_column('Weapon Tier', resizable=True, width=125)
    gridOptionsBuilder.configure_column('Weapon Type', resizable=True, width=125)
    gridOptionsBuilder.configure_column('Weapon Archetype', resizable=True, width=150)
    gridOptionsBuilder.configure_column('Weapon Slot', resizable=True, width=125)
    gridOptionsBuilder.configure_column('Weapon Element', resizable=True, width=135)

    # Hide columns where the filter is selected
    if len(selected_tier) == 1:
        gridOptionsBuilder.configure_column('Weapon Tier', resizable=True, hide=True)

    if selected_type != 'Select all':
        gridOptionsBuilder.configure_column('Weapon Type', resizable=True, hide=True)

    if selected_archetype != 'Select all':
        gridOptionsBuilder.configure_column('Weapon Archetype', resizable=True, hide=True)

    if selected_slot != 'Select all':
        gridOptionsBuilder.configure_column('Weapon Slot', resizable=True, hide=True)

    if selected_element != 'Select all':
        gridOptionsBuilder.configure_column('Weapon Element', resizable=True, hide=True)

    if selected_sunset == 'Yes':
        gridOptionsBuilder.configure_column('Is Sunset', resizable=True, hide=True)

    # Build and display the grid table
    gridOptions = gridOptionsBuilder.build()
    grid_table = AgGrid(file, gridOptions=gridOptions, height=400, theme='balham')
    # Return the grid table object
    return grid_table

def create_hyperlinks_v1(dataframe, grid_table, col1, col2, col3, col4):
    # Create hyperlink for light.gg
    try:
        hyperlink_df = dataframe[['Weapon Name', 'Weapon Hash']]
        sel_row_1 = grid_table.selected_rows
        selected_hash_1 = sel_row_1[0]["Weapon Hash"]
        hyperlink_df = hyperlink_df.loc[hyperlink_df['Weapon Hash'] == selected_hash_1]
        selected_name_1 = hyperlink_df['Weapon Name'].iloc[0]
        selected_url_1 = "https://www.light.gg/db/items/{}/{}".format(selected_hash_1, selected_name_1)
        hyperlink_text_1 = "Light.gg - {}".format(selected_name_1)
        link_text_1 = '[{}]({})'.format(hyperlink_text_1, selected_url_1.replace(' ', '%20'))
        # Use st.write to display the formatted hyperlink text
        col1.write(link_text_1, unsafe_allow_html=True)
    except Exception:
        col1.write('Select Weapon to see Light.gg link', unsafe_allow_html=True)

    # Create hyperlink for D2 Foundry
    try:
        hyperlink_df = dataframe[['Weapon Name', 'Weapon Hash']]
        sel_row_2 = grid_table.selected_rows
        selected_hash_2 = sel_row_2[0]["Weapon Hash"]
        hyperlink_df = hyperlink_df.loc[hyperlink_df['Weapon Hash'] == selected_hash_2]
        selected_name_2 = hyperlink_df['Weapon Name'].iloc[0]
        selected_url_2 = "https://d2foundry.gg/w/{}".format(selected_hash_2)
        hyperlink_text_2 = "D2 Foundry - {}".format(selected_name_2)
        link_text_2 = '[{}]({})'.format(hyperlink_text_2, selected_url_2.replace(' ', '%20'))
        # Use st.write to display the formatted hyperlink text
        col2.write(link_text_2, unsafe_allow_html=True)
    except Exception:
        col2.write('Select Weapon to see D2 Foundry link', unsafe_allow_html=True)

    # Create hyperlink for DIM
    try:
        selected_url_3 = "https://app.destinyitemmanager.com/"
        link_text_3 = 'Destiny Item Manager (DIM)'
        # Use st.write to display the formatted hyperlink text
        col3.write(f'<a href="{selected_url_3}" target="_blank">{link_text_3}</a>', unsafe_allow_html=True)
    except Exception:
        pass

    # Create hyperlink for DIM Beta
    try:
        selected_url_4 = "https://beta.destinyitemmanager.com/"
        link_text_4 = 'BETA - Destiny Item Manager (DIM)'
        # Use st.write to display the formatted hyperlink text
        col4.write(f'<a href="{selected_url_4}" target="_blank">{link_text_4}</a>', unsafe_allow_html=True)
    except Exception:
        pass

def create_hyperlinks_v2(dataframe, grid_table, col5):
    # Create hyperlink for light.gg
    try:
        hyperlink_df = dataframe[['Weapon Name', 'Weapon Hash']]
        sel_row_1 = grid_table.selected_rows
        selected_hash_1 = sel_row_1[0]["Weapon Hash"]
        hyperlink_df = hyperlink_df.loc[hyperlink_df['Weapon Hash'] == selected_hash_1]
        selected_name_1 = hyperlink_df['Weapon Name'].iloc[0]
        selected_url_1 = "https://www.light.gg/db/items/{}/{}".format(selected_hash_1, selected_name_1)
        hyperlink_text_1 = "Light.gg - {}".format(selected_name_1)
        link_text_1 = '[{}]({})'.format(hyperlink_text_1, selected_url_1.replace(' ', '%20'))
        # Use st.write to display the formatted hyperlink text
        col5.write(link_text_1, unsafe_allow_html=True)
    except Exception:
        col5.write('Select Weapon to see Light.gg link', unsafe_allow_html=True)

    # Create hyperlink for D2 Foundry
    try:
        hyperlink_df = dataframe[['Weapon Name', 'Weapon Hash']]
        sel_row_2 = grid_table.selected_rows
        selected_hash_2 = sel_row_2[0]["Weapon Hash"]
        hyperlink_df = hyperlink_df.loc[hyperlink_df['Weapon Hash'] == selected_hash_2]
        selected_name_2 = hyperlink_df['Weapon Name'].iloc[0]
        selected_url_2 = "https://d2foundry.gg/w/{}".format(selected_hash_2)
        hyperlink_text_2 = "D2 Foundry - {}".format(selected_name_2)
        link_text_2 = '[{}]({})'.format(hyperlink_text_2, selected_url_2.replace(' ', '%20'))
        # Use st.write to display the formatted hyperlink text
        col5.write(link_text_2, unsafe_allow_html=True)
    except Exception:
        col5.write('Select Weapon to see D2 Foundry link', unsafe_allow_html=True)

    # Create hyperlink for DIM
    try:
        selected_url_3 = "https://app.destinyitemmanager.com/"
        link_text_3 = 'Destiny Item Manager (DIM)'
        # Use st.write to display the formatted hyperlink text
        col5.write(f'<a href="{selected_url_3}" target="_blank">{link_text_3}</a>', unsafe_allow_html=True)
    except Exception:
        pass

    # Create hyperlink for DIM Beta
    try:
        selected_url_4 = "https://beta.destinyitemmanager.com/"
        link_text_4 = 'BETA - Destiny Item Manager (DIM)'
        # Use st.write to display the formatted hyperlink text
        col5.write(f'<a href="{selected_url_4}" target="_blank">{link_text_4}</a>', unsafe_allow_html=True)
    except Exception:
        pass

@st.cache_data
def crafted_weapon_list(file):
    df = file.loc[file['Crafted'] == True]
    df = df[['Weapon Name With Season', 'Weapon Name', 'Weapon Tier', 'Weapon Type', 'Weapon Archetype', 'Crafted Level']]
    df = df.sort_values(by=('Crafted Level'), ascending=False)
    return df