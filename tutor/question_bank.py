QUESTION_BANK = [

    # ========================================================
    # ARRAYS
    # ========================================================

    {
        "question_id":
            "arrays_001",

        "concept_id":
            "dsa_arrays",

        "difficulty":
            "BEGINNER",

        "question": (
            "What is the main advantage of "
            "using an array for indexed access?"
        ),

        "expected_answer": (
            "Arrays allow direct access to an "
            "element using its index, usually "
            "in O(1) time."
        ),
    },

    {
        "question_id":
            "arrays_002",

        "concept_id":
            "dsa_arrays",

        "difficulty":
            "INTERMEDIATE",

        "question": (
            "Why is inserting an element at "
            "the beginning of an array usually "
            "O(n)?"
        ),

        "expected_answer": (
            "Existing elements usually need "
            "to be shifted one position to "
            "make space for the new element."
        ),
    },

    # ========================================================
    # TREES
    # ========================================================

    {
        "question_id":
            "trees_001",

        "concept_id":
            "dsa_trees",

        "difficulty":
            "BEGINNER",

        "question": (
            "What is the root node of a tree?"
        ),

        "expected_answer": (
            "The root is the topmost node of "
            "a tree and has no parent."
        ),
    },

    {
        "question_id":
            "trees_002",

        "concept_id":
            "dsa_trees",

        "difficulty":
            "INTERMEDIATE",

        "question": (
            "What is the difference between "
            "a leaf node and an internal node?"
        ),

        "expected_answer": (
            "A leaf node has no children, "
            "while an internal node has at "
            "least one child."
        ),
    },

    # ========================================================
    # BST
    # ========================================================

    {
        "question_id":
            "bst_001",

        "concept_id":
            "dsa_bst",

        "difficulty":
            "BEGINNER",

        "question": (
            "In a Binary Search Tree, where "
            "are values smaller than the "
            "current node generally stored?"
        ),

        "expected_answer": (
            "Values smaller than the current "
            "node are stored in the left subtree."
        ),
    },

    {
        "question_id":
            "bst_002",

        "concept_id":
            "dsa_bst",

        "difficulty":
            "INTERMEDIATE",

        "question": (
            "What is the average search "
            "complexity of a balanced Binary "
            "Search Tree, and why?"
        ),

        "expected_answer": (
            "O(log n), because each comparison "
            "approximately eliminates half of "
            "the remaining search space in a "
            "balanced tree."
        ),
    },

    {
        "question_id":
            "bst_003",

        "concept_id":
            "dsa_bst",

        "difficulty":
            "ADVANCED",

        "question": (
            "Why can search in an unbalanced "
            "Binary Search Tree degrade to O(n)?"
        ),

        "expected_answer": (
            "If the tree becomes highly skewed, "
            "it behaves like a linked list, so "
            "search may visit every node."
        ),
    },
]


def get_question(
    question_id: str,
):

    for question in QUESTION_BANK:

        if (
            question["question_id"]
            == question_id
        ):
            return question

    return None


def get_questions_for_concept(
    concept_id: str,
):

    return [
        question
        for question in QUESTION_BANK
        if (
            question["concept_id"]
            == concept_id
        )
    ]