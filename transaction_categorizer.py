import pandas as pd
import numpy as np
import re
import pickle
from datetime import datetime

class TransactionCategorizer:
    """
    A class to categorize bank transactions into different expense categories
    using both rule-based logic and machine learning.
    """
    
    def __init__(self, model_path=None, preprocessor_path=None):
        """
        Initialize the TransactionCategorizer with optional model paths.
        
        Args:
            model_path: Path to the trained model pickle file
            preprocessor_path: Path to the preprocessor pickle file
        """
        self.model = None
        self.preprocessor = None
        
        if model_path and preprocessor_path:
            self.load_model(model_path, preprocessor_path)
            
        self.categories = ['FOOD', 'FRIENDS_FAMILY', 'PURCHASES', 'SHOPPING', 
                          'ENTERTAINMENT', 'TRAVEL', 'UTILITIES', 'INCOME', 'OTHER']
    
    def load_model(self, model_path, preprocessor_path):
        """
        Load the trained model and preprocessor from pickle files.
        
        Args:
            model_path: Path to the trained model pickle file
            preprocessor_path: Path to the preprocessor pickle file
        """
        try:
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
                
            with open(preprocessor_path, 'rb') as f:
                self.preprocessor = pickle.load(f)
                
            print("Model and preprocessor loaded successfully.")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def extract_features(self, transaction_data):
        """
        Extract features from a transaction dictionary or DataFrame row.
        
        Args:
            transaction_data: Dictionary or pandas Series containing transaction information
            
        Returns:
            Dictionary of extracted features
        """
        # Convert to dictionary if it's a pandas Series
        if isinstance(transaction_data, pd.Series):
            transaction = transaction_data.to_dict()
        else:
            transaction = transaction_data.copy()
            
        features = {}
        
        # Extract transaction type
        particulars = transaction.get('Particulars', '')
        features['TransactionType'] = self.extract_transaction_type(particulars)
        
        # Extract payee name
        payee_name = self.extract_payee_name(particulars)
        features['PayeeName'] = payee_name
        features['HasPayee'] = 0 if payee_name is None else 1
        
        # Extract transaction amount
        if 'Withdrawl' in transaction and 'Deposit' in transaction:
            withdrawl = transaction.get('Withdrawl', 0) or 0
            deposit = transaction.get('Deposit', 0) or 0
            
            if withdrawl > 0:
                features['TransactionAmount'] = -withdrawl
            elif deposit > 0:
                features['TransactionAmount'] = deposit
            else:
                features['TransactionAmount'] = 0
        else:
            features['TransactionAmount'] = transaction.get('TransactionAmount', 0)
        
        # Extract keywords
        features['Keywords'] = self.extract_keywords(particulars)
        
        # Extract time-based features
        date = transaction.get('Date')
        if date:
            if isinstance(date, str):
                try:
                    date = datetime.strptime(date, '%d-%b-%Y')
                except:
                    try:
                        date = datetime.strptime(date, '%Y-%m-%d')
                    except:
                        date = None
            
            if date:
                features['DayOfWeek'] = date.weekday()
                features['IsWeekend'] = 1 if date.weekday() >= 5 else 0
                features['Month'] = date.month
            else:
                features['DayOfWeek'] = 0
                features['IsWeekend'] = 0
                features['Month'] = 1
        else:
            features['DayOfWeek'] = 0
            features['IsWeekend'] = 0
            features['Month'] = 1
        
        # Amount-based features
        amount = abs(features['TransactionAmount'])
        features['IsRoundAmount'] = 1 if amount % 10 == 0 else 0
        
        # Rule-based features
        features['is_small_upi_no_payee'] = 1 if (
            features['TransactionType'] == 'UPI' and 
            features['HasPayee'] == 0 and 
            amount < 200
        ) else 0
        
        features['is_upi_with_payee'] = 1 if (
            features['TransactionType'] == 'UPI' and 
            features['HasPayee'] == 1
        ) else 0
        
        features['is_large_amount'] = 1 if amount > 200 else 0
        
        return features
    
    def extract_transaction_type(self, description):
        """Extract the transaction type from the description."""
        if not isinstance(description, str):
            return 'OTHER'
            
        description = description.upper()
        if 'UPI' in description:
            return 'UPI'
        elif 'POS' in description or 'BOOKMYSHOW' in description:
            return 'CARD_PAYMENT'
        elif 'IMPS' in description:
            return 'IMPS'
        elif 'INT.PD' in description:
            return 'INTEREST'
        elif 'REFUND' in description:
            return 'REFUND'
        elif 'CMS' in description:
            return 'CMS'
        else:
            return 'OTHER'
    
    def extract_payee_name(self, description):
        """Extract the payee name from the description."""
        if not isinstance(description, str) or 'UPI' not in description.upper():
            return None
            
        # Try to extract the payee name using pattern between slashes
        patterns = [
            r'/([A-Z]{2,}?)/',  # Capture 2+ uppercase letters between slashes
            r'/([A-Za-z]{2,}?)/',  # Capture 2+ letters between slashes
            r'([A-Za-z]{3,})@'  # Capture 3+ letters before @
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, description)
            if matches and len(matches) > 0:
                return matches[0]
        
        return None
    
    def extract_keywords(self, description):
        """Extract keywords from the description."""
        if not isinstance(description, str):
            return ''
            
        # List of common keywords to look for
        keywords = ['food', 'grocery', 'restaurant', 'cinema', 'movie', 'travel', 'uber', 'ola',
                    'amazon', 'flipkart', 'payment', 'bill', 'recharge', 'salary', 'rent', 
                    'transfer', 'education', 'health', 'medicine', 'hospital', 'entertainment']
        
        found_keywords = []
        description_lower = description.lower()
        
        # Check for common merchants
        if 'amazon' in description_lower:
            found_keywords.append('amazon')
        if 'bookmyshow' in description_lower:
            found_keywords.append('entertainment')
        if 'meesho' in description_lower or 'flipkart' in description_lower:
            found_keywords.append('shopping')
        if 'jio' in description_lower or 'airtel' in description_lower or 'voda' in description_lower:
            found_keywords.append('telecom')
        if 'railway' in description_lower or 'travel' in description_lower or 'cmrl' in description_lower:
            found_keywords.append('travel')
        if 'paytm' in description_lower or 'phonepe' in description_lower or 'gpay' in description_lower:
            found_keywords.append('payment_app')
        
        # Check for other keywords
        for keyword in keywords:
            if keyword in description_lower:
                found_keywords.append(keyword)
        
        return ','.join(found_keywords) if found_keywords else 'other'
    
    def categorize(self, transaction):
        """
        Categorize a transaction using hybrid approach (rules first, then ML).
        
        Args:
            transaction: Dictionary containing transaction data
            
        Returns:
            Predicted category as a string
        """
        # Extract features
        features = self.extract_features(transaction)
        
        # Apply rule-based logic first
        if features['TransactionType'] == 'UPI' and features['HasPayee'] == 0 and abs(features['TransactionAmount']) < 200:
            return 'FOOD'  # UPI transactions without payee name and under $200
        elif features['TransactionType'] == 'UPI' and features['HasPayee'] == 1 and features['TransactionAmount'] < 0:
            return 'FRIENDS_FAMILY'  # UPI transactions with payee name
        elif abs(features['TransactionAmount']) > 200 and features['TransactionAmount'] < 0:
            return 'PURCHASES'  # Transactions over $200
        elif features['TransactionType'] == 'INTEREST' or features['TransactionAmount'] > 0:
            return 'INCOME'
            
        # Check keywords for specific categories
        keywords = features['Keywords'].lower() if isinstance(features['Keywords'], str) else ''
        
        if 'amazon' in keywords or 'shopping' in keywords:
            return 'SHOPPING'
        elif 'entertainment' in keywords:
            return 'ENTERTAINMENT'
        elif 'travel' in keywords:
            return 'TRAVEL'
        elif 'telecom' in keywords:
            return 'UTILITIES'
            
        # If no rules match and model is loaded, use ML model
        if self.model is not None and self.preprocessor is not None:
            # Keep only the features used in the model
            model_features = ['TransactionType', 'HasPayee', 'TransactionAmount', 
                             'DayOfWeek', 'IsWeekend', 'Month', 'IsRoundAmount',
                             'is_small_upi_no_payee', 'is_upi_with_payee', 'is_large_amount']
            
            features_df = pd.DataFrame([{k: features[k] for k in model_features if k in features}])
            
            # Fill missing features with zeros
            for feature in model_features:
                if feature not in features_df.columns:
                    features_df[feature] = 0
            
            # Preprocess the features
            features_processed = self.preprocessor.transform(features_df)
            
            # Predict using the model
            return self.model.predict(features_processed)[0]
            
        return 'OTHER'  # Default category if no rules match and no model is loaded
    
    def categorize_dataframe(self, df):
        """
        Categorize all transactions in a DataFrame.
        
        Args:
            df: pandas DataFrame containing transaction data
            
        Returns:
            DataFrame with added 'Category' column
        """
        categories = []
        for _, row in df.iterrows():
            categories.append(self.categorize(row))
            
        result_df = df.copy()
        result_df['Category'] = categories
        return result_df
    
    def categorize_csv(self, input_file, output_file=None):
        """
        Categorize all transactions in a CSV file.
        
        Args:
            input_file: Path to input CSV file
            output_file: Path to output CSV file (default: input_file + '_categorized.csv')
            
        Returns:
            DataFrame with added 'Category' column, and saves to output_file if provided
        """
        try:
            # Load the CSV
            df = pd.read_csv(input_file)
            
            # Categorize transactions
            result_df = self.categorize_dataframe(df)
            
            # Save to output file if provided
            if output_file:
                result_df.to_csv(output_file, index=False)
                print(f"Categorized transactions saved to {output_file}")
            
            return result_df
            
        except Exception as e:
            print(f"Error processing CSV file: {e}")
            return None
