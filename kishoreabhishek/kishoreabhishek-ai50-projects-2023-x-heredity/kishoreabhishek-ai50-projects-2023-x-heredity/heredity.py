import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """

    jpdict = preparejpkeys(people,one_gene,two_genes,have_trait)
    for p in people.keys():
        if people[p]['mother'] is None:
            gcount = jpdict[p][0]
            btrait = jpdict[p][1]
            jpdict[p].append(PROBS["gene"][gcount])
            ptrait = PROBS["gene"][gcount]*PROBS["trait"][gcount][btrait]
            jpdict[p].append(ptrait)
    # print(jpdict)
    for p in people.keys():
        if people[p]['mother'] is not None:
            if jpdict[p][0] == 0:
                r = fromp(p,people,jpdict,0,"mother",have_trait)*fromp(p,people,jpdict,0,"father",have_trait)
            elif jpdict[p][0] == 1:
                r = fromp(p,people,jpdict,1,"mother",have_trait)*fromp(p,people,jpdict,0,"father",have_trait) + fromp(p,people,jpdict,
                                            0,"mother",have_trait) * fromp(p,people,jpdict,1,"father",have_trait)
            else:
                r = fromp(p,people,jpdict,1,"mother",have_trait)*fromp(p,people,jpdict,1,"father",have_trait)
            jpdict[p].append(r)
            if p in have_trait:
                jpdict[p].append(PROBS['trait'][jpdict[p][0]][True]*r)
            else:
                jpdict[p].append(PROBS['trait'][jpdict[p][0]][False] * r)

    # print("done")
    R = 1
    for k in jpdict.keys():
        R = R*jpdict[k][3]
    return R
def calculategeneprob():
    pass

def fromp(p,people,jpdict,gnum,parent,have_trait):
    pname = people[p][parent]
    parentgcount = jpdict[pname][0]
    
    if parentgcount == 0:
        r = 0*(1-PROBS["mutation"]) + 1*PROBS["mutation"]
        if gnum == 1:
            result = r
        else:
            result = 1 - r
    elif parentgcount == 1:
        r = (0.5*(1-PROBS["mutation"])) + (0.5*PROBS["mutation"])
        if gnum == 1:
            result = r
        else:
            result = 1-r
    else:
        r = 1*(1-PROBS["mutation"]) + (0*PROBS["mutation"])
        if gnum == 1:
            result = r
        else:
            result = 1-r

    return result


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        if person in one_gene:
            probabilities[person]['gene'][1] = p + probabilities[person]['gene'][1]
        elif person in two_genes:
            probabilities[person]['gene'][2] = p + probabilities[person]['gene'][2]
        else:
            probabilities[person]['gene'][0] = p + probabilities[person]['gene'][0]
        if person in have_trait:
            probabilities[person]['trait'][True] = p + probabilities[person]['trait'][True]
        else:
            probabilities[person]['trait'][False] = p + probabilities[person]['trait'][False]

def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for p in probabilities:
        plist = [probabilities[p]['gene'][0],probabilities[p]['gene'][1],probabilities[p]['gene'][2]]
        k1,k2 = plist[1]/plist[0], plist[2]/plist[0]
        P0 = 1/(1+k1+k2)
        P1 = k1*P0
        P2 = 1-P0-P1
        probabilities[p]['gene'][0] = P0
        probabilities[p]['gene'][1] = P1
        probabilities[p]['gene'][2] = P2
        if probabilities[p]['trait'][False] > 0:
            k = probabilities[p]['trait'][True]/probabilities[p]['trait'][False]
            probabilities[p]['trait'][False] = 1/(1+k)

        else:
            probabilities[p]['trait'][False] = 0
        probabilities[p]['trait'][True] = 1 - probabilities[p]['trait'][False]


def preparejpkeys(people, one_gene, two_genes, have_trait):
    l = dict()
    oneortwogene=[]
    for p in one_gene:
        l[p]=[1,False]
        oneortwogene.append(p)
    for p in two_genes:
        l[p]=[2,False]
        oneortwogene.append(p)
    for p in people:
        if p not in oneortwogene:
            l[p]=[0,False]
    for p in have_trait:
        l[p][1] = True
    return l




if __name__ == "__main__":
    main()
