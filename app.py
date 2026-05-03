def salvar_dados(df):
    try:
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sheet_id = extrair_id_planilha(url)
        
        # --- CORREÇÃO AQUI: Limpa valores NaN e substitui por vazio ---
        # Isso impede o erro de "Invalid JSON payload"
        df = df.fillna("") 
        
        # Prepara os dados: cabeçalho + valores
        valores = [df.columns.values.tolist()] + df.values.tolist()
        body = {"values": valores}
        
        service.spreadsheets().values().update(
            spreadsheetId=sheet_id, 
            range="A1", 
            valueInputOption="RAW", 
            body=body
        ).execute()
        return True
    except Exception as e:
        # Exibe o erro de forma mais amigável
        st.error(f"Erro ao salvar: {e}")
        return False
