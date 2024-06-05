import importlib.resources
import json

with importlib.resources.open_text("cltl.commons.language_data", "lexicon.json") as file:
    lexicon = json.load(file)

with importlib.resources.open_text("cltl.commons.language_data", "cfg.txt") as file:
    cfg = file.read()

def lexicon_lookup_subword(word, typ=None):
    match_word  = ""
    predicate = ""
    feature = lexicon_lookup(word, typ)
    if feature:
        predicate = feature["predicate"]
        match_word = word
    else:
        words = word.split('-')
        for w in words:
            feature = lexicon_lookup(w, typ)
            if feature:
                predicate = feature["predicate"]
                match_word = w
                break
    return predicate, match_word

def lexicon_lookup_subword_class(word, typ=None):
    match_word  = ""

    if word in lexicon[typ]:
        match_word = word
    else:
        words = word.split('-')
        for w in words:
            if w in lexicon[typ]:
                match_word = w
                break
    return match_word

def has_subword(word):
    words = word.split('-')
    for w in words:
        if w==word:
            return True
    return False

def lexicon_lookup(word, typ=None):
    """
    Look up and return features of a given word in the lexicon.
    :param word: word which we're looking up
    :param typ: type of word, if type is category then returns the lexicon entry and the word type
    :return: lexicon entry of the word
    """

    # Define pronoun categories.
    pronouns = lexicon["pronouns"]
    subject_pros = pronouns["subject"]
    object_pros = pronouns["object"]
    possessive_pros = pronouns["possessive"]
    dep_possessives = possessive_pros["dependent"]
    indep_possessives = possessive_pros["independent"]
    reflexive_pros = pronouns["reflexive"]
    indefinite_pros = pronouns["indefinite"]
    indefinite_person = indefinite_pros["person"]
    indefinite_place = indefinite_pros["place"]
    indefinite_thing = indefinite_pros["thing"]

    # Define verbal categories.
    verbs = lexicon["verbs"]
    to_be = verbs["to be"]
    aux_verbs = verbs["auxiliaries"]
    have = aux_verbs['have']
    to_do = aux_verbs["to do"]
    modals = aux_verbs["modals"]
    lexicals = verbs["lexical verbs"]

    # Define determiner categories.
    determiners = lexicon["determiners"]
    articles = determiners["articles"]
    demonstratives = determiners["demonstratives"]
    possessive_dets = determiners["possessives"]
    quantifiers = determiners["quantifiers"]
    wh_dets = determiners["wh-determiners"]
    numerals = determiners["numerals"]
    cardinals = numerals["cardinals"]
    ordinals = numerals["ordinals"]
    s_genitive = determiners["s-genitive"]

    # Define conjunction categories.
    conjunctions = lexicon["conjunctions"]
    coordinators = conjunctions["coordinating"]
    subordinators = conjunctions["subordinating"]

    # Define a question word category.
    question_words = lexicon["question words"]

    # Define a kinship category.
    kinship = lexicon["kinship"]
    # Define an activities category.
    activities = lexicon["activities"]
    # Define a kinship category.
    feelings = lexicon["feelings"]

    if typ == 'verb':
        categories = [to_be,
                      to_do,
                      have,
                      modals,
                      lexicals]

    elif typ == 'pos':
        categories = [dep_possessives]

    elif typ == 'to_be':
        categories = [to_be]

    elif typ == 'aux':
        categories = [to_do, to_be, have]

    elif typ == 'modal':
        categories = [modals]

    elif typ == 'pronouns':
        categories = [subject_pros,
                      object_pros,
                      dep_possessives,
                      indep_possessives,
                      reflexive_pros,
                      indefinite_person,
                      indefinite_place,
                      indefinite_thing]
    elif typ == 'lexical':
        categories = [lexicals]
    elif typ == 'kinship':
        categories = [kinship]
    elif typ == 'activities':
        categories = [activities]
    elif typ == 'feelings':
        categories = [feelings]
    elif typ == 'det':
        categories = [articles, demonstratives, possessive_dets, possessive_pros, cardinals, ordinals]
    else:
        categories = [subject_pros,
                      object_pros,
                      dep_possessives,
                      indep_possessives,
                      reflexive_pros,
                      indefinite_person,
                      indefinite_place,
                      indefinite_thing,
                      to_be,
                      to_do,
                      have,
                      modals,
                      lexicals,
                      articles,
                      demonstratives,
                      possessive_dets,
                      quantifiers,
                      wh_dets,
                      cardinals,
                      ordinals,
                      s_genitive,
                      coordinators,
                      subordinators,
                      question_words,
                      kinship,
                      activities,
                      feelings]

    for category in categories:
        if type(category)=='dict':
            for item in category:
                if word == item:
                    if typ == 'category':
                        return category, category[item]
                    #print('category, item', category, item)
                    return category[item]
    return None



