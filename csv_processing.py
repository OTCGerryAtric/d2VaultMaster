import streamlit as st
import pandas as pd
import numpy as np

@st.cache_data
def load_manifest_data(file):
    # Load file
    df = pd.read_csv(file)

    # Re-Order Columns
    cols = df.columns.tolist()
    first_cols = ['Weapon Name With Season', 'Weapon Name', 'Weapon Season', 'Weapon Hash', 'Weapon Tier', 'Weapon Type', 'Weapon Archetype',  'Weapon Slot', 'Weapon Element',
                  'Weapon Current Version', 'Weapon Power Cap', 'Is Sunset']
    remaining_cols = [col for col in cols if col not in first_cols]
    df = df[first_cols + remaining_cols]
    df = df.rename(columns={'Weapon Range': 'Range'})
    return df

@st.cache_data
def load_dim_weapon_data(file, manifest_weapon_data):
    df = pd.read_csv(file)
    df = pd.merge(df, manifest_weapon_data[['Weapon Hash', 'Weapon Name With Season', 'Weapon Name', 'Weapon Season', 'Weapon Tier',
                                            'Weapon Type', 'Weapon Archetype', 'Weapon Slot', 'Weapon Element', 'Weapon Current Version',
                                            'Weapon Power Cap', 'Is Sunset']], left_on='Hash', right_on='Weapon Hash', how='left')

    df = df.rename(columns={'Id': 'Weapon ID'})

    cols = df.columns.tolist()
    first_cols = ['Weapon Name With Season', 'Weapon Name', 'Weapon Season', 'Weapon Hash', 'Weapon ID', 'Weapon Tier', 'Weapon Type', 'Weapon Archetype',
                  'Weapon Slot', 'Weapon Element',
                  'Weapon Current Version', 'Weapon Power Cap', 'Is Sunset']
    remaining_cols = [col for col in cols if col not in first_cols]
    df = df[first_cols + remaining_cols]
    df = df.drop(
        columns=['Name', 'Hash', 'Tag', 'Source', 'Tier', 'Type', 'Category', 'Element', 'Power', 'Power Limit', 'Owner', 'Locked', 'Equipped', 'Year', 'Season', 'Event', 'Recoil',
                 'AA', 'Impact', 'Range', 'Zoom', 'Blast Radius', 'Velocity', 'Stability', 'ROF', 'Reload', 'Mag', 'Handling', 'Charge Time', 'Guard Resistance', 'Draw Time', 'Accuracy',
                 'Charge Rate', 'Guard Efficiency', 'Swing Speed', 'Shield Duration', 'Kill Tracker', 'Foundry', 'Loadouts', 'Notes', 'Perks 0'])

    dim_perk_columns = df.filter(regex='^Perks').columns
    df[dim_perk_columns] = df[dim_perk_columns].replace(to_replace='\*', value='', regex=True)

    # Replace Enhanced Battery
    df = df.replace('Enhanced Battery', 'E_nhanced Battery')

    # Remove Enhanced from Perks
    for column in df.columns:
        if column.startswith('Perk'):
            df[column] = df[column].str.replace('Enhanced ', '', regex=False)

        # Replace Enhanced Battery
        df = df.replace('E_nhanced Battery', 'Enhanced Battery')
    return df

@st.cache_data
def load_dim_armour_data(file):
    cols_to_use = ['Name', 'Hash', 'Id', 'Tier', 'Type', 'Equippable', 'Energy Capacity', 'Mobility (Base)', 'Resilience (Base)', 'Recovery (Base)', 'Discipline (Base)', 'Intellect (Base)', 'Strength (Base)', 'Total (Base)']
    col_names = {'Id': 'id', 'Equippable': 'Character', 'Energy Capacity': 'MW_Tier', 'Mobility (Base)': 'base_mob', 'Resilience (Base)': 'base_res', 'Recovery (Base)': 'base_rec', 'Discipline (Base)': 'base_dis',
                 'Intellect (Base)': 'base_int', 'Strength (Base)': 'base_str', 'Total (Base)': 'base_total'}
    df = pd.read_csv(file, usecols=cols_to_use)
    df = df.rename(columns=col_names)
    df['Type'] = df['Type'].replace({'Hunter Cloak', 'Warlock Bond', 'Titan Mark'}, 'Class Item').replace('Chest armour', 'Chest').replace('Leg armour', 'Legs')
    df["base_mob_res"] = df['base_mob'] + df['base_res']
    df["base_mob_rec"] = df['base_mob'] + df['base_rec']
    df["base_res_rec"] = df['base_res'] + df['base_rec']
    df["base_group_1"] = df['base_mob'] + df['base_res'] + df['base_rec']
    df["base_group_2"] = df['base_dis'] + df['base_int'] + df['base_str']
    df["mw_mob"] = df['base_mob'] + 2
    df["mw_res"] = df['base_res'] + 2
    df["mw_rec"] = df['base_rec'] + 2
    df["mw_dis"] = df['base_dis'] + 2
    df["mw_int"] = df['base_int'] + 2
    df["mw_str"] = df['base_str'] + 2
    df["mw_total"] = df['base_total'] + 12
    df["mw_mob_res"] = df['mw_mob'] + df['mw_res']
    df["mw_mob_rec"] = df['mw_mob'] + df['mw_rec']
    df["mw_res_rec"] = df['mw_res'] + df['mw_rec']
    df["mw_group_1"] = df['mw_mob'] + df['mw_res'] + df['mw_rec']
    df["mw_group_2"] = df['mw_dis'] + df['mw_int'] + df['mw_str']
    return df
