def salvar_novo_lead(lista_dados):
    try:
        service = conectar_google_sheets()
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        # Extrai o ID da planilha da URL
        sheet_id = url.split("/d/")[1].split("/")[0]
        
        # O segredo está aqui: usamos o nome da aba (ex: 'Página1') ou apenas 'A1'
        # O método 'append' vai encontrar a última linha preenchida e adicionar abaixo
        range_name = "A1" 
        
        body = {
            "values": [lista_dados]
        }
        
        service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range=range_name,
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS", # Garante que ele insira uma nova linha
            body=body
        ).execute()
        return True
    except Exception as e:
        print(f"Erro técnico: {e}")
        return False
