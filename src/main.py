__author__ = 'Raymond Macharia <raymond.machira@gmail.com>'

import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from math import sqrt
import numpy as np

class Analysis:
    sentiment_dicts = []
    id_dicts = []
    data = None

    def read_sentiments(self):
        with open("alchemyapi/output.csv") as file:
            # discard first line
            for line in file.readlines()[1:]:
                line = line.split(",")
                # print line
                # print {'id': int(line[0]),'s_value':float(line[2])}
                self.sentiment_dicts.append({'id': int(line[0]),'s_value':float(line[2])})

    def read_ids(self):
        with open("data/WA_data.csv") as file:
            for line in file.readlines()[1:]:
                line = line.split(',')
                self.id_dicts.append({'year':int(line[0]),
                                      'status':line[1],
                                      'gender':line[2],
                                      'ID':int(line[3]),
                                      'R_list_ind':int(line[4])})
            # self.id_dicts = list(csv.DictReader(file))

    def create_data_frame(self):
        id_data = pd.DataFrame(self.id_dicts)
        # print self.sentiment_dicts
        sentiment_data = pd.DataFrame(self.sentiment_dicts)

        self.data = pd.merge(id_data, sentiment_data, how='left', left_on='R_list_ind', right_on='id')


    def male_female_diff(self):
        self.mine_t_test_cat('gender','m','f','Male','Female')

        ax = self.data.boxplot(column='s_value', by='gender', return_type='axes')
        # count_female, average_female ,var_female = self.gender_stats('f')
        #
        # count_male, average_male ,var_male = self.gender_stats('m')
        #
        # print count_female,average_female,var_female
        # print count_male, average_male, var_male
        #
        # # self.t_test_cat('gender','m','f',label="T-Test of Avg. Male vs Female sentiment")
        # # T Statistic
        # tstat =  self.mine_t_test(average_female,average_male,var_female,var_male,count_female,count_male)
        # # P value
        # print tstat
        # print stats.distributions.t.cdf(tstat,count_female+count_male-2)



    def plot(self):
        # plt.show()
        plt.scatter(self.data.year,self.data.s_value)
        plt.show()


    def basic_stats_for_category(self, category, value):
        grp = self.data[(self.data[category] == value) & self.data.s_value]
        count = grp.count(axis=0)['s_value']
        average = grp.mean(axis=0,skipna=True)['s_value']
        variance = grp.var(axis=0,skipna=True)['s_value']

        return count, average, variance


    def print_descriptively(self, label, data):
        print "\nNumbers for %s WAs" % label
        print "Number: %d \n" \
              "Mean: %.2f \n" \
              "Variance: %.2f" % data

    def mine_t_test_cat(self, category, values1, values2, label1="", label2=""):
        m, u1, var1 = self.basic_stats_for_category(category, values1)
        n, u2, var2 = self.basic_stats_for_category(category, values2)

        if label1 != "" and label2 != "":
            print"################## Performing T-Tests for %s vs %s WAs ################## "% (label1,label2)
            self.print_descriptively(label1, (m,u1,var1))
            self.print_descriptively(label2,(n, u2, var2))

        print "\nAssuming Equal variance: "
        sp = sqrt(((var1 * (m-1.0) + var2 * (n-1.0)))/(n+m-2.0))
        num = u1-u2
        denom = (sp * sqrt(1.0/m + 1.0/n))
        t_value = num/denom

        print "\nt_value: %.2f" % (t_value)

        p_value = stats.distributions.t.cdf(t_value,n+m-2)

        print "p-value for t: %.2f \n\n" % (p_value)

    def new_returning(self):
        print("\n\n"
              "##############################"
              "Sentiments of (New - Returning) WAs"
              "##################################")

        new_wa = self.data[(self.data.status == 'NEW') & self.data.s_value]
        ret_wa = self.data[(self.data.status == 'RET') & self.data.s_value]
        pair_deltas = []

        n_ids = new_wa['ID'].values
        r_ids = ret_wa['ID'].values

        for id in n_ids:
            if id in r_ids:
                t = new_wa[new_wa.ID == id].s_value.values
                s = ret_wa[ret_wa.ID == id].mean(axis=0).s_value
                pair_deltas.append(t-s)


        self.print_descriptively(label="Numbers for New WAs", data=(len(n_ids),new_wa.mean().s_value,new_wa.var().s_value))
        self.print_descriptively(label="Numbers for Returning WAs", data=(len(r_ids),ret_wa.mean().s_value,ret_wa.var().s_value))


        new_male_was = self.data[(self.data.ID in n_ids) & (self.data.gender == 'm')].s_value
        new_female_was = self.data(self.data.ID in r_ids) & (self.data.gender == 'f')].s_value
        # mean_pair_deltas = np.mean(pair_deltas)
        # var_pair_deltas = np.std(pair_deltas,ddof=1,dtype=np.float64)
        # t_pair_deltas = mean_pair_deltas/(var_pair_deltas/sqrt(len(pair_deltas)+0.0))
        t_pair_deltas, p_value_pair_deltas = stats.ttest_1samp(pair_deltas, 0)

        self.print_descriptively(label="New vs Returning WAs",
                                 data=(len(pair_deltas),np.mean(pair_deltas),np.var(pair_deltas)))
        print("T_score: %.4f" % t_pair_deltas)
        print("P_value: %.4f" % p_value_pair_deltas)


if __name__ == '__main__':
    a = Analysis()
    a.read_sentiments()
    a.read_ids()
    a.create_data_frame()
    a.male_female_diff()
    a.new_returning()
    # a.plot()
    plt.show()




    # def gender_stats(self,gender):
    #     frm = self.data[(self.data.gender==gender) & self.data.s_value]
    #     count = frm.count(axis=0)['s_value']
    #     average = frm.mean(axis=0, skipna=True)['s_value']
    #     variance = frm.var(axis=0,skipna=True)['s_value']
    #     return count, average, variance