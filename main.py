from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
import json

chrome_options = Options()
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-popup-blocking")  # Desativa bloqueio de pop-ups

navegador = webdriver.Chrome(options=chrome_options)
navegador.maximize_window()

navegador.get("https://www.smiles.com.br/home")

try:
    consent_button = WebDriverWait(navegador, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Aceitar')]"))
    )
    consent_button.click()
    time.sleep(2)  
except:
    print("Não foi necessário aceitar os cookies")

ida = WebDriverWait(navegador, 20).until(
    EC.presence_of_element_located((By.ID, "inp_flightOrigin_1"))
)
ida.click()
time.sleep(1)  

guarulhos_button = WebDriverWait(navegador, 20).until(
    EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'high') and contains(., 'Guarulhos')]"))
)
guarulhos_button.click()
time.sleep(2)  

volta = WebDriverWait(navegador, 20).until(
    EC.presence_of_element_located((By.ID, "inp_flightDestination_1"))
)
volta.click()
time.sleep(1)  

volta.send_keys("Miami")
time.sleep(2)  

miami_button = WebDriverWait(navegador, 20).until(
    EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'high') and contains(., 'Miami')]"))
)
miami_button.click()
time.sleep(2)  

ida_e_volta_button = WebDriverWait(navegador, 20).until(
    EC.element_to_be_clickable((By.ID, "drop_fligthType"))
)
ida_e_volta_button.click()
time.sleep(1)  

somente_ida_button = WebDriverWait(navegador, 20).until(
    EC.element_to_be_clickable((By.ID, "opt_oneWay"))
)
somente_ida_button.click()
time.sleep(1)  

campo_data = WebDriverWait(navegador, 20).until(
    EC.presence_of_element_located((By.ID, "inp_flightDate_1"))
)

campo_data.click()
time.sleep(2)

hoje = datetime.now()
data_formatada = hoje.strftime('%d/%m/%Y')

campo_data.clear()
campo_data.send_keys(data_formatada)
time.sleep(1)

buscar = WebDriverWait(navegador, 20).until(
    EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="btn-flight-submit"]'))
)
buscar.click()

WebDriverWait(navegador, 30).until(
    EC.presence_of_element_located((By.CLASS_NAME, "flight-list"))
)
time.sleep(5)

# Clicar em "Mostrar mais passagens" até não ter mais
while True:
    try:
        botao_mostrar_mais = WebDriverWait(navegador, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Mostrar mais passagens')]"))
        )
        navegador.execute_script("arguments[0].click();", botao_mostrar_mais)
        time.sleep(2)
    except:
        break

# Coletar todos os voos da página
voos = navegador.find_elements(By.CLASS_NAME, "flight-card-container")

dados_voos = []

for voo in voos:
    try:
        empresa = voo.find_element(By.CLASS_NAME, "airline-name").text
    except:
        empresa = None

    try:
        classe = voo.find_element(By.CLASS_NAME, "flight-class").text
    except:
        classe = None

    try:
        valor = voo.find_element(By.CLASS_NAME, "money-amount").text
    except:
        valor = None

    try:
        duracao = voo.find_element(By.CLASS_NAME, "flight-duration").text
    except:
        duracao = None

    try:
        horario_saida = voo.find_elements(By.CLASS_NAME, "time")[0].text
    except:
        horario_saida = None

    try:
        horario_chegada = voo.find_elements(By.CLASS_NAME, "time")[1].text
    except:
        horario_chegada = None

    dados_voos.append({
        "Empresa": empresa,
        "Classe": classe,
        "Valor": valor,
        "Duração": duracao,
        "Horário de Saída": horario_saida,
        "Horário de Chegada": horario_chegada
    })

print(f"Total de voos capturados: {len(dados_voos)}")

with open("voos_gru_mia.json", "w", encoding="utf-8") as f:
    json.dump(dados_voos, f, indent=4, ensure_ascii=False)

navegador.quit()
