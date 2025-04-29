from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from datetime import datetime, timedelta
import json

chrome_options = Options()
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--ignore-certificate-errors") 

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

dia_base = datetime.now().day
mes_atual = datetime.now().month
ano_atual = datetime.now().year

id_data_atual = f"date_{dia_base}{mes_atual}{ano_atual}"
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
    botao_confirmar.click()

time.sleep(2)

botao_buscar = WebDriverWait(navegador, 20).until(
    EC.element_to_be_clickable((By.ID, "btn_search"))
)
botao_buscar.click()
time.sleep(1.5)

try:
    modal_content = WebDriverWait(navegador, 20).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "modal-content"))
    )
    botao_seguinte = WebDriverWait(navegador, 20).until(
        EC.element_to_be_clickable((By.ID, "btn_sameDayInternational"))
    )
    botao_seguinte.click()
    time.sleep(5)
except TimeoutException:
    print("Modal não apareceu, continuando...")

# --- Página de voos ---
dias_verificados = 0
max_dias = 10
lista_voos = []

while dias_verificados < max_dias:
    time.sleep(2)

    not_found_elements = navegador.find_elements(By.CLASS_NAME, "select-flight-not-found-card")

    if not_found_elements:
        print(f"Dia {dias_verificados + 1}: Nenhum voo encontrado, tentando próximo dia...")
    else:
        print(f"Dia {dias_verificados + 1}: Voos disponíveis, capturando...")

    # Carregar todos os voos disponíveis
    while True:
        try:
            botao_mais_passagens = WebDriverWait(navegador, 5).until(
                EC.element_to_be_clickable((By.ID, "SelectFlightList-ida-more"))
            )
            botao_mais_passagens.click()
            print("Botão 'Mostrar mais passagens' clicado!")
            time.sleep(3)
        except TimeoutException:
            print("Todos os voos carregados para o dia.")
            break

    voos = navegador.find_elements(By.CLASS_NAME, "header")
    print(f"Encontrados {len(voos)} voos.")
    
    for idx, voo in enumerate(voos, start=1):
        try:
            company_seat = voo.find_elements(By.CSS_SELECTOR, "p.company-and-seat")
            if company_seat:
                companhia = voo.find_element(By.XPATH, ".//p[contains(@class, 'company-and-seat')]/span[@class='company']").text if voo.find_elements(By.XPATH, ".//p[contains(@class, 'company-and-seat')]/span[@class='company']") else "Não informado"
                classe = voo.find_element(By.XPATH, ".//p[contains(@class, 'company-and-seat')]/span[@class='seat']").text if voo.find_elements(By.XPATH, ".//p[contains(@class, 'company-and-seat')]/span[@class='seat']") else "Não informado"
            
            horarios = voo.find_elements(By.CLASS_NAME, "iata-code")
            horario_partida = horarios[0].text if len(horarios) > 0 else "Não informado"
            horario_chegada = horarios[1].text if len(horarios) > 1 else "Não informado"
            
            duracao = voo.find_element(By.CLASS_NAME, "scale-duration__time").text if voo.find_elements(By.CLASS_NAME, "scale-duration__time") else "Não informado"
            preco = voo.find_element(By.CLASS_NAME, "miles").text if voo.find_elements(By.CLASS_NAME, "miles") else "Não informado"

            data_voo = datetime(ano_atual, mes_atual, dia_base) + timedelta(days=dias_verificados)

            lista_voos.append({
                "dia_pesquisado": data_voo.strftime("%d/%m/%Y"),
                "companhia": companhia,
                "classe": classe,
                "horario_partida": horario_partida,
                "horario_chegada": horario_chegada,
                "duracao_voo": duracao,
                "preco": preco
            })

        except Exception as e:
            print(f"Erro ao capturar voo {idx}: {str(e)}")
            continue

    # Navegar para o próximo dia

    try:
        navegador.execute_script("window.scrollTo(0, 0);")
        time.sleep(1.5)

        botao_calendario = WebDriverWait(navegador, 20).until(
            EC.element_to_be_clickable((By.ID, "SelectFlightToolbar-button-calender-ida"))
        )
        botao_calendario.click()
        time.sleep(2)

        proxima_data = datetime(ano_atual, mes_atual, dia_base) + timedelta(days=dias_verificados + 1)
        dia_alvo = proxima_data.day
        mes_alvo = proxima_data.month
        ano_alvo = proxima_data.year

        print(f"Tentando selecionar {dia_alvo}/{mes_alvo}/{ano_alvo}")

        # encontrar o dia no calendário
        encontrado = False
        tentativas = 0
        
        while not encontrado and tentativas < 3:
            try:
                dia_elemento = WebDriverWait(navegador, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f"//div[@class='flight-calendar-wrapper']//div[@data-testid='day-{dia_alvo}']//div[contains(@class, 'flight-calendar-custom-day') and not(contains(@class, 'disabled'))]"))
                )
                dia_elemento.click()
                print(f"Selecionado dia {dia_alvo} usando data-testid")
                encontrado = True
            except:
                try:
                    # Se não encontrar, tentamos pelo ID renderDay
                    data_formatada = proxima_data.strftime("%a %b %d %Y").replace(" 0", " ")
                    dia_elemento = WebDriverWait(navegador, 5).until(
                        EC.element_to_be_clickable((By.XPATH, f"//div[contains(@id, 'renderDay-{data_formatada}') and not(contains(@class, 'disabled'))]"))
                    )
                    dia_elemento.click()
                    print(f"Selecionado dia {dia_alvo} usando renderDay")
                    encontrado = True
                except:
                    try:
                        # Se ainda não encontrar, tentar pelo texto do dia
                        dia_elemento = WebDriverWait(navegador, 5).until(
                            EC.element_to_be_clickable((By.XPATH, f"//div[@class='flight-calendar-wrapper']//span[@class='day' and text()='{dia_alvo}']/ancestor::div[contains(@class, 'flight-calendar-custom-day') and not(contains(@class, 'disabled'))]"))
                        )
                        dia_elemento.click()
                        print(f"Selecionado dia {dia_alvo} usando texto do dia")
                        encontrado = True
                    except:
                        # se não encontrar em nenhum dos métodos acima, tentar mudar de mês
                        try:
                            if tentativas < 2:  # 
                                botao_proximo_mes = WebDriverWait(navegador, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, "//span[@data-testid='calendar-arrow-right' and not(contains(@class, 'disabled'))]"))
                                )
                                botao_proximo_mes.click()
                                print("Clicado no botão de próximo mês")
                                time.sleep(2)
                        except:
                            pass
                        tentativas += 1

        if not encontrado:
            raise Exception(f"Não foi possível selecionar o dia {dia_alvo} após {tentativas} tentativas")

        botao_confirmar_nova_data = WebDriverWait(navegador, 20).until(
            EC.element_to_be_clickable((By.ID, "SelectFlightCalendar-search-button"))
        )
        botao_confirmar_nova_data.click()
        time.sleep(5)

    except Exception as e:
        print(f"Erro ao selecionar próximo dia: {str(e)}")
        navegador.save_screenshot(f"erro_dia_{dias_verificados+1}.png")
        break

    dias_verificados += 1

with open("voos_encontrados.json", "w", encoding="utf-8") as f:
    json.dump(lista_voos, f, ensure_ascii=False, indent=4)

print(f"Finalizado: {dias_verificados} dias verificados e {len(lista_voos)} voos salvos no arquivo 'voos_encontrados.json'.")
navegador.quit()