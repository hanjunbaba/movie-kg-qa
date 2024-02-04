import streamlit as st
from streamlit_chatbox import *
import time
from question import question_from_user
from answer import answer_from_robot
from streamlit_agraph import agraph, Config
from match_mov_peo import match_things
from st_aggrid import AgGrid, GridOptionsBuilder

def kg_graph(nodes, edges):
    config = Config(width=500,
                    height=500,
                    directed=False, 
                    physics=True, 
                    hierarchical=False,
                    # **kwargs
                    )
    return agraph(nodes=nodes, edges=edges, config=config)

chat_box = ChatBox(
    assistant_avatar="./imgs/robot.png",
    user_avatar="./imgs/user.png",
    greetings=[':rose: **Hi!** **你好呀！** :rose:',
                ':robot_face: :rainbow[我是一个基于电影知识图谱的问答机器人小张同学，我有很多功能：]',
                ':gray[——————] :one: **电影知识图谱问答功能** :woman-gesturing-ok: :gray[——————]',
                ':gray[——————] :two: **相关部分知识图谱展示** :man-gesturing-ok: :gray[——————]',
                ':orange[**——————————————————————————————————**]',
                ':robot_face: :rainbow[我的知识中包含超过4000部电影的演员、导演、编剧及上映信息，示例如下：]',
                ':gray[——————] :one: **《XXX》这部电影的演员有谁？**:raising_hand:  :gray[ ——————]',
                ':gray[——————] :two: **由 XXX 导演的作品有哪些？**:man-raising-hand: :gray[ ——————]',
                ':gray[——————] :three: **介绍下《XXX》这部电影？**:man-raising-hand: :gray[————]',
                ':robot_face: :rainbow[请注意，在向我提问时请将电影名用《书名号》括起来哦！] :rose:',
                ':orange[**——————————————————————————————————**]']
        )


with st.sidebar:
    st.header('电影知识图谱问答系统')
    tab1, tab2 = st.tabs(["模糊搜索","知识图谱"])
    with tab1:
        col1, col2 = st.columns([1, 3])
        with col1:
            option = st.selectbox('搜索内容', ['电影', '人物'],index=1) 
        with col2:
            name = st.text_input('请在此输入名称: ')
        col3, col4 = st.columns(2)
        with col3:
            num = st.number_input(label='查询数量', min_value=0, max_value=10, value=3, step=1)
        with col4:
            rate = st.number_input(label='相似度', min_value=0.0, max_value=1.0, value=0.5, step=0.1)
        if st.button('搜索'):
            # st.dataframe(match_things(name, option, num, rate), width=500)
            df = match_things(name, option, num, rate)
            gb = GridOptionsBuilder.from_dataframe(df)
            go = gb.build()
            AgGrid(df, gridOptions=go, height=210, fit_columns_on_grid_load=True,reload_data=False)


chat_box.init_session()
chat_box.output_messages()

if query := st.chat_input('请输入您想问的问题……'):
    chat_box.user_say(query)
    ques = question_from_user(query)
    anwser = answer_from_robot(ques.IR, ques.EN, ques.mov, ques.li_mov)
    elements = chat_box.ai_say(
        [
            Markdown("正在思考。。。", in_expander=False,
                     expanded=True, title="answer"),
        ]
    )
    text = ""
    for x in anwser.answer_list:
        text += x + '<br>'
        chat_box.update_msg(text, element_index=0, streaming=True)
        chat_box.update_msg(text, element_index=0, streaming=False, state="complete")
    time.sleep(1)
    if anwser.prob_mov:
        aps = ''
        for ap in anwser.prob_mov:
            aps += ap+'<br>'
        chat_box.ai_say(
        [
            Markdown(aps, in_expander=True,
                     title="您可能要找的是：",state='complete'),
        ]
        )
    time.sleep(1)
    if anwser.simi_mov:
        sms = ''
        for sm in anwser.simi_mov:
            sms += sm+'<br>'
        chat_box.ai_say(
        [
            Markdown(sms, in_expander=True,
                    title="相关推荐：",state='complete'),
        ]
        )
    with st.sidebar:
        with tab2:
            kg_graph(anwser.all_nodes, anwser.all_edges)