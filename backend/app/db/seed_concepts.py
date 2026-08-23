from backend.app.db.models import Concept
from backend.app.db.session import SessionLocal


CONCEPTS = [
    {
        "concept_id": "dsa_arrays",
        "topic_name": "Arrays",
        "prerequisite_concept_id": None,
        "concept_description": (
            "Arrays store elements in contiguous memory "
            "and allow indexed access."
        ),
    },
    {
        "concept_id": "dsa_linked_lists",
        "topic_name": "Linked Lists",
        "prerequisite_concept_id": "dsa_arrays",
        "concept_description": (
            "Linked lists store data in nodes connected "
            "using references or pointers."
        ),
    },
    {
        "concept_id": "dsa_stack",
        "topic_name": "Stacks",
        "prerequisite_concept_id": "dsa_arrays",
        "concept_description": (
            "A stack is a LIFO data structure."
        ),
    },
    {
        "concept_id": "dsa_queue",
        "topic_name": "Queues",
        "prerequisite_concept_id": "dsa_arrays",
        "concept_description": (
            "A queue is a FIFO data structure."
        ),
    },
    {
        "concept_id": "dsa_trees",
        "topic_name": "Trees",
        "prerequisite_concept_id": "dsa_linked_lists",
        "concept_description": (
            "Trees represent hierarchical relationships "
            "using nodes and edges."
        ),
    },
    {
        "concept_id": "dsa_bst",
        "topic_name": "Binary Search Trees",
        "prerequisite_concept_id": "dsa_trees",
        "concept_description": (
            "A binary search tree keeps smaller values "
            "on the left and larger values on the right."
        ),
    },
    {
        "concept_id": "dsa_graphs",
        "topic_name": "Graphs",
        "prerequisite_concept_id": "dsa_trees",
        "concept_description": (
            "Graphs represent relationships between "
            "vertices using edges."
        ),
    },
]


def seed_concepts():
    db = SessionLocal()

    try:
        for item in CONCEPTS:
            existing = db.get(
                Concept,
                item["concept_id"],
            )

            if existing:
                existing.topic_name = item["topic_name"]
                existing.prerequisite_concept_id = (
                    item["prerequisite_concept_id"]
                )
                existing.concept_description = (
                    item["concept_description"]
                )

            else:
                concept = Concept(
                    concept_id=item["concept_id"],
                    topic_name=item["topic_name"],
                    grade_level=None,
                    prerequisite_concept_id=(
                        item["prerequisite_concept_id"]
                    ),
                    concept_description=(
                        item["concept_description"]
                    ),
                    embedding=None,
                )

                db.add(concept)

            db.flush()

        db.commit()

        print("Concept graph seeded successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_concepts()