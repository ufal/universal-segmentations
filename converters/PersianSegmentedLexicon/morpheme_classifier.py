from collections import Counter
class MorphemeClassifier:
    def __init__(self):
        self.morph_cntr=Counter()

    def Update(self, morph_list):
        self.morph_cntr.update(morph_list)

    #returns list of morph classes. It has the same order as the provided morph list
    def Guess(self, morph_list):
        len_=len(morph_list)
        if(len_<1):
            return None
        elif(len_==1):
            return ["root"]

        min_id =0
        min_cnt=self.morph_cntr.get(morph_list[0],0)
        i=1
        while i<len_:
            cnt=self.morph_cntr.get(morph_list[i],0)
            if(cnt<min_cnt and morph_list[i]!=""):
                min_id=i
                min_cnt=cnt
            i+=1

        class_list=[]
        i=0
        while i<len_:
            if(i<min_id):
                class_list.append("prefix")
            elif(i==min_id):
                class_list.append("root")
            else:
                class_list.append("suffix")
            i+=1
        return class_list