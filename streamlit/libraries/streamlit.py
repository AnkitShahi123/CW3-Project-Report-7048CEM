import streamlit as st
import pandas as pd
from hccpy.hcc import HCCEngine
from hccpy.hhshcc import HHSHCCEngine
import numpy as np
from snowflake.snowpark.session import Session
from snowflake.snowpark.context import get_active_session
import time
import json



st.set_page_config(layout="wide")
show_dataframe = False
selected_dataframe = None
selected_schema = None


session = get_active_session()




ELIGIBILITY_KEY = ["CFA-Community Full Benefit Dual Aged", 
               "CFD-Community Full Benefit Dual Disabled", 
               "CNA-Community NonDual Aged", 
               "CND-Community NonDual Disabled", 
               "CPA-Community Partial Benefit Dual Aged", 
               "CPD-Community Partial Benefit Dual Disabled", 
               "INS-Long Term Institutional", 
               "NE-New Enrollee", 
               "SNPNE-SNP NE"]
ELIGIBILITY_VALUES =["CFA","CFD","CNA","CND","CPA","CPD","INS","NE","SNPNE"]
ELIGIBILITY_MAPPING={"CFA-Community Full Benefit Dual Aged":"CFA", 
               "CFD-Community Full Benefit Dual Disabled":"CFD", 
               "CNA-Community NonDual Aged":"CNA", 
               "CND-Community NonDual Disabled":"CND", 
               "CPA-Community Partial Benefit Dual Aged":"CPA", 
               "CPD-Community Partial Benefit Dual Disabled":"CPD", 
               "INS-Long Term Institutional":"INS", 
               "NE-New Enrollee":"NE", 
               "SNPNE-SNP NE":"SNPNE"
                    }  
OREC_KEY = ["Old","Disability","End-state","Both DIB and ESRD"]
OREC_VALUES = ["0","1","2","3"]
OREC_MAPPING= {"Old":"0","Disability":"1","End-state":"2","Both DIB and ESRD":"3"}
SEX = ["M", "F"]
METALLIC_PLATE_KEY =["Platinum","Gold","Silver","Bronze","Catastrophic"]
METALLIC_PLATE_MAPPING = {"Platinum":"P",
                          "Gold":"G",
                          "Silver":"S",
                          "Bronze":"B",
                          "Catastrophic":"C"}

hcc_version_years = {
    22: [2017,2018,2019,2020,2021,2022],
    23:[2018,2019,"Combined"],
    24:[2019,2020,2021,2022,"Combined"],
    28:[2024,"Combined"],
    "ESRD":[2024,"Combined"]
}

options = []
for version, years in hcc_version_years.items():
    for year in years:
        options.append(f"{version}/{year}")


heading_prop= [('background','#76d0f1'),('font-size','16px'),('font-weight','bold')]
head_properties= [('font-size','16px'),('text-align','center'),('font-weight','bold'),('border','1.2px solid')]
cell_properties=[('border','1.2px solid')]
df_style = [{"selector":":has(th.col_heading) ","props":heading_prop},{"selector":"th","props":head_properties},{"selector":"td","props":cell_properties}]



beta1,beta2 = st.columns([10,1])

beta1.title("RISK ADJUSTMENT FACTOR (RAF) CALCULATOR")




individual_tab, tab2, tab3 = st.tabs([
    "Individual RAF Calculator ","Lookup for hypothetical RAF","Population RAF calculator"
])


with individual_tab:
    individual_col1, individual_col2 = st.columns([2.25,1])
    

    result = None
    result1 = None
    
    with individual_col1:
        
        
        c1 = st.container()
        c1.subheader("Instruction")
        c1.write("1. Modify the input parameters for RAF and click Run to observe the Risk Score and HCC List.")

        obj1 , obj2, obj3   = st.columns(3)
        
        
       

        
        individual_model = obj1.selectbox("Model", ["HCC", "HHS"], key="model_selectbox")
        if individual_model == "HCC":
            # individual_hcc_version = obj2.selectbox("Version", [22, 23, 24, 28, "ESRD"], key="version_selectbox")

            individual_hcc_model_dx2cc_year = obj2.selectbox("Version/DX2CC_Year",options, key="dx2cc_year_selectbox")
            individual_hcc_version =  individual_hcc_model_dx2cc_year.split('/')[0]
            individual_hcc_dx2cc_year = individual_hcc_model_dx2cc_year.split('/')[1]
            individual_hcc_dx_lst = st.text_input("DX List (comma-separated)",'A0103 , D701, B377', key="dx_lst_input")

            obj4 , obj5, obj6   = st.columns(3)
            individual_hcc_age = obj4.number_input("Age", min_value=0, key="age_input")
            individual_hcc_sex = obj5.selectbox("Sex", SEX, key="sex_selectbox")
            
            individual_hcc_elig = obj4.selectbox("Eligibility", ELIGIBILITY_KEY, key="elig_selectbox")
            individual_hcc_orec = obj5.selectbox("Original Medicare Eligibility Reason", OREC_KEY, key="orec_selectbox")
            individual_hcc_medicaid = st.checkbox("Is medicaid", ["TRUE", "FALSE"])

            if st.button(label = "Run"):
                dx_lst = individual_hcc_dx_lst.split(",")  
                engine = HCCEngine(str(individual_hcc_version), str(individual_hcc_dx2cc_year))
                result = engine.profile(dx_lst, individual_hcc_age, individual_hcc_sex, ELIGIBILITY_MAPPING[individual_hcc_elig], OREC_MAPPING[individual_hcc_orec], individual_hcc_medicaid)
                # individual_col2.write(individual_hcc_model_dx2cc_year)
                # individual_col2.write(individual_hcc_version)
                # individual_col2.write(individual_hcc_dx2cc_year)
                
                
                

        elif individual_model == "HHS":
            individual_hhs_myear = obj2.selectbox("Measurement Year", ["2019", "2022"])

            individual_hhs_dx_lst = st.text_input("DX List (comma-separated)","A0105")
            individual_hhs_pr_lst = st.text_input("PR List (comma-separated)","J0282")
            individual_hhs_rx_lst = st.text_input("RX List (comma-separated)","00002751017")

            obj7 , obj8, obj9   = st.columns(3)
            individual_hhs_age = obj7.number_input("Age", min_value=0)
            individual_hhs_sex = obj8.selectbox("Sex", ["M", "F"])
            individual_hhs_enroll_months = obj7.number_input("Enroll Months", min_value=0, max_value=13)
            individual_hhs_metallic_plate = obj8.selectbox("Metallic Plate Level", METALLIC_PLATE_KEY)

            if st.button(label = "Run"):
                dx_lst = individual_hhs_dx_lst.split(",")
                pr_lst = individual_hhs_pr_lst.split(",")
                rx_lst = individual_hhs_rx_lst.split(",")
                engine = HHSHCCEngine(individual_hhs_myear)
                result = engine.profile(dx_lst, pr_lst, rx_lst, individual_hhs_age, individual_hhs_sex, individual_hhs_enroll_months, METALLIC_PLATE_MAPPING[individual_hhs_metallic_plate])
                    



    with individual_col2:
        for _ in range(8):
            st.write(" ")
        
        if result is not None:
            
            risk_score_result = ({'Risk Score':result["risk_score"],'HCC List':[', '.join(result['hcc_lst']) if result["hcc_lst"] else "None"]})
            
            risk_score_df1 = pd.DataFrame(risk_score_result,index=["Summary"])
            
            
            
            risk_score_df2 = (risk_score_df1.T.style.set_table_styles(df_style))
            
             
            st.table(risk_score_df2)
            
            
            
            

with tab2:
    
    for k in ['searched']:
        if k not in st.session_state:
            st.session_state[k] = None
    hypothetical_col1, hypothetical_col2 = st.columns([2.25,1])

    @st.cache_data
    def get_data(subscriber_id):
        result1 = session.sql(
        """
        select *
        from risk_score_base_table
        """
        ).collect()
        df = pd.DataFrame(result1)
        df = df[df['SUBSCRIBER_ID'] == subscriber_id]
        return df

    
        
    with hypothetical_col1: 

        c2 = st.container()
        c2.subheader("Instruction")
        c2.write("""1. Input the subscriber id for which you wish to generate the Risk Score. \n 2. If the subscriber id is located in the Abacus Risk Score profile table: The associated parameters are populated.   \n 3. Modify the input parameters for RAF and click Calculate to observe the adjustments of the Risk Adjustment Factor.""")

        
        
        hypothetical_subscriber_id = st.text_input("Search by subscriber id", "R78451250")
        
        new_df = session.sql("""select * from platform_base_table""").collect()
        new_df1 = pd.DataFrame(new_df)
        
        new_df1 = new_df1[new_df1['SUBSCRIBER_ID'] == hypothetical_subscriber_id]
        data1 = new_df1.iloc[0]
        
        
 
        if st.button("Search") or st.session_state["searched"]:
            st.session_state["searched"] = True

            with st.spinner("Loading...."):
                time.sleep(1)
            
            
            df = get_data(hypothetical_subscriber_id)
            if not df.empty:
                data = df.iloc[0]
                
                obj7 , obj8 , obj9 = st.columns(3)
                model = obj7.selectbox("Model", ["HCC", "HHS"], key="test_selectbox")

                if individual_model == "HCC":
                    # version = obj8.selectbox("Version", [22, 23, 24, 28, "ESRD"])
                    hcc_model_dx2cc_year = obj8.selectbox("Version/DX2CC_Year",options, key="hypothetical_dx2cc_year_selectbox")
                    version =  hcc_model_dx2cc_year.split('/')[0]
                    dx2cc_year = hcc_model_dx2cc_year.split('/')[1]
                    
                    # dx2cc_year = obj9.selectbox("DX2CC Year",hypothetical_available_years )
                    
                    dx_lst = st.text_input("DX List (comma-separated)", data['DIAGNOSES'])

                    obj10, obj11, obj12 = st.columns(3)

                    age = obj10.number_input("Age",value= data['AGE'])
                    sex = obj11.selectbox("Sex",SEX, index =SEX.index(data['BASE_DEMOGRAPHIC_SEX']))
                    elig = obj10.selectbox("Eligibility", ELIGIBILITY_KEY, index=ELIGIBILITY_VALUES.index(data['ELIG']))
                    orec = obj11.selectbox("Original Medical Eligibility Reason", OREC_KEY, index= OREC_VALUES.index(data['OREC']))
                    medicaid = st.checkbox("Is medicaid?", data['MEDICAID'])

                    
                    risk_json = json.loads(data1['RISK_SCORE_JSON'])
                    current_risk_score = risk_json['risk_score']
                    current_hcc_list = [', '.join(risk_json['hcc_lst']) if risk_json["hcc_lst"] else "None"]
                    
                    current_model_year = risk_json['model']+"/2017"
                    risk_data = {'Risk score': current_risk_score,'HCC List': current_hcc_list, 'Model/Year':current_model_year,'Diagnoses':data1['DIAGNOSES']}
                    df_data = pd.DataFrame(risk_data, index =["Current Risk score"])
                    
                    for _ in range(12):
                        hypothetical_col2.write(" ")
                    hypothetical_col2.table(df_data.T.style.set_table_styles(df_style))

                    if st.button(label = "Calculate"):
                        dx_lst = dx_lst.split(",")  
                        engine = HCCEngine(str(version), str(dx2cc_year))
                        result1 = engine.profile(dx_lst, age, sex, ELIGIBILITY_MAPPING[elig], OREC_MAPPING[orec], medicaid)

                # elif individual_model == "HHS":  
                #     hhs_myear = obj8.selectbox("Select Measurement Year", ["2019", "2022"], key = "key_myyear")

                #     hhs_dx_lst = st.text_input("DX List (comma-separated)",data['DX_LST'])
                #     hhs_pr_lst = st.text_input("PR List (comma-separated)",data['PR_LST'])
                #     hhs_rx_lst = st.text_input("RX List (comma-separated)",data['RX_LST'])

                #     obj10 , obj11, obj12   = st.columns(3)
                #     hhs_age = obj10.number_input("Age", data['AGE'])
                #     hhs_sex = obj11.selectbox("Sex", SEX, index =SEX.index(data['SEX']))
                #     hhs_enroll_months = obj10.number_input("Enroll Months", ENROLL_MONTH, index =ENROLL_MONTH.index(data['ENROLL_MONTH']))
                #     hhs_metallic_plate = obj11.selectbox("Metallic Plate Level",METALLIC_PLATE, index =METALLIC_PLATE.index(data['METALLIC_PLATE']))
                        

    with hypothetical_col2:
        
        

        if result1 is not None: 
           
            hypothetical_risk_score = result1['risk_score']
            hypothetical_hcc_list = [', '.join(result1['hcc_lst']) if result1["hcc_lst"] else "None"]
             

            

            added_hcc = ', '.join(set(result1["hcc_lst"])- set(risk_json['hcc_lst']))
            subtracted_hcc = ', '.join(set(risk_json["hcc_lst"])- set(result1['hcc_lst']))
             
            added_diagnoses = ', '.join((set(dx_lst))- set([data1['DIAGNOSES']]))
            subtracted_diagnoses = ', '.join(set([data1['DIAGNOSES']])- (set(dx_lst)))
             

            risk_score_df = pd.DataFrame({'Risk Score':[hypothetical_risk_score],
                                          'HCC List':', '.join(result1['hcc_lst']) if result1["hcc_lst"] else "None",
                                          'Added Diagnoses':  [added_diagnoses] if added_diagnoses else "None"  ,
                                          'Subtracted Diagnoses': [subtracted_diagnoses] if subtracted_diagnoses else "None"  ,
                                          'Added HCC': [added_hcc] if added_hcc else "None"  ,
                                          'Subtracted HCC': [subtracted_hcc] if subtracted_hcc else "None" ,
                                          },index =["Hypothetical Risk Score"])
            st.table(risk_score_df.T.style.set_table_styles(df_style)) 

            
             

from snowflake.snowpark.functions import col 
    
with tab3:
    entire_col1, entire_col2 = st.columns([2.25,1])
    
    
    
    with entire_col1:
        c3 = st.container()
        c3.subheader("Instruction")
        c3.write("1. Calculation of the Risk Score for the entire population provided as input.")
        
        
        df1 = session.sql(
            """
            select *
            from risk_score_base_table
            """
        ).collect()
        df1 = pd.DataFrame(df1)
        
        
        obj7 , obj8 , obj9 = st.columns(3)

        entire_model = obj7.selectbox("Select Model", ["HCC", "HHS"], key="entire_model_selectbox")

        if entire_model == "HCC":
            entire_hcc_version = obj8.selectbox("Select Version", [22, 23, 24, 28, "ESRD"], key="entire_version_selectbox")
            entire_hcc_dx2cc_year = obj9.selectbox(
                "Select DX2CC Year",
                ["Combined", 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024], key="entire_dx2cc_year_selectbox")
            

            if st.button(label = "Run",key ="hcc_button"):
                engine = HCCEngine(str(entire_hcc_version), str(entire_hcc_dx2cc_year))
                df1["risk_score_json"] = df1.apply(
                    lambda x: engine.profile(
                        [i.strip() for i in x.DIAGNOSES.split(",")],
                        x.AGE,
                        x.BASE_DEMOGRAPHIC_SEX,
                        x.ELIG,
                        x.OREC,
                        x.MEDICAID
                        
                    ),
                    axis=1,
                )
                df1["riskscore"] = df1.apply(lambda x: x["risk_score_json"].get('risk_score'), axis=1)
                show_dataframe = True

        elif entire_model == "HHS":
            entire_hhs_myear = obj8.selectbox("Select Measurement Year", ["2019", "2022"])

            if st.button(label = "Run", key="hhs_button"):
                engine = HHSHCCEngine(str(entire_hhs_myear))
                df1['risk_score_json'] = df1.apply(
                    lambda x:engine.profile(
                        [i.strip() for i in x.DX_LST.split(",")],
                        [i.strip() for i in x.PR_LST.split(",")],
                        [i.strip() for i in x.RX_LST.split(",")],
                        x.AGE,
                        x.SEX,
                        x.ENROLL_MONTH,
                        x.METALLIC_PLATE 
                    ),axis =1
                )
                df1["riskscore"] = df1.apply(lambda x: x["risk_score_json"].get('risk_score'), axis=1)
                show_dataframe = True
        
   
        

    if show_dataframe:
        st.write(df1)
    


        
    