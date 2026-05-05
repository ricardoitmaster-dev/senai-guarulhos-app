# --- INTERFACE (TRECHO CORRIGIDO) ---
path_logo = os.path.join("imagens", "logo.png")
path_fachada = os.path.join("imagens", "fachada.jpg")

# Logo (Já estava correto, mas mantive a estrutura)
if os.path.exists(path_logo):
    logo_base = get_base64_of_bin_file(path_logo)
    st.markdown(f'''
        <div class="logo-container">
            <div class="moldura-3d-ajustada" style="width:150px; margin: 0 auto;">
                <img src="data:image/png;base64,{logo_base}">
            </div>
        </div>
    ''', unsafe_allow_html=True)

st.markdown('<div class="header-senai"><h1>SENAI GUARULHOS</h1><p>Unidade 122 - Registro de Interesse Profissional</p></div>', unsafe_allow_html=True)

# Fachada (CORREÇÃO AQUI: adicionado display: table para a caixa se ajustar à imagem)
if os.path.exists(path_fachada):
    fachada_base = get_base64_of_bin_file(path_fachada)
    st.markdown(f'''
        <div style="text-align: center;">
            <div class="moldura-3d-ajustada" style="display: inline-block; width: auto; max-width: 80%;">
                <img src="data:image/jpeg;base64,{fachada_base}" style="display: block; width: auto; max-height: 400px;">
            </div>
        </div>
    ''', unsafe_allow_html=True)
