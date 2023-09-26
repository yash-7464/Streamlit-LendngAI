transform_df = session.table( 'LENDINGAI_DB.BASE.TBL_ID_TABLE')

    # Convert Snowflake DataFrames to pandas DataFrames

    trans_id_data = transform_df.to_pandas()

    data=trans_id_data['id'].iloc[:20000]

    col1,col2,col3=st.columns(3)

    with col2:

            # Create the dropdown

            st.write("Select Application ID:")

            selected_id = st.selectbox("", data)

            # Define a CSS style for the dropdown

        # Filter the DataFrame based on the selected "ID"

            filtered_df = trans_id_data[trans_id_data['id'] == selected_id]

            # Display "EMP_TITLE" values based on the selected "ID"

    col4, col5, col6 = st.columns(3)

    with col4:

            st.write("")

            st.write("Occupation of Employee:")

            st.success(filtered_df['EMP_TITLE'].values[0])

            # Display "TITLE" values based on the selected "ID"

    with col5:

            st.write("")

            st.write("Current Loan:")

            st.success(filtered_df['TITLE'].values[0])

            # Display "LOAN_AMNT" values based on the selected "ID"

    with col6:

            st.write("")

            st.write("Loan Amount:")

            st.success(filtered_df['LOAN_AMNT'].values[0])

    filtered_titles = filtered_df['TITLE'].tolist()

            #selected_title = col1.selectbox("Select title", filtered_titles)

    INPUT_LIST = [filtered_titles]

    INPUT_PRODUCT= filtered_titles

                #snowflake_array = snowflake_session.to_array(INPUT_PRODUCT)

    snowflake_array=','.join(map(str, INPUT_PRODUCT))

    k=session.call('LENDINGAI_DB.BASE.SP_RECOMMENDER',snowflake_array)

    arr=k.split(',')

    loans=["Business","Medical expenses","Major purchase","Learning and training","Credit card refinancing","Debt consolidation","Car financing","Vacation","Moving and relocation","Green loans","Home improvement","Home buying"]

    loan_images=["business_loan.jpg","medical_expenses_loan.jpg","major_purchase_loan.jpg","learning_loan.jpg","credit_card_refinancing.jpg","debt_consolidation.png","car_financing_loan.png","vacation_loan.png","moving_loan.png","green_loan.jpg","home_improvement.jpg","home_buying_loan.png"]

    imgs=dict(zip(loans,loan_images))

    if len(arr)==2:

        arr[0]=arr[0][:-1]

        arr[1]=arr[1][2:]

        res=arr

        with col5:

            st.write("")

            st.write("Recommended Loan(s):")

            colr1,colr2=st.columns(2)

            with colr1:

                st.markdown("<center><b>{}</b></center>".format(res[0]),unsafe_allow_html=True)

                st.image(imgs[res[0]])

            with colr2:

                st.markdown("<center><b>{}</b></center>".format(res[1]),unsafe_allow_html=True)

                st.image(imgs[res[1]])

    elif len(arr)==1:

        res=arr

        with col5:

            st.write("")

            st.write("Recommended Loan(s):")

            col11,col12,col13=st.columns([1,3,1])

            with col12:

                st.markdown("<center><b>{}</b></center>".format(res[0]),unsafe_allow_html=True)

                st.image(imgs[res[0]])
