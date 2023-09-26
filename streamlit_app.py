import streamlit as st
import pandas as pd
import math
from PIL import Image
from streamlit_option_menu import option_menu
import plotly.express as px
from snowflake.snowpark import Session
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np
from snowflake.snowpark.functions import avg, sum, col, lit
from config import connection_parameters
st.set_page_config(page_title="Lending AI",layout="wide",initial_sidebar_state="expanded")
session=Session.builder.configs(connection_parameters).create()
col1,col2=st.columns(2)
image = Image.open('LendingAI.png')
st.image(image, width=250)
selected_opt  = option_menu(None, ["Predictor App" ,"Defaulter App","Recommendation App","Segmentation",'Applications Data','Churn Data','Defaulter Data'],  
default_index=0, orientation="horizontal",icons=None,
                menu_icon=None,
                styles={              
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                # "icon": {"color": "orange", "font-size": "25px"},
                "icon":{"display":"none"},
                "nav": {"background-color":"#f2f5f9"},
                "nav-link": {"font-size": "10px",
                "font-weight":"bold",
                "color":"#1d1160",
                "border-right":"2px solid #4B0082",
                "border-left":"1.5px solid #4B0082",
                "border-top":"1.5px solid #4B0082",
                "border-bottom":"1.5px solid #4B0082",
                "padding":"10px",
                "text-transform": "uppercase",
                "border-radius":"1px",
                "margin":"1px",
                "--hover-color": "#e1e1e1"},
                "nav-link-selected": {"background-color":"#1d1160", "color":"#ffffff"},
                })
if selected_opt == 'Predictor App':
    col1, col2=st.columns([3.2,6.8])
    with col1:
            employment_length = st.selectbox('Experience:', ['< 1 year', '1 year', '2 years', '3 years', '4 years', '5 years', '6 years', '7 years', '8 years', '9 years', '10+ years'])
            loan_title = st.selectbox('Type of Loan:', ['Major purchase', 'Debt consolidation', 'Home improvement', 'Moving and relocation', 'Home buying', 'Business', 'Vacation', 'Car financing', 'Medical expenses', 'Credit card refinancing'])
            age = st.selectbox('Age:', ['< 18', '18-24', '25-34', '35-44', '45-54', '55-64', '65+'])
            amount_requested = st.number_input('Loan Amount:', min_value=0,value=1000)
            tenure = st.selectbox('Loan Repayment Tenure:', ['36 Months','60 Months'])
            btn=st.button("Predict")
    with col2:
        if btn:
            lst = [480, 50, employment_length,loan_title,amount_requested]
            df = pd.DataFrame([lst], columns=['RISK_SCORE','DEBT_TO_INCOME_RATIO','EMPLOYMENT_LENGTH', 'LOAN_TITLE','AMOUNT_REQUESTED'])
            snow_df = session.create_dataframe(df)
            snow_df.write.mode("overwrite").saveAsTable("LENDINGAI_DB.BASE.TBL_APPLICATIONSCORE_VALIDATION_DS_SNOWPARK")
            res = session.call('LENDINGAI_DB.MART.SP_APPLICATIONSCORE_LR_VALIDATIONPROC_SNOWPARK')
            probability_of_approval = math.floor(float(res[18:20] + '.' + res[21]))
            probability_of_rejection = math.ceil(float(res[7:9] + '.' + res[11]))
            fig = px.bar(
                x=['Approved', 'Rejected'],
                y=[probability_of_approval, probability_of_rejection],
                color=['Approved', 'Rejected'],  
                color_discrete_map={'Approved': '#00A300', 'Rejected': '#FF4500'},
                labels={'x': 'Loan', 'y': 'Probability'}
            )
            fig.update_traces(marker_line_color='black', marker_line_width=1,hovertemplate=None)
            for i in range(2):
                fig.add_annotation(
                            x=['Approved', 'Rejected'][i],
                            y=[probability_of_approval, probability_of_rejection][i]+2,
                            text=f'{[probability_of_approval, probability_of_rejection][i]}%',
                            showarrow=False,
                            font=dict(size=14, color='black'),
                            align='center',
                            valign='bottom' if [probability_of_approval, probability_of_rejection][i] > 50 else 'top',
                        )
            st.write("")
            st.markdown("<center><b>Probability of Loan Approval</b></center>",unsafe_allow_html=True)
            st.plotly_chart(fig,use_container_width=True)
if selected_opt =='Defaulter App':
    col1, col2=st.columns([2.8,7.2])
    with col1:
            loan_amnt = st.number_input('Loan Amount:',value=10000)
            home_ownership = st.selectbox('Home Ownership:',('OWN', 'RENT', 'MORTGAGE','ANY'))
            annual_income = st.number_input('Annnual Income:', value=120000)
            loan_type = st.selectbox('Type of Loan:',
            ('Credit card refinancing','Debt consolidation','Home improvement','Major purchase','Business','Medical expenses','Moving and relocation','Vacation','Home buying','Green loan','Car financing','Other'))
            int_rate=st.number_input('Interest Rate:',value=10)
            credit_score=st.number_input('Credit Score:',value=0)
            term = st.radio("Loan Repayment Term:",["36 months", "60 months"],horizontal=True)
            Employee_Expe = ["< 1 year","2 years","3 years","4 years","5 years","6 years","7 years","8 years","9 years","10+ years"]
            emp_lengt = st.select_slider('Experience:', options=Employee_Expe)
            btn=st.button("Check")
    def is_valid_data2(credit_score,loan_amnt,annual_income,int_rate):
        if(0<=credit_score<=900  and loan_amnt>=0 and annual_income>=0 and int_rate>=0):
            return True
        return False  
    with col2:
        if btn:
            if is_valid_data2(credit_score,loan_amnt,annual_income,int_rate):
                if credit_score==0:
                    risk_score=596
                    if int_rate>20:
                        risk_score+=80
                    elif 15<=int_rate<20:
                        risk_score+=60
                    elif 10<=int_rate<15:
                        risk_score+=30
                    elif 5<=int_rate<10:
                        risk_score+=10
                else:
                    risk_score=credit_score
                lst=[emp_lengt,int_rate,float(loan_amnt),term,home_ownership,float(annual_income),loan_type,risk_score]
                df=pd.DataFrame([lst],columns=['EMP_LENGTH', 'INT_RATE', 'LOAN_AMNT', 'TERM', 'HOME_OWNERSHIP', 'ANNUAL_INC', 'TITLE','RISK_SCORE'])
                snow_df=session.create_dataframe(df)
                snow_df.write.mode("overwrite").saveAsTable("LENDINGAI_DB.BASE.TBL_DEFAULTER_VALIDATION_DS")
                res=session.call('LENDINGAI_DB.MART.SP_DEFAULTER_VALIDATION_PROC')
                probability_of_nondefaulter,probability_of_defaulter=math.floor(float(res[7:9]+'.'+res[11])), math.ceil(float(res[18:20]+'.'+res[21]))
                fig = px.bar(                                     
                    x=['No', 'Yes'],
                    y=[probability_of_nondefaulter, probability_of_defaulter],
                    color=['No','Yes'],
                    color_discrete_map = {'Yes': '#00A300', 'No': '#FF4500'},
                    labels={'x': 'Defaulter', 'y': 'Probability'})
                fig.update_traces(marker_line_color='black', marker_line_width=1,hovertemplate=None)
                fig.update_layout(title_text='Probability of Customer Defaulter',width=500)
                for _ in range(6):
                    st.write("")
                st.plotly_chart(fig,use_container_width=True)
                features=res[28:93].split(',')
                features[0]=features[0][1:]
                features[-1]=features[-1][:-1]
                importances=res[93:].split(',')
                importances[0]=importances[0][1:]
                importances[-1]=importances[-1][:-1]
                df=pd.DataFrame(list(zip(features,importances)),columns=['Features','Importance'])
                fig = px.bar(df, x="Importance", y="Features", orientation='h')
                fig.update_traces(marker_line_color='black', marker_line_width=1,hovertemplate=None)
                fig.update_layout(title_text='Top 5 Features Influencing Prediction',width=500)
                fig.update_layout(yaxis=dict(autorange="reversed"))
                for _ in range(6):
                    st.write("")
                st.plotly_chart(fig,use_container_width=True)
            else:
                st.error("Entered Invalid data, Please check your Inputs...")
if selected_opt == 'Applications Data':
    res = session.call('LENDINGAI_DB.MART.SP_APPLICATIONSCORE_LR_VALIDATIONPROC_SNOWPARK')
    col1, col2, col3 = st.columns(3)
    with col1:
        emp_length = st.selectbox("Experience:", ['< 1 year', '1 year', '2 years', '3 years', '4 years', '5 years', '6 years', '7 years', '8 years', '9 years', '10+ years'], key="emp_length")
        debt_to_income_ratio = st.number_input('DTI Ratio:', min_value=0.0, key="debt_to_income_ratio")
    with col2:
        amount_requested = st.number_input('Loan Amount:', min_value=0, key="amount_requested")
        loan_title = st.selectbox('Type of Loan:', ['Major purchase', 'Debt consolidation', 'Home improvement', 'Moving and relocation', 'Home buying', 'Business', 'Vacation', 'Car financing', 'Medical expenses', 'Credit card refinancing'], key="loan_title")
    with col3:
        risk_score = st.number_input('Credit Score:', min_value=0, key="risk_score")
        application_status = st.selectbox("Select the application status", ['Approved', 'Rejected','Both'], key="application_status")
    col4,col5=st.columns(2)
    with col4:
        age = st.selectbox('Age:', ['0-18', '18-24', '25-34', '35-44', '45-54', '55-64', '65+'])
    with col5:
        tenure = st.selectbox('Loan Repayment Tenure:', ['36 Months','60 Months'])
    # Predict
    if risk_score == 0:  # assuming default value of the input is 0 when nothing is entered
        risk_score = 624
    if debt_to_income_ratio >= 500:
        risk_score += 10
    elif debt_to_income_ratio >= 200:
        risk_score += 20
    elif debt_to_income_ratio >= 100:
        risk_score += 30
    elif debt_to_income_ratio >= 50:
        risk_score += 50
    elif debt_to_income_ratio >= 20:
        risk_score += 60
    elif debt_to_income_ratio >= 10:
        risk_score += 70
    else:
        risk_score += 80
    risk_score += debt_to_income_ratio
    def is_valid_data(risk_score, amount_requested):
        if (0 <= risk_score <= 1000 and amount_requested >= 0):
            return True
        return False
    col11,col12,col13,col14,col15=st.columns(5)
    with col13:
        for _ in range(2):
            st.write("")
        btn4=st.button('Retrieve Related Applications',key='button_cntr2')
    if btn4:
        if is_valid_data(risk_score, amount_requested):
            lst = [risk_score, debt_to_income_ratio,emp_length,loan_title,amount_requested]
            df = pd.DataFrame([lst], columns=['RISK_SCORE','DEBT_TO_INCOME_RATIO','EMPLOYMENT_LENGTH','LOAN_TITLE','AMOUNT_REQUESTED'])
            snow_df = session.create_dataframe(df)
            snow_df.write.mode("overwrite").saveAsTable("LENDINGAI_DB.BASE.TBL_APPLICATIONSCORE_APPLICATIONS_SNOWPARK")
            res1 = session.sql('CALL LENDINGAI_DB.BASE.SP_APPLICATIONSCORE_APPLICANTIONS_SNOWPARK()').collect()
            app_df = pd.DataFrame(res1)
        if application_status == "Approved":
            app_df = app_df[app_df['APPLICATION_STATUS'] == 1]
        elif application_status == "Rejected":
            app_df = app_df[app_df['APPLICATION_STATUS'] == 0]
        elif application_status == "Both":
             app_df = app_df[(app_df['APPLICATION_STATUS'] == 1) | (app_df['APPLICATION_STATUS'] == 0)]
        final_appscore_df = app_df[['RISK_SCORE','DEBT_TO_INCOME_RATIO','EMPLOYMENT_LENGTH','LOAN_TITLE','AMOUNT_REQUESTED']]
        fig2 = go.Figure(data=[go.Table(
                columnwidth=[2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5],
                header=dict(
                    values=["<b>EMPLOYMENT LENGTH</b>", "<b>DEBT TO INCOME RATIO</b>", "<b>AMOUNT REQUESTED</b>", "<b>LOAN TITLE</b>", "<b>CREDIT SCORE</b>"],
                    fill_color='#CDCDD6',
                    font_color="#4C4C54",
                    align=['center'],
                    line_color='#ffffff',
                    font_size=14,
                    height=40
                ),
                cells=dict(values=[final_appscore_df.EMPLOYMENT_LENGTH,final_appscore_df.DEBT_TO_INCOME_RATIO,final_appscore_df.AMOUNT_REQUESTED,final_appscore_df.LOAN_TITLE,final_appscore_df.RISK_SCORE],fill_color = [['white','#f0f2f6']*3200], align=['center'], font_size = 12))])
                # Update the layout of the Plotly table
        fig2.update_layout(
                    autosize=False,
                    width=1400,
                    height=400,
                    margin=dict(l=0, r=0, b=0, t=0, pad=4),
                    paper_bgcolor="#ffffff"
                )
        st.subheader("List of Applications")
        st.plotly_chart(fig2)
if selected_opt =='Churn Data':
    col1, col2 ,col3= st.columns(3)
    with col1:
      loan_amnt = st.number_input('Loan Amount:',value=10000)
      st.write("")
      home_ownership = st.selectbox('Type of Home Ownership:',
    ('OWN', 'RENT', 'MORTGAGE','ANY'))
      st.write("")
      term = st.radio(
    "Loan Repayment Term:",
    ["36 months", "60 months"])
    with col2:
      annual_income = st.number_input('Annual Income:', value=120000)
      st.write("")
      loan_type = st.selectbox('Type of Loan:',
      ('Credit card refinancing','Debt consolidation','Home improvement','Major purchase','Business','Medical expenses','Moving and relocation','Vacation','Home buying','Green loan','Car financing','Other'))
      st.write("")
      Employee_Exp = ["< 1 year","2 years","3 years","4 years","5 years","6 years","7 years","8 years","9 years","10+ years"]
      emp_length = st.select_slider("Experience:", options=Employee_Exp)
    with col3:
      int_rate=st.number_input('Interest Rate:',value=10)
      st.write("")
      credit_score=st.number_input('Credit Score (Optional)',value=0)
      st.write("")
      appln_type = st.selectbox('Select preferred application data for retrievel:',
      ('None','Retrieve Churned Applications ','Retrieve Retained Applications','Retrieve Both Applications'))
    col11,col12,col13,col14,col15,col16,col17,col18,col19=st.columns(9)
    with col15:
        for _ in range(2):
            st.write("")
        btn1=st.button('Get Data',key='button_cntr6')
    def is_valid_data(credit_score,loan_amnt,annual_income,int_rate):
        if(0<=credit_score<=900  and loan_amnt>=0 and annual_income>=0 and int_rate>=0):
            return True
        return False  
    if btn1:
        if is_valid_data(credit_score,loan_amnt,annual_income,int_rate):
            if credit_score==0:
                risk_score=602
                if int_rate>20:
                    risk_score+=80
                elif 15<=int_rate<20:
                    risk_score+=60
                elif 10<=int_rate<15:
                    risk_score+=30
                elif 5<=int_rate<10:
                    risk_score+=10
            else:
                risk_score=credit_score
            lst=[emp_length,int_rate,float(loan_amnt),term,home_ownership,float(annual_income),loan_type,risk_score]
            df=pd.DataFrame([lst],columns=['EMP_LENGTH', 'INT_RATE', 'LOAN_AMNT', 'TERM', 'HOME_OWNERSHIP', 'ANNUAL_INC', 'TITLE','RISK_SCORE'])
            snow_df=session.create_dataframe(df)
            snow_df.write.mode("overwrite").saveAsTable("LENDINGAI_DB.BASE.TBL_CHURN_VALIDATION_DS")
            res=session.call('LENDINGAI_DB.MART.SP_CHURN_VALIDATION_PROC')
            churn_or_not=res[1]
            with col15:
                st.write("")    
                if churn_or_not=='0':
                    st.success("Churn likelihood: No")
                else:
                    st.warning("Churn likelihood: Yes")
            if appln_type== 'None':
                st.write("")
            elif appln_type=='Retrieve Churned Applications ':
                res=session.sql('CALL LENDINGAI_DB.BASE.SP_CHURN_APPLICATIONS()').collect()
                df=pd.DataFrame(res)
                churned_df=df[df['LOAN_STATUS_BIN']==1]
                final_churned_df=churned_df[['EMP_LENGTH', 'INT_RATE', 'LOAN_AMNT', 'TERM', 'HOME_OWNERSHIP', 'ANNUAL_INC', 'TITLE','RISK_SCORE']]
                fig2 = go.Figure(data=[go.Table(
                columnwidth=[2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5],
                header=dict(
                    values=["<b>EMP_LENGTH</b>", "<b>INT_RATE</b>", "<b>LOAN_AMNT</b>", "<b>TERM</b>", "<b>HOME_OWNERSHIP</b>","<b>ANNUL_INC</b>", "<b>TITLE</b>","<b>CREDIT SCORE</b>"],
                    fill_color='#CDCDD6',
                    font_color="#4C4C54",
                    align=['center'],
                    line_color='#ffffff',
                    font_size=14,
                    height=40
                ),
                cells=dict(values=[final_churned_df.EMP_LENGTH,final_churned_df.INT_RATE,final_churned_df.LOAN_AMNT,final_churned_df.TERM,final_churned_df.HOME_OWNERSHIP,final_churned_df.ANNUAL_INC,final_churned_df.TITLE,final_churned_df.RISK_SCORE],fill_color = [['white','#f0f2f6']*3200], align=['center'], font_size = 12))])
                # Update the layout of the Plotly table
                fig2.update_layout(
                    autosize=False,
                    width=1400,
                    height=400,
                    margin=dict(l=0, r=0, b=0, t=0, pad=4),
                    paper_bgcolor="#ffffff"
                )
                st.subheader("List of Churned Applications")
                st.plotly_chart(fig2)
            elif appln_type == 'Retrieve Retained Applications':
                res=session.sql('CALL LENDINGAI_DB.BASE.SP_CHURN_APPLICATIONS()').collect()
                df=pd.DataFrame(res)
                churned_df=df[df['LOAN_STATUS_BIN']==0]
                final_churned_df=churned_df[['EMP_LENGTH', 'INT_RATE', 'LOAN_AMNT', 'TERM', 'HOME_OWNERSHIP', 'ANNUAL_INC', 'TITLE','RISK_SCORE']]
                fig3 = go.Figure(data=[go.Table(
                columnwidth=[2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5],
                header=dict(
                    values=["<b>EMP_LENGTH</b>", "<b>INT_RATE</b>", "<b>LOAN_AMNT</b>", "<b>TERM</b>", "<b>HOME_OWNERSHIP</b>","<b>ANNUL_INC</b>", "<b>TITLE</b>","<b>CREDIT SCORE</b>"],
                    fill_color='#CDCDD6',
                    font_color="#4C4C54",
                    align=['center'],
                    line_color='#ffffff',
                    font_size=14,
                    height=40
                ),
                cells=dict(values=[final_churned_df.EMP_LENGTH,final_churned_df.INT_RATE,final_churned_df.LOAN_AMNT,final_churned_df.TERM,final_churned_df.HOME_OWNERSHIP,final_churned_df.ANNUAL_INC,final_churned_df.TITLE,final_churned_df.RISK_SCORE],fill_color = [['white','#f0f2f6']*3200], align=['center'], font_size = 12))])
                # Update the layout of the Plotly table
                fig3.update_layout(
                    autosize=False,
                    width=1400,
                    height=400,
                    margin=dict(l=0, r=0, b=0, t=0, pad=4),
                    paper_bgcolor="#ffffff"
                )
                st.subheader("List of Retained Applications")
                st.plotly_chart(fig3)
            elif appln_type == 'Retrieve Both Applications':
                res=session.sql('CALL LENDINGAI_DB.BASE.SP_CHURN_APPLICATIONS()').collect()
                churned_df=pd.DataFrame(res)
                final_churned_df=churned_df[['EMP_LENGTH', 'INT_RATE', 'LOAN_AMNT', 'TERM', 'HOME_OWNERSHIP', 'ANNUAL_INC', 'TITLE','RISK_SCORE']]
                fig4 = go.Figure(data=[go.Table(
                columnwidth=[2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5],
                header=dict(
                    values=["<b>EMP_LENGTH</b>", "<b>INT_RATE</b>", "<b>LOAN_AMNT</b>", "<b>TERM</b>", "<b>HOME_OWNERSHIP</b>","<b>ANNUL_INC</b>", "<b>TITLE</b>","<b>CREDIT SCORE</b>"],
                    fill_color='#CDCDD6',
                    font_color="#4C4C54",
                    align=['center'],
                    line_color='#ffffff',
                    font_size=14,
                    height=40
                ),
                cells=dict(values=[final_churned_df.EMP_LENGTH,final_churned_df.INT_RATE,final_churned_df.LOAN_AMNT,final_churned_df.TERM,final_churned_df.HOME_OWNERSHIP,final_churned_df.ANNUAL_INC,final_churned_df.TITLE,final_churned_df.RISK_SCORE],fill_color = [['white','#f0f2f6']*3200], align=['center'], font_size = 12))])
                # Update the layout of the Plotly table
                fig4.update_layout(
                    autosize=False,
                    width=1400,
                    height=400,
                    margin=dict(l=0, r=0, b=0, t=0, pad=4),
                    paper_bgcolor="#ffffff"
                )
                st.subheader("List of Both Churned and Retained Applications")
                st.plotly_chart(fig4)
        else:
            st.error("Entered Invalid data, Please check your Inputs...")
