
import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as pt
from pathlib import Path

current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
css_file = current_dir/"styles"/"main.css"


#Excel File for Region Population
excel_file = pd.read_excel("ph2022popdata.xlsx",engine='openpyxl')
Data = pd.DataFrame(excel_file)
age_ranges = ['0-4','5-9','10-14','15-19','20-24','25-29','30-34','35-39','40-44','45-49','50-54','55-59','60-64','65-69','70-74','75-79','80 and over']
Data["Age"] = pd.Categorical(Data["Age"], categories= age_ranges, ordered= True)
Data["Region"] = Data["Region"].replace('Cotabato (North Cotabato)','North Cotabato')
Data["Region"] = Data["Region"].replace('City of Isabela','Isabela')
Data["Region"] = Data["Region"].replace('Samar (Western Samar)','Western Samar')
Pop_Data = Data[~Data["Region"].str.contains('Region')]


#Excel File for Region Coordinates
Coor_Data = pd.read_excel("Coordinates.xlsx", engine='openpyxl')


#Merging the Data Sets
Grouped_Population = pd.DataFrame(Pop_Data.groupby("Region")[["Total"]].sum())
Grouped_Population.sort_values(by="Region",inplace=True,ascending=False)
Map_Data = Grouped_Population.merge(Coor_Data, how = 'left', on = 'Region')

Data_Selection = Pop_Data[["Region","Age","Male","Female"]].melt(id_vars=["Region","Age"],var_name="Gender",value_name="Pop Count")

scatter_plot_data = pd.DataFrame(Grouped_Population)
scatter_plot_data.reset_index(inplace=True)





#-----------------STREAMLIT SECTION---------------------

st.set_page_config(page_title="Data Visualizations",layout='wide')

#Injecting CSS styling
with open(css_file) as f:
    st.markdown("<style>{}</style>".format(f.read()),unsafe_allow_html=True)

##----Multi-Select-----
st.title("Python Programming for better Data Analysis")
st.write("---")
column1,column2 = st.columns((3,1))
with column1:
    st.header("Filtered DataFrame")
    st.dataframe(Pop_Data)
with column2:
    st.write("""
    The Data used in this visualization was taken 
    and filtered from the 2022 Population Census of 
    the Philippines (SOURCE::Philippine Statistics
    Authorithy). The data is categorized by ranges
    of ages and divided between Males and Females
    throughout the different regions.
    """)

options =  st.multiselect(
    "Select Region",
    sorted(Pop_Data["Region"].unique()),
    default= sorted(Pop_Data["Region"].unique())
)

select_hist = Data_Selection.query(
    "Region == @options"
)

select_scat = scatter_plot_data.query(
    "Region == @options"
)

col1, col2 = st.columns(2)

with col1:
    hist = pt.histogram(select_hist, x="Age", color="Gender", y="Pop Count", hover_data=select_hist.columns,
                        color_discrete_sequence=["blue", "red"])
    hist.update_layout(yaxis=dict(title="Total Population"),xaxis=dict(title="Age Range"))
    st.plotly_chart(hist)

with col2:
    scat = pt.scatter(select_scat, x="Total", y="Region", size="Total", color="Total",
                      color_continuous_scale="Viridis")
    scat.update_layout(yaxis=dict(title="Region"),xaxis=dict(title="Total Population"))
    st.plotly_chart(scat)





st.write("\n")
st.write("Pydeck Maped POPULATION DATA")
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/dark-v10',
    initial_view_state=pdk.ViewState(
        latitude= 13.6662,
        longitude= 123.327,
        zoom=5,
        pitch=60
    ),
    layers=[
        pdk.Layer(
            'ColumnLayer',
            data=Map_Data,
            get_position = ['lon','lat'],
            get_elevation = ["Total"],
            elevation_scale = .05,
            get_color = '[255,125,0]',
            radius = 5000,
            pickable = True,
            auto_highlight = True,
            tooltip ={"text":"Population : {Total}"}
        )
    ]
))