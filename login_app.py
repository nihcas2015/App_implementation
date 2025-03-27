import streamlit as st
import hashlib
import os
import json
from datetime import datetime
import uuid
import pdfplumber
import pandas as pd
from io import BytesIO  # Add this import at the top
import matplotlib.pyplot as plt
import seaborn as sns
from transaction_categorizer import TransactionCategorizer
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini AI
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    # Initialize the model
    gemini_model = genai.GenerativeModel('gemini-2.0-flash')
else:
    gemini_model = None
    st.warning("Financial advice features will not be available.")

class MobileAuthApp:
    def __init__(self):
        # Initialize session state variables
        if 'page' not in st.session_state:
            st.session_state.page = 'login'
        
        # User credentials file
        self.credentials_file = 'user_credentials.txt'
        
        # PDF upload directory
        self.upload_dir = 'uploaded_pdfs'
        os.makedirs(self.upload_dir, exist_ok=True)
        
        # PDF metadata file
        self.pdf_metadata_file = 'pdf_metadata.json'
        if not os.path.exists(self.pdf_metadata_file):
            with open(self.pdf_metadata_file, 'w') as f:
                json.dump({}, f)
        
        # Initialize transaction categorizer
        model_path = os.path.join(os.path.dirname(__file__), 'transaction_categorizer_model.pkl')
        preprocessor_path = os.path.join(os.path.dirname(__file__), 'transaction_preprocessor.pkl')
        self.transaction_categorizer = TransactionCategorizer(model_path if os.path.exists(model_path) else None, 
                                                            preprocessor_path if os.path.exists(preprocessor_path) else None)
        
        # Custom CSS for dark-themed mobile-like design
        self.apply_custom_css()
    
    def apply_custom_css(self):
        st.markdown("""
        <style>
        :root {
            /* Dark theme color palette */
            --bg-primary: #121212;
            --bg-secondary: #1E1E1E;
            --text-primary: #E0E0E0;
            --text-secondary: #B0B0B0;
            --accent-primary: #BB86FC;
            --accent-secondary: #03DAC6;
        }
        
        .stApp {
            max-width: 400px;
            margin: 0 auto;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            height: 100vh;
        }
        
        /* Override Streamlit default styles */
        .stTextInput > div > div > input {
            background-color: var(--bg-secondary) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--accent-primary) !important;
            border-radius: 10px;
            height: 50px;
            padding: 0 15px;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: var(--accent-secondary) !important;
            box-shadow: 0 0 5px rgba(187, 134, 252, 0.5);
        }
        
        .stButton > button {
            background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%) !important;
            color: var(--bg-primary) !important;
            font-weight: bold;
            border-radius: 25px;
            height: 50px;
            width: 100%;
            border: none;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            opacity: 0.9 !important;
            transform: scale(1.02);
        }
        
        .login-container {
            background-color: var(--bg-secondary);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 8px 15px rgba(0,0,0,0.2);
        }
        
        /* Custom link styles */
        a {
            color: var(--accent-secondary);
            text-decoration: none;
            transition: color 0.3s ease;
        }
        
        a:hover {
            color: var(--accent-primary);
            text-decoration: underline;
        }
        
        /* Error and success message styles */
        .stAlert-error {
            background-color: rgba(255, 23, 68, 0.1);
            color: #FF1744;
            border-left: 4px solid #FF1744;
        }
        
        .stAlert-success {
            background-color: rgba(0, 230, 118, 0.1);
            color: #00E676;
            border-left: 4px solid #00E676;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def hash_credentials(self, username, password):
        """
        Convert username and password to SHA-256 hash
        """
        # Combine username and password before hashing
        combined = f"{username}:{password}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def save_credentials(self, name, client_id, username, password):
        """
        Save user credentials to a text file
        """
        hashed_credentials = self.hash_credentials(username, password)
        
        # Check if credentials already exist
        if self.check_credentials_exist(hashed_credentials):
            return False
        
        # Append new credentials to file
        with open(self.credentials_file, 'a') as f:
            # Format: hashed_credentials,name,client_id,username
            f.write(f"{hashed_credentials},{name},{client_id},{username}\n")
        
        return True
    
    def check_credentials_exist(self, hashed_credentials):
        """
        Check if hashed credentials already exist in the file
        """
        if not os.path.exists(self.credentials_file):
            return False
        
        with open(self.credentials_file, 'r') as f:
            for line in f:
                if line.startswith(hashed_credentials):
                    return True
        
        return False
    
    def validate_login(self, username, password):
        """
        Validate user login credentials
        """
        hashed_credentials = self.hash_credentials(username, password)
        
        if not os.path.exists(self.credentials_file):
            return False
        
        with open(self.credentials_file, 'r') as f:
            for line in f:
                if line.startswith(hashed_credentials):
                    return True
        
        return False
    
    def login_page(self):
        """Render login page"""
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<h2 style="text-align:center; color:var(--accent-primary);">Welcome Back</h2>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center; color:var(--text-secondary);">Sign in to continue</p>', unsafe_allow_html=True)
        
        # Login form
        username = st.text_input("Username", key="login_username", 
                                 help="Enter your registered username")
        password = st.text_input("Password", type="password", key="login_password",
                                 help="Enter your account password")
        
        col1, col2 = st.columns(2)
        
        with col1:
            login_btn = st.button("Login")
        
        with col2:
            signup_btn = st.button("Create Account")
        
        if login_btn:
            if username and password:
                if self.validate_login(username, password):
                    # Set session state for login
                    st.session_state['current_username'] = username
                    st.session_state['page'] = 'file_upload'
                    # Use st.rerun() instead of st.experimental_rerun()
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.error("Please fill in all fields")
        
        if signup_btn:
            st.session_state['page'] = 'signup'
            st.rerun()
        
        # Forgot password link
        st.markdown('''
        <div style="text-align:center; margin-top:10px;">
            <a href="#">Forgot Password?</a>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def signup_page(self):
        """Render signup page"""
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<h2 style="text-align:center; color:var(--accent-primary);">Create Account</h2>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center; color:var(--text-secondary);">Join our platform</p>', unsafe_allow_html=True)
        
        # Signup form
        name = st.text_input("Full Name", key="signup_name",
                             help="Enter your full legal name")
        client_id = st.text_input("Client ID", key="signup_client_id",
                                  help="Your unique client identification number")
        username = st.text_input("Username", key="signup_username",
                                 help="Choose a unique username")
        password = st.text_input("Password", type="password", key="signup_password",
                                 help="Create a strong password")
        
        col1, col2 = st.columns(2)
        
        with col1:
            signup_btn = st.button("Sign Up")
        
        with col2:
            login_return_btn = st.button("Back to Login")
        
        if signup_btn:
            if name and client_id and username and password:
                # Attempt to save credentials
                if self.save_credentials(name, client_id, username, password):
                    st.success("Account Created Successfully!")
                    # Redirect to login page
                    st.session_state['page'] = 'login'
                    st.rerun()
                else:
                    st.error("Username already exists. Please choose another.")
            else:
                st.error("Please fill in all fields")
        
        if login_return_btn:
            st.session_state['page'] = 'login'
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def get_user_upload_dir(self, username):
        """Create and return a user-specific upload directory"""
        user_dir = os.path.join(self.upload_dir, username)
        os.makedirs(user_dir, exist_ok=True)
        return user_dir
    
    def prepare_transaction_summary(self, summary):
        """Prepare transaction summary for AI processing by cleaning and formatting it"""
        if summary is None:
            return "No transaction data available."
            
        # Remove any potentially problematic characters or formatting
        cleaned_summary = summary.replace('\r', ' ').replace('\t', ' ')
        
        # Limit length if needed (Gemini has token limits)
        if len(cleaned_summary) > 8000:  # Arbitrary limit to avoid token issues
            cleaned_summary = cleaned_summary[:8000] + "...(summary truncated)"
            
        return cleaned_summary

    def extract_table_pdfplumber(self, pdf_path, password=None):
        """Extract tables from PDF using pdfplumber"""
        all_data = []
        column_names = None
        
        try:
            # Open PDF with password if provided
            with pdfplumber.open(pdf_path, password=password) as pdf:
                # Process each page
                for page_num, page in enumerate(pdf.pages, 1):
                    extracted_table = page.extract_table()
                    
                    if extracted_table:
                        # For the first table with data, get column names
                        if column_names is None and len(extracted_table) > 0:
                            column_names = extracted_table[0]
                            # Add data rows from first table (skip header row)
                            all_data.extend(extracted_table[1:])
                        else:
                            # Check if subsequent tables have the same column structure
                            if len(extracted_table) > 0:
                                if extracted_table[0] == column_names:
                                    # Same structure, skip header
                                    all_data.extend(extracted_table[1:])
                                else:
                                    # Different header structure, try to map columns or add as is
                                    all_data.extend(extracted_table)
                                    
                        st.write(f"Processed page {page_num}: Found {len(extracted_table)} rows")

            # Create DataFrame from collected data
            if all_data and column_names:
                # Create DataFrame with consistent column names
                all_data = [row[:5] + row[6:] if len(row) > 5 else row for row in all_data]
                df = pd.DataFrame(all_data, columns=column_names)
                
                # Clean data - convert numeric columns
                for col in df.columns:
                    # Try to convert to numeric if possible
                    try:
                        df[col] = pd.to_numeric(df[col])
                    except:
                        pass  # Keep as is if conversion fails
                
                # Drop NaN rows that don't contain essential information
                if 'Particulars' in df.columns:
                    df = df.dropna(subset=['Particulars'])
                if 'Balance' in df.columns:
                    df = df.dropna(subset=['Balance'])
                
                # Categorize transactions using the TransactionCategorizer
                try:
                    categorized_df = self.transaction_categorizer.categorize_dataframe(df)
                    # Create a summary of spending by category
                    result = self.generate_category_summary(categorized_df)
                    st.session_state['category_summary'] = result
                    
                    # Generate financial advice based on the summary
                    prepared_summary = self.prepare_transaction_summary(result)
                    financial_advice = self.get_financial_advice(prepared_summary)
                    st.session_state['financial_advice'] = financial_advice
                    
                    return categorized_df
                except Exception as e:
                    st.error(f"Error categorizing transactions: {e}")
                    return df
            else:
                return None
                
        except Exception as e:
            st.error(f"Error extracting tables: {e}")
            return None

    def generate_category_summary(self, df):
        """Generate a summary of spending by category"""
        if 'Category' not in df.columns:
            return "No category data available"
            
        try:
            # Create a copy of the DataFrame to avoid modifying the original
            summary_df = df.copy()
            
            # Handle withdrawals and deposits if they exist
            if 'Withdrawl' in summary_df.columns and 'Deposit' in summary_df.columns:
                # Convert to numeric if they aren't already
                summary_df['Withdrawl'] = pd.to_numeric(summary_df['Withdrawl'], errors='coerce').fillna(0)
                summary_df['Deposit'] = pd.to_numeric(summary_df['Deposit'], errors='coerce').fillna(0)
                
                # Calculate total withdrawals by category (expenses)
                category_expenses = summary_df.groupby('Category')['Withdrawl'].sum().sort_values(ascending=False)
                
                # Calculate total deposits by category (income)
                category_income = summary_df.groupby('Category')['Deposit'].sum().sort_values(ascending=False)
                
                # Generate summary text
                summary_text = "Transaction Summary:\n\n"
                
                summary_text += "Expenses by Category:\n"
                for category, amount in category_expenses.items():
                    if amount > 0:  # Only include categories with expenses
                        summary_text += f"- {category}: ₹{amount:.2f}\n"
                
                summary_text += "\nIncome by Category:\n"
                for category, amount in category_income.items():
                    if amount > 0:  # Only include categories with income
                        summary_text += f"- {category}: ₹{amount:.2f}\n"
                
                # Calculate totals
                total_expense = summary_df['Withdrawl'].sum()
                total_income = summary_df['Deposit'].sum()
                net_flow = total_income - total_expense
                
                summary_text += f"\nTotal Expense: ₹{total_expense:.2f}"
                summary_text += f"\nTotal Income: ₹{total_income:.2f}"
                summary_text += f"\nNet Cash Flow: ₹{net_flow:.2f} ({'Positive' if net_flow >= 0 else 'Negative'})"
                
                return summary_text
            else:
                # If no withdrawals/deposits columns, just count transactions by category
                category_counts = df['Category'].value_counts()
                
                summary_text = "Transaction Categories:\n\n"
                for category, count in category_counts.items():
                    summary_text += f"- {category}: {count} transactions\n"
                
                return summary_text
                
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def save_pdf_metadata(self, username, filename, original_filename):
        """Save metadata about uploaded PDF files"""
        try:
            # Read existing metadata
            with open(self.pdf_metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Add new file metadata
            file_id = str(uuid.uuid4())
            metadata[file_id] = {
                'username': username,
                'filename': filename,
                'original_filename': original_filename,
                'upload_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'file_size': os.path.getsize(filename)
            }
            
            # Write updated metadata
            with open(self.pdf_metadata_file, 'w') as f:
                json.dump(metadata, f, indent=4)
                
            return file_id
        except Exception as e:
            st.error(f"Error saving file metadata: {str(e)}")
            return None
    
    def file_upload_page(self):
        """Render PDF file upload page"""
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<h2 style="text-align:center; color:var(--accent-primary);">PDF Upload</h2>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center; color:var(--text-secondary);">Upload your PDF files securely</p>', unsafe_allow_html=True)
        
        # Retrieve current username from session state
        current_username = st.session_state.get('current_username', 'Unknown User')
        st.write(f"Welcome, {current_username}")
        
        # File upload section
        uploaded_file = st.file_uploader(
            "Choose a PDF file", 
            type=['pdf'],
            help="Select a PDF file to upload"
        )
        
        # Optional password for protected PDFs
        pdf_password = st.text_input(
            "PDF Password (if protected)", 
            type="password",
            help="Leave blank if the PDF is not password-protected"
        )
        
        # File tags or categories
        file_tags = st.text_input(
            "Tags (comma separated)",
            help="Add tags to help organize your files"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            upload_btn = st.button("Upload PDF")
        
        with col2:
            view_files_btn = st.button("View My Files")
        
        logout_btn = st.button("Logout")
        
        if upload_btn and uploaded_file is not None:
            try:
                # Validate file extension
                if not uploaded_file.name.lower().endswith('.pdf'):
                    st.error("Only PDF files are allowed!")
                    return
                
                # Get user-specific directory
                user_dir = self.get_user_upload_dir(current_username)
                
                # Generate a unique filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_filename = uploaded_file.name.replace(' ', '_')
                unique_filename = os.path.join(
                    user_dir, 
                    f"{timestamp}_{safe_filename}"
                )
                
                # Save the uploaded file
                with open(unique_filename, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Save metadata including any tags
                tags = [tag.strip() for tag in file_tags.split(',')] if file_tags else []
                file_id = self.save_pdf_metadata(
                    current_username,
                    unique_filename,
                    uploaded_file.name,
                )
                
                if file_id:
                    st.success(f"PDF '{uploaded_file.name}' uploaded successfully!")
                    st.info(f"File ID: {file_id}")
                    
                    # Process the PDF to extract tables
                    with st.spinner("Extracting data from PDF..."):
                        password = pdf_password if pdf_password else None
                        df = self.extract_table_pdfplumber(unique_filename, password)
                        
                        if df is not None:
                            # Store the DataFrame in session state
                            st.session_state['extracted_df'] = df
                            st.session_state['current_pdf'] = unique_filename
                            st.session_state['page'] = 'view_dataframe'
                            st.success("Data extracted successfully! View the data table.")
                            st.rerun()
                        else:
                            st.warning("No tables found in the PDF or extraction failed.")
                else:
                    st.warning("File uploaded but metadata could not be saved.")
            except Exception as e:
                st.error(f"Error uploading PDF: {str(e)}")
        
        if view_files_btn:
            st.session_state['page'] = 'view_files'
            st.rerun()
        
        if logout_btn:
            # Clear login-related session state
            if 'current_username' in st.session_state:
                del st.session_state['current_username']
            st.session_state['page'] = 'login'
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def view_dataframe_page(self):
        """Display the extracted DataFrame from PDF"""
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<h2 style="text-align:center; color:var(--accent-primary);">Extracted Data</h2>', unsafe_allow_html=True)
        
        # Get the DataFrame from session state
        df = st.session_state.get('extracted_df', None)
        current_pdf = st.session_state.get('current_pdf', 'Unknown PDF')
        category_summary = st.session_state.get('category_summary', None)
        
        if df is not None:
            # Show PDF file name
            st.write(f"Data from: {os.path.basename(current_pdf)}")
            
            # Display DataFrame statistics
            st.write(f"Found {len(df)} rows and {len(df.columns)} columns")
            
            # Display tabs for data view, analysis, and financial advice
            tab1, tab2, tab3 = st.tabs(["Data", "Analysis", "Financial Advice"])
            
            with tab1:
                # Add search/filter capability
                search_term = st.text_input("Search in data", "")
                
                # Filter DataFrame if search term is provided
                filtered_df = df
                if search_term:
                    filtered_df = df[df.astype(str).apply(
                        lambda row: row.str.contains(search_term, case=False).any(), axis=1)]
                    st.write(f"Found {len(filtered_df)} matching rows")
                
                # Display the DataFrame
                st.dataframe(filtered_df)
                
                # Download options
                col1, col2 = st.columns(2)
                with col1:
                    # Download as CSV
                    csv = filtered_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download as CSV",
                        data=csv,
                        file_name=f"extracted_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    # Download as Excel - Fixed implementation using BytesIO
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        filtered_df.to_excel(writer, index=False)
                    output.seek(0)  # Go to the beginning of the BytesIO buffer
                    
                    st.download_button(
                        label="Download as Excel",
                        data=output,
                        file_name=f"extracted_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            
            with tab2:
                if 'Category' in df.columns:
                    # Show category summary
                    if category_summary:
                        st.subheader("Transaction Summary")
                        st.text(category_summary)
                    
                    # Show category distribution chart
                    st.subheader("Category Distribution")
                    fig, ax = plt.subplots(figsize=(10, 6))
                    category_counts = df['Category'].value_counts()
                    sns.barplot(x=category_counts.index, y=category_counts.values, ax=ax)
                    plt.xticks(rotation=45, ha='right')
                    plt.tight_layout()
                    st.pyplot(fig)
                    
                    # If we have withdrawal/deposit data, show spending by category
                    if 'Withdrawl' in df.columns:
                        st.subheader("Spending by Category")
                        fig2, ax2 = plt.subplots(figsize=(10, 6))
                        category_spending = df.groupby('Category')['Withdrawl'].sum().sort_values(ascending=False)
                        sns.barplot(x=category_spending.index, y=category_spending.values, ax=ax2)
                        plt.xticks(rotation=45, ha='right')
                        plt.tight_layout()
                        st.pyplot(fig2)
                else:
                    st.info("No category information available. Unable to show analysis.")
            
            with tab3:
                # Show financial advice
                financial_advice = st.session_state.get('financial_advice', 'Financial advice not generated yet.')
                st.markdown('<div style="padding: 20px; border-radius: 10px; background-color: var(--bg-secondary);">', unsafe_allow_html=True)
                st.markdown("## 💰 Your Financial Insights")
                st.markdown("Below is personalized financial advice based on your transaction data:")
                st.markdown(financial_advice)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Add a button to regenerate advice
                if st.button("Regenerate Financial Advice"):
                    if category_summary:
                        with st.spinner("Generating new financial insights..."):
                            new_advice = self.get_financial_advice(category_summary)
                            st.session_state['financial_advice'] = new_advice
                            st.rerun()
                    else:
                        st.error("No transaction summary available to generate advice.")
        else:
            st.error("No data available. Please upload a PDF first.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            back_btn = st.button("Back to Upload")
        
        with col2:
            logout_btn = st.button("Logout")
        
        if back_btn:
            st.session_state['page'] = 'file_upload'
            st.rerun()
        
        if logout_btn:
            if 'current_username' in st.session_state:
                del st.session_state['current_username']
            st.session_state['page'] = 'login'
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def view_files_page(self):
        """Render page to view uploaded PDF files"""
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<h2 style="text-align:center; color:var(--accent-primary);">Your Files</h2>', unsafe_allow_html=True)
        
        # Retrieve current username from session state
        current_username = st.session_state.get('current_username', 'Unknown User')
        
        try:
            # Load metadata
            with open(self.pdf_metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Filter for current user's files
            user_files = {k: v for k, v in metadata.items() if v['username'] == current_username}
            
            if not user_files:
                st.info("You haven't uploaded any files yet.")
            else:
                st.write(f"You have {len(user_files)} file(s) uploaded:")
                
                # Display files in a nice format
                for file_id, file_data in user_files.items():
                    with st.expander(f"{file_data['original_filename']} ({file_data['upload_date']})"):
                        st.write(f"Upload date: {file_data['upload_date']}")
                        st.write(f"File size: {file_data['file_size']/1024:.2f} KB")
                        
                        # Option to download the file
                        if os.path.exists(file_data['filename']):
                            with open(file_data['filename'], "rb") as f:
                                st.download_button(
                                    label="Download PDF",
                                    data=f,
                                    file_name=file_data['original_filename'],
                                    mime="application/pdf"
                                )
        except Exception as e:
            st.error(f"Error loading your files: {str(e)}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            back_btn = st.button("Back to Upload")
        
        with col2:
            logout_btn = st.button("Logout")
        
        if back_btn:
            st.session_state['page'] = 'file_upload'
            st.rerun()
        
        if logout_btn:
            if 'current_username' in st.session_state:
                del st.session_state['current_username']
            st.session_state['page'] = 'login'
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def get_financial_advice(self, transaction_summary):
        """Generate financial advice using Gemini AI based on transaction summary"""
        if not GOOGLE_API_KEY or gemini_model is None:
            return "Financial advice not available. Google API Key is missing."
            
        try:
            prompt = f"""
            You are a professional financial advisor. Based on the following bank transaction summary, 
            provide specific, actionable financial advice in bullet points.
            
            Focus on:
            - Spending patterns that could be optimized
            - Savings opportunities
            - Budget recommendations
            - Investment suggestions based on cash flow
            - Any concerning financial behaviors
            
            Make your advice practical and specific to this data. Be direct and helpful.
            
            Transaction Summary:
            {transaction_summary}
            
            Provide your advice in bullet points, with clear headings for different sections.
            """
            
            response = gemini_model.generate_content(prompt)
            
            # Handle different response formats from Gemini models
            if hasattr(response, 'text'):
                return response.text
            elif isinstance(response, dict) and 'candidates' in response:
                # Handle dictionary response format with candidates
                candidates = response['candidates']
                if candidates and len(candidates) > 0:
                    if 'content' in candidates[0] and 'parts' in candidates[0]['content']:
                        parts = candidates[0]['content']['parts']
                        if parts and len(parts) > 0:
                            return parts[0]['text']
            elif isinstance(response, dict) and 'text' in response:
                # Direct text in dictionary format
                return response['text']
            elif hasattr(response, 'candidates') and len(response.candidates) > 0:
                # Handle object with candidates attribute
                if hasattr(response.candidates[0], 'content'):
                    return response.candidates[0].content.text
            elif isinstance(response, str):
                # Already a string
                return response
            
            # If we got here, try to convert the whole response to a string
            try:
                return str(response)
            except:
                # Last resort fallback
                return "Unable to process the AI model response. Using fallback analysis."
                
        except Exception as e:
            st.warning(f"Debug info: {type(e).__name__}: {str(e)}")
            return f"Error generating financial advice: {str(e)}"

    def generate_fallback_analysis(self, df):
        """Generate basic analysis if Gemini model fails to provide analysis"""
        if df is None or 'Category' not in df.columns:
            return "Cannot generate analysis without categorized transaction data."
        
        try:
            analysis = "# Basic Financial Analysis\n\n"
            
            # Calculate basic statistics
            if 'Withdrawl' in df.columns and 'Deposit' in df.columns:
                total_expense = df['Withdrawl'].sum()
                total_income = df['Deposit'].sum()
                net_flow = total_income - total_expense
                
                # Overall summary
                analysis += f"## Summary\n"
                analysis += f"* Total Expenses: ₹{total_expense:.2f}\n"
                analysis += f"* Total Income: ₹{total_income:.2f}\n"
                analysis += f"* Net Cash Flow: ₹{net_flow:.2f} ({net_flow >= 0 and 'Positive' or 'Negative'})\n\n"
                
                # Category analysis
                analysis += f"## Spending by Category\n"
                category_expenses = df.groupby('Category')['Withdrawl'].sum().sort_values(ascending=False)
                for category, amount in category_expenses.items():
                    if amount > 0:
                        percent = (amount / total_expense) * 100
                        analysis += f"* {category}: ₹{amount:.2f} ({percent:.1f}%)\n"
                
                # Basic advice
                analysis += "\n## Basic Recommendations\n"
                
                # If negative cash flow
                if net_flow < 0:
                    analysis += "* Your spending exceeds your income. Consider creating a budget.\n"
                    # Find highest spending category
                    highest_category = category_expenses.index[0] if not category_expenses.empty else "N/A"
                    analysis += f"* Your highest spending category is {highest_category}. Look for ways to reduce these expenses.\n"
                else:
                    analysis += "* You have positive cash flow. Consider saving or investing the surplus.\n"
                    
                analysis += "* Track your expenses regularly to identify areas for improvement.\n"
                analysis += "* Consider creating an emergency fund if you don't have one already.\n"
            else:
                analysis += "* Limited transaction data available. Unable to provide detailed analysis.\n"
                
            return analysis
            
        except Exception as e:
            return f"Error generating fallback analysis: {str(e)}"

    def test_gemini_connection(self):
        """Test if the Gemini model is working properly and return status"""
        if not GOOGLE_API_KEY or gemini_model is None:
            return False, "API key not configured"
            
        try:
            # Simple test prompt
            test_prompt = "Give a one-sentence financial tip."
            response = gemini_model.generate_content(test_prompt)
            
            # Try to access the response in different ways
            if hasattr(response, 'text') and response.text:
                return True, "Connection successful"
            elif isinstance(response, dict) and ('text' in response or 'candidates' in response):
                return True, "Connection successful (dictionary response)"
            else:
                # If we got a response but can't extract text
                return False, f"Connection working but unexpected response format: {type(response)}"
                
        except Exception as e:
            return False, f"Connection failed: {type(e).__name__}: {str(e)}"

    def financial_advice_page(self):
        """Display detailed financial advice"""
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<h2 style="text-align:center; color:var(--accent-primary);">Financial Advice</h2>', unsafe_allow_html=True)
        
        financial_advice = st.session_state.get('financial_advice', None)
        category_summary = st.session_state.get('category_summary', None)
        extracted_df = st.session_state.get('extracted_df', None)
        
        # Add AI model status indicator
        model_status, status_msg = self.test_gemini_connection()
        
        if model_status:
            st.success(f"AI Model Status: Ready")
        else:
            st.error(f"AI Model Status: Issue detected - {status_msg}")
            
        # Check if financial advice is missing or error message
        advice_missing = (financial_advice is None or
                         financial_advice.startswith("Error generating") or
                         financial_advice.startswith("Financial advice not available"))
        
        if not advice_missing:
            # Display the advice from the model
            st.markdown('<div style="padding: 20px; border-radius: 10px; background-color: var(--bg-secondary);">', unsafe_allow_html=True)
            st.markdown("## 💰 Your Personalized Financial Insights")
            st.markdown(financial_advice)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            # Show fallback analysis if model failed
            st.warning("AI-powered financial advice is not available. Showing basic analysis instead.")
            
            if extracted_df is not None:
                fallback_analysis = self.generate_fallback_analysis(extracted_df)
                st.markdown('<div style="padding: 20px; border-radius: 10px; background-color: var(--bg-secondary);">', unsafe_allow_html=True)
                st.markdown(fallback_analysis)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Option to retry with AI
                if st.button("Try Again with AI"):
                    if category_summary:
                        with st.spinner("Generating AI financial insights..."):
                            try:
                                new_advice = self.get_financial_advice(category_summary)
                                st.session_state['financial_advice'] = new_advice
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to generate AI advice: {str(e)}")
                    else:
                        st.error("No transaction summary available to generate advice.")
            else:
                st.error("No transaction data available. Please upload and analyze a statement first.")
        
        # Add options to customize advice - show regardless of which analysis is displayed
        st.subheader("Need more specific advice?")
        specific_topic = st.selectbox("Choose a topic:", 
                                    ["Saving Strategies", "Debt Management", "Investment Options", 
                                     "Budget Planning", "Expense Reduction"])
        
        if st.button("Get Specific Advice"):
            if category_summary:
                with st.spinner(f"Generating advice on {specific_topic}..."):
                    try:
                        if gemini_model is not None:
                            prompt = f"""
                            As a financial advisor, provide detailed advice specifically on {specific_topic}
                            based on the following transaction data summary:
                            
                            {category_summary}
                            
                            Focus only on {specific_topic} with practical, actionable points.
                            Format your advice in bullet points with clear headings.
                            """
                            
                            response = gemini_model.generate_content(prompt)
                            st.markdown('<div style="padding: 20px; border-radius: 10px; background-color: var(--bg-secondary);">', unsafe_allow_html=True)
                            st.markdown(f"## {specific_topic} Advice")
                            st.markdown(response.text)
                            st.markdown("</div>", unsafe_allow_html=True)
                        else:
                            # Fallback for specific topic advice
                            st.info("AI model not available. Showing general advice for this topic.")
                            basic_advice = self.get_basic_topic_advice(specific_topic, extracted_df)
                            st.markdown('<div style="padding: 20px; border-radius: 10px; background-color: var(--bg-secondary);">', unsafe_allow_html=True)
                            st.markdown(f"## {specific_topic} - General Advice")
                            st.markdown(basic_advice)
                            st.markdown("</div>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error generating advice: {str(e)}")
            else:
                st.error("No transaction summary available to generate advice.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            back_btn = st.button("Back to Data")
        
        with col2:
            home_btn = st.button("Home")
        
        if back_btn:
            st.session_state['page'] = 'view_dataframe'
            st.rerun()
        
        if home_btn:
            st.session_state['page'] = 'file_upload'
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def get_basic_topic_advice(self, topic, df):
        """Provide basic advice on specific topics when AI is unavailable"""
        advice = f"# {topic} Advice\n\n"
        
        if topic == "Saving Strategies":
            advice += "* Set up automatic transfers to a savings account on payday\n"
            advice += "* Follow the 50/30/20 rule: 50% necessities, 30% wants, 20% savings\n"
            advice += "* Look for unnecessary subscriptions and recurring charges\n"
            advice += "* Consider using cash for discretionary spending to be more mindful\n"
            advice += "* Set specific savings goals with deadlines to stay motivated\n"
        
        elif topic == "Debt Management":
            advice += "* List all debts with interest rates and minimum payments\n"
            advice += "* Consider the snowball method (paying smallest debts first) or avalanche method (highest interest first)\n"
            advice += "* Avoid taking on new debt while paying off existing debt\n"
            advice += "* Look into debt consolidation options if you have high-interest debts\n"
            advice += "* Contact creditors about possible interest rate reductions\n"
        
        elif topic == "Investment Options":
            advice += "* Build an emergency fund before focusing heavily on investments\n"
            advice += "* Consider tax-advantaged retirement accounts first\n"
            advice += "* Look into low-cost index funds for long-term growth\n"
            advice += "* Diversify investments across different asset classes\n"
            advice += "* Start small and increase investment contributions over time\n"
        
        elif topic == "Budget Planning":
            advice += "* Track all expenses for a month to understand spending patterns\n"
            advice += "* Categorize expenses as needs, wants, and savings\n"
            advice += "* Use the envelope method or budgeting apps to stay on track\n"
            advice += "* Review and adjust your budget quarterly\n"
            advice += "* Include occasional expenses like gifts and maintenance in your budget\n"
        
        elif topic == "Expense Reduction":
            if df is not None and 'Category' in df.columns and 'Withdrawl' in df.columns:
                # Try to provide data-driven advice
                try:
                    top_expenses = df.groupby('Category')['Withdrawl'].sum().sort_values(ascending=False).head(3)
                    advice += f"* Your top spending categories are: {', '.join(top_expenses.index)}\n"
                    advice += "* Focus on reducing expenses in these categories first\n"
                except:
                    pass
            
            advice += "* Review subscriptions and cancel unused services\n"
            advice += "* Compare prices for regular purchases and switch to lower-cost options\n"
            advice += "* Use coupons and wait for sales for non-urgent purchases\n"
            advice += "* Consider meal planning to reduce food expenses\n"
            advice += "* Evaluate if you can negotiate bills like insurance, phone, internet\n"
        
        return advice
    
    def run(self):
        """Main application runner"""
        # Render the appropriate page based on session state
        page = st.session_state.get('page', 'login')
        
        if page == 'login':
            self.login_page()
        elif page == 'signup':
            self.signup_page()
        elif page == 'file_upload':
            self.file_upload_page()
        elif page == 'view_files':
            self.view_files_page()
        elif page == 'view_dataframe':
            self.view_dataframe_page()
        elif page == 'financial_advice':
            self.financial_advice_page()

def main():
    app = MobileAuthApp()
    app.run()

if __name__ == "__main__":
    main()
