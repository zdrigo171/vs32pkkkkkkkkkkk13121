#!/usr/bin/env python3
"""
Script de teste para verificar se o sistema está configurado corretamente.
"""

import sys
import os

def test_imports():
    """Testa se todas as dependências estão instaladas"""
    print("Testando importações...")
    
    try:
        import flask
        print(f"✓ Flask {flask.__version__} instalado")
    except ImportError:
        print("✗ Flask não encontrado")
        return False
    
    try:
        import selenium
        print(f"✓ Selenium {selenium.__version__} instalado")
    except ImportError:
        print("✗ Selenium não encontrado")
        return False
    
    try:
        from selenium import webdriver
        print("✓ WebDriver disponível")
    except ImportError:
        print("✗ WebDriver não disponível")
        return False
    
    return True

def test_files():
    """Testa se todos os arquivos necessários existem"""
    print("\nTestando arquivos...")
    
    required_files = [
        'app.py',
        'requirements.txt',
        'templates/login.html',
        'templates/mfa.html',
        'templates/new_location.html',
        'static/placeholder.txt'
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} não encontrado")
            all_exist = False
    
    return all_exist

def test_chrome():
    """Testa se o Chrome/ChromeDriver está disponível"""
    print("\nTestando Chrome/ChromeDriver...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.get('https://www.google.com')
        driver.quit()
        print("✓ Chrome/ChromeDriver funcionando")
        return True
    except Exception as e:
        print(f"✗ Erro com Chrome/ChromeDriver: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("=== Teste de Configuração do Sistema Discord Login ===\n")
    
    tests_passed = 0
    total_tests = 3
    
    if test_imports():
        tests_passed += 1
    
    if test_files():
        tests_passed += 1
    
    if test_chrome():
        tests_passed += 1
    
    print(f"\n=== Resultado: {tests_passed}/{total_tests} testes passaram ===")
    
    if tests_passed == total_tests:
        print("✓ Sistema pronto para uso!")
        print("\nPara iniciar o sistema, execute:")
        print("python app.py")
    else:
        print("✗ Alguns problemas precisam ser resolvidos antes de usar o sistema.")
        
        if tests_passed < 2:
            print("\nInstale as dependências com:")
            print("pip install -r requirements.txt")

if __name__ == "__main__":
    main()
