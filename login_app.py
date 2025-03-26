import streamlit as st
import re

class BankingApp:
    def __init__(self):
        # Initialize session state variables
        if 'page' not in st.session_state:
            st.session_state.page = 'home'
        
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
        .home-container {
            text-align: center;
            padding: 50px 20px;
        }
        .login-container {
            background-color: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        </style>
        """, unsafe_allow_html=True)
    
    def home_page(self):
        """Render home page"""
        st.markdown('<div class="home-container">', unsafe_allow_html=True)
        
        # Stylized logo or app name
        st.markdown('<h1 style="color:#6a11cb;">Money Move</h1>', unsafe_allow_html=True)
        
        # App description
        st.markdown('<p style="color:#666;">Keep your money moving with you</p>', unsafe_allow_html=True)
        
        # Get Started button
        if st.button("Get Started"):
            st.session_state.page = 'login'
            st.experimental_rerun()
        
        # Platform buttons
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div style="text-align:center;"><img src="https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg" width="50"/></div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div style="text-align:center;"><img src="https://upload.wikimedia.org/wikipedia/commons/5/53/Google_%22G%22_Logo.svg" width="50"/></div>', unsafe_allow_html=True)
        
        # Sign in link
        st.markdown('''
        <div style="text-align:center; margin-top:20px;">
            You have an account? <a href="#" style="color:#6a11cb;">Sign in</a>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def login_page(self):
        """Render login page"""
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<h2 style="text-align:center; color:#333;">Login</h2>', unsafe_allow_html=True)
        
        # Login form
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        login_btn = st.button("Login")
        
        if login_btn:
            if username and password:
                st.session_state.page = 'register'
                st.experimental_rerun()
            else:
                st.error("Please fill in all fields")
        
        # Forgot password and signup links
        st.markdown('''
        <div style="text-align:center; margin-top:10px;">
            <a href="#" style="color:#6a11cb; text-decoration:none;">Forgot Password?</a>
        </div>
        <div style="text-align:center; margin-top:10px;">
            Don't have an Account? <a href="#" style="color:#6a11cb;">Sign Up</a>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def register_page(self):
        """Render registration page"""
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<h2 style="text-align:center; color:#333;">Create Account</h2>', unsafe_allow_html=True)
        
        # Registration form
        full_name = st.text_input("Full Name", key="reg_full_name")
        client_id = st.text_input("Client ID", key="reg_client_id")
        username = st.text_input("Username", key="reg_username")
        password = st.text_input("Password", type="password", key="reg_password")
        
        register_btn = st.button("Register")
        
        if register_btn:
            # Basic validation
            if full_name and client_id and username and password:
                st.success("Registration Successful!")
                # You would typically add database or authentication logic here
            else:
                st.error("Please fill in all fields")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def run(self):
        """Main application runner"""
        # Render the appropriate page based on session state
        if st.session_state.page == 'home':
            self.home_page()
        elif st.session_state.page == 'login':
            self.login_page()
        elif st.session_state.page == 'register':
            self.register_page()

# Run the application
if __name__ == "__main__":
    BankingApp()