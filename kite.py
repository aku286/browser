from kiteconnect import KiteConnect

# Initialize Kite API
api_key = "vheh9zojsp1lmfo5"         # Replace with your API key
api_secret = "hufp5q3ffmykw81092zxth2q1rd70owu"    # Replace with your API secret
kite = KiteConnect(api_key=api_key)

# Generate the login URL
login_url = kite.login_url()
print("Login URL:", login_url)

# After logging in through the login_url, you will receive a request token
# Paste your request token here
request_token = "e4SmE8Rb1hG7frcg2kvYvwQ9eC7NyO8y"

# Generate session (access_token)
try:
    data = kite.generate_session(request_token, api_secret=api_secret)
    access_token = data["access_token"]
    kite.set_access_token(access_token)
    print("Access Token:", access_token)
except Exception as e:
    print("Error generating session:", e)

# Test connection - Fetch user profile
try:
    profile = kite.profile()
    print("Profile:", profile)
except Exception as e:
    print("Error fetching profile:", e)
