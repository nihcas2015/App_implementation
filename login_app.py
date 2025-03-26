import streamlit as st
import hashlib
import os
import json
from datetime import datetime
import uuid

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
    
    def save_pdf_metadata(self, username, filename, original_filename, description):
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
                'description': description,
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
        
        # Optional file description
        file_description = st.text_area(
            "File Description", 
            help="Provide a brief description of the uploaded PDF"
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
                    file_description,
                )
                
                if file_id:
                    st.success(f"PDF '{uploaded_file.name}' uploaded successfully!")
                    st.info(f"File ID: {file_id}")
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
                        st.write(f"Description: {file_data['description']}")
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

def main():
    app = MobileAuthApp()
    app.run()

if __name__ == "__main__":
    main()