import streamlit as st
import hashlib
import os

class MobileAuthApp:
    def __init__(self):
        # Initialize session state variables
        if 'page' not in st.session_state:
            st.session_state.page = 'login'
        
        # User credentials file
        self.credentials_file = 'user_credentials.txt'
        
        # Custom CSS for mobile-like design
        self.apply_custom_css()
        
        # Run the app
        self.run()
    
    def apply_custom_css(self):
        st.markdown("""
        <style>
        .stApp {
            max-width: 400px;
            margin: 0 auto;
            background: linear-gradient(135deg, #e0e0e0, #f5f5f5);
            height: 100vh;
        }
        .stTextInput > div > div > input {
            background-color: white;
            border-radius: 10px;
            height: 50px;
            padding: 0 15px;
        }
        .stButton > button {
            background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%) !important;
            color: white !important;
            border-radius: 25px;
            height: 50px;
            width: 100%;
            border: none;
        }
        .stButton > button:hover {
            opacity: 0.9 !important;
        }
        .login-container {
            background-color: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
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
        st.markdown('<h2 style="text-align:center; color:#333;">Login</h2>', unsafe_allow_html=True)
        
        # Login form
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        login_btn = st.button("Login")
        signup_btn = st.button("Sign Up")
        
        if login_btn:
            if username and password:
                if self.validate_login(username, password):
                    st.success("Login Successful!")
                else:
                    st.error("Invalid username or password")
            else:
                st.error("Please fill in all fields")
        
        if signup_btn:
            st.session_state.page = 'signup'
            st.experimental_rerun()
        
        # Forgot password link
        st.markdown('''
        <div style="text-align:center; margin-top:10px;">
            <a href="#" style="color:#6a11cb; text-decoration:none;">Forgot Password?</a>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def signup_page(self):
        """Render signup page"""
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<h2 style="text-align:center; color:#333;">Create Account</h2>', unsafe_allow_html=True)
        
        # Signup form
        name = st.text_input("Full Name", key="signup_name")
        client_id = st.text_input("Client ID", key="signup_client_id")
        username = st.text_input("Username", key="signup_username")
        password = st.text_input("Password", type="password", key="signup_password")
        
        signup_btn = st.button("Sign Up")
        
        if signup_btn:
            if name and client_id and username and password:
                # Attempt to save credentials
                if self.save_credentials(name, client_id, username, password):
                    st.success("Account Created Successfully!")
                    # Optionally, redirect to login page
                    st.session_state.page = 'login'
                    st.experimental_rerun()
                else:
                    st.error("Username already exists. Please choose another.")
            else:
                st.error("Please fill in all fields")
        
        # Back to login link
        st.markdown('''
        <div style="text-align:center; margin-top:10px;">
            Already have an account? <a href="#" style="color:#6a11cb;">Login</a>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def run(self):
        """Main application runner"""
        # Render the appropriate page based on session state
        if st.session_state.page == 'login':
            self.login_page()
        elif st.session_state.page == 'signup':
            self.signup_page()

# Run the application
if __name__ == "__main__":
    MobileAuthApp()