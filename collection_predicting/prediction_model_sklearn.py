#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 22/2/2017 下午 1:56
# @Author  : GUO Ganggang
# @email   : ganggangguo@csu.edu.cn
# @Site    : 
# @File    : prediction_model_sklearn.py
# @Software: PyCharm

"""
Multiclass SVMs (Crammer-Singer formulation).

A pure Python re-implementation of:

Large-scale Multiclass Support Vector Machine Training via Euclidean Projection onto the Simplex.
Mathieu Blondel, Akinori Fujino, and Naonori Ueda.
ICPR 2014.
http://www.mblondel.org/publications/mblondel-icpr2014.pdf
"""

import graphlab as gl
import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.utils import check_random_state
from sklearn.preprocessing import LabelEncoder
from sklearn import metrics
import codecs

def projection_simplex(v, z=1):
    """
    Projection onto the simplex:
        w^* = argmin_w 0.5 ||w-v||^2 s.t. \sum_i w_i = z, w_i >= 0
    """
    # For other algorithms computing the same projection, see
    # https://gist.github.com/mblondel/6f3b7aaad90606b98f71
    n_features = v.shape[0]
    u = np.sort(v)[::-1]
    cssv = np.cumsum(u) - z
    ind = np.arange(n_features) + 1
    cond = u - cssv / ind > 0
    rho = ind[cond][-1]
    theta = cssv[cond][-1] / float(rho)
    w = np.maximum(v - theta, 0)
    return w


class MulticlassSVM(BaseEstimator, ClassifierMixin):

    def __init__(self, C=1, max_iter=50, tol=0.05,
                 random_state=None, verbose=0):
        self.C = C
        self.max_iter = max_iter
        self.tol = tol,
        self.random_state = random_state
        self.verbose = verbose

    def _partial_gradient(self, X, y, i):
        # Partial gradient for the ith sample.
        g = np.dot(X[i], self.coef_.T) + 1
        g[y[i]] -= 1
        return g

    def _violation(self, g, y, i):
        # Optimality violation for the ith sample.
        smallest = np.inf
        for k in xrange(g.shape[0]):
            if k == y[i] and self.dual_coef_[k, i] >= self.C:
                continue
            elif k != y[i] and self.dual_coef_[k, i] >= 0:
                continue

            smallest = min(smallest, g[k])

        return g.max() - smallest

    def _solve_subproblem(self, g, y, norms, i):
        # Prepare inputs to the projection.
        Ci = np.zeros(g.shape[0])
        Ci[y[i]] = self.C
        beta_hat = norms[i] * (Ci - self.dual_coef_[:, i]) + g / norms[i]
        z = self.C * norms[i]

        # Compute projection onto the simplex.
        beta = projection_simplex(beta_hat, z)

        return Ci - self.dual_coef_[:, i] - beta / norms[i]

    def fit(self, X, y):
        n_samples, n_features = X.shape

        # Normalize labels.
        self._label_encoder = LabelEncoder()
        y = self._label_encoder.fit_transform(y)

        # Initialize primal and dual coefficients.
        n_classes = len(self._label_encoder.classes_)
        self.dual_coef_ = np.zeros((n_classes, n_samples), dtype=np.float64)
        self.coef_ = np.zeros((n_classes, n_features))

        # Pre-compute norms.
        norms = np.sqrt(np.sum(X ** 2, axis=1))

        # Shuffle sample indices.
        rs = check_random_state(self.random_state)
        ind = np.arange(n_samples)
        rs.shuffle(ind)

        violation_init = None
        for it in xrange(self.max_iter):
            violation_sum = 0

            for ii in xrange(n_samples):
                i = ind[ii]

                # All-zero samples can be safely ignored.
                if norms[i] == 0:
                    continue

                g = self._partial_gradient(X, y, i)
                v = self._violation(g, y, i)
                violation_sum += v

                if v < 1e-12:
                    continue

                # Solve subproblem for the ith sample.
                delta = self._solve_subproblem(g, y, norms, i)

                # Update primal and dual coefficients.
                self.coef_ += (delta * X[i][:, np.newaxis]).T
                self.dual_coef_[:, i] += delta

            if it == 0:
                violation_init = violation_sum

            vratio = violation_sum / violation_init

            if self.verbose >= 1:
                print "iter", it + 1, "violation", vratio

            if vratio < self.tol:
                if self.verbose >= 1:
                    print "Converged"
                break

        return self

    def predict(self, X):
        decision = np.dot(X, self.coef_.T)
        pred = decision.argmax(axis=1)
        return self._label_encoder.inverse_transform(pred)

def divide_data_set(dataSet):

    all_train_arrays = []
    all_train_labels = []
    features_names = dataSet.column_names()
    features_names.remove('target')
    for feature in features_names:
        all_train_arrays.append(dataSet[feature])
    all_train_arrays = [[r[col] for r in all_train_arrays] for col in range(len(all_train_arrays[0]))]
    all_train_labels.append(dataSet['target'])
    all_train_labels = [[r[col] for r in all_train_labels] for col in range(len(all_train_labels[0]))]
    X = np.array(all_train_arrays)
    y = np.array(all_train_labels)

    return X,y

def prediction(train_file,oFile,target,kfolds):
    accu_list = []
    pre_list = []
    rec_list = []
    f1_list = []
    data_zero = train_file[train_file[target] == 0]
    data_one = train_file[train_file[target] == 1]
    data_two = train_file[train_file[target] == 2]
    data_three = train_file[train_file[target] == 3]

    folds_zero = gl.cross_validation.KFold(data_zero, kfolds)
    folds_one = gl.cross_validation.KFold(data_one, kfolds)
    folds_two = gl.cross_validation.KFold(data_two, kfolds)
    folds_three = gl.cross_validation.KFold(data_three, kfolds)

    for i in range(kfolds):
        (train_data_0, test_data_0) = folds_zero[i]
        (train_data_1, test_data_1) = folds_one[i]
        (train_data_2, test_data_2) = folds_two[i]
        (train_data_3, test_data_3) = folds_three[i]

        test_data = test_data_0.append(test_data_1).append(test_data_2).append(test_data_3)
        train_data = train_data_0.append(train_data_1).append(train_data_2).append(train_data_3)

        test_data = test_data.dropna()
        train_data = train_data.dropna()

        train_arrays, train_labels = divide_data_set(train_data)
        test_arrays, test_labels = divide_data_set(test_data)

        clf = MulticlassSVM(C=0.1, tol=0.01, max_iter=100, random_state=0, verbose=1)
        clf.fit(train_arrays, train_labels)
        # acc = clf.score(test_arrays, test_labels)

        y_pred = clf.predict(test_arrays)

        accuracy = metrics.accuracy_score(test_labels, y_pred)
        precision = metrics.precision_score(test_labels, y_pred, average='macro')
        recall = metrics.recall_score(test_labels, y_pred, average='micro')
        f1_score = metrics.f1_score(test_labels, y_pred, average='weighted')

        accu_list.append(accuracy)
        pre_list.append(precision)
        rec_list.append(recall)
        f1_list.append(f1_score)

    total_accu = reduce(lambda x, y: x + y, accu_list)
    total_pre = reduce(lambda x, y: x + y, pre_list)
    total_rec = reduce(lambda x, y: x + y, rec_list)
    total_f1 = reduce(lambda x, y: x + y, f1_list)

    print str(kfolds) + "折交叉后的结果： " + str(total_accu / kfolds)

    with codecs.open(oFile, "a+", "utf-8") as oFile_handler:
        # oFile_handler.write('kfolds' + ',' + 'accuracy' +
        #                     ',' + 'precision' +
        #                     ',' + 'recall' \
        #                     + ',' + 'f1_score' \
        #                     + '\n')
        oFile_handler.write(str(kfolds) + ',' + str(float(total_accu) / kfolds)  +
                            ',' + str(float(total_pre) / kfolds) +
                            ',' + str(float(total_rec) / kfolds) \
                            + ',' + str(float(total_f1) / kfolds) \
                            + '\n')


if __name__ == "__main__":

    filePath = 'D:\\yongxiong\\zhongxing_data\\train_data\\'
    inFilePath = filePath + 'zhongxing_train_all_features_target_std.csv'
    train_file = gl.SFrame.read_csv(inFilePath, header=True, delimiter=",")
    outFilePath = filePath + "result_set\\SVM_result_zhongxing.csv"
    kfolds = 4
    target = 'target'
    prediction(train_file, outFilePath, target,kfolds)

