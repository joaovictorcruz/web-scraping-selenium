from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
from datetime import datetime
import json

chrome_options = Options()
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-popup-blocking")

navegador = webdriver.Chrome(options=chrome_options)
navegador.maximize_window()

navegador.get("https://www.smiles.com.br/home")

try:
    consent_button = WebDriverWait(navegador, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Aceitar')]"))
    )
    time.sleep(1.5)
    consent_button.click()
    time.sleep(2)
except TimeoutException:
    print("Não foi necessário aceitar os cookies.")

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
    EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'high') and contains(., 'Miami, Estados Unidos')]"))
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

campo_data_ida = WebDriverWait(navegador, 20).until(
    EC.element_to_be_clickable((By.ID, "startDateId"))
)
campo_data_ida.click()
time.sleep(2)

hoje = datetime.now().day
mes_atual = datetime.now().month
ano_atual = datetime.now().year

id_data_atual = f"date_{hoje}{mes_atual}{ano_atual}"
print(f"ID da data de hoje: {id_data_atual}")

td_data_atual = WebDriverWait(navegador, 20).until(
    EC.presence_of_element_located((By.XPATH, f"//td/span[@id='{id_data_atual}']/.."))
)
td_data_atual.click()
time.sleep(1)

botao_confirmar = WebDriverWait(navegador, 20).until(
    EC.element_to_be_clickable((By.ID, "btn_confirmCalendar"))
)

if "disabled" not in botao_confirmar.get_attribute("class"):
    botao_confirmar.click()
    print("Data confirmada!")
else:
    print("O botão 'Confirmar' ainda está desabilitado.")

time.sleep(2)

botao_buscar = WebDriverWait(navegador, 20).until(
    EC.element_to_be_clickable((By.ID, "btn_search"))
)
botao_buscar.click()
time.sleep(1.5)

modal_content = WebDriverWait(navegador, 20).until(
    EC.visibility_of_element_located((By.CLASS_NAME, "modal-content"))
)

botao_seguinte = WebDriverWait(navegador, 20).until(
    EC.element_to_be_clickable((By.ID, "btn_sameDayInternational"))
)
botao_seguinte.click()
time.sleep(5)

# --- Página de voos ---
dias_verificados = 0
max_dias = 10
dia_base = hoje

lista_voos = []

while dias_verificados < max_dias:
    time.sleep(2)

    not_found_elements = navegador.find_elements(By.CLASS_NAME, "select-flight-not-found-card")

    if not_found_elements:
        print(f"Dia {dias_verificados + 1}: Nenhum voo encontrado, tentando próximo dia...")

        try:
            botao_calendario = WebDriverWait(navegador, 20).until(
                EC.element_to_be_clickable((By.ID, "SelectFlightToolbar-button-calender-ida"))
            )
            botao_calendario.click()
            time.sleep(2)

            dia_procurar = dia_base + dias_verificados + 1
            id_dia = f"day-{dia_procurar}"

            proximo_dia_elemento = WebDriverWait(navegador, 20).until(
                EC.element_to_be_clickable((By.ID, id_dia))
            )
            proximo_dia_elemento.click()
            print(f"Selecionado novo dia: {dia_procurar}/{mes_atual}/{ano_atual}")

            botao_confirmar_nova_data = WebDriverWait(navegador, 20).until(
                EC.element_to_be_clickable((By.ID, "SelectFlightCalendar-search-button"))
            )
            botao_confirmar_nova_data.click()
            time.sleep(5)

        except TimeoutException:
            print(f"Não foi possível selecionar o dia {dia_procurar}. Tentando seguir...")
            break

    else:
        print(f"Dia {dias_verificados + 1}: Voos disponíveis, capturando...")

        # --- Novo código para clicar até acabar o botão ---
    while True:
        try:
            botao_mais_passagens = WebDriverWait(navegador, 5).until(
                EC.element_to_be_clickable((By.ID, "SelectFlightList-ida-more"))
            )
            botao_mais_passagens.click()
            print("Botão 'Mostrar mais passagens' clicado!")
            time.sleep(3)  # Espera carregar mais voos
        except TimeoutException:
            print("Nenhum botão 'Mostrar mais passagens' encontrado. Todos os voos carregados.")
            break

        voos = navegador.find_elements(By.CLASS_NAME, "header")
        print(f"Encontrados {len(voos)} voos.")

        for idx, voo in enumerate(voos, start=1):
            try:
                companhia = voo.find_elements(By.CLASS_NAME, "company")
                companhia = companhia[0].text if companhia else "Não informado"

                classe = voo.find_elements(By.CLASS_NAME, "seat")
                classe = classe[0].text if classe else "Não informado"

                horarios = voo.find_elements(By.CLASS_NAME, "iata-code")
                horario_partida = horarios[0].text if len(horarios) > 0 else "Não informado"
                horario_chegada = horarios[1].text if len(horarios) > 1 else "Não informado"

                duracao = voo.find_elements(By.CLASS_NAME, "scale-duration__time")
                duracao = duracao[0].text if duracao else "Não informado"

                preco = voo.find_elements(By.CLASS_NAME, "miles")
                preco = preco[0].text if preco else "Não informado"

                print(f"\nVoo {idx}: {companhia} | {classe} | {horario_partida} -> {horario_chegada} | {duracao} | {preco}")

                lista_voos.append({
                    "dia_pesquisado": f"{dia_base + dias_verificados}/{mes_atual}/{ano_atual}",
                    "companhia": companhia,
                    "classe": classe,
                    "horario_partida": horario_partida,
                    "horario_chegada": horario_chegada,
                    "duracao_voo": duracao,
                    "preco": preco
                })

            except Exception as e:
                print(f"Erro ao capturar voo {idx}: {e}")
                continue

        try:
            botao_proximo_dia = WebDriverWait(navegador, 20).until(
                EC.element_to_be_clickable((By.ID, "SelectFlightToolbar-button-next-day-ida"))
            )
            botao_proximo_dia.click()
            print("Avançando para o próximo dia...")
            time.sleep(15)
        except TimeoutException:
            print("Não foi possível clicar para próximo dia.")
            break

    dias_verificados += 1

with open("voos_encontrados.json", "w", encoding="utf-8") as f:
    json.dump(lista_voos, f, ensure_ascii=False, indent=4)

print("Finalizado: 10 dias verificados e voos salvos no arquivo 'voos_encontrados.json'.")
time.sleep(5)
navegador.quit()
