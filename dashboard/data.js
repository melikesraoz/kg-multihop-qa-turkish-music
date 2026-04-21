// Live Data from Neo4j DB
const projectData = {
    "overview": {
        "entities": 21898,
        "relations": 42678457,
        "paths": 5047214,
        "domains": "Football \u00b7 Cinema \u00b7 Biz \u00b7 Music \u00b7 Academia"
    },
    "distribution": {
        "labels": [
            "Other",
            "Music",
            "Football",
            "Cinema",
            "Business",
            "Academia"
        ],
        "data": [
            13472,
            3303,
            2439,
            1830,
            652,
            202
        ]
    },
    "seeds": [
        {
            "id": "Q248059",
            "name": "Zulfu Livaneli",
            "type": "OTHER",
            "relations": 18
        },
        {
            "id": "Q660599",
            "name": "Arif Sag",
            "type": "OTHER",
            "relations": 9
        },
        {
            "id": "Q334814",
            "name": "\u00fcmit besen",
            "type": "OTHER",
            "relations": 7
        },
        {
            "id": "Q962106",
            "name": "H\u00fcmeyra",
            "type": "OTHER",
            "relations": 13
        },
        {
            "id": "Q6823378",
            "name": "mete \u00f6zgencil",
            "type": "OTHER",
            "relations": 8
        },
        {
            "id": "Q388757",
            "name": "Sehrazat",
            "type": "OTHER",
            "relations": 10
        },
        {
            "id": "Q240368",
            "name": "haluk levent",
            "type": "OTHER",
            "relations": 7
        },
        {
            "id": "Q6093986",
            "name": "demet sagiroglu",
            "type": "OTHER",
            "relations": 5
        },
        {
            "id": "Q343693",
            "name": "\u0130lhan Usmanba\u015f",
            "type": "OTHER",
            "relations": 9
        },
        {
            "id": "Q4156426",
            "name": "Aynur Aydin",
            "type": "OTHER",
            "relations": 7
        }
    ],
    "relationFrequency": {
        "labels": [
            "COUNTRY",
            "COUNTRY_OF_CITIZENSHIP",
            "COUNTRY_OF_ORIGIN",
            "NARRATIVE_LOCATION",
            "DIPLOMATIC_RELATION",
            "PLACE_OF_BIRTH",
            "FACET_OF",
            "CONTAINS_ADMINISTRATIVE_TERRITORIAL_ENTITY",
            "FILMING_LOCATION",
            "PLACE_OF_DEATH"
        ],
        "data": [
            14114,
            6250,
            759,
            237,
            118,
            101,
            96,
            81,
            63,
            39
        ]
    },
    "relationImportance": {
        "labels": [
            "COUNTRY",
            "COUNTRY_OF_CITIZENSHIP",
            "COUNTRY_OF_ORIGIN",
            "NARRATIVE_LOCATION",
            "DIPLOMATIC_RELATION",
            "PLACE_OF_BIRTH",
            "FACET_OF",
            "CONTAINS_ADMINISTRATIVE_TERRITORIAL_ENTITY",
            "FILMING_LOCATION",
            "PLACE_OF_DEATH"
        ],
        "data": [
            21171.0,
            9375.0,
            1138.5,
            355.5,
            177.0,
            151.5,
            144.0,
            121.5,
            94.5,
            58.5
        ]
    },
    "benchmarks": {
        "labels": [
            "No-R",
            "V-RAG",
            "V-QE",
            "KG-RAG"
        ],
        "em": [
            0.34,
            0.34,
            0.28,
            0.6
        ],
        "f1": [
            0.41,
            0.4,
            0.33,
            0.68
        ]
    },
    "curves": [
        {
            "epoch": 5,
            "train_loss": 2.1,
            "val_loss": 2.2,
            "accuracy": 0.4
        },
        {
            "epoch": 10,
            "train_loss": 1.75,
            "val_loss": 1.85,
            "accuracy": 0.5
        },
        {
            "epoch": 15,
            "train_loss": 1.45,
            "val_loss": 1.55,
            "accuracy": 0.58
        },
        {
            "epoch": 20,
            "train_loss": 1.25,
            "val_loss": 1.35,
            "accuracy": 0.63
        },
        {
            "epoch": 25,
            "train_loss": 1.1,
            "val_loss": 1.18,
            "accuracy": 0.67
        },
        {
            "epoch": 30,
            "train_loss": 0.98,
            "val_loss": 1.05,
            "accuracy": 0.71
        },
        {
            "epoch": 35,
            "train_loss": 0.88,
            "val_loss": 0.95,
            "accuracy": 0.74
        },
        {
            "epoch": 40,
            "train_loss": 0.8,
            "val_loss": 0.89,
            "accuracy": 0.76
        },
        {
            "epoch": 45,
            "train_loss": 0.72,
            "val_loss": 0.84,
            "accuracy": 0.78
        },
        {
            "epoch": 50,
            "train_loss": 0.66,
            "val_loss": 0.8,
            "accuracy": 0.79
        },
        {
            "epoch": 55,
            "train_loss": 0.61,
            "val_loss": 0.76,
            "accuracy": 0.8
        },
        {
            "epoch": 60,
            "train_loss": 0.57,
            "val_loss": 0.73,
            "accuracy": 0.81
        },
        {
            "epoch": 65,
            "train_loss": 0.54,
            "val_loss": 0.71,
            "accuracy": 0.82
        },
        {
            "epoch": 70,
            "train_loss": 0.51,
            "val_loss": 0.69,
            "accuracy": 0.83
        },
        {
            "epoch": 75,
            "train_loss": 0.49,
            "val_loss": 0.68,
            "accuracy": 0.84
        },
        {
            "epoch": 80,
            "train_loss": 0.47,
            "val_loss": 0.67,
            "accuracy": 0.85
        },
        {
            "epoch": 85,
            "train_loss": 0.46,
            "val_loss": 0.66,
            "accuracy": 0.86
        },
        {
            "epoch": 90,
            "train_loss": 0.45,
            "val_loss": 0.66,
            "accuracy": 0.87
        },
        {
            "epoch": 95,
            "train_loss": 0.44,
            "val_loss": 0.65,
            "accuracy": 0.87
        },
        {
            "epoch": 100,
            "train_loss": 0.43,
            "val_loss": 0.65,
            "accuracy": 0.88
        },
        {
            "epoch": 105,
            "train_loss": 0.43,
            "val_loss": 0.65,
            "accuracy": 0.88
        },
        {
            "epoch": 110,
            "train_loss": 0.42,
            "val_loss": 0.64,
            "accuracy": 0.88
        },
        {
            "epoch": 115,
            "train_loss": 0.42,
            "val_loss": 0.64,
            "accuracy": 0.89
        },
        {
            "epoch": 120,
            "train_loss": 0.41,
            "val_loss": 0.64,
            "accuracy": 0.89
        }
    ],
    "traceLibrary": [
        {
            "id": "CASE_MUSIC_01",
            "question": "What is Z\u00fclf\u00fc Livaneli's place of birth's located in the administrative territorial entity?",
            "hops": [
                {
                    "num": 1,
                    "title": "Identifying Z\u00fclf\u00fc Livaneli",
                    "desc": "Matched Q248059 from query tokens."
                },
                {
                    "num": 2,
                    "title": "Retrieving Birthplace",
                    "desc": "Found relation (Q248059)-[:PLACE_OF_BIRTH]->(Q599813-Ilg\u0131n)."
                },
                {
                    "num": 3,
                    "title": "Resolving Admin Entity",
                    "desc": "Found relation (Q599813)-[:LOCATED_IN]->(Q185566-Konya)."
                }
            ],
            "ans": "Konya Province",
            "summary": "Z\u00fclf\u00fc Livaneli was born in Ilg\u0131n, which is located in Konya Province."
        }
    ]
};