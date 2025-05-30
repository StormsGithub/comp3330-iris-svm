# ---------------------------------------------------------- #
# File Name: svm_rbf_iris.py                                 #
# Author: Thomas O.                                          #
# Date Created: 9:32 PM, May 10, 2025                        #
# Date Modified: 6:19 PM May 11, 2025                        #
#                                                            #
# Purpose: COMP3330 Machine Intelligence - Assessment 2      #
# Description: Use scikit-learn to train an SVM classifier   #
#              with a non-linear kernel (RBF) on the Iris    #
#              dataset (Fisher, 1936).                       #
# ---------------------------------------------------------- #

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.inspection import DecisionBoundaryDisplay
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, ConfusionMatrixDisplay

# ------------ #
# Load dataset #
# ------------ #

# Define the columns within the Iris dataset
columns = ["sepal_length", "sepal_width", "petal_length", "petal_width", "species"]

# Read the data into a dataframe, assuming the dataset is in the same directory as the script
df = pd.read_csv("iris.data", header=None, names=columns)

# Separate features (X) from labels (y), except for the 'species' column
X = df.iloc[:, :-1].values

# Convert the flower names from string to integer (0, 1, 2)
y = df["species"].astype("category").cat.codes

# ---------------------------------- #
# Split training & test sets (80/20) #
# ---------------------------------- #

# Reproducibility seed - Negates run-to-run variance
RANDOM_STATE = 1

# Split the sets. We stratify 'y' to keep class proportions
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, stratify=y, random_state=RANDOM_STATE)

# ------------------------------------------------- #
# Construct the pipeline: Scale -> SVM (RBF Kernel) #
# ------------------------------------------------- #

# Learn features to zero mean unit variance on the training set, apply to validation set.
pipe = Pipeline([("scale", StandardScaler()), ("svc", SVC(kernel="rbf", random_state=RANDOM_STATE))])

# Exhaustive search for hyperparameters.
# Regularisation and Margin Width parameters selected by "ChatGPT 4o" based on established methodology.
param_grid = {"svc__C": [0.1, 1, 10, 100], "svc__gamma": [1e-3, 1e-2, 1e-1, 1]}

# Perform 5-fold cross-validation
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

# Test every pair of (C, gamma). Can adjust scoring parameter here:
# https://scikit-learn.org/stable/modules/model_evaluation.html#scoring-parameter
grid = GridSearchCV(pipe, param_grid, scoring="accuracy", cv=cv)

# Fit the search on the training data split
grid.fit(X_train, y_train)

# ----------------------------------------------------#
# Evaluate best model on the unmodified test data set #
# ----------------------------------------------------#

best = grid.best_estimator_     # Pipeline with best C and gamma
y_hat = best.predict(X_test)    # Class prediction for X_test

# Output layout selected by "ChatGPT 4o" to follow best-practice for showcasing model performance
print("Best parameters : ", grid.best_params_)
print("Test accuracy   : ", round(accuracy_score(y_test, y_hat), 3))
print("Macro-F1 score  : ", round(f1_score(y_test, y_hat, average='macro'), 3))

print("\nConfusion matrix:\n", confusion_matrix(y_test, y_hat))
print("Support vectors per class:", best["svc"].n_support_)

# ---------------------------#
# Results: Generate Graph(s) #
# ---------------------------#

# 2D decision surface (petal length vs petal width)
# Generated by "ChatGPT 4o" with manual review and commenting

feat_x, feat_y = 2, 3 # Name the column indices for more legible code

# Create a new pipeline on only two features with the previously tuned parameters
vis_pipe = Pipeline([("scale", StandardScaler()),
                     ("svc",   SVC(kernel="rbf",
                                   C=grid.best_params_["svc__C"],
                                   gamma=grid.best_params_["svc__gamma"],
                                   random_state=RANDOM_STATE))])

# Fit the trained data
vis_pipe.fit(X_train[:, [feat_x, feat_y]], y_train)

# This function automatically builds the mesh grid and contours
DecisionBoundaryDisplay.from_estimator(vis_pipe, X_train[:, [feat_x, feat_y]],
                                                response_method="predict",
                                                xlabel=columns[feat_x],
                                                ylabel=columns[feat_y],
                                                alpha=0.3)
# Overlay training points
plt.scatter(X_train[:, feat_x], X_train[:, feat_y], c=y_train, edgecolors="k")
plt.title("SVM Decision Boundary (Petal Length vs Petal Width)")
plt.tight_layout()
plt.show()

# Confusion Matrix - Demonstrate performance across classes
ConfusionMatrixDisplay.from_estimator(best, X_test, y_test)
plt.title("Confusion Matrix (Test Set)")
plt.show()