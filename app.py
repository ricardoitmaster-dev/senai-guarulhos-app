# No seu CSS, substitua ou adicione estas linhas:

st.markdown("""
    <style>
    /* Ajuste para que a moldura 3D envolva a imagem sem sobras */
    .moldura-fachada-ajustada {
        display: inline-block; /* Faz a caixa ter o tamanho exato do conteúdo */
        border-radius: 25px;
        box-shadow: 10px 10px 20px #bebebe, -10px -10px 20px #ffffff; /* O efeito 3D */
        border: 4px solid #e0e5ec;
        line-height: 0; /* Remove espaços vazios na base da imagem */
        overflow: hidden;
    }
    
    .moldura-fachada-ajustada img {
        width: 100%; /* A imagem ocupa todo o espaço da moldura */
        max-width: 800px; /* Você pode controlar o tamanho máximo aqui */
        height: auto;
        display: block;
    }
    </style>
    """, unsafe_allow_html=True)

# E na parte onde você exibe a fachada:
if os.path.exists(path_fachada):
    fachada_base = get_base64_of_bin_file(path_fachada)
    st.markdown(f'''
        <div style="text-align:center; padding: 20px;">
            <div class="moldura-fachada-ajustada">
                <img src="data:image/jpeg;base64,{fachada_base}">
            </div>
        </div>
    ''', unsafe_allow_html=True)
