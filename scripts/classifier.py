from __future__ import division, print_function
from sklearn.ensemble import RandomForestClassifier
from sklearn import tree 

from sklearn import preprocessing
from sklearn import metrics
from sklearn import svm
from sklearn.cross_validation import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn import tree
import pymysql as mdb
import numpy as np
import pandas as pd




def main():

    db = mdb.connect(user="root", host="localhost", db="scotus", charset='utf8')
    d = pd.read_sql("""SELECT docket, interrupted, amicus, words_BREYER, words_GINSBURG, 
        words_KENNEDY, words_ROBERTS, words_SCALIA, winner 
        FROM cases ORDER BY docket;""", con=db)

    
    feature_names = ['amicus', 'interrupted', 'words_BREYER', 'words_GINSBURG', 'words_KENNEDY', 'words_ROBERTS', 'words_SCALIA']
#    feature_names = ['amicus','interrupted', 'words_KENNEDY']
## After adding the word counts, removing amicus seems to improve the estimates.
## Interruptions do not have high feature weight (0.029) but removing them lowers precision, recall, and F1 across the board. 
## Kennedy's words carry the least weight among the justices, indicating that perhaps his speech is the least predictive of the outcome. Doesn't reveal much. That is IF the order is preserved...




    print(feature_names)

    print(d.shape)
    d_gold_start = int(d.shape[0] * 0.8)
    d_gold = d.iloc[d_gold_start:]
    d_rest = d.iloc[:d_gold_start]
    #print(d.head())





    X = d_rest[feature_names].values.astype(np.float)    
    y = preprocessing.LabelEncoder().fit_transform(d_rest.winner)
    
    ## Split into training and testing sets
#    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25)    

    ## Ensure the same split occurs every time we run the program, for now, to compare methods and hyperparameters
    this_test_start = X.shape[0] * 0.75 
    X_train = X[:this_test_start,]
    X_test = X[this_test_start:,]
    y_train = y[:this_test_start]
    y_test = y[this_test_start:]



    ## Define a scoring function with the Matthew correlation coefficient for cross-validation with unbalanced data
    mc_scorer = metrics.make_scorer(metrics.matthews_corrcoef)

    ##################### Random Forest #####################
    print('\nRandom Forest analyses:')   
    RF = RandomForestClassifier(n_estimators=100)
    RF_fit = RF.fit(X_train,y_train)
    RF_pred = RF_fit.predict(X_test)

    ## Feature importances are helpful
    print('\n\tRF feature_importances:', RF_fit.feature_importances_)
    
    print(metrics.classification_report(y_test, RF_pred))
    print(metrics.confusion_matrix(y_test, RF_pred))
    print('Test Accuracy:', RF_fit.score(X_test,y_test))
    print('Test Matthews corrcoef', metrics.matthews_corrcoef(y_test, RF_pred))
    
    RF_scores = cross_val_score(RF, X, y, cv=5, scoring=mc_scorer)
    print('\nCross-validation scores:', RF_scores)
    print("CV Avg Matthews CC: %0.2f (+/- %0.2f)" % (RF_scores.mean(), RF_scores.std() * 2))    
    print('-'*20)
    ## Transform removes the lower-importance features from the dataset and returns a trimmed input dataset. 
    ## In this case it removed the interruptions, but we already saw that removing them lowered performance.
    ## Was I overfitting?
    #print(RF.transform(X))

    ##################### Decision Tree #####################
#     print('\nDecision Tree analyses:')
#     DT = tree.DecisionTreeClassifier(max_depth=None, min_samples_split=1, random_state=0)
#     DT_fit = DT.fit(X_train, y_train)
#     DT_pred = DT_fit.predict(X_test)
# 
#     print(metrics.classification_report(y_test, DT_pred))
#     print(metrics.confusion_matrix(y_test, DT_pred))
#     print('Test Accuracy:', DT_fit.score(X_test,y_test))
#     print('Test Matthews corrcoef', metrics.matthews_corrcoef(y_test, DT_pred))
#    
#     DT_scores = cross_val_score(DT, X, y, cv=5, scoring=mc_scorer)
#     print('\nCross-validation scores:', DT_scores)
#     print("CV Avg Matthews CC: %0.2f (+/- %0.2f)" % (DT_scores.mean(), DT_scores.std() * 2))    
#     print('-'*20)
# 
#     #tree.export_graphviz(DT, out_file='tree.dot', feature_names=feature_names, max_depth=5) 


    ##################### SVM #####################
    print('\nSVM analyses:')
    my_svm = svm.SVC(C=0.2, kernel='linear', probability=True)
    svm_fit = my_svm.fit(X_train, y_train)
    svm_pred = svm_fit.predict(X_test)
    #SVC(C=1.0, cache_size=200, class_weight=None, coef0=0.0, degree=3, gamma=0.0, kernel='rbf', max_iter=-1, probability=False, random_state=None, shrinking=True, tol=0.001, verbose=False)

    print(metrics.classification_report(y_test, svm_pred))
    print(metrics.confusion_matrix(y_test, svm_pred))
    print('Test Accuracy:', svm_fit.score(X_test,y_test))
    print('Test Matthews corrcoef', metrics.matthews_corrcoef(y_test, svm_pred))
    
    SVM_scores = cross_val_score(my_svm, X, y, cv=5, scoring=mc_scorer)
    print('\nCross-validation scores:', SVM_scores)
    print("CV Avg Matthews CC: %0.2f (+/- %0.2f)" % (SVM_scores.mean(), SVM_scores.std() * 2))    
    
    #print(my_svm.predict([[-1, 1]]))


    
if __name__ == '__main__':
    main()
