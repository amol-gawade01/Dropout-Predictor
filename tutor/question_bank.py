QUESTION_BANK = [
    # ========================================================
    # ARRAYS
    # ========================================================
    {
        "question_id": "arrays_001",
        "concept_id": "dsa_arrays",
        "difficulty": "BEGINNER",
        "question": ("What is the main advantage of using an array for indexed access?"),
        "expected_answer": (
            "Arrays allow direct access to an element using its index, usually in O(1) time."
        ),
    },
    {
        "question_id": "arrays_002",
        "concept_id": "dsa_arrays",
        "difficulty": "INTERMEDIATE",
        "question": ("Why is inserting an element at the beginning of an array usually O(n)?"),
        "expected_answer": (
            "Existing elements usually need "
            "to be shifted one position to "
            "make space for the new element."
        ),
    },
    {
        "question_id": "arrays_003",
        "concept_id": "dsa_arrays",
        "difficulty": "BEGINNER",
        "question": "What is the time complexity of reading an array element when its index is known?",
        "expected_answer": "Reading an element by a known index takes O(1) constant time.",
    },
    {
        "question_id": "arrays_004",
        "concept_id": "dsa_arrays",
        "difficulty": "INTERMEDIATE",
        "question": "Why is appending to a dynamic array usually O(1) amortized time?",
        "expected_answer": "Most appends take constant time, and occasional resizing costs are spread across many appends.",
    },
    {
        "question_id": "arrays_005",
        "concept_id": "dsa_arrays",
        "difficulty": "ADVANCED",
        "question": "How would you find the second largest distinct value in an array in one pass?",
        "expected_answer": "Track the largest and second largest distinct values while scanning once, updating them when a larger value is found.",
    },
    # ========================================================
    # TREES
    # ========================================================
    {
        "question_id": "trees_001",
        "concept_id": "dsa_trees",
        "difficulty": "BEGINNER",
        "question": ("What is the root node of a tree?"),
        "expected_answer": ("The root is the topmost node of a tree and has no parent."),
    },
    {
        "question_id": "trees_002",
        "concept_id": "dsa_trees",
        "difficulty": "INTERMEDIATE",
        "question": ("What is the difference between a leaf node and an internal node?"),
        "expected_answer": (
            "A leaf node has no children, while an internal node has at least one child."
        ),
    },
    {
        "question_id": "trees_003",
        "concept_id": "dsa_trees",
        "difficulty": "BEGINNER",
        "question": "What is the height of a tree, and how is it measured?",
        "expected_answer": "The height is the number of edges on the longest path from the root to a leaf.",
    },
    {
        "question_id": "trees_004",
        "concept_id": "dsa_trees",
        "difficulty": "INTERMEDIATE",
        "question": "Why is breadth-first traversal useful for finding the shortest path in an unweighted tree?",
        "expected_answer": "It visits nodes level by level, so the first time a node is reached uses the fewest edges.",
    },
    {
        "question_id": "trees_005",
        "concept_id": "dsa_trees",
        "difficulty": "ADVANCED",
        "question": "What is the space complexity of a recursive depth-first traversal of a balanced tree?",
        "expected_answer": "The call stack uses O(h) space, which is O(log n) for a balanced tree.",
    },
    # ========================================================
    # BST
    # ========================================================
    {
        "question_id": "bst_001",
        "concept_id": "dsa_bst",
        "difficulty": "BEGINNER",
        "question": (
            "In a Binary Search Tree, where "
            "are values smaller than the "
            "current node generally stored?"
        ),
        "expected_answer": ("Values smaller than the current node are stored in the left subtree."),
    },
    {
        "question_id": "bst_002",
        "concept_id": "dsa_bst",
        "difficulty": "INTERMEDIATE",
        "question": (
            "What is the average search complexity of a balanced Binary Search Tree, and why?"
        ),
        "expected_answer": (
            "O(log n), because each comparison "
            "approximately eliminates half of "
            "the remaining search space in a "
            "balanced tree."
        ),
    },
    {
        "question_id": "bst_003",
        "concept_id": "dsa_bst",
        "difficulty": "ADVANCED",
        "question": ("Why can search in an unbalanced Binary Search Tree degrade to O(n)?"),
        "expected_answer": (
            "If the tree becomes highly skewed, "
            "it behaves like a linked list, so "
            "search may visit every node."
        ),
    },
    {
        "question_id": "bst_004",
        "concept_id": "dsa_bst",
        "difficulty": "BEGINNER",
        "question": "What traversal of a Binary Search Tree visits values in sorted order?",
        "expected_answer": "In-order traversal visits the left subtree, node, then right subtree and produces sorted order.",
    },
    {
        "question_id": "bst_005",
        "concept_id": "dsa_bst",
        "difficulty": "INTERMEDIATE",
        "question": "What condition must hold for a Binary Search Tree to have logarithmic height?",
        "expected_answer": "The tree must remain reasonably balanced so each level does not become heavily skewed.",
    },
    {
        "question_id": "bst_006",
        "concept_id": "dsa_bst",
        "difficulty": "ADVANCED",
        "question": "How can you delete a node with two children from a Binary Search Tree?",
        "expected_answer": "Replace it with its in-order successor or predecessor, then delete that replacement node from its original position.",
    },
    {
        "question_id": "arrays_006",
        "concept_id": "dsa_arrays",
        "difficulty": "BEGINNER",
        "question": "What happens when you access an array index outside its valid range?",
        "expected_answer": "It causes an out-of-bounds error or undefined behavior, depending on the language.",
    },
    {
        "question_id": "arrays_007",
        "concept_id": "dsa_arrays",
        "difficulty": "INTERMEDIATE",
        "question": "How can two pointers help find a pair with a target sum in a sorted array?",
        "expected_answer": "Start at both ends and move a pointer inward based on whether the sum is too small or too large.",
    },
    {
        "question_id": "trees_006",
        "concept_id": "dsa_trees",
        "difficulty": "BEGINNER",
        "question": "What is a parent-child relationship in a tree?",
        "expected_answer": "A parent is directly connected above a child, and the child is directly below that parent.",
    },
    {
        "question_id": "trees_007",
        "concept_id": "dsa_trees",
        "difficulty": "ADVANCED",
        "question": "How can you determine whether a binary tree is height-balanced?",
        "expected_answer": "Compute subtree heights bottom-up and ensure their difference is at most one at every node.",
    },
    {
        "question_id": "bst_007",
        "concept_id": "dsa_bst",
        "difficulty": "BEGINNER",
        "question": "Where would you insert a value greater than the current node in a Binary Search Tree?",
        "expected_answer": "Continue into the right subtree until an empty position is found.",
    },
    {
        "question_id": "bst_008",
        "concept_id": "dsa_bst",
        "difficulty": "INTERMEDIATE",
        "question": "How can you find the minimum value in a non-empty Binary Search Tree?",
        "expected_answer": "Follow left-child links from the root until reaching a node with no left child.",
    },
]


QUESTION_TRANSLATIONS = {
    "hi-IN": {
        "arrays_001": "इंडेक्स का उपयोग करके ऐरे में सीधे पहुँचने का मुख्य लाभ क्या है?",
        "arrays_002": "ऐरे की शुरुआत में नया तत्व जोड़ना सामान्यतः O(n) क्यों होता है?",
        "arrays_003": "इंडेक्स ज्ञात होने पर ऐरे के तत्व को पढ़ने की समय जटिलता क्या होती है?",
        "arrays_004": "डायनेमिक ऐरे में तत्व जोड़ना औसतन O(1) समय क्यों लेता है?",
        "arrays_005": "एक ही बार ऐरे को पढ़कर दूसरा सबसे बड़ा अलग मान कैसे खोजेंगे?",
        "arrays_006": "ऐरे की वैध सीमा से बाहर के इंडेक्स को उपयोग करने पर क्या होता है?",
        "arrays_007": "क्रमबद्ध ऐरे में लक्ष्य योग वाली जोड़ी खोजने में दो पॉइंटर कैसे मदद करते हैं?",
        "trees_001": "ट्री का रूट नोड क्या होता है?",
        "trees_002": "लीफ नोड और आंतरिक नोड में क्या अंतर है?",
        "trees_003": "ट्री की ऊँचाई क्या होती है और इसे कैसे मापा जाता है?",
        "trees_004": "बिना भार वाले ट्री में सबसे छोटा पथ खोजने के लिए ब्रेड्थ-फर्स्ट ट्रैवर्सल उपयोगी क्यों है?",
        "trees_005": "संतुलित ट्री के रिकर्सिव डेप्थ-फर्स्ट ट्रैवर्सल की स्पेस जटिलता क्या है?",
        "trees_006": "ट्री में पैरेंट और चाइल्ड का संबंध क्या होता है?",
        "trees_007": "आप कैसे जाँचेंगे कि कोई बाइनरी ट्री ऊँचाई के अनुसार संतुलित है?",
        "bst_001": "बाइनरी सर्च ट्री में वर्तमान नोड से छोटे मान सामान्यतः कहाँ रखे जाते हैं?",
        "bst_002": "संतुलित बाइनरी सर्च ट्री में खोज की औसत जटिलता क्या है और क्यों?",
        "bst_003": "असंतुलित बाइनरी सर्च ट्री में खोज O(n) तक क्यों पहुँच सकती है?",
        "bst_004": "बाइनरी सर्च ट्री का कौन-सा ट्रैवर्सल मानों को क्रमबद्ध रूप में दिखाता है?",
        "bst_005": "बाइनरी सर्च ट्री की ऊँचाई लॉगरिदमिक रहने के लिए कौन-सी शर्त आवश्यक है?",
        "bst_006": "दो चाइल्ड वाले नोड को बाइनरी सर्च ट्री से कैसे हटाएँगे?",
        "bst_007": "बाइनरी सर्च ट्री में वर्तमान नोड से बड़ा मान कहाँ जोड़ा जाता है?",
        "bst_008": "खाली न होने वाले बाइनरी सर्च ट्री में न्यूनतम मान कैसे खोजेंगे?",
    },
    "mr-IN": {
        "arrays_001": "इंडेक्स वापरून ॲरेमधील घटक थेट मिळवण्याचा मुख्य फायदा काय आहे?",
        "arrays_002": "ॲरेच्या सुरुवातीला नवीन घटक घालणे सामान्यतः O(n) का असते?",
        "arrays_003": "इंडेक्स माहीत असल्यास ॲरेमधील घटक वाचण्याची वेळ जटिलता किती असते?",
        "arrays_004": "डायनॅमिक ॲरेमध्ये घटक जोडण्यासाठी सरासरी O(1) वेळ का लागतो?",
        "arrays_005": "ॲरे एकदाच वाचून दुसरे सर्वात मोठे वेगळे मूल्य कसे शोधाल?",
        "arrays_006": "ॲरेच्या वैध मर्यादेबाहेरील इंडेक्स वापरल्यास काय होते?",
        "arrays_007": "क्रमबद्ध ॲरेमध्ये अपेक्षित बेरीज असलेली जोडी शोधण्यासाठी दोन पॉइंटर कसे मदत करतात?",
        "trees_001": "ट्रीमधील रूट नोड म्हणजे काय?",
        "trees_002": "लीफ नोड आणि अंतर्गत नोड यांच्यात काय फरक आहे?",
        "trees_003": "ट्रीची उंची म्हणजे काय आणि ती कशी मोजली जाते?",
        "trees_004": "वजन नसलेल्या ट्रीमध्ये सर्वात लहान मार्ग शोधण्यासाठी ब्रेड्थ-फर्स्ट ट्रॅव्हर्सल उपयुक्त का आहे?",
        "trees_005": "संतुलित ट्रीच्या रिकर्सिव डेप्थ-फर्स्ट ट्रॅव्हर्सलची स्पेस जटिलता किती आहे?",
        "trees_006": "ट्रीमध्ये पॅरेंट आणि चाइल्ड यांचा संबंध काय असतो?",
        "trees_007": "बायनरी ट्री उंचीनुसार संतुलित आहे की नाही हे कसे तपासाल?",
        "bst_001": "बायनरी सर्च ट्रीमध्ये वर्तमान नोडपेक्षा लहान मूल्ये सामान्यतः कुठे ठेवली जातात?",
        "bst_002": "संतुलित बायनरी सर्च ट्रीमध्ये शोधाची सरासरी जटिलता किती असते आणि का?",
        "bst_003": "असंतुलित बायनरी सर्च ट्रीमध्ये शोध O(n) पर्यंत का जाऊ शकतो?",
        "bst_004": "बायनरी सर्च ट्रीचा कोणता ट्रॅव्हर्सल मूल्ये क्रमाने दाखवतो?",
        "bst_005": "बायनरी सर्च ट्रीची उंची लॉगरिदमिक राहण्यासाठी कोणती अट आवश्यक आहे?",
        "bst_006": "दोन चाइल्ड असलेला नोड बायनरी सर्च ट्रीमधून कसा काढाल?",
        "bst_007": "बायनरी सर्च ट्रीमध्ये वर्तमान नोडपेक्षा मोठे मूल्य कुठे घातले जाते?",
        "bst_008": "रिकाम्या नसलेल्या बायनरी सर्च ट्रीमध्ये किमान मूल्य कसे शोधाल?",
    },
}


def get_question(
    question_id: str,
):

    for question in QUESTION_BANK:
        if question["question_id"] == question_id:
            return question

    return None


def get_questions_for_concept(
    concept_id: str,
):

    return [question for question in QUESTION_BANK if (question["concept_id"] == concept_id)]


def get_display_question(question, language_code: str = "en-IN"):
    """Return a localized display copy without changing evaluation data."""
    translated = QUESTION_TRANSLATIONS.get(language_code, {}).get(question["question_id"])
    if not translated:
        return question["question"]
    return translated
