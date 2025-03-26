import streamlit as st
import re

class AuthApp:
    def __init__(self):
        # Set page configuration
        st.set_page_config(page_title="Login/Register", page_icon=":mobile_phone:", layout="centered")
        
        # Custom CSS for mobile-like design
        self.apply_custom_css()
        
        # Initialize session state for tracking authentication state
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        
        # Run the app
        self.run()
    
    def apply_custom_css(self):
        st.markdown("""
        <style>
        .stApp {
            max-width: 400px;
            margin: 0 auto;
            background: linear-gradient(135deg, #ff6b6b, #ff8a5b);
            height: 100vh;
        }
        .stTextInput > div > div > input {
            background-color: white;
            border-radius: 10px;
            height: 50px;
            padding: 0 15px;
        }
        .stButton > button {
            background-color: #ff4500 !important;
            color: white !important;
            border-radius: 25px;
            height: 50px;
            width: 100%;
        }
        .stButton > button:hover {
            background-color: #ff6347 !important;
        }
        .login-container {
            background-color: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        </style>
        """, unsafe_allow_html=True)
    
    def validate_email(self, email):
        """Basic email validation"""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None
    
    def validate_phone(self, phone):
        """Basic phone number validation"""
        phone_regex = r'^\+?1?\d{10,14}$'
        return re.match(phone_regex, phone) is not None
    
    def validate_password(self, password):
        """Password validation (at least 8 characters, one uppercase, one number)"""
        return (len(password) >= 8 and 
                any(c.isupper() for c in password) and 
                any(c.isdigit() for c in password))
    
    def login_page(self):
        """Render login page"""
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<h2 style="text-align:center; color:#333;">WELCOME!!</h2>', unsafe_allow_html=True)
        
        # Login form
        username = st.text_input("Username/Email", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        login_btn = st.button("Login", key="login_btn")
        
        if login_btn:
            if not username or not password:
                st.error("Please fill in all fields")
            else:
                # Placeholder authentication logic
                st.success("Login Successful!")
                st.session_state.authenticated = True
        
        # Additional links
        st.markdown('''
        <div style="text-align:center; margin-top:10px;">
            <a href="#" style="color:#ff4500; text-decoration:none;">Forgot Password?</a>
        </div>
        <div style="text-align:center; margin-top:10px;">
            Don't have an Account? <a href="#" style="color:#ff4500;">Register</a>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def register_page(self):
        """Render registration page"""
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<h2 style="text-align:center; color:#333;">REGISTER</h2>', unsafe_allow_html=True)
        
        # Registration form
        full_name = st.text_input("Full Name", key="reg_full_name")
        username_email = st.text_input("Username / Email", key="reg_username")
        phone = st.text_input("Phone Number", key="reg_phone")
        password = st.text_input("Password", type="password", key="reg_password")
        
        register_btn = st.button("Sign Up", key="register_btn")
        
        if register_btn:
            # Validation checks
            errors = []
            if not full_name:
                errors.append("Full name is required")
            if not username_email or not self.validate_email(username_email):
                errors.append("Invalid email address")
            if not phone or not self.validate_phone(phone):
                errors.append("Invalid phone number")
            if not password or not self.validate_password(password):
                errors.append("Password must be at least 8 characters with one uppercase and one number")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                st.success("Registration Successful!")
                st.session_state.authenticated = True
        
        # Already a member link
        st.markdown('''
        <div style="text-align:center; margin-top:10px;">
            Already A Member? <a href="#" style="color:#ff4500;">Sign in</a>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def run(self):
        """Main application runner"""
        # Create tabs for Login and Register
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            self.login_page()
        
        with tab2:
            self.register_page()
        
        # Optional: Add a logout or dashboard page for authenticated users
        if st.session_state.authenticated:
            st.sidebar.title("Dashboard")
            if st.sidebar.button("Logout"):
                st.session_state.authenticated = False
                st.experimental_rerun()

# Run the application
if __name__ == "__main__":
    AuthApp()