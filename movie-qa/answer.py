from py2neo import Graph
from streamlit_agraph import agraph, Node, Edge, Config
import difflib

#知识图谱连接参数
uri = ""
username = ""
password = ""

class answer_from_robot():
    def __init__(self, IR, en_dict, right_name, mov_li):
        self.graph = Graph(uri, auth=(username,password))
        self.IR = IR
        self.en_dict = en_dict
        self.right_name = right_name
        self.mov_li = mov_li
        self.simi_mov, self.prob_mov = self.get_simi_prob(self.en_dict, self.right_name,self.mov_li)
        self.answer_list, self.all_nodes, self.all_edges = self.answer_ques(self.IR, self.en_dict, self.right_name)
    
    def answer_ques(self, IR, en_dict, right_name):
        easy_ques = ['导演','演员','编剧','上映地区','类型','上映时间','语言']
        shuxing_ques = ['rate','url','length']
        node = []
        edge = []
        all_nodes = []
        all_edges = []
        all_answers = []
        if not IR:
            all_answers.append('脑子炸了呀，没明白您的意思o(╥﹏╥)o')
        for ir in IR:
            if ir in easy_ques:
                answers, nodes, edges, node, edge = self.esay_answers(en_dict, right_name, ir, node, edge)
                all_answers.extend(answers)
                all_nodes.extend(nodes)
                all_edges.extend(edges)
                
            if ir in shuxing_ques:
                answers, nodes, edges, node = self.shuxing_answers(en_dict, right_name, ir, node)
                all_answers.extend(answers)
                all_nodes.extend(nodes)
                all_edges.extend(edges)

            if ir == '介绍':
                for eq in easy_ques:
                    answers, nodes, edges, node, edge = self.esay_answers(en_dict, right_name, eq, node, edge)
                    all_answers.extend(answers)
                    all_nodes.extend(nodes)
                    all_edges.extend(edges)
                    
                for sq in shuxing_ques:
                    answers, nodes, edges, node = self.shuxing_answers(en_dict, right_name, sq, node)
                    all_answers.extend(answers)
                    all_nodes.extend(nodes)
                    all_edges.extend(edges)
            if ir == '推荐':
                all_answers.extend(self.reco_answers())
        return all_answers, all_nodes, all_edges

    def esay_answers(self, en_dict, right_name, relation, node, edge):#导演、演员、编剧、上映地区、类型、上映时间、语言
        nodes = []
        edges = []
        color = 'yellow'
        only_mov = ['上映地区','类型','上映时间','语言']
        if relation == '上映地区':
            color = 'blue'
        if relation == '类型':
            color = 'red'
        if relation == '上映时间':
            color = 'orange'
        if relation == '语言':
            color = 'gray'
        answers = []
        if en_dict['电影']:
            for n in en_dict['电影']:
                if n in right_name:
                    answer = self.graph.run("MATCH (:Movie {name:'" + n + "'})-[:"+relation+"]-(p) RETURN p").data()
                    if n not in node:
                        nodes.append(Node(id=n, 
                                    label=n, 
                                    size=25, 
                                    color='green',))
                        node.append(n)
                    if not answer:
                        www = self.graph.run("MATCH (m:Movie{name:'" + n + "'}) RETURN m.url").data()
                        answers.append('暂时缺少《'+n+'》'+relation+'相关信息，详情可以通过下面的网址进行查询：')
                        answers.append(n+' : '+www[0]['m.url'])
                    else:
                        r = ''
                        for an in answer:
                            r += an['p']['name'] + ' '
                            if an['p']['name'] not in node:
                                nodes.append(Node(id=an['p']['name'], 
                                            label=an['p']['name'], 
                                            size=25, 
                                            color=color,))
                                node.append(an['p']['name'])
                            if (n, an['p']['name']) not in edge:
                                edges.append(Edge(source=n, 
                                            label=relation, 
                                            target=an['p']['name'], ))
                                edge.append((n, an['p']['name']))
                        answers.append('《'+n+'》'+'的'+relation+'：' + r)

                else:
                    answers.append('暂时缺少《'+n+'》'+relation+'相关信息，请核对电影名')
        if en_dict['人物'] and relation not in only_mov:
            for n in en_dict['人物']:
                answer = self.graph.run("MATCH (m)-[:"+relation+"]-(:People {name:'" + n + "'}) RETURN m").data()
                if n not in node:
                    nodes.append(Node(id=n, 
                                label=n, 
                                size=25, 
                                color=color,))
                    node.append(n)
                if not answer:
                    answers.append('暂时缺少' + n +'作为'+ relation+'的电影的相关信息')
                else:
                    r = ''
                    for an in answer:
                        r += '《' + an['m']['name'] + '》 '
                        if an['m']['name'] not in node:
                            nodes.append(Node(id=an['m']['name'], 
                                        label=an['m']['name'], 
                                        size=25, 
                                        color='green',))
                            node.append(an['m']['name'])
                        if (n, an['m']['name']) not in edge:
                            edges.append( Edge(source=n, 
                                        label=relation, 
                                        target=an['m']['name'], ))
                            edge.append((n, an['m']['name']))
                    answers.append(n+'作为'+ relation+'的影视作品：' + r)
        if not en_dict['电影'] and not en_dict['人物']:
            answers.append('缺少电影或人物信息，请核对电影名或人物姓名后再次提问 ||-_-||')
        return answers, nodes, edges, node, edge
    
    def shuxing_answers(self, en_dict, right_name, relation, node):
        nodes = []
        edges = []
        answers = []
        if en_dict['电影']:
            for n in en_dict['电影']:
                if n in right_name:
                    answer = self.graph.run("MATCH (m:Movie {name:'" + n + "'}) RETURN m."+relation).data()
                    if n not in node:
                        nodes.append(Node(id=n, 
                                    label=n, 
                                    size=25, 
                                    color='green',))
                        node.append(n)
                    if not answer:
                        www = self.graph.run("MATCH (m:Movie{name:'" + n + "'}) RETURN m.url").data()
                        answers.append('暂时缺少《'+n+'》评分相关信息，详情可以通过下面的网址进行查询：')
                        answers.append(n+' : '+www[0]['m.url'])
                    else:
                        r = ''
                        for an in answer:
                            r += str(an['m.'+relation])
                        if relation == 'rate':
                            answers.append('《'+n+'》'+'的豆瓣评分是：' + r)
                        if relation == 'length':
                            answers.append('《'+n+'》'+'的时长是：' + r)
                        if relation == 'url':
                            answers.append('《'+n+'》'+'的豆瓣影视链接是：' + r)
        else:
            answers.append('缺少电影信息，请核对电影名后再次提问 ||-_-||')
        return answers, nodes, edges, node
    
    def reco_answers(self):
        return ['功能未开通']
    
    def get_simi_prob(self, en_dict, right_name, mov_li):
        simi_mov = []
        prob_mov = []
        for n in en_dict['电影']:
            if n in right_name:
                simi_mov.extend(difflib.get_close_matches(n, mov_li, 10, cutoff=0.5))
            else:
                prob_mov.extend(difflib.get_close_matches(n, mov_li, 10, cutoff=0.5))
        return simi_mov, prob_mov
    
