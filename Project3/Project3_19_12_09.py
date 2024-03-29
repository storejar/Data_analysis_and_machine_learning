# -*- coding: utf-8 -*-
"""
Created on Tue Dec 10 17:10:41 2019

@author: annam
"""

import pandas as pd
import os
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import SGDClassifier
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, accuracy_score, roc_auc_score
from sklearn import metrics
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import scikitplot as skplt
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.svm import SVC
import xgboost as xgb
import seaborn as sns
import time
import shap
from matplotlib import pyplot


#read data and create a dataframe
cwd = os.getcwd()
filename = cwd + '/online_shoppers_intention.csv'
nanDict = {}
df = pd.read_csv(filename, sep=',', header=0, na_values=nanDict)

print(df.shape)

print(pd.DataFrame(df))

# exploratory data analysis

plt.rc('font', size=15)
fig=plt.figure(figsize=(10,10))
sums = df.Revenue.groupby(df.Month).sum()
plt.title(r'Revenue by month', fontsize=20)
plt.pie(sums, labels=sums.index);
fig.savefig('revenue_by_month.png')
plt.show()
plt.close()

fig=plt.figure(figsize=(9,9))
sums1 = df.Revenue.groupby(df.VisitorType).sum()
plt.title(r'Revenue by visitor type', fontsize=20)
plt.pie(sums1, labels=sums1.index);
fig.savefig('revenue_by_vis_type.png')
plt.show()
plt.close()

fig=plt.figure(figsize=(6,6))
sns.countplot(df['Revenue'])
plt.title(r'Revenue rate', fontsize=20)
plt.show()
fig.savefig('revenue_rate.png')
plt.close()

plt.rcdefaults()

print(df)
df.describe()

# data preprocessing


df.isnull().sum() #counts how many null values there are in each column

df.dropna(inplace=True) #drops rows with null values in columns and updates the dataframe automatically


# delete rows which contain -1 for duration values
df_m = np.asmatrix(df)
print(df_m.shape)
delete_rows = []
for row in range(df_m.shape[0]):
    #print(df_m[row,0])
    if int(df_m[row,0]) == 0:
        if int(df_m[row,1]) != 0:
            delete_rows.append(row)
            first = True 
    if int(df_m[row,2]) == 0:
        if int(df_m[row,3]) != 0:
            first = True 
            if row in delete_rows:
                first = False
            if first == True:
                delete_rows.append(row)
    if int(df_m[row,4]) == 0:
        if int(df_m[row,5]) != 0:
            first = True 
            if row in delete_rows:
                first = False
            if first == True:
                delete_rows.append(row)
    if int(df_m[row,1]) < 0:
        first = True 
        if row in delete_rows:
            first = False
        if first == True:
            delete_rows.append(row)
    if int(df_m[row,3]) < 0:
        first = True 
        if row in delete_rows:
            first = False
        if first == True:
            delete_rows.append(row)
    if int(df_m[row,5]) == -1:
        first = True 
        if row in delete_rows:
            first = False
        if first == True:
            delete_rows.append(row)
a=df.iloc[delete_rows, :]
list_df=a.index
df = df.drop(list_df)

print(df)

# we now want to create dummy variabiles for categorical variables.
# we remove revenue from the design matrix, because it will then become our response variable
df2 = df.drop(['Revenue'], axis=1)
print(df2.columns)
X = pd.get_dummies(df2,drop_first=True) #drop first drops the first level in order to get k-1 variables starting from k

X.Weekend = X.Weekend.astype(int)
print(pd.DataFrame(X))
#print(X.shape)
#x_1 = np.asmatrix(X)
#print(pd.DataFrame(x_1[10:17]))
X.head()
columnsNamesArr = X.columns.values
print(X.shape)
y = df['Revenue']
print(y.shape)
# =============================================================================
# df_m=np.delete(df_m, delete_rows, axis=0)
# print(df_m.shape)
# print(pd.DataFrame(df_m))
# =============================================================================


y = y.astype(int) #consider y now as a dummy variable
print(y)

scalar = StandardScaler()
X = scalar.fit_transform(X)
X = pd.DataFrame(X)
X.columns = columnsNamesArr

fig1=plt.figure(figsize=(20,15))
# use the heatmap function from seaborn to plot the correlation matrix
# annot = True to print the values inside the square
ax0=sns.heatmap(data=df2.corr().round(2), annot=True)
bottom, top = ax0.get_ylim()
ax0.set_ylim(bottom + 0.5, top - 0.5)
plt.title(r'Correlation heatmap', fontsize=25)
plt.show()
fig1.savefig('corr_matrix.png')
plt.close()

pca = PCA()
pca.fit(X)
cumsum = np.cumsum(pca.explained_variance_ratio_)
d = np.argmax(cumsum >= 0.95) + 1
print(d)
pca = PCA(n_components=0.95)
X_reduced = pca.fit_transform(X)
print(X_reduced)

#split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)
X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(X_reduced, y, test_size=0.20, random_state=42)


# Logistic Regression

print("\n Building Logistic Regression")

lr = LogisticRegression(random_state=42)
model_lr = lr.fit(X_train,y_train)
y_pred_lr = model_lr.predict(X_test)
print("\n Accuracy of Logistic Regression: ",accuracy_score(y_test,y_pred_lr))
print("\n AUC of Logistec Regression: ",metrics.roc_auc_score(y_test,y_pred_lr)*100)

# confusion matrix
plt.rc('font', size=13)
h=skplt.metrics.plot_confusion_matrix(y_test, y_pred_lr, normalize=True, title='Logistic regression confusion matrix')
print(h.yaxis_inverted())
fig=h.get_figure()
#plt.ylim([-0.5, 1.5])
plt.ylim([1.5, -0.5])
plt.show()
fig.savefig('CM_LR.png')
plt.close()
plt.rcdefaults()

# Logistic Regression after PCA
print("\n Building Logistic Regression")
model_lr_r = lr.fit(X_train_r,y_train_r)
y_pred_lr_r = model_lr_r.predict(X_test_r)
print("\n Accuracy of Logistic Regression: ",accuracy_score(y_test_r,y_pred_lr_r))
print("\n AUC of Logistec Regression: ",metrics.roc_auc_score(y_test_r,y_pred_lr_r)*100)


# confusion matrix
skplt.metrics.plot_confusion_matrix(y_test_r, y_pred_lr_r, normalize=True)
plt.ylim([-0.5, 1.5])
plt.show()


# Random Forest

print("\n Building Random Forest Model")
# Random Forest
model_rf_classi = RandomForestClassifier()
model_rf = model_rf_classi.fit(X_train,y_train)
y_pred_enrf = model_rf.predict(X_test)
print("\n Done")
print("\n Accuracy of Random Forest: ",accuracy_score(y_test,y_pred_enrf))
print("\n AUC of Random Forest: ",metrics.roc_auc_score(y_test,y_pred_enrf)*100)
print("Training Accuracy :", model_rf.score(X_train, y_train))
print("Testing Accuracy :", model_rf.score(X_test, y_test))


list_n_trees=[]
list_accur=[]
list_auc_rf=[]
n_trees_l=[1,10,100,500,1000,2000]
for n_trees in n_trees_l:
    t0 = time.time()
    model = RandomForestClassifier(n_estimators=n_trees, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred_rf = model.predict(X_test)
    
    # evaluating the model
    print("Number of trees:", n_trees)
    print("Training Accuracy :", model.score(X_train, y_train))
    print("Testing Accuracy :", model.score(X_test, y_test))
    print("\n Accuracy of Random Forest (i.e. test acc): ",accuracy_score(y_test,y_pred_rf))
    print("\n AUC of Random Forest: ",metrics.roc_auc_score(y_test,y_pred_rf)*100)
    print (time.time()-t0,"seconds process time")
    
    list_n_trees.append(n_trees)
    list_accur.append(model.score(X_test, y_test))
    list_auc_rf.append(metrics.roc_auc_score(y_test,y_pred_rf)*100)

best_acc = max(list_accur)
print(best_acc)
print(max(list_auc_rf))

# Random Forest with 100 trees - accuracy is better, AUC is better for 2000 trees but it does not differ much from the 100 one, we stick with that
model_rf_classi = RandomForestClassifier(n_estimators=100, random_state=42)
model_rf = model_rf_classi.fit(X_train,y_train)
y_pred_enrf = model_rf.predict(X_test)
print("\n Done")
print("\n Accuracy of Random Forest: ",accuracy_score(y_test,y_pred_enrf))
print("\n AUC of Random Forest: ",metrics.roc_auc_score(y_test,y_pred_enrf)*100)
print("Training Accuracy :", model_rf.score(X_train, y_train))
print("Testing Accuracy :", model_rf.score(X_test, y_test))

fig1=plt.figure(figsize=(12,9))
plt.plot(list_n_trees, list_accur, label='Accuracy')
plt.ylabel(r'Accuracy',fontsize=20)
plt.xlabel(r'Number of trees',fontsize=20)
plt.title(r'Accuracy vs number of trees for RF',fontsize=20)
plt.legend(fontsize=20)
fig1.savefig('RF_accur_vs_trees.png')
plt.show()
plt.close()

# confusion matrix
plt.rc('font', size=13)
h=skplt.metrics.plot_confusion_matrix(y_test, y_pred_rf, normalize=True, title='Random forests confusion matrix')
print(h.yaxis_inverted())
fig=h.get_figure()
#plt.ylim([-0.5, 1.5])
plt.ylim([1.5, -0.5])
plt.show()
fig.savefig('CM_RF.png')
plt.close()
plt.rcdefaults()

# Support Vector Machine

# Support Vector Machine
print("\n Building Support Vector Machine")

for ker in ('linear', 'rbf', 'poly'):
    svc = SVC(kernel=ker)
    model = svc.fit(X_train,y_train)
    y_pred_svc = model.predict(X_test)
    print("\n Kernel:",ker)
    print("\n Accuracy of SVM: ",accuracy_score(y_test,y_pred_svc))
    print("\n AUC of SVM: ",metrics.roc_auc_score(y_test,y_pred_svc)*100)

list_accur_svm=[]   
list_auc_svm=[]
list_results=[]
list_c=[]
list_g=[]
c_vals =[0.1,1,10,100]
g_vals =[0.001,0.01,0.1]
for c in c_vals:
    for g in g_vals:
        svc = SVC(kernel='rbf', C=c, gamma=g, random_state=42)
        model = svc.fit(X_train,y_train)
        y_pred_svc = model.predict(X_test)
        print("\n Kernel:",'rbf')
        print("\n C:",c)
        print("\n gamma:",g)
        print("\n Accuracy of SVM: ",accuracy_score(y_test,y_pred_svc))
        print("\n AUC of SVM: ",metrics.roc_auc_score(y_test,y_pred_svc)*100)
        list_accur_svm.append(accuracy_score(y_test,y_pred_svc))
        list_auc_svm.append(metrics.roc_auc_score(y_test,y_pred_svc)*100)
        list_results.append((accuracy_score(y_test,y_pred_svc),metrics.roc_auc_score(y_test,y_pred_svc)*100,'rbf',c,g))
        list_c.append(c)
        list_g.append(g)    
print(list_results)

def calc_edges(lmbd_vals):
    border=3
    edges=np.zeros(len(lmbd_vals)+1)
    edges[0]=border*lmbd_vals[0]/10
    for i in range(1,len(edges)):
        edges[i]=border*lmbd_vals[i-1]
    #print(edges)
    return edges

edges_c = calc_edges(c_vals)
edges_g = calc_edges(g_vals)
                            
plt.rc('font', size=20)
fig1=plt.figure(figsize=(12,9))
fig1, ax1 = plt.subplots(figsize=(12,9))
h1=plt.hist2d(list_c, list_g, weights=list_accur_svm, bins=(edges_c,edges_g))
ax1.set_aspect("equal")
hist, xbins, ybins, im = ax1.hist2d(list_c, list_g, weights=list_accur_svm, bins=(edges_c,edges_g))
scale_hist=3 #position of numbers in histogram fields
for i in range(len(ybins)-1):
    for j in range(len(xbins)-1):
        ax1.text(scale_hist*xbins[j],scale_hist*ybins[i], round(hist[j,i],3), 
                color="w", ha="center", va="center", fontweight="bold", fontsize=25)
plt.colorbar(h1[3])
plt.xlabel(r'C values',fontsize=20)
plt.ylabel(r'Gamma',fontsize=20)
plt.title(r'SVC accuracy',fontsize=20)
plt.xscale('log')
plt.yscale('log')
fig1.savefig('SVC_accuracy.png')
plt.show()
plt.close()  

plt.rc('font', size=20)
fig1=plt.figure(figsize=(12,9))
fig1, ax1 = plt.subplots(figsize=(12,9))
h1=plt.hist2d(list_c, list_g, weights=list_auc_svm, bins=(edges_c,edges_g))
ax1.set_aspect("equal")
hist, xbins, ybins, im = ax1.hist2d(list_c, list_g, weights=list_auc_svm, bins=(edges_c,edges_g))
scale_hist=3 #position of numbers in histogram fields
for i in range(len(ybins)-1):
    for j in range(len(xbins)-1):
        ax1.text(scale_hist*xbins[j],scale_hist*ybins[i], round(hist[j,i],3), 
                color="w", ha="center", va="center", fontweight="bold", fontsize=25)
plt.colorbar(h1[3])
plt.xlabel(r'C values',fontsize=20)
plt.ylabel(r'Gamma',fontsize=20)
plt.title(r'SVC AUC',fontsize=20)
plt.xscale('log')
plt.yscale('log')
fig1.savefig('SVC_AUC.png')
plt.show()
plt.close()      

plt.rcdefaults()
                            

#the best parameter combination is c=10, gamma=0.1 and kernel=rbf, based on AUC (accuracy is one of the highest anyway)                          
svc = SVC(kernel='rbf', C=10, gamma=0.1, random_state=42)
model = svc.fit(X_train,y_train)
y_pred_svc_best = model.predict(X_test)
print("\n Accuracy of SVM: ",accuracy_score(y_test,y_pred_svc_best))
print("\n AUC of SVM: ",metrics.roc_auc_score(y_test,y_pred_svc_best)*100)                           


fig2=plt.figure(figsize=(12,9))
plt.plot(list_c, list_accur_svm, label='Accuracy')
plt.ylabel(r'Accuracy',fontsize=20)
plt.xlabel(r'C values',fontsize=20)
plt.title(r'Accuracy vs c values SVC',fontsize=20)
plt.legend(fontsize=20)
fig2.savefig('SVC_accur_vs_c_parameter.png')
plt.show()
plt.close()

# confusion matrix
plt.rc('font', size=13)
h=skplt.metrics.plot_confusion_matrix(y_test, y_pred_svc, normalize=True, title='SVC confusion matrix')
print(h.yaxis_inverted())
fig=h.get_figure()
#plt.ylim([-0.5, 1.5])
plt.ylim([1.5, -0.5])
plt.show()
fig.savefig('CM_SVC.png')
plt.close()
plt.rcdefaults()


#XGboost

l_rate =[0.0001, 0.001, 0.01, 0.1, 0.3, 1]
n_trees = [10, 50, 100, 200, 500, 1000]
list_accur_xg=[]   
list_auc_xg=[]
list_rate=[]
list_trees=[]
for rate in l_rate:
    for tree in n_trees:
        np.random.seed(42)          
        xg_clf = xgb.XGBClassifier(eta=rate, n_estimators=tree, random_state=42)
        xg_clf.fit(X_train, y_train)
            
        y_pred_xg = xg_clf.predict(X_test)
            
        print("learning rate:", rate)
        print("number of trees:", tree)
        print("Test set accuracy:", xg_clf.score(X_test,y_test))
        print("\n AUC of XGBoost: ",metrics.roc_auc_score(y_test,y_pred_xg)*100)
        list_accur_xg.append(xg_clf.score(X_test,y_test))
        list_auc_xg.append(metrics.roc_auc_score(y_test,y_pred_xg)*100)
        list_rate.append(rate)
        list_trees.append(tree) 

print(max(list_accur_xg))
print(max(list_auc_xg))

#use hardcoded edges because calc_edges function operates only with equidistant values which are powers of 10
edges_rate=[3.e-05, 3.e-04, 3.e-03, 3.e-02, 2.e-01, 8.e-01, 3.e+00]
edges_trees=[7,20,60,150,300,750,1500]


plt.rc('font', size=20)
fig1=plt.figure(figsize=(12,9))
fig1, ax1 = plt.subplots(figsize=(12,9))
h1=plt.hist2d(list_rate, list_trees, weights=list_accur_xg, bins=(edges_rate,edges_trees))
ax1.set_aspect("equal")
hist, xbins, ybins, im = ax1.hist2d(list_rate, list_trees, weights=list_accur_xg, bins=(edges_rate,edges_trees))
scale_hist=3 #position of numbers in histogram fields
for i in range(len(ybins)-1):
    for j in range(len(xbins)-2):
        ax1.text(scale_hist*xbins[j],scale_hist/2.3*ybins[i], round(hist[j,i],3), 
                color="w", ha="center", va="center", fontweight="bold", fontsize=25)
plt.colorbar(h1[3])
plt.xlabel(r'$\eta$',fontsize=20)
plt.ylabel(r'# trees',fontsize=20)
plt.title(r'XGB accuracy',fontsize=20)
plt.xscale('log')
plt.yscale('log')
fig1.savefig('XGB_accuracy.png')
plt.show()
plt.close()  

plt.rc('font', size=20)
fig1=plt.figure(figsize=(12,9))
fig1, ax1 = plt.subplots(figsize=(12,9))
h1=plt.hist2d(list_rate, list_trees, weights=list_auc_xg, bins=(edges_rate,edges_trees))
ax1.set_aspect("equal")
hist, xbins, ybins, im = ax1.hist2d(list_rate, list_trees, weights=list_auc_xg, bins=(edges_rate,edges_trees))
scale_hist=3 #position of numbers in histogram fields
for i in range(len(ybins)-1):
    for j in range(len(xbins)-2):
        ax1.text(scale_hist*xbins[j],scale_hist/2.3*ybins[i], round(hist[j,i],2), 
                color="w", ha="center", va="center", fontweight="bold", fontsize=25)
plt.colorbar(h1[3])
plt.xlabel(r'$\eta$',fontsize=20)
plt.ylabel(r'# trees',fontsize=20)
plt.title(r'XGB AUC',fontsize=20)
plt.xscale('log')
plt.yscale('log')
fig1.savefig('XGB_AUC.png')
plt.show()
plt.close()   

plt.rcdefaults()

#learning rate doesn't matter that much, the only parameter making big changes is the number of trees and the best result is obtained with 100
 
# study xgboost and consider the possibility for early stopping due to overfitting

xg_clf = xgb.XGBClassifier(n_estimators=500, random_state=42)
eval_set = [(X_train, y_train), (X_test, y_test)]
xg_clf.fit(X_train, y_train, eval_metric=["error", "logloss"], eval_set=eval_set, verbose=True)

print(X_test)
y_pred_xg = xg_clf.predict(X_test)
predictions = [round(value) for value in y_pred_xg]

print("Test set accuracy:", xg_clf.score(X_test,y_test))


results = xg_clf.evals_result()
epochs = len(results['validation_0']['error'])
x_axis = range(0, epochs)


# plot log loss
fig, ax = pyplot.subplots()
ax.plot(x_axis, results['validation_0']['logloss'], label='Train')
ax.plot(x_axis, results['validation_1']['logloss'], label='Test')
ax.legend(fontsize=20)
pyplot.ylabel('Log Loss',fontsize=20)
pyplot.xlabel('Number of trees',fontsize=20)
pyplot.title('XGBoost Log Loss',fontsize=20)
pyplot.show()
fig.savefig('XGB_LogLoss.png')
pyplot.close()

# plot classification error
fig, ax = pyplot.subplots()
ax.plot(x_axis, results['validation_0']['error'], label='Train')
ax.plot(x_axis, results['validation_1']['error'], label='Test')
ax.legend(fontsize=20)
pyplot.ylabel('Classification Error',fontsize=20)
pyplot.xlabel('Number of trees',fontsize=20)
pyplot.title('XGBoost Classification Error',fontsize=20)
pyplot.show()
fig.savefig('XGB_ClassErr.png')
# since overfitting tendencies are not totally clear (at least before number of epochs=60, it's not necessary)

# we can try to fit the model allowing for early stopping when the loss over a range of 10 epochs starts increasing too much

# fit model no training data
xg1_clf = xgb.XGBClassifier(n_estimators=500, random_state=42)
eval_set = [(X_test, y_test)]
xg1_clf.fit(X_train, y_train, early_stopping_rounds=10, eval_metric="logloss", eval_set=eval_set, verbose=True)
# make predictions for test data
y_pred = xg1_clf.predict(X_test)
predictions = [round(value) for value in y_pred]
# evaluate predictions
accuracy = accuracy_score(y_test, predictions)

#best iteration is 92, early stopping because overfitting is observed after 90-100 epochs (best seen if we increase the number of estimators(=epochs) to 500)

#having 92 estimators we get the best result in terms of loss function, learning rate is 0.3 by default
xg_clf = xgb.XGBClassifier(n_estimators=92, random_state=42)
xg_model=xg_clf.fit(X_train, y_train)

y_pred_xg = xg_clf.predict(X_test)
predictions = [round(value) for value in y_pred_xg]

print("Test set accuracy with Random Forests and scaled data:", xg_clf.score(X_test,y_test))
print("\n AUC of XGBoost: ",metrics.roc_auc_score(y_test,y_pred_xg)*100)
#no clear tendency of overfitting is observed
# =============================================================================
# xg_clf = xgb.XGBClassifier(learning_rate=0.00001, n_estimators=1, random_state=42)
# xg_clf.fit(X_train,y_train)
# 
# y_pred_xg = xg_clf.predict(X_test)
# xg_clf.score(X_test,y_pred_xg)
# 
# print("Test set accuracy with Random Forests and scaled data: {:.4f}".format(xg_clf.score(X_test,y_pred_xg)))
# 
# =============================================================================

# confusion matrix
plt.rc('font', size=13)
#fig=plt.figure()
h=skplt.metrics.plot_confusion_matrix(y_test, y_pred_xg, normalize=True, title='XGB confusion matrix')
print(h.yaxis_inverted())
fig=h.get_figure()
#plt.ylim([-0.5, 1.5])
plt.ylim([1.5, -0.5])
plt.show()
fig.savefig('CM_XGB.png')
plt.close()
plt.rcdefaults()

#Need to rerun all the methods with the best selected parameters before the plot

#best combination by looking at AUC values
t0 = time.time()                            
svc = SVC(gamma=0.1,kernel='rbf',C=10)
model = svc.fit(X_train,y_train)
y_pred_svc = model.predict(X_test)
time_svc= time.time()-t0                            

fpr_svc, tpr_svc, threshold = metrics.roc_curve(y_test,y_pred_svc)
roc_auc_svc = metrics.auc(fpr_svc, tpr_svc)

# Logistic regression
t0 = time.time()                            
lr = LogisticRegression()
model_lr = lr.fit(X_train,y_train)
y_pred_lr = model_lr.predict(X_test)
time_lr= time.time()-t0                             
                            
fpr_lr, tpr_lr, threshold = metrics.roc_curve(y_test,y_pred_lr)
roc_auc_lr = metrics.auc(fpr_lr, tpr_lr)

#random forest with 100 trees
t0 = time.time()                            
model_rf_classi = RandomForestClassifier(n_estimators=100)
model_rf = model_rf_classi.fit(X_train,y_train)
y_pred_enrf = model_rf.predict(X_test)
time_rf= time.time()-t0
                            
fpr_enrf, tpr_enrf, threshold = metrics.roc_curve(y_test,y_pred_enrf)
roc_auc_enrf = metrics.auc(fpr_enrf, tpr_enrf)
                         
# Best XGBoost
t0 = time.time()                             
xg_clf = xgb.XGBClassifier(n_estimators=92, random_state=42)
xg_model=xg_clf.fit(X_train, y_train)  
y_pred_xg = xg_clf.predict(X_test)                            
time_xg= time.time()-t0
                            
fpr_xg, tpr_xg, threshold = metrics.roc_curve(y_test,y_pred_xg)
roc_auc_xg = metrics.auc(fpr_xg, tpr_xg)
                            
# Time
print("Logistic regression:",time_lr,"seconds process time")
print("Support Vector Classifier:",time_svc,"seconds process time")
print("Random forest:",time_rf,"seconds process time")
print("XGBoost:",time_xg,"seconds process time")


plt.rc('font', size=15)
fig=plt.figure()
plt.title('Receiver Operating Characteristic')
plt.plot(fpr_svc, tpr_svc, 'b', label = 'AUC = %0.2f SVC' % roc_auc_svc,color="g")
plt.plot(fpr_lr, tpr_lr, 'b', label = 'AUC = %0.2f LR' % roc_auc_lr)
plt.plot(fpr_xg, tpr_xg, 'b', label = 'AUC = %0.2f XG' % roc_auc_xg,color="y")
plt.plot(fpr_enrf, tpr_enrf, 'b', label = 'AUC = %0.2f RF' % roc_auc_enrf,color="r")
plt.legend(loc = 'lower right')
plt.plot([0, 1], [0, 1],'r--')
plt.xlim([0, 1])
plt.ylim([0, 1])
plt.ylabel('True Positive Rate')
plt.xlabel('False Positive Rate')
plt.show()
fig.savefig('ROC.png')
plt.close()
plt.rcdefaults()
                            
# Importance and Shap
#shap index for random forest
explainer = shap.TreeExplainer(model_rf)
shap_values = explainer.shap_values(X_test)
#print(shap_values)

fig=plt.figure()
shap.summary_plot(shap_values, X_test, plot_type = 'bar')
plt.show()
fig.savefig('RF_SHAP_sum_bar.png', bbox_inches='tight')
plt.close()

fig=plt.figure()
shap.summary_plot(shap_values[1], X_test)
plt.show()
fig.savefig('RF_SHAP_sum_dot.png', bbox_inches='tight')
plt.close()
   
                            
# importance for XGBoost
h=xgb.plot_importance(xg_model)
plt.title('Feature importance, weight',fontsize=15)
fig=h.get_figure()
plt.show()
fig.savefig('XGB_feature_importance.png', bbox_inches='tight')
plt.close()

xgb.plot_importance(xg_model,importance_type="gain")
plt.title('Feature importance, gain',fontsize=15)
plt.show()

xgb.plot_importance(xg_model,importance_type="cover")
plt.title('Feature importance, cover',fontsize=15)
plt.show()

#shap index for XGBoost
explainer = shap.TreeExplainer(xg_model)
shap_values = explainer.shap_values(X_test)
#print(shap_values.shape)

fig=plt.figure()
shap.summary_plot(shap_values, X_test, plot_type = 'bar')
plt.show()
fig.savefig('XGB_SHAP_sum_bar.png', bbox_inches='tight')
plt.close()

fig=plt.figure()
shap.summary_plot(shap_values, X_test)
plt.show()
fig.savefig('XGB_SHAP_sum_dot.png', bbox_inches='tight')
plt.close()                    
