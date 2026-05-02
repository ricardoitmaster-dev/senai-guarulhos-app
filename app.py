# --- LÓGICA DE ENVIO (COM FEEDBACK AO USUÁRIO) ---
if btn:
    # Verifica se os campos obrigatórios foram preenchidos
    if nome and email and area_sel != "Selecione..." and curso_sel != "Selecione...":
        if service:
            df_atual = ler_dados()
            
            # Criando o novo registro
            novo = pd.DataFrame([{
                "nome": nome, 
                "email": email, 
                "whatsapp": whats, 
                "area": area_sel, 
                "curso": curso_sel, 
                "sugestao": sugestao, 
                "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }])
            
            # Tentativa de salvar no Google Sheets (Sua conexão que já funciona)
            if salvar_dados(pd.concat([df_atual, novo], ignore_index=True)):
                # --- ESTA É A MENSAGEM QUE VOCÊ SOLICITOU ---
                st.success(f"### ✅ Sucesso, {nome}!")
                st.info("Seu interesse foi registrado em nosso sistema. **Assim que o curso for aberto, a equipe do SENAI Guarulhos 122 entrará em contato através dos dados informados.**")
                st.balloons()
            else:
                st.error("Erro técnico ao salvar os dados. Por favor, tente novamente em instantes.")
    else:
        st.warning("Por favor, preencha todos os campos (Nome, E-mail, Área e Curso) para prosseguir.")
