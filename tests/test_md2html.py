import markdown2

md_str = f"""<p style="color:cyan">Prompt Tokens count: [10]</p>\n以下是三位名人的列表：

1. **Elon Musk**  
   ![Elon Musk](https://upload.wikimedia.org/wikipedia/commons/thumb/e/ed/Elon_Musk_Royal_Society.jpg/220px-Elon_Musk_Royal_Society.jpg)  
   Elon Musk是一位企业家和工程师，也是多家知名科技公司的创始人之一，包括特斯拉汽车、SpaceX太空探索技术公司和Neuralink脑机接口公司。他以其对可持续能源、电动汽车和太空探索的积极推动而闻名。

2. **Oprah Winfrey**  
   ![Oprah Winfrey](https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Oprah_Winfrey_2010.jpg/220px-Oprah_Winfrey_2010.jpg)  
   奥普拉·温弗瑞是美国的一位知名电视主持人、制片人和慈善家。她主持过自己的著名脱口秀节目《奥普拉秀》长达25年之久，并在媒体界取得了巨大成功。奥普拉也积极参与慈善事业，致力于改善教育、妇女权益和儿童福利等领域。

3. **Barack Obama**  
   ![Barack Obama](https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/President_Barack_Obama.jpg/220px-President_Barack_Obama.jpg)  
   巴拉克·奥巴马是美国历史上第44任总统，也是美国历史上首位非洲裔总统。他在任期内推动了包括医疗保健改革、经济复苏和气候变化政策在内的一系列重要议程。奥巴马以其鼓励多元化、倡导平等和推动社会变革的领导风格而备受赞誉
<p style="color:cyan">Response Tokens count: [551] [stop]</p>
"""
html_str = markdown2.markdown(md_str)
print(html_str)
