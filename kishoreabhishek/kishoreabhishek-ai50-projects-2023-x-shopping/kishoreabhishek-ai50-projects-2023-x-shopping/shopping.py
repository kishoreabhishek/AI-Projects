import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    with open(filename) as f:
        reader = csv.reader(f)
        next(reader)
        evidence = list()
        labels = list()

        for row in reader:
            i=0
            templ = []
            for cell in row[:17]:
                if i in [0,2,4,11,12,13,14]:
                    templ.append(int(cell))
                elif i in [1,3,5,6,7,8,9]:
                    templ.append(float(cell))
                elif i==10:
                    templ.append(monthToNum()[cell.upper()]-1)
                elif i==15:
                    if cell == 'Returning_Visitor':
                        templ.append(1)
                    else:
                        templ.append(0)
                elif i==16:
                    if cell == 'TRUE':
                        templ.append(1)
                    else:
                        templ.append(0)
                else:
                    templ.append(cell)
                i=i+1
            evidence.append(templ)
            labels.append(1 if row[-1] == 'TRUE' else 0)
        data = (evidence,labels)
        return data

def monthToNum():
    return {
            'JAN': 1,
            'FEB': 2,
            'MAR': 3,
            'APR': 4,
            'MAY': 5,
            'JUNE': 6,
            'JUL': 7,
            'AUG': 8,
            'SEP': 9,
            'OCT': 10,
            'NOV': 11,
            'DEC': 12
    }
def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence,labels)
    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    sensitivitycnt = 0
    totaltruecnt=0
    totalfalsecount =0
    specifitycount=0
    for i in range(len(labels)):
        if labels[i] == 1:
            totaltruecnt = totaltruecnt+1
            if predictions[i] == 1:
                sensitivitycnt = sensitivitycnt+1
        if labels[i] == 0:
            totalfalsecount = totalfalsecount+1
            if predictions[i] == 0:
                specifitycount = specifitycount+1
    return sensitivitycnt/totaltruecnt,specifitycount/totalfalsecount


    raise NotImplementedError


if __name__ == "__main__":
    main()
