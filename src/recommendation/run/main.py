import random
import pymysql
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import csv
import xgboost as xgb
from numpy import loadtxt
from xgboost import XGBClassifier
from xgboost import plot_importance
from xgboost import plot_tree

#파일경로 수정---------------------------------------------git 경로에 맞게 설정해야함 : train, test, train_y, model 사용
#import feature
#import dataset
#import model

# RDS와 연결 설정 
db = pymysql.connect(host="", port=3306, user="", passwd="",db="")

# import 함수 수정할 부분
train_x = train_result()
train_y = make_answer(train_x)
test = test_result()


# submission form
out_df=test[["order_id", "product_id","user_id"]]


# 최종 data set
# array 형식으로 변경 - id feature는 모두 drop, 바이너리 트리에 맞지 않은 정보
train_x = np.array(train_x.drop(["order_id", "user_id", "product_id","aisle_id","department_id"], axis=1))
test = test.drop(["order_id", "user_id", "product_id","aisle_id","department_id"], axis=1)
test = np.array(test)


# xgboost : 모델을 생성하기위한 데이터, 답, 모델 생성후 예측할 데이터
pred = model.runXGB(train_x, train_y, test)


temp = pred

cutoff = temp.mean()
temp[temp>=cutoff] = 1
temp[temp<cutoff] = 0


# 주문 번호랑 상품 번호에 맞춰서 칼럼 추가
out_df["Pred"] = temp
out_df.head()

# 재구매한다고 결과가 나온 것만 뽑아내기!
#  predict =1
out_df = out_df.ix[out_df["Pred"].astype('int')==1]


# 중복 제거
out_df = out_df.drop_duplicates()


### 구매할 거라고 예상한 product_id 연결
def merge_products(x):
    return " ".join(list(x.astype('str')))
    
    
############### kaggle 제출용
kaggle = out_df.groupby("order_id")["product_id"].aggregate(merge_products).reset_index()
kaggle.columns = ["order_id", "products"]

SQL = "SELECT order_id FROM submission"
sub_df = pd.read_sql(SQL, db)
sub_df = pd.merge(sub_df, kaggle, how="left", on="order_id")
sub_df["products"].fillna("None", inplace=True)
sub_df.to_csv("kaggle_n.csv", index=False)
del SQL

# random으로 한 개만 뽑기
product = list(map(lambda x: random.choice(x.split()) , sub_df['products']))

sub_df['products'] = product
sub_df.head()

# kaggle csv로 저장!!!!
sub_df["products"].fillna("None", inplace=True)
sub_df.to_csv("kaggle_1.csv", index=False)
del sub_df


############### user 기준 - 우리 프로젝트 결과
result = out_df.groupby("user_id")["product_id"].aggregate(merge_products).reset_index()

result.to_csv("user_n.csv", index=False)

product = list(map(lambda x: random.choice(x.split()) , result['product_id']))

result['product_id'] = map(int, product)
result.head()

# csv로 저장
result["product_id"].fillna(0, inplace=True)
result.to_csv("user_1.csv", index=False)
