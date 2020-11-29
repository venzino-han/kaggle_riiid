import pandas as pd

def lectureLabelChange(df):
    df["answered_correctly"].replace({-1: 1}, inplace=True)

def priorQuestionChange(df):
    df["prior_question_elapsed_time"].fillna(0., inplace=True)
    df["prior_question_had_explanation"].fillna(False, inplace=True)


''' 
누적 문제 수, 누적 정답 수
누적 정확도 계산 (with weight) 
df column 추가

# 특정 사용자가 이전 시점에 풀었던 문제들의 정확도
# 사용자별 누적 정확도 계산

# row 별로 계산 진행 --> 시계열 특성 고려
# i-1 까지
## 이전 정확도 * 이전문제 개수 * w + 정답여부 / w + 1
## w<1 w를 사용하여 과거데이터에 대한 가중치 조정
'''
def addAccumulateAcc(df, w):
    # 사용자 누적 정확도를 담을 dict
    userAccDict = {}
    accList = []
    countList = []
    rightNums = []

    # 시점별 누적 정확도 계산
    # 초기값 0.5 설정
    for i in range(len(df)):
        row = df.iloc[i]
        uid = row.user_id
        correct = row.answered_correctly

        if uid not in userAccDict:
            userAccDict[uid] = [1, 0, 0.5]  # num of quiz, num of correct, Acc
            accList.append(0.5)
            countList.append(0)
            rightNums.append(0)
        else:
            accList.append(userAccDict[uid][2])
            countList.append(userAccDict[uid][0] - 1)
            rightNums.append(userAccDict[uid][1])

        # 누적 정확도 계산 --> 다음 row에 추가
        # lecture 인 경우도 1로 통일
        if correct == 1:
            userAccDict[uid][1] += 1
            userAccDict[uid][2] = (userAccDict[uid][2] * userAccDict[uid][0] * w + 1) / (userAccDict[uid][0] * w + 1)
            userAccDict[uid][0] += 1
        else:
            userAccDict[uid][2] = (userAccDict[uid][2] * userAccDict[uid][0] * w + 0) / (userAccDict[uid][0] * w + 1)
            userAccDict[uid][0] += 1

    df['accumulate_user_acc'] = accList
    df['accumulate_user_count'] = countList
    df['accumulate_user_right'] = rightNums


'''
이전 K번 문제풀이 정확도 계산
최초 0.5 --> 이후 1회 이상일때는 평균 적용
'''
def addWindowAcc(df, k):
    # 이전 k번 동안 풀어온 문제 정확도
    # 사용자 단위 횟수 정확도를 담을 dict
    userAccDict = {}
    accList = []
    for i in range(len(df)):
        row = df.iloc[i]
        uid = row.user_id
        correct = row.answered_correctly

        if uid not in userAccDict:
            userAccDict[uid] = []  # num of quiz, num of correct, Acc
            accList.append(0.5)
        else:
            accList.append(sum(userAccDict[uid]) / len(userAccDict[uid]))

        userAccDict[uid].append(correct)
        if len(userAccDict[uid]) > k:
            userAccDict[uid].pop(0)

    df['k_user_acc'] = accList


## 문제의 정답률을 시점별로 정리
''' 
누적 정답률 계산
df column 추가

# 특정 문제의 이전 정확도 계산
# row 별로 계산 진행 --> 시계열 특성 고려
# i-1 까지

'''


def addAccumulateCountDiff(df):
    # 문제별 누적 정답률을 담을 dict
    quizDiffDict = {}
    countList = []
    diffList = []
    rightNums = []

    # 시점별 누적 정답률 계산
    # 초기값 0.5 설정
    for i in range(len(df)):
        row = df.iloc[i]
        qid = row.content_id
        correct = row.answered_correctly

        if qid not in quizDiffDict:
            quizDiffDict[qid] = [1, 0, 0.5]  # num of quiz, num of correct, diff
            diffList.append(0.5)
            countList.append(1)
            rightNums.append(0)
        else:
            diffList.append(quizDiffDict[qid][2])
            countList.append(quizDiffDict[qid][0])
            rightNums.append(quizDiffDict[qid][1])

        # 누적 정확도 계산 --> 다음 row에 추가
        if correct == 1:
            quizDiffDict[qid][1] += 1
            quizDiffDict[qid][2] = (quizDiffDict[qid][2] * quizDiffDict[qid][0] + 1) / (quizDiffDict[qid][0] + 1)
            quizDiffDict[qid][0] += 1
        else:
            quizDiffDict[qid][2] = (quizDiffDict[qid][2] * quizDiffDict[qid][0] + 0) / (quizDiffDict[qid][0] + 1)
            quizDiffDict[qid][0] += 1

    df['accumulate_quiz_count'] = countList
    df['accumulate_quiz_difficulty'] = diffList
    df['accumulate_quiz_correct'] = rightNums