import re
import jieba
#分词器
jieba.load_userdict(r"C:\Users\50738\Desktop\mvkg\data\word_dic\all.txt")

class question_from_user():#问题类
    def __init__(self, ques):
        self.Q = ques
        self.li_mov = self.load_enti_list('mov')#list
        self.li_dis = self.load_enti_list('dis')
        self.li_lan = self.load_enti_list('lan')
        self.li_mv = self.load_enti_list('mv')
        self.li_peo = self.load_enti_list('peo')
        self.li_year = self.load_enti_list('year')
        self.EN, ques_ = self.get_EN(ques, self.li_dis, self.li_lan, self.li_mv, self.li_peo, self.li_year)
        self.IR = self.get_IR(ques_)
        self.simi, self.mov = self.mov_match(self.li_mov,self.EN['电影'])#xx

    def load_enti_list(self,name):#读取实体文件
        f = open(r'./data/word_dic/'+name+'.txt','r', encoding='utf-8')
        return f.read().splitlines()    
    
    def get_IR(self, ques):#意图识别
        dic_classes = {    
            '导演' : ['导演','指导','执导'],
            '演员' : ['出演','演员','演出'],
            '编剧' : ['编剧'],
            '上映地区' : ['地区','地点','国家','地方','哪里','哪上映','哪播出','哪播的'], 
            '类型' : ['类型','类别','什么类','啥类'],
            '上映时间' : ['时候','什么时间','哪年','啥时间'],
            '语言' : ['语言','语种','什么语','啥语'],
            'rate' : ['评分','分值'], 
            'length' : ['时长','多长时间','几分钟','多久'],
            'url' : ['网址','链接','网站'],
            '介绍' : ['介绍','简介'],
            '推荐' : ['推荐'],
            }
        all_IR = []
        for i in dic_classes:
            for j in dic_classes[i]:
                if j in ques and i not in all_IR:
                    all_IR.append(i)
        return all_IR
    
    def mov_match(self, li_mov, en_mov):#找出输入正确的电影名及相似电影名
        simi = []
        right_name = []
        for em in en_mov:
            for lm in li_mov:
                if em in lm and em != lm:
                    simi.append(lm)
                if em == lm:
                    right_name.append(lm)
        return simi,right_name
    
    def match_word(self, word, li, li_):#判断实体是否出现在问题中
        for l in li:
            if word == l:
                li_.append(l)

    def get_EN(self, ques, li_dis, li_lan, li_mv, li_peo, li_year):#获取句子中所有实体
        ques_movie = re.findall("《(.*?)》",ques) #正则抽书名号内的电影名
        ques = re.sub(r'《.*?》', "",ques)
        ques_word_list = jieba.lcut(ques)
        enti_dicts = {}
        dis_ = []
        lan_ = []
        mv_ = []
        peo_ = []
        yea_ = []
        for wl in ques_word_list:
            self.match_word(wl,li_dis,dis_)
            self.match_word(wl,li_lan,lan_)
            self.match_word(wl,li_mv,mv_)
            self.match_word(wl,li_peo,peo_)
            self.match_word(wl,li_year,yea_)
        enti_dicts['电影'] = ques_movie
        enti_dicts['地区'] = dis_
        enti_dicts['语言'] = lan_
        enti_dicts['类别'] = mv_
        enti_dicts['人物'] = peo_
        enti_dicts['年份'] = yea_
        return enti_dicts, ques

        