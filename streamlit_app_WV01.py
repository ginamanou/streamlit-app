import streamlit as st

import pandas as pd
import numpy as np

import math

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import os
import warnings
warnings.filterwarnings("ignore")

from Tools.SMPA_tools_WV01 import *

st.set_page_config(
    page_title="My 1st Streamlit App",
    page_icon="👋",
    layout="wide",
    initial_sidebar_state="expanded"
)

#alt.themes.enable("dark")

# Perform some css hacking in order to incease the font size of the expander labels
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")

st.markdown("""
        <style>
        .small-font {
            font-size:14px !important;
        }
        </style>
        
        <style>
        .big-font {
            font-size:20px !important;
        }
        </style>
        """, unsafe_allow_html=True)

with st.sidebar:
    st.title(":chart_with_upwards_trend: SMPA Analysis")#, anchor="title")
    st.markdown("""
        This app was built specifically for small punch creep and uniaxial creep analysis and visualization of results.  

        > :blue[**Through the app you can achieve the following:**]
        - Create interactive plots
        - Download graphs
        - Compare different experiments
        - Analyze data
        - Export the results 

        > :orange[**Things to keep in mind** ] :blue[**for a smooth interaction with the app:**]
        - The interface was designed to be used in a linear manner from top to bottom.  
                
        - Make sure that you load **csv** files that do not contain any special characters.
        - The structure of the files needs to only involve **a header and the data.**  
                  
          If there is extra description or other rows at the beginning or at the end **they should be first removed** !!   
            """)
    
with st.expander(" :arrow_heading_up: Imports section", expanded=True):
    st.markdown('''                
        :point_down: :blue[In this section you are expected to provide certain information regarding the input data]
    '''
    )

    selected_type_of_exp = st.radio("Choose the type of experiments you want to visualize/analyze.",
                                    ["Uniaxial creep", "Small punch creep"],
                                    key="type_of_exp")

    if st.session_state.type_of_exp == "Uniaxial creep":
        col1, col2, col3 = st.columns(3)
        time_uc = col1.text_input("Select the column that represents **Time** on your data", key='select_uc_time_col')
        lvdt1 = col2.text_input("Select the column that represents **LVDT1** on your data", key='select_lvdt1_col')
        lvdt2 = col3.text_input("Select the column that represents **LVDT2** on your data", key='select_lvdt2_col')
    else:
        col1, col2, col3, col4 = st.columns(4)
        time_spc = col1.text_input("Type the name of the column that represents **Time** in your data", key="select_spc_time_col")
        u_col = col2.text_input("Type the name of the column that represents **Deflection** in your data", key="select_u_col")
        force_col = col3.text_input("Type the name of the column that represents **Force** in your data", key="select_force_col")
        temp_col = col4.text_input("Type the name of the column that represents **Temperature** in your data", key="select_temp_col")    

    if (st.session_state.type_of_exp == "Uniaxial creep"):
        st.markdown('<p class="small-font">- Add the full paths of the experiments you want to visualize/analyze.</p>', unsafe_allow_html=True)
        st.markdown('<p class="small-font">- Add the gauge length of each specimen.</p>', unsafe_allow_html=True)
        st.markdown('<p class="small-font">- After adding an entry press enter.</p>', unsafe_allow_html=True)
        #st.markdown('<p class="small-font">- Avoid deleting the content of a row using the backspace. Instead, delete the entire row by selecting it and clicking on the trash bin symbol in the top right of the table.</p>', unsafe_allow_html=True)

        table_file_input = pd.DataFrame(columns=['Path', 'Gauge length', 'Preferred LVDT for plotting'])
        edit_table_file_input = st.data_editor(table_file_input, column_config={
            "Path": st.column_config.TextColumn(width='large'),
            "Gauge length": st.column_config.NumberColumn(width='small'),
            "Preferred LVDT for plotting": st.column_config.SelectboxColumn(options=["LVDT 1", "LVDT 2", "Average of LVDTs"], width='small')
        }, hide_index=True, num_rows= 'dynamic', use_container_width=True, key="file_upload_df")
        
    else:
        st.markdown('<p class="small-font">- Add the full paths of the experiments you want to visualize/analyze below.</p>', unsafe_allow_html=True)
        st.markdown('<p class="small-font">- After adding an entry press enter.</p>', unsafe_allow_html=True)
        #st.markdown('<p class="small-font">- Avoid deleting the content of a row using the backspace. Instead, delete the entire row by selecting it and clicking on the trash bin symbol in the top right of the table.</p>', unsafe_allow_html=True)

        table_file_input = pd.DataFrame(columns=['Path'])
        edit_table_file_input = st.data_editor(table_file_input, hide_index=True, num_rows= 'dynamic', use_container_width=True, key="file_upload_df")

    all_dfs = {}
    all_gauges = {}
    all_lvdts_for_plot = {}
    trace_spc_1 = []
    trace_spc_2 = []
    trace_uc = []
    if (edit_table_file_input.empty != True): 
        # if edit_table_file_input.loc[0, "Path"] != None:
        #     if st.session_state.type_of_exp == "Uniaxial creep":
        #         col1, col2, col3 = st.columns(3)
        #         time_uc = col1.text_input("Select the column that represents time on your data", key='select_uc_time_col')
        #         lvdt1 = col2.text_input("Select the column that represents LVDT1 on your data", key='select_lvdt1_col')
        #         lvdt2 = col3.text_input("Select the column that represents LVDT2 on your data", key='select_lvdt2_col')
        #     else:
        #         col1, col2, col3, col4 = st.columns(4)
        #         time_spc = col1.text_input("Type the name of the column that represents **time** in your data", key="select_spc_time_col")
        #         u_col = col2.text_input("Type the name of the column that represents **deflection** in your data", key="select_u_col")
        #         force_col = col3.text_input("Type the name of the column that represents **force** in your data", key="select_force_col")
        #         temp_col = col4.text_input("Type the name of the column that represents **temperature** in your data", key="select_temp_col")       

        for i in range(0, len(edit_table_file_input)):
            if edit_table_file_input.loc[i, "Path"] != None:
                st.session_state.df_added = "not_valid"
                row_path = edit_table_file_input.loc[i, "Path"].strip()#.encode('ascii', errors='replace').rstrip()
                row_path = row_path.replace('\\', '/')
                #st.write(st.session_state) 
                try: 
                    df = pd.read_csv(row_path)
                    st.session_state.df_added = "valid"   
                except FileNotFoundError:
                    st.markdown(":red[**Attention!!**] You haven't provided a valid path. Make sure that you add the full path to your csv files.")

                #st.write(st.session_state)
                
                file_with_ext = row_path.split('/')[-1]
                folder_name = file_with_ext.removesuffix('.csv')
                #st.write(type(file_with_ext))

                if (st.session_state.type_of_exp == "Small punch creep") & (st.session_state.df_added == "valid"):
                    count_blanks = 0
                    if (st.session_state.select_spc_time_col == ""):
                        count_blanks +=1
                    if (st.session_state.select_u_col == ""):
                        count_blanks +=1
                    if (st.session_state.select_force_col == ""): 
                        count_blanks +=1
                    if (st.session_state.select_temp_col == ""):
                        count_blanks +=1
                    if count_blanks > 1:
                        pass
                    else:
                        if (st.session_state.select_spc_time_col != "") & (st.session_state.select_u_col != "") & (st.session_state.select_force_col != "") & (st.session_state.select_temp_col != ""):
                            if (st.session_state.select_spc_time_col != st.session_state.select_u_col) & (st.session_state.select_spc_time_col != st.session_state.select_force_col) & (st.session_state.select_spc_time_col != st.session_state.select_temp_col) & (st.session_state.select_u_col != st.session_state.select_force_col) & (st.session_state.select_u_col != st.session_state.select_temp_col) & (st.session_state.select_force_col != st.session_state.select_temp_col):
                                try:
                                    df_new = df_spc_for_app(df, st.session_state.select_spc_time_col, st.session_state.select_u_col, st.session_state.select_force_col, st.session_state.select_temp_col)
                                    all_dfs[folder_name] = df_new

                                    trace_cd = go.Scatter(
                                        x=df_new["TotalHours"],
                                        y=df_new["u"],
                                        mode='lines+markers',
                                        name=folder_name,
                                    )
                                    trace_spc_1.append(trace_cd)

                                    trace_fd = go.Scatter(
                                        x=df_new["u"],
                                        y=df_new["Force"],
                                        mode='lines+markers',
                                        name=folder_name,
                                    )
                                    trace_spc_2.append(trace_fd)
                                except KeyError:
                                    st.markdown(":red[**Attention!!**] Check again the spelling of the column names")
                            # else:
                            #     st.markdown(":red[**Attention!!**] You have selected the same column name as representative of different data. Revise your entries above in order to continue.")

                if (st.session_state.type_of_exp == "Uniaxial creep") & (st.session_state.df_added == "valid"):
                    count_blanks_uc = 0
                    if (st.session_state.select_uc_time_col == ""):
                        count_blanks_uc +=1
                    if (st.session_state.select_lvdt1_col == ""):
                        count_blanks_uc +=1
                    if (st.session_state.select_lvdt2_col == ""): 
                        count_blanks_uc +=1
                    if count_blanks_uc > 1:
                        pass
                    else:
                        if (st.session_state.select_uc_time_col != "") & (st.session_state.select_lvdt1_col != "") & (st.session_state.select_lvdt2_col != ""):
                            #if ("select_uc_time_col" in st.session_state) & ("select_lvdt1_col" in st.session_state) & ("select_lvdt2_col" in st.session_state):
                            if (st.session_state.select_uc_time_col != st.session_state.select_lvdt1_col) & (st.session_state.select_uc_time_col != st.session_state.select_lvdt2_col) & (st.session_state.select_lvdt1_col != st.session_state.select_lvdt2_col):
                                try:
                                    df_new = df_uc_for_app(df, st.session_state.select_uc_time_col, st.session_state.select_lvdt1_col, st.session_state.select_lvdt2_col)

                                    row_gauge = edit_table_file_input.loc[i, "Gauge length"]
                                    selected_lvdt = edit_table_file_input.loc[i, "Preferred LVDT for plotting"]

                                    if row_gauge != None:
                                        all_gauges[folder_name] = row_gauge
                                        df_new2 = calculate_strain(df_new, row_gauge)
                                        all_dfs[folder_name] = df_new2
                                        #st.write(df_new2)

                                        if selected_lvdt != None:
                                            all_lvdts_for_plot[folder_name] = selected_lvdt

                                            if selected_lvdt == "LVDT 1":
                                                trace_s = go.Scatter(
                                                    x=df_new2["TotalHours"],
                                                    y=df_new2["strain1"],
                                                    mode='lines+markers',
                                                    name=folder_name,
                                                )
                                                trace_uc.append(trace_s)
                                            elif selected_lvdt == "LVDT 2":
                                                trace_s = go.Scatter(
                                                    x=df_new2["TotalHours"],
                                                    y=df_new2["strain2"],
                                                    mode='lines+markers',
                                                    name=folder_name,
                                                )
                                                trace_uc.append(trace_s)
                                            else:
                                                trace_s = go.Scatter(
                                                    x=df_new2["TotalHours"],
                                                    y=df_new2["strain_avg"],
                                                    mode='lines+markers',
                                                    name=folder_name,
                                                )
                                                trace_uc.append(trace_s)
                                except KeyError:
                                    st.markdown(":red[**Attention!!] Check again the spelling of the column names")

with st.expander(" :arrow_right: Visualization section", expanded=False):
    st.markdown('''                
        :point_down: :blue[In this section you can visualize one or multiple experiments and compare them]
    '''
    )  

    if (st.session_state.type_of_exp == "Small punch creep"):
        if ("select_spc_time_col" in st.session_state) & ("select_u_col" in st.session_state) & ("select_force_col" in st.session_state) & ("select_temp_col" in st.session_state):
            if (st.session_state.select_spc_time_col != "") & (st.session_state.select_u_col != "") & (st.session_state.select_force_col != "") & (st.session_state.select_temp_col != ""):
                if (st.session_state.select_spc_time_col != st.session_state.select_u_col) & (st.session_state.select_spc_time_col != st.session_state.select_force_col) & (st.session_state.select_spc_time_col != st.session_state.select_temp_col) & (st.session_state.select_u_col != st.session_state.select_force_col) & (st.session_state.select_u_col != st.session_state.select_temp_col) & (st.session_state.select_force_col != st.session_state.select_temp_col):
                    if (edit_table_file_input.empty != True):
                        def page_df():
                            for item in all_dfs.keys():
                                st.write("#### Experiment: " + item)
                                st.dataframe(all_dfs[item])

                        def page_creep_deflection_plot():
                            fig_cd = go.Figure()#make_subplots()
                            for tr in trace_spc_1:
                                fig_cd.add_trace(tr)
                                fig_cd.update_layout(title=dict(text="Creep deflection curve"),
                                                    xaxis_title="Time [h]", 
                                                    yaxis_title="Deflection [µm]",
                                                    showlegend=True)
                            st.plotly_chart(fig_cd, use_container_width=True)
                            
                        def page_force_deflection_plot():
                            fig_fd = go.Figure()#make_subplots()
                            for tra in trace_spc_2:
                                fig_fd.add_trace(tra)
                                fig_fd.update_layout(title=dict(text="Force-deflection curve"),
                                                    xaxis_title="Deflection [µm]", 
                                                    yaxis_title="Force [N]",
                                                    showlegend=True)
                            st.plotly_chart(fig_fd, use_container_width=True)        

                        pages={
                            "Preview data": page_df,
                            "Creep deflection curve": page_creep_deflection_plot,
                            "Force-deflection curve": page_force_deflection_plot 
                        }
                        try:
                            selected_plot = st.selectbox(
                                "Choose a page",
                                pages.keys(),
                                key="selected_plot_spc"
                                )

                            pages[selected_plot]()
                        except ValueError:
                            st.markdown(":red[**Attention!!**] Make sure that you have selected the column names above correctly.")
                else:
                    st.markdown(":red[**Attention!!**] You have selected the same column name as representative of different data. Revise your entries in the **Imports section** in order to continue.")
            else:
                st.markdown(":red[**Attention!!**] One or more of the representative column names have been left empty. Revise your entries in the **Imports section** in order to continue.")
            
    if (st.session_state.type_of_exp == "Uniaxial creep"):
        if ("select_uc_time_col" in st.session_state) & ("select_lvdt1_col" in st.session_state) & ("select_lvdt2_col" in st.session_state):
            if (st.session_state.select_uc_time_col != "") & (st.session_state.select_lvdt1_col != "") & (st.session_state.select_lvdt2_col != ""):
                if (st.session_state.select_uc_time_col != st.session_state.select_lvdt1_col) & (st.session_state.select_uc_time_col != st.session_state.select_lvdt2_col) & (st.session_state.select_lvdt1_col != st.session_state.select_lvdt2_col):
                    if (edit_table_file_input.empty != True):
                        def page_df():
                            for item in all_dfs.keys():
                                st.write("#### Experiment: " + item)
                                st.dataframe(all_dfs[item])

                        def page_creep_strain_plot():
                            fig_strain = make_subplots()
                            for tro in trace_uc:
                                fig_strain.add_trace(tro)
                                fig_strain.update_layout(title=dict(text="Creep strain curve"),
                                                    xaxis_title="Time [h]", 
                                                    yaxis_title="Strain [%]",
                                                    showlegend=True)
                            st.plotly_chart(fig_strain, use_container_width=True)

                        pages={
                            "Preview data": page_df,
                            "Creep strain curve": page_creep_strain_plot
                        }

                        selected_plot = st.selectbox(
                                    "Choose a page",
                                    pages.keys(),
                                    key="selected_plot_uc"
                                    )
                        
                        try:
                            if selected_plot == 'Preview data':
                                if (row_gauge == None):
                                    st.markdown(":red[**Attention!!**] In the **Imports section** you haven't added information regarding the gauge length.")
                                else:
                                    pages[selected_plot]()
                            else:
                                if (row_gauge != None) & (selected_lvdt != None):
                                    pages[selected_plot]()
                                else:
                                    if (row_gauge == None):
                                        st.markdown(":red[**Attention!!**] In the **Imports section** you haven't added information regarding the gauge length.")
                                    if (selected_lvdt == None):
                                        st.markdown(":red[**Attention!!**] In the **Imports section** you haven't selected your preferred LVDT for plotting.")
                            #pages[selected_plot]()
                        except:
                            st.markdown(":red[**Attention!!**] Make sure that you have selected the column names above correctly.")                                
                else:
                    st.markdown(":red[**Attention!!**] You have selected the same column name as representative of different data. Revise your entries in the **Imports section** in order to continue.")
            else:
                st.markdown(":red[**Attention!!**] One or more of the representative column names have been left empty. Revise your entries in the **Imports section** in order to continue.")

with st.expander(" :arrow_right: Analysis section", expanded=False):
    st.markdown(r"""                
        :point_down: :blue[In this section you can analyze the data that you want by selecting below one of the experiments you have uploaded]
    """
    )

    names = []
    for file in all_dfs.keys():
        names.append(file)

    # col1, col2 = st.columns(2)
    # selected_exp = col1.radio(
    #     "Choose the experiment you want to analyze",
    #     names,
    #     key='selected_exp'
    # )

    if (st.session_state.type_of_exp == "Small punch creep"):
        if ("select_spc_time_col" in st.session_state) & ("select_u_col" in st.session_state) & ("select_force_col" in st.session_state) & ("select_temp_col" in st.session_state):
            if (st.session_state.select_spc_time_col != "") & (st.session_state.select_u_col != "") & (st.session_state.select_force_col != "") & (st.session_state.select_temp_col != ""):
                if (st.session_state.select_spc_time_col != st.session_state.select_u_col) & (st.session_state.select_spc_time_col != st.session_state.select_force_col) & (st.session_state.select_spc_time_col != st.session_state.select_temp_col) & (st.session_state.select_u_col != st.session_state.select_force_col) & (st.session_state.select_u_col != st.session_state.select_temp_col) & (st.session_state.select_force_col != st.session_state.select_temp_col):
                    if (edit_table_file_input.empty != True):
                        col1, col2 = st.columns(2)
                        selected_exp = col1.radio(
                            "Choose the experiment you want to analyze",
                            names,
                            key='selected_exp'
                        )
                        #if selected_exp != None:
                        df = all_dfs[selected_exp]
                        col1, col2 = st.columns(2)
                        force = col1.number_input("Type in the **Force** in N under which your experiment was performed", format="%0.1f")
                        temp = col2.number_input("Type in the **Temperature** in °C under which your experiment was performed", format="%0.1f")
                        #st.write(df)

                        # stop_start = calculate_t0_index(df, 20, 5)
                        # stop_end = calculate_tR_index(df, 500, 200, 'u')

                        # df_lim = df[stop_start:stop_end+1]
                        # df_lim.reset_index(inplace=True)
                        # df_lim = df_lim.drop(columns=['index'])
                        # df_lim.u = df_lim.u - df_lim.u[0]

                        # df_lim['TotalSeconds'] = df_lim['DateTime'].diff().dt.total_seconds().cumsum()       # Calculate the total amount of seconds since the start of the experimet
                        # df_lim.loc[0, 'TotalSeconds'] = 0
                        # df_lim['TotalSeconds'] = df_lim['TotalSeconds'].astype(int, errors='ignore')
                        # df_lim['TotalMinutes'] = df_lim['TotalSeconds']/60
                        # df_lim['TotalHours'] = df_lim['TotalSeconds']/3600

                        # t0 = 0
                        # tR = df_lim.TotalSeconds[len(df_lim)-1]
                        
                        st.markdown(''' **<p class="big-font"> :blue[STEP 1:] Preprocessing/Cleaning of the deflection data (if necessary)</p>** ''', unsafe_allow_html=True)
                        col1, col2 = st.columns([1, 2])
                        col1.text("")
                        col1.text("")
                        col1.markdown('''
                            Often we start logging the data before the full load has been applied.  
                            Also, often times the data acquisition continues even after the rupture of the specimen.  
                            As a result, the raw data present many invalid values at the beginning and the end of experiments.  
                                
                            If this is the case, use the interactive tools of the graph on the right to zoom and hover over the datapoints and identify the point of the start of the experiment and the time to rupture.
                        ''')
                        fig_toclean = go.Figure()#make_subplots()
                        fig_toclean.add_trace(go.Scatter(
                                                x=df.TotalHours,
                                                y=df.u,
                                                mode='lines+markers',
                                                name="deflection uncleaned")
                                    )

                        fig_toclean.update_layout(title=dict(text="Creep deflection curve"),
                                            xaxis_title="Time [h]", 
                                            yaxis_title="Deflection [µm]",
                                            showlegend=True)
                        col2.plotly_chart(fig_toclean, use_container_width=True)

                        stop_start = col1.number_input("Type the value of the identified (from the graph) initial deflection.", step=50, key='stop_start')
                        stop_end = col1.number_input("Type the value of the identified (from the graph) deflection at rupture.", step=50, key='stop_end')
                        #st.write(st.session_state)

                        if (stop_start != 0): 
                            if (stop_end > stop_start):
                                df_lim = df[(df.u >= stop_start) & (df.u <= stop_end)]
                                df_lim.reset_index(inplace=True)
                                #df_lim = df.drop(columns=['index'])
                                df_lim.u = df_lim.u - df_lim.u[0]

                                df_lim['TotalSeconds'] = df_lim['DateTime'].diff().dt.total_seconds().cumsum()       # Calculate the total amount of seconds since the start of the experimet
                                df_lim.loc[0, 'TotalSeconds'] = 0
                                df_lim['TotalSeconds'] = df_lim['TotalSeconds'].astype(int, errors='ignore')
                                df_lim['TotalMinutes'] = df_lim['TotalSeconds']/60
                                df_lim['TotalHours'] = df_lim['TotalSeconds']/3600

                                tR = df_lim.TotalSeconds[len(df_lim)-1]
                            else:
                                st.markdown("The deflection at rupture cannot precede the initial deflection. You have entered the values wrong.")
                        else:
                            if (stop_end != 0):
                                df_lim = df[:stop_end]
                                df_lim.reset_index(inplace=True)
                                df_lim = df.drop(columns=['index'])

                                tR = df_lim.TotalSeconds[len(df_lim)-1]
                            else:
                                st.markdown("**No cleaning was performed.** The algorithm will proceed with the input data as is.")
                                df_lim = df.copy()
                                tR = df_lim.TotalSeconds[len(df_lim)-1]

                        t0 = 0
                        
                        st.markdown(''' **<p class="big-font"> :blue[STEP 2:] Calculation of the deflection rate </p>** ''', unsafe_allow_html=True)

                        col1, col2 = st.columns([1,2])
                        
                        ### Alternative 1
                        col1.text("")
                        col1.text("")
                        
                        col1.markdown(''' 
                                    The current methodology splits the dataset into sections 
                                    and calculates the deflection rate as the regression slope 
                                    of all the data points that fall into each section.
                                    ''')  
                        col1.markdown(''' <span style="text-decoration:underline"> Hint: </span> The suggested number of sections is **between 100 and 400**.''', unsafe_allow_html=True)

                        sections_num = col1.number_input("Type the number of sections", min_value=50, max_value=500, step=10, key="sections_to_split")

                        interval_points = (tR - t0)/int(sections_num)
                        col1.markdown("Each of the " + str(sections_num) + " sections contains " + str(math.floor(interval_points)) + " data points (corresponding to " + str(math.floor(interval_points)) + " seconds.)")

                        dudt, t_points, u_points = calculate_rate_of_variable(df_lim, 'u', interval_points, t0, tR)

                        fig1 = make_subplots(specs=[[{"secondary_y": True}]])
                        fig1.add_trace(go.Scatter(
                                            x=t_points,
                                            y=u_points,
                                            mode='lines+markers',
                                            name="deflection"),
                                            secondary_y=False,
                                )
                        
                        fig1.add_trace(go.Scatter(
                                            x=t_points,
                                            y=dudt,
                                            mode='lines+markers',
                                            name="deflection rate"),
                                            secondary_y=True,
                                        )

                        # Add figure title
                        fig1.update_layout(
                            title_text="Deflection & deflection rate")

                        # Set x-axis title
                        fig1.update_xaxes(title_text="Time [h]")

                        # Set y-axes titles
                        fig1.update_yaxes(title_text="Deflection [µm]", secondary_y=False)
                        fig1.update_yaxes(title_text="Deflection rate [µm/h]", secondary_y=True)

                        col2.plotly_chart(fig1, use_container_width=True)

                        st.markdown(''' **<p class="big-font"> :blue[STEP 3:] Smoothening of the deflection rate curve (optional) </p>** ''', unsafe_allow_html=True)

                        sm = st.checkbox('Smooth curve using moving average', key='smooth')

                        if  sm == True:
                            col1, col2 = st.columns([1,2])
                            col1.text("")
                            col1.text("")
                            window_size = col1.select_slider("Select a window size", [x for x in range(7, 51)])
                            moving_averages, tt, uu_list= smoothen_curve(dudt, t_points, u_points, window_size)

                            fig2 = go.Figure()
                            fig2.add_trace(go.Scatter(
                                                x=tt,
                                                y=moving_averages,
                                                mode='lines+markers',
                                                name="smooth curve")
                                    )
                            
                            # Add figure title
                            fig2.update_layout(title_text="Smoothened curve")

                            # Set axes titles
                            fig2.update_xaxes(title_text="Time [h]", range=[0, max(tt)+10])

                            fig2.update_yaxes(title_text="Deflection rate [µm/h]")

                            st.plotly_chart(fig2, use_container_width=True)

                        def secondary_deflection(defl_rate, time, low, high):
                            lower_limit = low
                            upper_limit = high
                            tt_middle = []
                            middle_part = []
                            for i in range(len(time)):
                                if (time[i]>=lower_limit) & (time[i]<=upper_limit):
                                    tt_middle.append(time[i])
                                    middle_part.append(defl_rate[i])

                            return middle_part, tt_middle
                        
                        st.markdown(''' **<p class="big-font"> :blue[STEP 4:] Calculation of the minimum deflection rate </p>** ''', unsafe_allow_html=True)

                        col1, col2 = st.columns([1,2])
                        col1.text("")
                        col1.text("")
                        col1.markdown(''' <span style="text-decoration:underline"> Small description of the methodology </span> ''', unsafe_allow_html=True)
                        col1.markdown(''' 
                                    - First, a second degree polynomial curve is fitted to the datapoints of the deflection rate.  
                                    - Then, the minimum deflection rate is considered the same as the minimum point of the fitted curve, in order to reduce uncertainty due to the noise in the signal.  
                                        
                                    Actions to be taken:
                                    1. Observe and interact with the deflection rate graph either in STEP 2 or STEP 3 (if you proceeded with smoothening).
                                    2. Try to roughly isolate by eye the part of the curve where the minimum deflection rate is located.''')
                        col1.markdown('''
                                    <span style="text-decoration:underline"> NOTE: </span>
                                    ''', unsafe_allow_html=True)
                        col1.markdown('''
                                    In some cases, it has been noticed that the deflection rate curve presents two minima instead of one.  
                                    There is no clear answer to why this happens, but it could be an indication of cracking at some point during the experiment.  
                                    It is suggested that before making any conclusions, you first make sure that the temperature profile didn't deviate considerably from the target.   
                                    By checking the box below, both minima will be identified by the algorithm.  
                                    ''')
                        double_min = col1.checkbox("Double minimum", key='double_min')
                        col1.markdown('''
                                    3. Move the sides of the slider(s) so that they match the bounds (in terms of time) of the previously isolated part(s) of the minimum(a).
                                    4. The graph depicts the identified minimum deflection rate(s).  
                                        ''')
                        if sm == True:                    
                            if double_min == True:
                                col2.text("")
                                col2.text("")
                                col2.markdown('''Select the bounds of those parts of the curve where there is a local minimum''')
                                sel_limits1 = col2.slider("First part", int(tt[0]+1), int(tt[len(tt)-1]+1), value=(int(tt[0]+1), int(tt[len(tt)-1]+1)))
                                sel_limits2 = col2.slider("Second part", int(tt[0]+1), int(tt[len(tt)-1]+1), value=(int(tt[0]+1), int(tt[len(tt)-1]+1)))

                                # Isolate the parts of the curve with a local minimum
                                middle_part1, tt_middle1 = secondary_deflection(moving_averages, tt, sel_limits1[0], sel_limits1[1])
                                middle_part2, tt_middle2 = secondary_deflection(moving_averages, tt, sel_limits2[0], sel_limits2[1])

                                # Calculate a fitted curve
                                polynomial1 = calc_polynomial(middle_part1, tt_middle1)
                                polynomial2 = calc_polynomial(middle_part2, tt_middle2)

                                # Find the local minimum
                                crit1 = polynomial1.deriv().r
                                r_crit1 = crit1[crit1.imag==0].real
                                test1 = polynomial1.deriv(2)(r_crit1)

                                crit2 = polynomial2.deriv().r
                                r_crit2 = crit2[crit2.imag==0].real
                                test2 = polynomial2.deriv(2)(r_crit2)

                                # Compute the local minima excluding range boundaries
                                x_min1 = r_crit1[test1>0]
                                y_min1 = polynomial1(x_min1)

                                x_min2 = r_crit2[test2>0]
                                y_min2 = polynomial2(x_min2)

                                fig3 = go.Figure()
                                fig3.add_trace(go.Scatter(
                                                    x=tt,
                                                    y=moving_averages,
                                                    mode='lines+markers',
                                                    name="deflection rate",
                                                    showlegend=True)
                                        )

                                fig3.add_trace(go.Scatter(
                                                    x=x_min1,
                                                    y=y_min1,
                                                    mode='markers',
                                                    name="local minimum 1",
                                                    marker=dict(
                                                                color='MediumPurple',
                                                                size=12#,
                                                                # line=dict(
                                                                #     color='MediumPurple',
                                                                #     width=12
                                                                # )
                                                            ),
                                                            showlegend=True
                                                        )
                                                    )
                                
                                fig3.add_trace(go.Scatter(
                                                    x=x_min2,
                                                    y=y_min2,
                                                    mode='markers',
                                                    name="local minimum 2",
                                                    marker=dict(
                                                                color='mediumvioletred',
                                                                size=12#,
                                                                # line=dict(
                                                                #     color='MediumPurple',
                                                                #     width=12
                                                                # )
                                                            ),
                                                            showlegend=True
                                                        )
                                                    )
                                
                                # Add figure title
                                fig3.update_layout(title_text="Minimum deflection rate")

                                # Set axes titles
                                fig3.update_xaxes(title_text="Time [h]")
                                fig3.update_yaxes(title_text="Deflection rate [µm/h]")
                            else:
                                col2.text("")
                                col2.text("")
                                sel_limits = col2.slider("Select the bounds of the curve where the minimum is located", int(tt[0]+1), int(tt[len(tt)-1]+1), value=(int(tt[0]+1), int(tt[len(tt)-1]+1)))
                                # Isolate the middle part of the curve
                                middle_part, tt_middle = secondary_deflection(moving_averages, tt, sel_limits[0], sel_limits[1])

                                # Calculate a fitted curve
                                polynomial = calc_polynomial(middle_part, tt_middle)

                                # Find the local minimum
                                crit = polynomial.deriv().r
                                r_crit = crit[crit.imag==0].real
                                test = polynomial.deriv(2)(r_crit)

                                # Compute the local minimum excluding range boundaries
                                x_min1 = r_crit[test>0]
                                y_min1 = polynomial(x_min1)

                                # Compute a curve based on the fitted poly
                                xc = np.arange(int(tt_middle[0]), int(tt_middle[len(tt_middle)-1]+1), 0.02)
                                yc = polynomial(xc)

                                fig3 = go.Figure()
                                fig3.add_trace(go.Scatter(
                                                    x=tt_middle,
                                                    y=middle_part,
                                                    mode='lines+markers',
                                                    name="deflection rate",
                                                    showlegend=True)
                                        )
                                
                                fig3.add_trace(go.Scatter(
                                                    x=xc,
                                                    y=yc,
                                                    mode='lines',
                                                    name="fitted curve",
                                                    line=dict(
                                                        color='mediumvioletred'
                                                    ),
                                                    showlegend=True)
                                        )

                                fig3.add_trace(go.Scatter(
                                                    x=x_min1,
                                                    y=y_min1,
                                                    mode='markers',
                                                    name="global minimum",
                                                    marker=dict(
                                                                color='MediumPurple',
                                                                size=12#,
                                                                # line=dict(
                                                                #     color='MediumPurple',
                                                                #     width=12
                                                                # )
                                                            ),
                                                            showlegend=True
                                                        )
                                                    )

                                # Add figure title
                                fig3.update_layout(title_text="Minimum deflection rate")

                                # Set axes titles
                                fig3.update_xaxes(title_text="Time [h]")
                                fig3.update_yaxes(title_text="Deflection rate [µm/h]")
                        else:
                            if double_min == True:
                                col2.text("")
                                col2.text("")
                                col2.markdown('''Select the bounds of those parts of the curve where there is a local minimum''')
                                sel_limits1 = col2.slider("First part", int(t_points[0]+1), int(t_points[len(t_points)-1]+1), value=(int(t_points[0]+1), int(t_points[len(t_points)-1]+1)))
                                sel_limits2 = col2.slider("Second part", int(t_points[0]+1), int(t_points[len(t_points)-1]+1), value=(int(t_points[0]+1), int(t_points[len(t_points)-1]+1)))

                                # Isolate the parts of the curve with a local minimum
                                middle_part1, tt_middle1 = secondary_deflection(dudt, t_points, sel_limits1[0], sel_limits1[1])
                                middle_part2, tt_middle2 = secondary_deflection(dudt, t_points, sel_limits2[0], sel_limits2[1])

                                # Calculate a fitted curve
                                polynomial1 = calc_polynomial(middle_part1, tt_middle1)
                                polynomial2 = calc_polynomial(middle_part2, tt_middle2)

                                # Find the local minimum
                                crit1 = polynomial1.deriv().r
                                r_crit1 = crit1[crit1.imag==0].real
                                test1 = polynomial1.deriv(2)(r_crit1)

                                crit2 = polynomial2.deriv().r
                                r_crit2 = crit2[crit2.imag==0].real
                                test2 = polynomial2.deriv(2)(r_crit2)

                                # Compute the local minima excluding range boundaries
                                x_min1 = r_crit1[test1>0]
                                y_min1 = polynomial1(x_min1)

                                x_min2 = r_crit2[test2>0]
                                y_min2 = polynomial2(x_min2)

                                fig3 = go.Figure()
                                fig3.add_trace(go.Scatter(
                                                    x=t_points,
                                                    y=dudt,
                                                    mode='lines+markers',
                                                    name="deflection rate",
                                                    showlegend=True)
                                        )

                                fig3.add_trace(go.Scatter(
                                                    x=x_min1,
                                                    y=y_min1,
                                                    mode='markers',
                                                    name="local minimum 1",
                                                    marker=dict(
                                                                color='MediumPurple',
                                                                size=12#,
                                                                # line=dict(
                                                                #     color='MediumPurple',
                                                                #     width=12
                                                                # )
                                                            ),
                                                            showlegend=True
                                                        )
                                                    )
                                
                                fig3.add_trace(go.Scatter(
                                                    x=x_min2,
                                                    y=y_min2,
                                                    mode='markers',
                                                    name="local minimum 2",
                                                    marker=dict(
                                                                color='mediumvioletred',
                                                                size=12#,
                                                                # line=dict(
                                                                #     color='MediumPurple',
                                                                #     width=12
                                                                # )
                                                            ),
                                                            showlegend=True
                                                        )
                                                    )
                                
                                # Add figure title
                                fig3.update_layout(title_text="Minimum deflection rate")

                                # Set axes titles
                                fig3.update_xaxes(title_text="Time [h]")
                                fig3.update_yaxes(title_text="Deflection rate [µm/h]")
                            else:
                                col2.text("")
                                col2.text("")
                                sel_limits = col2.slider("Select the bounds of the curve where the minimum is located", int(t_points[0]+1), int(t_points[len(t_points)-1]+1), value=(int(t_points[0]+1), int(t_points[len(t_points)-1]+1)))
                                # Isolate the middle part of the curve
                                middle_part, tt_middle = secondary_deflection(dudt, t_points, sel_limits[0], sel_limits[1])

                                # Calculate a fitted curve
                                polynomial = calc_polynomial(middle_part, tt_middle)

                                # Find the local minimum
                                crit = polynomial.deriv().r
                                r_crit = crit[crit.imag==0].real
                                test = polynomial.deriv(2)(r_crit)

                                # Compute the local minimum excluding range boundaries
                                x_min1 = r_crit[test>0]
                                y_min1 = polynomial(x_min1)

                                # Compute a curve based on the fitted poly
                                xc = np.arange(int(tt_middle[0]), int(tt_middle[len(tt_middle)-1]+1), 0.02)
                                yc = polynomial(xc)

                                fig3 = go.Figure()
                                fig3.add_trace(go.Scatter(
                                                    x=tt_middle,
                                                    y=middle_part,
                                                    mode='lines+markers',
                                                    name="deflection rate",
                                                    showlegend=True)
                                        )
                                
                                fig3.add_trace(go.Scatter(
                                                    x=xc,
                                                    y=yc,
                                                    mode='lines',
                                                    name="fitted curve",
                                                    line=dict(
                                                        color='mediumvioletred'
                                                    ),
                                                    showlegend=True)
                                        )

                                fig3.add_trace(go.Scatter(
                                                    x=x_min1,
                                                    y=y_min1,
                                                    mode='markers',
                                                    name="global minimum",
                                                    marker=dict(
                                                                color='MediumPurple',
                                                                size=12#,
                                                                # line=dict(
                                                                #     color='MediumPurple',
                                                                #     width=12
                                                                # )
                                                            ),
                                                            showlegend=True
                                                        )
                                                    )

                                # Add figure title
                                fig3.update_layout(title_text="Minimum deflection rate")

                                # Set axes titles
                                fig3.update_xaxes(title_text="Time [h]")
                                fig3.update_yaxes(title_text="Deflection rate [µm/h]")

                            col2.plotly_chart(fig3, use_container_width=True)

                        st.markdown(''' **<p class="big-font"> :blue[STEP 5:] Results </p>** ''', unsafe_allow_html=True)
                        
                        time1 = x_min1[0].copy()
                        u_rate_min1 = y_min1[0].copy()
                        u_at_u_rate_min1 = df_lim.u[(df_lim.TotalHours>=time1)].values[0]/1000  # in mm 
                        equiv_stress1 = (int(force)/(1.916*(u_at_u_rate_min1**0.6579)))  # in mpa 
                        equiv_strain1 = 0.3922*((u_rate_min1/1000)**1.191)    # u_rate_min1 in mm/h

                        if double_min == True:
                            try:
                                time2 = x_min2[0].copy()
                                u_rate_min2 = y_min2[0].copy()
                                u_at_u_rate_min2 = df_lim.u[(df_lim.TotalHours<=time2)].values[-1]/1000  # in mm
                                equiv_stress2 = (int(force)/(1.916*(u_at_u_rate_min2**0.6579)))  # in mpa
                                equiv_strain2 =  0.3922*((u_rate_min2/1000)**1.191)    # u_rate_min2 in mm/h

                                cols = ['Experiment', 'Temperature [°C]', 'Force [N]', 'Time to rupture [h]', 'Minimum delfection rate 1 [µm/h]', 'Time at minimum delfection rate 1 [h]', 'Deflection at minimum delfection rate 1 [mm]', 'Equivalent stress 1 [MPa]', 'Equivalent strain rate 1 [1/h]', 'Minimum delfection rate 2 [µm/h]', 'Time at minimum delfection rate 2 [h]', 'Deflection at minimum delfection rate 2 [mm]', 'Equivalent stress 2 [MPa]', 'Equivalent strain rate 2 [1/h]']
                                spc_matrix = pd.DataFrame(columns = cols)
                                spc_matrix.loc[len(spc_matrix)] = [selected_exp, temp, force, tR, u_rate_min1, time1, u_at_u_rate_min1, equiv_stress1, equiv_strain1, u_rate_min2, time2, u_at_u_rate_min2, equiv_stress2, equiv_strain2]
                                csv = spc_matrix.to_csv().encode('utf-8')
                                #st.markdown(''' <span style="text-decoration:underline"> Summary: </span> ''', unsafe_allow_html=True)

                                if 'final_table' not in st.session_state:
                                    st.session_state.final_table = False

                                def show_table():
                                    st.session_state.final_table = not st.session_state.final_table

                                st.button('Show/Hide table', on_click=show_table)
                                if st.session_state.final_table:
                                #if st.button("Show table", key='show_final_table'):
                                    st.table(spc_matrix)
                                    st.text("")

                                    if st.download_button(
                                                        label="Download",
                                                        data=csv,
                                                        file_name=f'streamlit_output.csv',
                                                        mime='text/csv'):
                                        st.balloons()
                            except IndexError:
                                st.markdown(":red[**Attention!!**] It was not possible to identify a second minimum. Try to further adjust the bounds.")
                        else:
                            cols = ['Experiment', 'Temperature [°C]', 'Force [N]', 'Time to rupture [h]', 'Minimum delfection rate [µm/h]', 'Time at minimum delfection rate [h]', 'Deflection at minimum delfection rate [mm]', 'Equivalent stress [MPa]', 'Equivalent strain rate [1/h]']
                            spc_matrix = pd.DataFrame(columns = cols)
                            spc_matrix.loc[len(spc_matrix)] = [selected_exp, temp, force, tR, u_rate_min1, time1, u_at_u_rate_min1, equiv_stress1, equiv_strain1]
                            csv = spc_matrix.to_csv().encode('utf-8')
                            #st.markdown(''' <span style="text-decoration:underline"> Summary: </span> ''', unsafe_allow_html=True)

                            if 'final_table' not in st.session_state:
                                st.session_state.final_table = False

                            def show_table():
                                st.session_state.final_table = not st.session_state.final_table

                            st.button('Show/Hide table', on_click=show_table)
                            if st.session_state.final_table:
                            #if st.button("Show table", key='show_final_table'):
                                st.table(spc_matrix)
                                st.text("")

                                if st.download_button(
                                                    label="Download",
                                                    data=csv,
                                                    file_name=f'streamlit_output.csv',
                                                    mime='text/csv'):
                                    st.balloons()
                    else:
                        st.markdown(":red[**Attention!!**] You haven't provided a path")
                else:
                    st.markdown(":red[**Attention!!**] You have selected the same column name as representative of different data. Revise your entries in the **Imports section** in order to continue.")
            else:
                st.markdown(":red[**Attention!!**] One or more of the representative column names have been left empty. Revise your entries in the **Imports section** in order to continue.")

    if (st.session_state.type_of_exp == "Uniaxial creep"):
        if ("select_uc_time_col" in st.session_state) & ("select_lvdt1_col" in st.session_state) & ("select_lvdt2_col" in st.session_state):
            if (st.session_state.select_uc_time_col != "") & (st.session_state.select_lvdt1_col != "") & (st.session_state.select_lvdt2_col != ""):
                if (st.session_state.select_uc_time_col != st.session_state.select_lvdt1_col) & (st.session_state.select_uc_time_col != st.session_state.select_lvdt2_col) & (st.session_state.select_lvdt1_col != st.session_state.select_lvdt2_col):
                    if (edit_table_file_input.empty != True):
                        ch1 = False
                        for metr in edit_table_file_input["Gauge length"]:
                            if metr == None:
                                ch1 = True
                        if ch1 == False:
                            col1, col2 = st.columns(2)
                            selected_exp = col1.radio(
                                "Choose the experiment you want to analyze",
                                names,
                                key='selected_exp'
                            )

                            df = all_dfs[selected_exp]
                            col1, col2 = st.columns(2)
                            stress = col1.number_input("Type in the **Stress** in MPa under which your experiment was performed", format="%0.1f")
                            temp = col2.number_input("Type in the **Temperature** in °C under which your experiment was performed", format="%0.1f")
                            
                            st.markdown(''' **<p class="big-font"> :blue[STEP 1:] Preprocessing/Cleaning of the strain data (if necessary)</p>** ''', unsafe_allow_html=True)
                            col1, col2 = st.columns([1, 2])
                            col1.text("")
                            col1.text("")
                            col1.markdown('''
                                Often we start logging the data before the full load has been applied.  
                                Also, often times the data acquisition continues even after the rupture of the specimen.  
                                As a result, the raw data present many invalid values at the beginning and the end of experiments.  
                                    
                                If this is the case, use the interactive tools of the graph on the right to zoom and hover over the datapoints and identify the point of the start of the experiment and the time to rupture.
                            ''')

                            # Remove NaN values from the selected LVDT
                            if df.lvdt1.isna().sum() > 0:
                                df = df.dropna(subset=['lvdt1'])
                                df.reset_index(inplace=True)
                                df = df.drop(columns=['index'])
                            if df.lvdt2.isna().sum() > 0:
                                df = df.dropna(subset=['lvdt2'])
                                df.reset_index(inplace=True)
                                df = df.drop(columns=['index'])                                

                            if all_lvdts_for_plot[selected_exp] == 'LVDT 1':
                                var = 'strain1'
                            elif all_lvdts_for_plot[selected_exp] == 'LVDT 2':
                                var = 'strain2' 
                            else:
                                var = 'strain_avg' 

                            fig_toclean = go.Figure()
                            fig_toclean.add_trace(go.Scatter(
                                                    x=df.TotalHours,
                                                    y=df[var],
                                                    mode='lines+markers',
                                                    name="strain uncleaned")
                                        )

                            fig_toclean.update_layout(title=dict(text="Creep strain curve"),
                                                xaxis_title="Time [h]", 
                                                yaxis_title="Strain [%]",
                                                showlegend=True)
                            col2.plotly_chart(fig_toclean, use_container_width=True)

                            stop_start = col1.number_input("Type the value of the identified (from the graph) time of initial strain (when the full load started being applied).", key='stop_start')
                            stop_end = col1.number_input("Type the value of the identified (from the graph) time to rupture.", key='stop_end')
                            #st.write(st.session_state)

                            if (stop_start != 0): 
                                if (stop_end > stop_start):
                                    df_lim = df[(df.TotalHours >= stop_start) & (df.TotalHours <= stop_end)]
                                    df_lim.reset_index(inplace=True)
                                    df_lim = df_lim.drop(columns=['index'])
                                    df_lim[var] = df_lim[var] - df_lim.loc[0, var]

                                    df_lim['TotalSeconds'] = df_lim['DateTime'].diff().dt.total_seconds().cumsum()       # Calculate the total amount of seconds since the start of the experimet
                                    df_lim.loc[0, 'TotalSeconds'] = 0
                                    df_lim['TotalSeconds'] = df_lim['TotalSeconds'].astype(int, errors='ignore')
                                    df_lim['TotalMinutes'] = df_lim['TotalSeconds']/60
                                    df_lim['TotalHours'] = df_lim['TotalSeconds']/3600

                                    tR = df_lim.TotalSeconds[len(df_lim)-1]
                                else:
                                    st.markdown(" :red[**Attention!!**] The time to rupture **cannot** precede the time of initial strain. You haven't entered the values correctly.")
                            else:
                                if (stop_end != 0):
                                    df_lim = df[:stop_end]
                                    df_lim.reset_index(inplace=True)
                                    df_lim = df_lim.drop(columns=['index'])

                                    tR = df_lim.TotalSeconds[len(df_lim)-1]
                                else:
                                    st.markdown("**No cleaning was performed.** The algorithm will proceed with the input data as is.")
                                    df_lim = df.copy()
                                    tR = df_lim.TotalSeconds[len(df_lim)-1]

                            t0 = 0                                

                            st.markdown(''' **<p class="big-font"> :blue[STEP 2:] Calculation of the strain rate </p>** ''', unsafe_allow_html=True)

                            col1, col2 = st.columns([1,2])
                        
                            col1.text("")
                            col1.text("")
                            
                            col1.markdown(''' 
                                        The current methodology splits the dataset into sections 
                                        and calculates the strain rate as the regression slope 
                                        of all the data points that fall into each section.
                                        ''')  
                            col1.markdown(''' <span style="text-decoration:underline"> Hint: </span> The suggested number of sections is **between 100 and 400**.''', unsafe_allow_html=True)

                            sections_num = col1.number_input("Type the number of sections", min_value=50, max_value=500, step=10, key="sections_to_split")

                            interval_points = (tR - t0)/int(sections_num)
                            col1.markdown("Each of the " + str(sections_num) + " sections contains " + str(math.floor(interval_points)) + " data points.")

                            dvardt, t_points, var_points = calculate_rate_of_variable(df_lim, var, interval_points, t0, tR)

                            fig1 = make_subplots(specs=[[{"secondary_y": True}]])
                            fig1.add_trace(go.Scatter(
                                                x=t_points,
                                                y=var_points,
                                                mode='lines+markers',
                                                name="strain"),
                                                secondary_y=False,
                                    )
                            
                            fig1.add_trace(go.Scatter(
                                                x=t_points,
                                                y=dvardt,
                                                mode='lines+markers',
                                                name="strain rate"),
                                                secondary_y=True,
                                            )

                            # Add figure title
                            fig1.update_layout(
                                title_text="Strain & strain rate")

                            # Set x-axis title
                            fig1.update_xaxes(title_text="Time [h]")

                            # Set y-axes titles
                            fig1.update_yaxes(title_text="Strain [%]", secondary_y=False)
                            fig1.update_yaxes(title_text="Strain rate [1/h]", secondary_y=True)

                            col2.plotly_chart(fig1, use_container_width=True)

                            def secondary_strain(str_rate, time, lower_limit, upper_limit):
                                tt_middle = []
                                middle_part = []
                                for i in range(len(time)):
                                    if (time[i]>=lower_limit) & (time[i]<=upper_limit):
                                        tt_middle.append(time[i])
                                        middle_part.append(str_rate[i])

                                return middle_part, tt_middle
                            
                            st.markdown(''' **<p class="big-font"> :blue[STEP 3:] Calculation of the minimum strain rate </p>** ''', unsafe_allow_html=True)
                            
                            col1, col2 = st.columns([1,2])
                            col1.text("")
                            col1.text("")
                            col1.markdown(''' <span style="text-decoration:underline"> Small description of the methodology </span> ''', unsafe_allow_html=True)
                            col1.markdown(''' 
                                        - First, a second degree polynomial curve is fitted to the datapoints of the strain rate.  
                                        - Then, the minimum strain rate is considered the same as the minimum point of the fitted curve, in order to reduce uncertainty due to the noise in the signal.  
                                            
                                        Actions to be taken:
                                        1. Observe and interact with the strain rate graph in STEP 2.
                                        2. Try to roughly isolate by eye the part of the curve where the minimum strain rate is located.  
                                        3. Move the sides of the slider so that they match the bounds (in terms of time) of the previously isolated part of the minimum.
                                        4. The graph depicts the identified minimum strain rate.  
                                            ''')

                            col2.text("")
                            col2.text("")
                            sel_limits = col2.slider("Select the bounds of the curve where the minimum is located", int(t_points[0]+1), int(t_points[len(t_points)-1]+1), value=(int(t_points[0]+1), int(t_points[len(t_points)-1]+1)))
                            # Isolate the middle part of the curve
                            middle_part, tt_middle = secondary_strain(dvardt, t_points, sel_limits[0], sel_limits[1])

                            # Calculate a fitted curve
                            polynomial = calc_polynomial(middle_part, tt_middle)

                            # Find the global minimum
                            crit = polynomial.deriv().r
                            r_crit = crit[crit.imag==0].real
                            test = polynomial.deriv(2)(r_crit)

                            # Compute the global minimum excluding range boundaries
                            x_min1 = r_crit[test>0]
                            y_min1 = polynomial(x_min1)

                            # Compute a curve based on the fitted poly
                            xc = np.arange(int(tt_middle[0]), int(tt_middle[len(tt_middle)-1]+1), 0.02)
                            yc = polynomial(xc)

                            fig3 = go.Figure()
                            fig3.add_trace(go.Scatter(
                                                x=tt_middle,
                                                y=middle_part,
                                                mode='lines+markers',
                                                name="strain rate",
                                                showlegend=True)
                                    )
                            
                            fig3.add_trace(go.Scatter(
                                                x=xc,
                                                y=yc,
                                                mode='lines',
                                                name="fitted curve",
                                                line=dict(
                                                    color='mediumvioletred'
                                                ),
                                                showlegend=True)
                                    )

                            fig3.add_trace(go.Scatter(
                                                x=x_min1,
                                                y=y_min1,
                                                mode='markers',
                                                name="minimum",
                                                marker=dict(
                                                            color='MediumPurple',
                                                            size=12#,
                                                            # line=dict(
                                                            #     color='MediumPurple',
                                                            #     width=12
                                                            # )
                                                        ),
                                                        showlegend=True
                                                    )
                                                )

                            # Add figure title
                            fig3.update_layout(title_text="Minimum strain rate")

                            # Set axes titles
                            fig3.update_xaxes(title_text="Time [h]")
                            fig3.update_yaxes(title_text="Strain rate [1/h]")

                            col2.plotly_chart(fig3, use_container_width=True)

                            st.markdown(''' **<p class="big-font"> :blue[STEP 4:] Results </p>** ''', unsafe_allow_html=True)
                            
                            time1 = x_min1[0].copy()
                            str_rate_min1 = y_min1[0].copy()
                            str_at_u_rate_min1 = df_lim[var][(df_lim.TotalHours>=time1)].values[0]/1000  # in mm 

                            cols = ['Experiment', 'Temperature [°C]', 'Stress [N]', 'Time to rupture [h]', 'Minimum strain rate [1/h]', 'Time at minimum strain rate [h]', 'Strain at minimum strain rate [%]']
                            uc_matrix = pd.DataFrame(columns = cols)
                            uc_matrix.loc[len(uc_matrix)] = [selected_exp, temp, stress, tR, str_rate_min1, time1, str_at_u_rate_min1]
                            csv = uc_matrix.to_csv().encode('utf-8')

                            if 'final_table' not in st.session_state:
                                st.session_state.final_table = False

                            def show_table():
                                st.session_state.final_table = not st.session_state.final_table

                            st.button('Show/Hide table', on_click=show_table)
                            if st.session_state.final_table:
                            #if st.button("Show table", key='show_final_table'):
                                st.table(uc_matrix)
                                st.text("")

                                if st.download_button(
                                                    label="Download",
                                                    data=csv,
                                                    file_name=f'streamlit_output.csv',
                                                    mime='text/csv'):
                                    st.balloons()
                        else:
                            st.markdown(":red[**Attention!!**] You haven't added information regarding the gauge length. Revise your entries in the **Imports section** in order to continue.")
                    else:
                        st.markdown(":red[**Attention!!**] You haven't provided a path")
                else:
                    st.markdown(":red[**Attention!!**] You have selected the same column name as representative of different data. Revise your entries in the **Imports section** in order to continue.")
            else:
                st.markdown(":red[**Attention!!**] One or more of the representative column names have been left empty. Revise your entries in the **Imports section** in order to continue.")
