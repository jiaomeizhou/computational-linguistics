import sys, os, re
from pyltp import *

from nltk import DependencyGraph


class LtpParsing(object):
    def __init__(self, model_dir='D:/Downloads/ltp_data_v3.4.0'):
        self.segmentor = Segmentor()
        self.segmentor.load(os.path.join(model_dir, "cws.model"))
        self.postagger = Postagger()
        self.postagger.load(os.path.join(model_dir, "pos.model"))
        self.parser = Parser()
        self.parser.load(os.path.join(model_dir, "parser.model"))

    def par(self, infilm, outfilm):
        input_data = open(infilm, 'r', encoding='utf-8')
        output_data = open(outfilm, 'w+', encoding='utf-8')
        for line in input_data.readlines():
            line = line.strip()
            # 分词
            words = self.segmentor.segment(line)
            # self.segmentor.load_with_lexicon('lexicon')  # 使用自定义词典，lexicon外部词典文件路径
            #print('分词：' + '\t'.join(words))

            # 词性标注
            postags = self.postagger.postag(words)
            # print('词性标注：' + '\t'.join(postags))

            # 句法分析
            arcs = self.parser.parse(words, postags)
            rely_id = [arc.head for arc in arcs]  # 提取依存父节点id
            relation = [arc.relation for arc in arcs]  # 提取依存关系
            heads = ['Root' if id == 0 else words[id - 1] for id in rely_id]  # 匹配依存父节点词语

            output_data.write(line)
            output_data.write('\n')
            par_result = ''
            for i in range(len(words)):
                if arcs[i].head == 0:
                    arcs[i].relation = "ROOT"
                par_result += "\t" + words[i] + "(" + arcs[i].relation + ")" + "\t" + postags[i] + "\t" + str(
                    arcs[i].head) + "\t" + arcs[i].relation + "\n"
                output_data.write(relation[i] + '(' + words[i] + ', ' + heads[i] + ')' + '\n')
            # 识别程度补语
            degree_word = ['极', '很', '透','慌', '死', '坏', '多', '万分', '一些', '一点']
            for i in range(len(words)):
                if ('ADV' == relation[i] or 'CMP' == relation[i]) and any(_ in words[i] for _ in degree_word):
                    output_data.write(line + '语法点：程度补语' + '\n')
            # 识别地点状语
            place_word = ['在', '里', '上', '下', '中', '外']
            for i in range(len(words)):
                if 'ADV' == relation[i] and (words[i] == '在' or words[i] == '里'):
                    output_data.write(line + '语法点：地点状语' + '\n')
            # 识别动量补语
            measure_word = ['次', '遍', '回', '趟', '下', '顿', '声', '阵', '番', '遭', '场']
            for i in range(len(words)):
                if ('CMP' == relation[i] or 'ATT' == relation[i]) and any(_ in words[i] for _ in measure_word):
                    output_data.write(line + '语法点：动量补语' + '\n')
            # 识别兼语句
            causative_verb = ['请', '要求', '建议', '让', '使', '叫', '派', '命令', '吩咐', '禁止', '请求', '选举', '教', '劝', '号召']
            if 'DBL' in relation and any(_ in words for _ in causative_verb):
                output_data.write(line + '语法点：兼语句' + '\n')
            # 结果补语
            result_word = ['完', '懂', '成', '好', '光', '饱', '对', '错']
            for i in range(len(words)):
                if 'CMP' == relation[i] and any(_ in words[i] for _ in result_word):
                    output_data.write(line + '语法点：结果补语' + '\n')
            # 可能补语
            potential_word = ['得', '不', '了']
            for i in range(len(words)):
                if 'RAD' == relation[i] and words[i] == '得':
                    output_data.write(line + '语法点：可能补语' + '\n')
                elif 'ADV' == relation[i] and words[i] == '不':
                    output_data.write(line + '语法点：可能补语' + '\n')
            # 趋向补语
            trend_word = ['上', '去', '来', '过去', '上去']
            for i in range(len(words)):
                if 'CMP' == relation[i] and any(_ in words[i] for _ in trend_word):
                    output_data.write(line + '语法点：趋向补语' + '\n')
                elif 'ADV' == relation[i] and words[i] == '去':
                    output_data.write(line + '语法点：趋向补语' + '\n')
                elif 'ATT' == relation[i] and words[i] == '过去':
                    output_data.write(line + '语法点：趋向补语' + '\n')
            # 时间状语
            time_word = ['小时', '后来', '分钟', '天', '星期', '时候', '年', '过去', '将来', '正', '现在', '早', '晚', '周', '月', '节', '初', '午']
            for i in range(len(words)):
                if 'ATT' == relation[i] and any(_ in words[i] for _ in time_word):
                    output_data.write(line + '语法点：时间状语' + '\n')
                elif 'ADV' == relation[i] and any(_ in words[i] for _ in time_word):
                    output_data.write(line + '语法点：时间状语' + '\n')
            # 时量补语
            for i in range(len(words)):
                if 'CMP' == relation[i] and any(_ in words[i] for _ in time_word):
                    output_data.write(line + '语法点：时量补语' + '\n')
                if 'ATT' == relation[i] and any(_ in words[i] for _ in time_word):
                    output_data.write(line + '语法点：时量补语' + '\n')
            # 双宾语
            for i in range(len(words)):
                if 'IOB' == relation[i] and 'ATT' == relation[i+1] and ('VOB' == relation[i+2] or 'VOB' == relation[i+3] or 'VOB' == relation[i+4]):
                    output_data.write(line + '语法点：双宾语' + '\n')
                elif 'HED' == relation[i] and 'CMP' == relation[i+1] and 'ATT' == relation[i+2]:
                    output_data.write(line + '语法点：双宾语' + '\n')

            #print(par_result)
            #conlltree = DependencyGraph(par_result)  # 转换为依存句法图
            #tree = conlltree.tree()  # 构建树结构
            #tree.draw()  # 显示输出的树
            output_data.write('\n')
        input_data.close()
        output_data.close()

    def release_model(self):
        # 释放模型
        self.segmentor.release()
        self.postagger.release()
        self.parser.release()


if __name__ == '__main__':
    infilm = 'data/双宾语.txt'
    outfilm = 'data/双宾语_output2.txt'
    ltp = LtpParsing()
    ltp.par(infilm, outfilm)
    ltp.release_model()