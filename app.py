# app.py

from flask import Flask, request, render_template
import pandas as pd

# 커스텀 파일
from myeasyocr import OCR
from decision import I_P, connect_division_to_recommend


app = Flask(__name__)
app.debug=True

# 전역변수로 지정 ( 함수 두개에서 같이 사용하기 때문 )
ocr_result = []

# Main page
@app.route('/')
def start():
    return render_template('index0.html')

@app.route('/main')
def main():
    return render_template('index1.html')

@app.route('/ques_type')
def question():
    return render_template('index2.html')

@app.route('/ques_concern', methods=['GET', 'POST'])
def question_type():        
    return render_template('index3.html')

@app.route('/typeResult', methods=['GET', 'POST'])
def typeResult():
    # 앞에서 체크한 피부고민 받아오기
    type = request.args.get('type')
    concern_list = request.args.get('concern_list')
    
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('error.html')
        file = request.files.get('file')
        if not file:
            return render_template('error.html')

        img_bytes = file.read()
        
        # txt 파일 불러오기 : user_dictionary는 전역으로 불러와야함
        with open("data/user_dictionary.txt", "r", encoding='utf-8') as file:
            strings = file.readlines()
        user_dictionary = [x.replace('\n','') for x in strings]
        
        ocr = OCR()
        ocr_result = ocr.ocrWord(img_bytes, user_dictionary)  # OCR결과 전역변수에 저장 (추천시스템에서 사용)
        print(ocr_result)
        
        # 사용자의 피부타입과 피부고민에 안좋은 성분 리스트
        ip = I_P(concern_list, type)
        ingred_list = ip.c_p()
        print(ingred_list)
        
        # 성분 설명 파일 불러오기
        df = pd.read_csv('./data/ingred_info.csv', encoding="CP949")
        
        # 안좋은 성분 리스트
        result = []
        
        # 안좋은 성분 설명 리스트
        result_info = []
        
        for i in ocr_result:
            if i in ingred_list:
                result.append(i)
                desc = df.loc[df['성분명'] == i, '성분 설명'].values
                if len(desc) > 0:
                    result_info.append(' : '+ str(desc[0]).replace('[','').replace(']',''))
                else:
                    result_info.append('')

        # 안좋은 성분 갯수
        cnt = len(result)
        
        return render_template('index5.html', type=type, cnt=cnt, result=result, result_info=result_info, concern_list=concern_list)

    return render_template('index4.html')

@app.route('/select', methods=['GET', 'POST'])
def select() :
    type = request.args.get('type')
    concern_list = request.args.get('concern_list')  
    concern_list = eval((concern_list))    # 배열로 변환
    
    ip = I_P(concern_list, type)
    prod_type = request.args.get('prod_type')

    # 선택창에서 받아온 제품종류 prod_type 값이 있으면 :
    if prod_type:
        
        # 사용자 제품성분 (OCR 데이터)와 피부타입, 피부고민 (ip 객체)를 이용해서 추천제품 top5 받아오기
        fr = connect_division_to_recommend(ocr_result, ip)
        if prod_type == '스킨/토너':
            # fr.base_check('파일명')
            df = fr.base_check('skin_toner')
        elif prod_type == '로션/에멀젼':
            df = fr.base_check('lotion')
        elif prod_type == '올인원':
            df = fr.base_check('allinone')
        elif prod_type == '에센스/세럼':
            df = fr.base_check('essence')
        elif prod_type == '크림':
            df = fr.base_check('cream')
        elif prod_type == '아이크림':
            df = fr.base_check('eye_cream')
        elif prod_type == '미스트/픽서':
            df = fr.base_check('mist_fixer')
        elif prod_type == '페이스오일':
            df = fr.base_check('faceoil')
        
        # 추천제품을 보여주기 위한 제품리스트 top5 ( 제품명, 제품이미지, 제품구매링크, 제품가격, 1ml당 가격)
        prod_list = [df.iloc[0]['이름'],df.iloc[1]['이름'],df.iloc[2]['이름'],df.iloc[3]['이름'],df.iloc[4]['이름']]
        prod_img = [df.iloc[0]['img_src'],df.iloc[1]['img_src'],df.iloc[2]['img_src'],df.iloc[3]['img_src'],df.iloc[4]['img_src']]
        prod_href = [df.iloc[0]['href'],df.iloc[1]['href'],df.iloc[2]['href'],df.iloc[3]['href'],df.iloc[4]['href']]
        prod_price = [str(df.iloc[0]['가격']).replace('.0','원'),str(df.iloc[1]['가격']).replace('.0','원'),
                      str(df.iloc[2]['가격']).replace('.0','원'),str(df.iloc[3]['가격']).replace('.0','원'),str(df.iloc[4]['가격']).replace('.0','원')]
        prod_price_rate = [str(df.iloc[0]['1ml당 가격']), str(df.iloc[1]['1ml당 가격']), str(df.iloc[2]['1ml당 가격']),
                           str(df.iloc[3]['1ml당 가격']), str(df.iloc[4]['1ml당 가격'])]
        
        return render_template('index6.html', type=type, concern_list=concern_list, prod_type=prod_type, prod_list=prod_list, prod_img=prod_img, prod_href=prod_href, prod_price=prod_price, prod_price_rate=prod_price_rate)
    
    return render_template('index6.html', type=type, concern_list=concern_list , prod_type=prod_type)

@app.route('/test', methods=['GET', 'POST'])
def test() :
    return render_template('index7.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5003, debug=True)