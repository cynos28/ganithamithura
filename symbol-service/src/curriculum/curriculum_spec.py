"""
Curriculum Specification for Math Tutor

Defines learning progressions for Grades 1-3 with detailed constraints
for each level and sublevel (Starter, Explorer, Solver, Champion).

Each specification includes:
- Operand ranges
- Result/product ranges
- Operation types allowed
- Examples
- BODMAS rule application
"""

CURRICULUM = {
    'GRADE_01': {
        'name': 'Grade 1 - Addition Learning Curve',
        'Level_1': { # "Addition (+) means joining"
            'Starter': {
                'name': 'Foundations',
                'focus': 'Addition means joining',
                'what_is_taught': 'Addition (+) means joining and finding how many altogether.',
                'students_should_understand': ['Addition means joining', 'Plus (+) sign means together'],
                'addends_max': 7,
                'result_max': 7,
                'examples': ['2 + 3 = 5', '1 + 2 = 3', '6 + 1 = 7'],
                'narrative_intro': "Hello, little friend. Welcome back. Today, we are going to learn something fun. We are going to learn about addition. Addition is something we use every day. We use addition when we get more things. We use addition when we put things together. Do not worry. We will go slowly. We will learn step by step. Let’s begin.",
                'story_1_guide': "Let me tell you a small story. I have apples. I have two apples. One apple. Two apples. These apples are mine. I am holding them carefully. Now something happens. My mother comes to me. She gives me more apples. She gives me three apples. One apple. Two apples. Three apples. Now I have my apples and my mother’s apples. (Pause). When we get more, we add. We use a special sign. This sign is called plus. Plus means join. Join means together. When we see plus, we put groups together. Now I put all the apples together. My two apples and my mother’s three apples join together. They are now one big group. Let us count together. One. Two. Three. Four. Five. Now I have five apples. Two plus three equals five.",
                'story_2_guide': "Let me tell you another story. I have toys. I have one toy. One toy is mine. Now my friend comes. My friend gives me more toys. My friend gives me four toys. One toy. Two toys. Three toys. Four toys. Now we join them. One toy and four toys join together. (Counting) One. Two. Three. Four. Five. One plus four equals five.",
                'conclusion_guide': "Let us remember what we learned today. Addition means joining. Plus means together. When we join groups, we find how many altogether. Two plus three equals five. One plus four equals five. Addition helps us know how many we have in all. You did a wonderful job today. You are learning well. Now you are ready to go back and practice. See you again."
            },
            'Explorer': { # "Patterns (Doubles)"
                'name': 'Patterns',
                'focus': 'Doubles and Near-Doubles',
                'what_is_taught': 'Recognizing simple addition patterns like doubles.',
                'students_should_understand': ['Same numbers make doubles', 'Doubles make addition easy'],
                'addends_max': 5,
                'result_max': 10,
                'examples': ['4 + 4 = 8', '3 + 4 = 7'],
                'narrative_intro': "Hello, little friend. Welcome back. You did very well. You already know that addition means joining. Today, we will learn something new. We will learn how some numbers like to join in special ways. Some numbers look the same. Some numbers look almost the same. These special ways help us understand addition better. Let’s go slowly and learn together.",
                'story_1_guide': "I have balls. I have four red balls. One red ball. Two red balls. Three red balls. Four red balls. Now I have blue balls. I have four blue balls. One blue ball. Two blue balls. Three blue balls. Four blue balls. I put the red balls and blue balls together. Four and four join. They are the same number. Let us count all the balls. One. Two. Three. Four. Five. Six. Seven. Eight. Four plus four equals eight. When the numbers are the same, we call this a double. Doubles are special. Same number and same number. Two and two. Three and three. Four and four. Doubles make addition easy.",
                'story_2_guide': "Now let me tell you another story. I have three pencils. One pencil. Two pencils. Three pencils. My teacher gives me four more pencils. One pencil. Two pencils. Three pencils. Four pencils. Three and four are close friends. They are almost the same. Now we join them together. Let us count. One. Two. Three. Four. Five. Six. Seven. Three plus four equals seven. This is called a near-double.",
                'conclusion_guide': "Let us remember today’s learning. Same numbers make doubles. Close numbers make near-doubles. Four plus four equals eight. Three plus four equals seven. These patterns help us understand addition. You are learning smart ways to add. Well done, little friend. Now you are ready to practice."
            },
            'Solver': { # "Building totals near 10"
                'name': 'Making Ten',
                'focus': 'Building totals near 10',
                'what_is_taught': 'Ten is a friendly number. Many pairs make 10.',
                'students_should_understand': ['10 is important', 'We can group to make 10'],
                'addends_max': 9,
                'result_max': 12,
                'examples': ['6 + 4 = 10', '7 + 3 = 10'],
                'narrative_intro': "Hello again, little learner. Welcome back. You already know how to join numbers. Today, we will learn about a special number. This number is ten. Ten is very important in addition. Let’s learn why.",
                'story_1_guide': "I have crayons. I have six crayons. One. Two. Three. Four. Five. Six. My friend gives me more crayons. My friend gives me four crayons. One. Two. Three. Four. Now I join them together. Six and four join. Six plus four equals ten. Ten feels complete. Ten is a friendly number. Many numbers like to join and make ten. Five and five. Six and four. Seven and three.",
                'story_2_guide': "Here is another story. I have seven stickers. My sister gives me three more. Seven plus three equals ten. Now she gives me one more sticker. Ten and one join. Ten plus one equals eleven. We moved past ten.",
                'conclusion_guide': "Let us remember. Ten is important. Many numbers join to make ten. Six plus four equals ten. Seven plus three equals ten. Understanding ten helps us add better. You are learning well. Now you are ready to continue."
            },
            'Champion': { # "Flexible thinking"
                'name': 'Flexible Thinking',
                'focus': 'Different ways to make the same total',
                'what_is_taught': 'Addition is flexible. Same answer can be made different ways.',
                'students_should_understand': ['More than one way to reach a total', 'Addition is flexible'],
                'addends_max': 9,
                'result_max': 14,
                'examples': ['6 + 6 = 12', '7 + 5 = 12'],
                'narrative_intro': "Hello, smart learner. Welcome back. Today, we will learn something special. We will learn that addition is flexible. That means there is more than one way to make the same answer.",
                'story_1_guide': "I want twelve blocks. I take six blocks. One. Two. Three. Four. Five. Six. Then I take six more blocks. Six and six join. Six plus six equals twelve.",
                'story_2_guide': "Now I try a different way. I take seven blocks. Then I take five blocks. Seven and five join. Seven plus five equals twelve. The total is the same. Addition is flexible. The answer can stay the same, even when the numbers change. We can choose different pairs. We can still reach the same total. Eight plus four equals twelve. Nine plus three equals twelve. Many paths. One answer.",
                'conclusion_guide': "Let us remember today’s lesson. Addition is flexible. The same total can be made in many ways. Six plus six equals twelve. Seven plus five equals twelve. Understanding is more important than speed. You are thinking like a champion. Now you are ready to practice. See you again."
            }
        },
        'Level_2': { # "Missing Addends"
            'Starter': {
                'name': 'Missing Parts',
                'focus': 'Missing Addends',
                'what_is_taught': 'Sometimes a number is hidden. We can find it.',
                'students_should_understand': ['Addition has parts and a whole', 'Hidden numbers can be found'],
                'operations': ['missing_addend'],
                'addends_max': 9,
                'result_max': 10,
                'examples': ['4 + ? = 9', '6 + ? = 10'],
                'narrative_intro': "Hello, little friend. Welcome back. You have been learning very well. You already know how to add numbers. You know that addition means joining. Today, we will learn something new about addition. Sometimes, we do not see all the numbers. Sometimes, one number is hidden. Do not worry. We can still find the answer. We will go slowly. We will learn step by step. Let’s begin.",
                'story_1_guide': "Let me tell you a small story. I have apples. Some apples are on the table. Some apples are in a basket. Together, there are nine apples. I can see the apples on the table. I see four apples. One apple. Two apples. Three apples. Four apples. I cannot see the apples in the basket. But I know they are there. I know the total is nine. When one part is hidden, addition still works. The apples on the table and the apples in the basket join together. Four apples plus something equals nine apples. Let us think carefully. Four apples are here. Nine apples are in all. The missing part is five. Four plus five equals nine.",
                'story_2_guide': "Let me tell you another story. I have toys. Some toys are on the floor. Some toys are in a box. Together, there are ten toys. I can see six toys on the floor. One toy. Two toys. Three toys. Four toys. Five toys. Six toys. I cannot see the toys in the box. But I know the total is ten. Six plus something equals ten. The missing part is four. Six plus four equals ten.",
                'conclusion_guide': "Let us remember what we learned today. Addition has parts and a whole. Sometimes one part is hidden. We can find the missing part. Four plus five equals nine. Six plus four equals ten. You are learning to think carefully. You are doing a wonderful job. Now you are ready."
            },
            'Explorer': { # "Crossing 10"
                'name': 'Crossing 10',
                'focus': 'Crossing the 10 boundary',
                'what_is_taught': 'What happens when numbers go past 10.',
                'students_should_understand': ['Numbers become bigger', 'Crossing 10'],
                'addends_max': 9,
                'result_max': 15,
                'examples': ['9 + 2 = 11', '8 + 5 = 13'],
                'narrative_intro': "Hello, little explorer. Welcome back. You already know how to add numbers. You know how to join groups. Today, we will learn something exciting. We will learn what happens when numbers go past ten. Ten is a special number. When we pass ten, numbers become bigger. Do not worry. We will go slowly. We will learn step by step. Let’s begin.",
                'story_1_guide': "Let me tell you a small story. I have balls. I have nine balls. One. Two. Three. Four. Five. Six. Seven. Eight. Nine. Now my friend comes. My friend gives me two more balls. When we add to nine, we reach ten. Nine plus one makes ten. One more makes eleven. Nine plus two equals eleven.",
                'story_2_guide': "Here is another story. I have eight crayons. One to eight. My teacher gives me five more crayons. Eight plus five equals thirteen.",
                'conclusion_guide': "Let us remember what we learned today. Ten is a special number. Some additions cross ten. Nine plus two equals eleven. Eight plus five equals thirteen. You are learning bigger numbers. You are doing very well. Now you are ready to go back and practice. See you again."
            },
            'Solver': { # "Adding Three Numbers"
                'name': 'Three Numbers',
                'focus': 'Adding three numbers',
                'what_is_taught': 'We can join three groups together by grouping.',
                'students_should_understand': ['Group two first', 'Order does not change total'],
                'operations': ['three_addends'],
                'addends_max': 9,
                'result_max': 15,
                'examples': ['4 + 5 + 3 = 12'],
                'narrative_intro': "Hello again, little thinker. Welcome back. You know how to add two numbers. Today, we will add three numbers. Adding three numbers means joining more groups. We will take our time. We will think carefully. Let’s begin.",
                'story_1_guide': "Let me tell you a story. I have three groups of blocks. The first group has four blocks. The second group has five blocks. The third group has three blocks. When we add three numbers, we can group them. We choose two numbers first. Four and five join. Four plus five equals nine. Now nine joins with three. Nine plus three equals twelve. Four plus five plus three equals twelve.",
                'story_2_guide': "Here is another example. I have six blocks, two blocks, and five blocks. Six and two make eight. Eight and five make thirteen.",
                'conclusion_guide': "Let us remember today’s learning. Three numbers can join together. Grouping makes addition easier. Four plus five plus three equals twelve. Six plus two plus five equals thirteen. You are learning strong math ideas. Well done. Now you are ready to go back and practice."
            },
            'Champion': { # "Larger Facts"
                'name': 'Larger Facts',
                'focus': 'Larger addition confidence',
                'what_is_taught': 'Using all skills for bigger numbers up to 17.',
                'students_should_understand': ['Big numbers follow same rules', 'Confidence'],
                'addends_max': 10,
                'result_max': 17,
                'examples': ['9 + 8 = 17', '10 + 5 = 15'],
                'narrative_intro': "Welcome back, champion learner. You have learned many addition ideas. You can join numbers. You can cross ten. You can add three numbers. Today, we will use all of this together. You are ready for bigger numbers. Let’s begin.",
                'story_1_guide': "Let me tell you a story. I have nine stickers. My friend gives me eight more stickers. Nine plus eight equals seventeen.",
                'story_2_guide': "I have ten blocks. My teacher gives me five more blocks. Ten plus five equals fifteen.",
                'conclusion_guide': "Let us remember today’s lesson. Addition works for big numbers too. The same ideas always help us. Nine plus eight equals seventeen. Ten plus five equals fifteen. You are thinking like a champion. You should feel proud. Now you are ready to go back and practice. See you again."
            }
        },
        'Level_3': { # "Missing Addends with Larger Totals"
            'Starter': {
                'name': 'Higher Missing Addends',
                'focus': 'Missing parts with totals near 20',
                'what_is_taught': 'Finding hidden numbers when the total is large (16-18).',
                'students_should_understand': ['Reasoning replaces counting', 'Part + Part = Whole'],
                'addends_max': 10,
                'result_max': 18,
                'examples': ['8 + ? = 16', '9 + ? = 18'],
                'narrative_intro': "Hello, little friend. Welcome back. You have learned a lot about addition. You know how numbers join. You know how to find totals. Today, we will see bigger totals. One number may still be hidden. But do not worry. The idea is the same. We will go slowly. We will think carefully. Let’s begin.",
                'story_1_guide': "Let me tell you a small story. I know the total number of apples is sixteen. Sixteen apples in all. I can see some apples. I see eight apples. One. Two. Three. Four. Five. Six. Seven. Eight. I cannot see the rest of the apples. But I know they are there. When one part is hidden, we think about the whole. Eight apples are here. Sixteen apples are in all. Eight plus eight equals sixteen.",
                'story_2_guide': "Here is another story. The total is eighteen toys. I can see nine toys. One to nine. Nine plus nine equals eighteen.",
                'conclusion_guide': "Let us remember what we learned today. Sometimes a number is hidden. We can still find it. Eight plus eight equals sixteen. Nine plus nine equals eighteen. You are learning strong thinking skills. Well done. Now you are ready to go back and practice."
            },
            'Explorer': { # "Higher Patterns"
                'name': 'Higher Patterns',
                'focus': 'Doubles/Near-Doubles to 20',
                'what_is_taught': 'Using patterns for sums like 8+9.',
                'students_should_understand': ['Doubles help us solve near-doubles'],
                'addends_max': 10,
                'result_max': 20,
                'examples': ['8 + 8 = 16', '8 + 9 = 17'],
                'narrative_intro': "Welcome back, little explorer. You already know about patterns in addition. Today, the numbers will be bigger. But patterns still help us. Let us look at some strong number pairs. Let’s begin.",
                'story_1_guide': "I have eight blocks. I take eight more blocks. Eight plus eight equals sixteen. These numbers are the same. This is called a double.",
                'story_2_guide': "Now I try something close. I take eight blocks. Then I take nine blocks. Eight plus nine equals seventeen. Eight and nine are close numbers. This is a near-double.",
                'conclusion_guide': "Let us remember today’s learning. Eight plus eight equals sixteen. Eight plus nine equals seventeen. Patterns help us add. Even with bigger numbers. You are learning smart ways to think. Now you are ready to go back and practice."
            },
            'Solver': { # "Grouping to 20"
                'name': 'Grouping to 20',
                'focus': 'Three numbers summing to ~20',
                'what_is_taught': 'Grouping efficiently to reach totals near 20.',
                'students_should_understand': ['Look for pairs that make 10 first'],
                'addends_max': 10,
                'result_max': 20,
                'examples': ['6 + 7 + 5 = 18'],
                'narrative_intro': "Hello again, careful thinker. You know how to add three numbers. Today, the totals will be bigger. We will stay calm and focused. Grouping will help us. Let’s begin.",
                'story_1_guide': "I have three numbers. Six. Seven. Five. We add them step by step. Six and seven make thirteen. Thirteen and five make eighteen. Six plus seven plus five equals eighteen.",
                'story_2_guide': "Here is another example. Eight plus six plus four. Six and four make ten. Ten and eight make eighteen.",
                'conclusion_guide': "Let us remember what we learned today. Three numbers can make big totals. Grouping helps us think clearly. Six plus seven plus five equals eighteen. Eight plus six plus four equals eighteen. You are solving big ideas now. Well done."
            },
            'Champion': { # "Target 20"
                'name': 'Target 20',
                'focus': 'Making exactly 20',
                'what_is_taught': 'Different combinations that result in exactly 20.',
                'students_should_understand': ['Working backwards', 'Goal is 20'],
                'addends_max': 12,
                'result_max': 20,
                'examples': ['? + 9 = 20', '8 + 7 + 5 = 20'],
                'narrative_intro': "Welcome back, math champion. You have learned many addition ideas. Today, we will reach a big goal. The goal is twenty. You are ready for this step. Let’s begin.",
                'story_1_guide': "I see nine. The total must be twenty. Nine plus eleven equals twenty.",
                'story_2_guide': "Now I try another way. Eight plus seven plus five. Eight and seven make fifteen. Fifteen and five make twenty.",
                'conclusion_guide': "Let us remember today’s lesson. Twenty can be made in many ways. Nine plus eleven equals twenty. Eight plus seven plus five equals twenty. You have reached a big goal. You are thinking like a champion. Now you are ready to go back and practice. See you again."
            }
        },
    },
    'GRADE_02': { # User referred to this as "Level 2"
        'name': 'Grade 2 - Deeper Addition Concepts',
        'Level_1': { 
            'Starter': {
                'name': 'Missing Parts',
                'focus': 'Missing Addends',
                'what_is_taught': 'Sometimes a number is hidden. We find the missing part.',
                'students_should_understand': ['Addition has parts and a whole', 'We can find the missing part'],
                'operations': ['missing_addend'],
                'addends_max': 9,
                'result_max': 10,
                'examples': ['4 + ? = 9', '6 + ? = 10'],
                'narrative_intro': 'Hello! Today we play a mystery game. One number is hiding!',
                'what_should_teach': 'Story about apples in a basket (hidden) vs on table (visible).'
            },
            'Explorer': {
                'name': 'Crossing 10',
                'focus': 'Crossing 10 boundary',
                'what_is_taught': 'What happens when numbers get bigger than 10? They "cross" ten.',
                'students_should_understand': ['Numbers grow past 10', '9 needs 1 more to be 10'],
                'addends_max': 9,
                'result_max': 15,
                'examples': ['9 + 2 = 11', '8 + 5 = 13'],
                'narrative_intro': 'Hello Explorer. Today we see what happens when numbers get really big and cross 10.',
                'what_should_teach': 'Story about having 9 balls and getting 2 more.'
            },
            'Solver': {
                'name': 'Three Numbers',
                'focus': 'Adding three numbers',
                'what_is_taught': 'We can join three groups together by starting with two.',
                'students_should_understand': ['Group two numbers first', 'Then add the third'],
                'operations': ['three_addends'],
                'addends_max': 9,
                'result_max': 15,
                'examples': ['4 + 5 + 3 = 12'],
                'narrative_intro': 'Hello Thinker. Today we join THREE groups together.',
                'what_should_teach': 'Story about three groups of blocks.'
            },
            'Champion': {
                'name': 'Larger Facts',
                'focus': 'Larger addition confidence',
                'what_is_taught': 'Using all our skills for bigger numbers up to 20.',
                'students_should_understand': ['Big numbers follow same rules', 'Trust your counting'],
                'addends_max': 10,
                'result_max': 17,
                'examples': ['9 + 8 = 17', '10 + 5 = 15'],
                'narrative_intro': 'Hello Champion. You are ready for big numbers!',
                'what_should_teach': 'Story about 9 stickers plus 8 stickers.'
            }
        }
    },
    'GRADE_03': { # User referred to this as "Level 3"
        'name': 'Grade 3 - Advanced Mental Strategies',
        'Level_1': {
            'Starter': {
                'name': 'Higher Missing Addends',
                'focus': 'Missing parts with totals near 20',
                'what_is_taught': 'Finding hidden numbers when the total is large (16-18).',
                'students_should_understand': ['Reasoning replaces counting', 'Part + Part = Whole'],
                'addends_max': 10,
                'result_max': 18,
                'examples': ['8 + ? = 16', '9 + ? = 18'],
                'narrative_intro': 'Hello! We revisit our mystery game, but the numbers are bigger now.',
                'what_should_teach': 'Story about 16 total apples, seeing only 8.'
            },
            'Explorer': {
                'name': 'Higher Patterns',
                'focus': 'Doubles/Near-Doubles to 20',
                'what_is_taught': 'Using patterns for sums like 8+9.',
                'students_should_understand': ['Doubles help us solve near-doubles'],
                'addends_max': 10,
                'result_max': 20,
                'examples': ['8 + 8 = 16', '8 + 9 = 17'],
                'narrative_intro': 'Hello! Let\'s look for number patterns in the big numbers.',
                'what_should_teach': 'Story comparing 8+8 and 8+9.'
            },
            'Solver': {
                'name': 'Grouping to 20',
                'focus': 'Three numbers summing to ~20',
                'what_is_taught': 'Grouping efficiently to reach totals near 20.',
                'students_should_understand': ['Look for pairs that make 10 first'],
                'addends_max': 10,
                'result_max': 20,
                'examples': ['6 + 7 + 5 = 18'],
                'narrative_intro': 'Hello! We are building big towers with three numbers.',
                'what_should_teach': 'Story about 6, 7, and 5 joining.'
            },
            'Champion': {
                'name': 'Target 20',
                'focus': 'Making exactly 20',
                'what_is_taught': 'Different combinations that result in exactly 20.',
                'students_should_understand': ['Working backwards from target', 'Start with the biggest number'],
                'addends_max': 12,
                'result_max': 20,
                'examples': ['? + 9 = 20', '8 + 7 + 5 = 20'],
                'narrative_intro': 'Hello Champion. Our goal today is the number TWENTY.',
                'what_should_teach': 'Story about different ways to fill a box of 20.'
            }
        }
    }
}

def get_curriculum_spec(grade: str, level: int, sublevel: str) -> dict:
    """
    Get curriculum specification for a student profile.

    Args:
        grade: 'GRADE_01', 'GRADE_02', or 'GRADE_03'
        level: 1, 2, or 3
        sublevel: 'Starter', 'Explorer', 'Solver', or 'Champion'

    Returns:
        Dictionary with curriculum specification and constraints
    """
    try:
        grade_key = f'GRADE_{grade.zfill(2)}'
        level_key = f'Level_{level}'

        spec = CURRICULUM.get(grade_key, {}).get(level_key, {}).get(sublevel, {})

        if spec:
            return spec
        else:
            raise ValueError(f"Invalid curriculum spec: {grade}/{level}/{sublevel}")

    except Exception as e:
        print(f"Error fetching curriculum: {e}")
        return {}

def get_bodmas_rules() -> dict:
    """
    Get BODMAS (order of operations) rules.

    Returns:
        Dictionary defining operation order and rules
    """
    return {
        'order': ['Brackets', 'Orders (Powers)', 'Division', 'Multiplication', 'Addition', 'Subtraction'],
        'acronym': 'BODMAS',
        'description': 'Order of operations to follow when solving equations',
        'rules': {
            'Brackets': 'Solve expressions inside brackets first',
            'Orders': 'Apply powers and roots',
            'Division': 'Division and multiplication are equal priority (left to right)',
            'Multiplication': 'Multiplication and division are equal priority (left to right)',
            'Addition': 'Addition and subtraction are equal priority (left to right)',
            'Subtraction': 'Subtraction follows addition with same priority'
        }
    }

if __name__ == "__main__":
    # Test curriculum retrieval
    print("Testing Curriculum Specification")
    print("=" * 50)

    # Example: Grade 1, Level 2, Starter
    spec = get_curriculum_spec('01', 2, 'Starter')
    print(f"\nGrade 1, Level 2, Starter:")
    print(f"Description: {spec.get('description')}")
    print(f"Operand Max: {spec.get('result_max')}")
    print(f"Examples: {spec.get('examples')}")

    # Example: Grade 3, Level 3, Champion
    spec = get_curriculum_spec('03', 3, 'Champion')
    print(f"\nGrade 3, Level 3, Champion:")
    print(f"Description: {spec.get('description')}")
    print(f"Examples: {spec.get('examples')}")

    # BODMAS rules
    bodmas = get_bodmas_rules()
    print(f"\nBODMAS Order: {' → '.join(bodmas['order'])}")
